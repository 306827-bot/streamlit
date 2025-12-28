import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import os

# ---------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------
st.set_page_config(page_title="Dashboard de Ventas", layout="wide")
st.title(" Dashboard de Ventas – Vista Ejecutiva")

# ---------------------------------------
# CARGA DATASET DESDE DOS ZIP
# ---------------------------------------
@st.cache_data
def load_and_merge_zips(zip_paths):
    dfs = []

    for zip_path in zip_paths:
        with zipfile.ZipFile(zip_path, "r") as z:
            csv_files = [f for f in z.namelist() if f.endswith(".csv")]

            if not csv_files:
                st.error(f"No hay CSV dentro de {zip_path}")
                st.stop()

            for csv_name in csv_files:
                with z.open(csv_name) as f:
                    df_tmp = pd.read_csv(f, parse_dates=["date"])
                    dfs.append(df_tmp)

    df = pd.concat(dfs, ignore_index=True)

    df = df[
        [
            "date",
            "store_nbr",
            "state",
            "family",
            "sales",
            "onpromotion",
            "transactions",
        ]
    ]

    # Limpieza mínima
    df["onpromotion"] = df["onpromotion"].fillna(0)
    df["transactions"] = df["transactions"].fillna(0)

    # Variables temporales
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.dayofweek + 1

    return df


ZIP_FILES = ["parte_1.zip", "parte_2.zip"]

for z in ZIP_FILES:
    if not os.path.exists(z):
        st.error(f" No se encuentra {z} en el repositorio")
        st.stop()

df = load_and_merge_zips(ZIP_FILES)

# ---------------------------------------
# TABS
# ---------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [" Visión Global", " Por Tienda", " Por Estado", " Extra"]
)

# =======================================
# TAB 1: VISIÓN GLOBAL
# =======================================
with tab1:
    st.header("Visión global de las ventas")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Número total de tiendas", f"{df['store_nbr'].nunique():,}".replace(",", "."))
    col2.metric("Número total de productos", f"{df['family'].nunique():,}".replace(",", "."))
    col3.metric("Estados cubiertos", f"{df['state'].nunique():,}".replace(",", "."))

    months = df["date"].dt.to_period("M")
    col4.metric(
        "Periodo analizado",
        f"{months.nunique():,}".replace(",", ".") + " meses",
        f"{months.min()} → {months.max()}"
    )

    st.markdown("---")

    # Top productos
    st.subheader("Top 10 productos más vendidos")

    top_products = (
        df.groupby("family")["sales"]
        .sum()
        .sort_values()
        .tail(10)
        .reset_index()
    )

    st.plotly_chart(
        px.bar(
            top_products,
            x="sales",
            y="family",
            orientation="h",
            color="sales",
            color_continuous_scale="Blues",
            text=top_products["sales"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        ),
        use_container_width=True
    )

    # Ventas por tienda
    st.subheader("Distribución de ventas por tienda")

    sales_by_store = df.groupby("store_nbr")["sales"].sum().reset_index()

    st.plotly_chart(
        px.bar(
            sales_by_store,
            x="store_nbr",
            y="sales",
            color="sales",
            color_continuous_scale="Viridis",
            text=sales_by_store["sales"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        ),
        use_container_width=True
    )

    # PROMOCIONES – CAMBIO A BARRAS VERTICALES
    st.subheader("Top 10 tiendas con mayores ventas en promoción")

    promo_sales_store = (
        df[df["onpromotion"] == 1]
        .groupby("store_nbr")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    st.plotly_chart(
        px.bar(
            promo_sales_store,
            x="store_nbr",
            y="sales",
            color="sales",
            color_continuous_scale="Reds",
            text=promo_sales_store["sales"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        ),
        use_container_width=True
    )

    st.markdown("---")

    # Estacionalidad
    st.subheader("Estacionalidad de las ventas")

    day_map = {
        1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves",
        5: "Viernes", 6: "Sábado", 7: "Domingo"
    }

    dow = df.groupby("day_of_week")["sales"].mean().reset_index()
    dow["day_name"] = dow["day_of_week"].map(day_map)

    st.plotly_chart(
        px.bar(
            dow,
            x="day_name",
            y="sales",
            color="sales",
            text=dow["sales"].apply(lambda x: f"{x:,.1f}".replace(",", "."))
        ),
        use_container_width=True
    )

    weekly_avg = df.groupby("week")["sales"].mean().reset_index()
    st.plotly_chart(px.bar(weekly_avg, x="week", y="sales"), use_container_width=True)

    month_map = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    monthly = df.groupby("month")["sales"].mean().reset_index()
    monthly["month_name"] = monthly["month"].map(month_map)

    st.plotly_chart(px.bar(monthly, x="month_name", y="sales"), use_container_width=True)

# =======================================
# TAB 2: POR TIENDA
# =======================================
with tab2:
    st.header("Análisis por tienda")

    store = st.selectbox("Selecciona una tienda", sorted(df["store_nbr"].unique()))
    df_store = df[df["store_nbr"] == store]

    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas totales", f"{df_store['sales'].sum():,.0f}".replace(",", "."))
    col2.metric("Productos vendidos", f"{len(df_store):,}".replace(",", "."))
    col3.metric("Productos en promoción", f"{df_store[df_store['onpromotion']==1].shape[0]:,}".replace(",", "."))

    sales_year = df_store.groupby("year")["sales"].sum().reset_index()
    st.plotly_chart(px.bar(sales_year, x="year", y="sales"), use_container_width=True)

# =======================================
# TAB 3: POR ESTADO
# =======================================
with tab3:
    st.header("Análisis por estado")

    state = st.selectbox(
        "Selecciona un estado",
        sorted(df["state"].dropna().unique())
    )

    df_state = df[df["state"] == state]

    st.markdown("---")

    # Evolución transacciones
    trans_year = df_state.groupby("year")["transactions"].sum().reset_index()

    st.subheader(f"Evolución anual de las transacciones – {state}")

    st.plotly_chart(
        px.bar(
            trans_year,
            x="year",
            y="transactions",
            color="transactions",
            color_continuous_scale="Teal"
        ),
        use_container_width=True
    )

    st.markdown("---")

    # Top 10 tiendas (VERTICAL, COME PROMOCIONES)
    st.subheader("Top 10 tiendas con mayores ventas en el estado")

    top_stores = (
        df_state.groupby("store_nbr")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    top_stores["store_nbr"] = top_stores["store_nbr"].astype(str)

    st.plotly_chart(
        px.bar(
            top_stores,
            x="store_nbr",
            y="sales",
            color="sales",
            color_continuous_scale="Reds",
            text=top_stores["sales"].apply(lambda x: f"{int(x):,}".replace(",", "."))
        ).update_traces(textposition="outside"),
        use_container_width=True
    )

# =======================================
# TAB 4: EXTRA
# =======================================
with tab4:
    st.header("Patrones de venta: visión avanzada")

    st.subheader("Mapa de calor: ventas medias por día y mes")

    month_map = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    pivot = (
        df.groupby(["month", "day_of_week"])["sales"]
        .mean()
        .reset_index()
    )

    pivot["Mes"] = pivot["month"].map(month_map)
    pivot["Día"] = pivot["day_of_week"].map(day_map)

    heat = pivot.pivot(index="Día", columns="Mes", values="sales")

    st.plotly_chart(
        px.imshow(
            heat,
            aspect="auto",
            color_continuous_scale="Blues",
            labels=dict(
                x="Mes",
                y="Día de la semana",
                color="Ventas medias"
            )
        ),
        use_container_width=True
    )
