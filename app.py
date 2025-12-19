# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------
st.set_page_config(page_title="Dashboard Vendite", layout="wide")
st.title("📊 Dashboard Vendite – Executive View")

# ---------------------------------------
# UPLOAD DATASET
# ---------------------------------------
st.sidebar.header("Caricamento dati")

uploaded_file = st.sidebar.file_uploader(
    "Carica il dataset CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.warning("⬅️ Carica un file CSV per visualizzare il dashboard")
    st.stop()

# ---------------------------------------
# CARICAMENTO E PREPROCESSING
# ---------------------------------------
@st.cache_data
def load_data(file):
    df = pd.read_csv(file, parse_dates=["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.dayofweek + 1  # 1=Lun ... 7=Dom

    return df

df = load_data(uploaded_file)

# ---------------------------------------
# TABS
# ---------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["🌍 Global Overview", "🏪 Per Negozio", "🌎 Per Stato", "✨ Extra"]
)

# =======================================
# TAB 1: OVERVIEW GLOBALE
# =======================================
with tab1:
    st.header("Overview Globale delle Vendite")

    # -----------------------------------
    # a) Indicatori chiave
    # -----------------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Numero totale negozi", df["store_nbr"].nunique())
    col2.metric("Numero totale prodotti", df["family"].nunique())
    col3.metric("Stati coperti", df["state"].nunique())

    months = df["date"].dt.to_period("M")
    col4.metric(
        "Periodo analizzato",
        f"{months.nunique()} mesi",
        f"{months.min()} → {months.max()}"
    )

    st.markdown("---")

    # -----------------------------------
    # b) Top prodotti
    # -----------------------------------
    st.subheader("Top 10 Prodotti più venduti")

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
            text="sales",
            labels={"sales": "Vendite totali", "family": "Prodotto"}
        ).update_traces(texttemplate="%{text:.0f}", textposition="outside"),
        use_container_width=True
    )

    # -----------------------------------
    # c) Vendite per negozio
    # -----------------------------------
    st.subheader("Distribuzione delle vendite per negozio")

    sales_by_store = (
        df.groupby("store_nbr")["sales"]
        .sum()
        .reset_index()
    )

    st.plotly_chart(
        px.bar(
            sales_by_store,
            x="store_nbr",
            y="sales",
            color="sales",
            color_continuous_scale="Viridis",
            text="sales",
            labels={"store_nbr": "Negozio", "sales": "Vendite totali"}
        ).update_traces(texttemplate="%{text:.0f}", textposition="outside"),
        use_container_width=True
    )

    # -----------------------------------
    # d) TOP 10 negozi per vendite in promozione (CORRETTO)
    # -----------------------------------
    st.subheader("Top 10 negozi con maggiori vendite in promozione")

    promo_sales_store = (
        df[df["onpromotion"] == 1]
        .groupby("store_nbr")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .sort_values("sales")
    )

    st.plotly_chart(
        px.bar(
            promo_sales_store,
            x="sales",
            y="store_nbr",
            orientation="h",
            color="sales",
            color_continuous_scale="Reds",
            text="sales",
            labels={
                "store_nbr": "Negozio",
                "sales": "Vendite in promozione"
            }
        ).update_traces(texttemplate="%{text:.0f}", textposition="outside"),
        use_container_width=True
    )

    st.markdown("---")

    # -----------------------------------
    # e) Stagionalità
    # -----------------------------------
    st.subheader("Stagionalità delle vendite")

    # Giorni della settimana
    day_map = {
        1: "Lunedì",
        2: "Martedì",
        3: "Mercoledì",
        4: "Giovedì",
        5: "Venerdì",
        6: "Sabato",
        7: "Domenica"
    }

    dow = df.groupby("day_of_week")["sales"].mean().reset_index()
    dow["day_name"] = dow["day_of_week"].map(day_map)

    st.plotly_chart(
        px.bar(
            dow,
            x="day_name",
            y="sales",
            color="sales",
            color_continuous_scale="Teal",
            text="sales",
            labels={"day_name": "Giorno della settimana", "sales": "Vendite medie"}
        ).update_traces(texttemplate="%{text:.1f}", textposition="outside"),
        use_container_width=True
    )

    # Vendite medie per settimana dell'anno
    weekly_avg = df.groupby("week")["sales"].mean().reset_index()

    st.plotly_chart(
        px.bar(
            weekly_avg,
            x="week",
            y="sales",
            color="sales",
            color_continuous_scale="Cividis",
            labels={"week": "Settimana dell'anno", "sales": "Vendite medie"}
        ),
        use_container_width=True
    )

    # Vendite medie per mese
    month_map = {
        1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile",
        5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto",
        9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"
    }

    monthly = df.groupby("month")["sales"].mean().reset_index()
    monthly["month_name"] = monthly["month"].map(month_map)

    st.plotly_chart(
        px.bar(
            monthly,
            x="month_name",
            y="sales",
            color="sales",
            color_continuous_scale="Plasma",
            text="sales",
            labels={"month_name": "Mese", "sales": "Vendite medie"}
        ).update_traces(texttemplate="%{text:.1f}", textposition="outside"),
        use_container_width=True
    )



# =======================================
# TAB 2: PER NEGOZIO
# =======================================
with tab2:
    st.header("Analisi per negozio")

    store = st.selectbox(
        "Seleziona negozio",
        sorted(df["store_nbr"].unique())
    )

    df_store = df[df["store_nbr"] == store]

    col1, col2, col3 = st.columns(3)
    col1.metric("Vendite totali", round(df_store["sales"].sum(), 2))
    col2.metric("Prodotti venduti", df_store["family"].count())
    col3.metric(
        "Prodotti venduti in promozione",
        df_store[df_store["onpromotion"] == 1]["family"].count()
    )

    st.subheader("Vendite totali per anno")
    sales_year = df_store.groupby("year")["sales"].sum().reset_index()
    st.plotly_chart(
        px.bar(sales_year, x="year", y="sales"),
        use_container_width=True
    )

# =======================================
# TAB 3: PER STATO
# =======================================
with tab3:
    st.header("Analisi per stato")

    state = st.selectbox(
        "Seleziona stato",
        sorted(df["state"].dropna().unique())
    )

    df_state = df[df["state"] == state]

    st.subheader("Numero totale di transazioni per anno")
    trans_year = df_state.groupby("year")["transactions"].sum().reset_index()
    st.plotly_chart(
        px.bar(trans_year, x="year", y="transactions"),
        use_container_width=True
    )

    st.subheader("Ranking negozi per vendite")
    top_stores = (
        df_state.groupby("store_nbr")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    st.plotly_chart(
        px.bar(top_stores, x="sales", y="store_nbr", orientation="h"),
        use_container_width=True
    )

    st.subheader("Prodotto più venduto nello stato")
    top_product = (
        df_state.groupby("family")["sales"]
        .sum()
        .idxmax()
    )
    st.success(f"📦 Prodotto più venduto: **{top_product}**")

# =======================================
# TAB 4: EXTRA / SURPRISE
# =======================================
with tab4:
    st.header("Insights avanzati per il management")

    st.subheader("Heatmap vendite medie (mese vs giorno settimana)")
    pivot = (
        df.groupby(["month", "day_of_week"])["sales"]
        .mean()
        .reset_index()
    )
    heat = pivot.pivot(
        index="day_of_week",
        columns="month",
        values="sales"
    )
    st.plotly_chart(
        px.imshow(heat, aspect="auto"),
        use_container_width=True
    )

    st.subheader("Confronto vendite medie: Promo vs No Promo")
    promo_cmp = df.groupby("onpromotion")["sales"].mean().reset_index()
    st.plotly_chart(
        px.bar(promo_cmp, x="onpromotion", y="sales"),
        use_container_width=True
    )

    st.success("Dashboard pronta per il CEO 🚀")
