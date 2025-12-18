# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------
# CONFIGURAZIONE PAGINA (UNA SOLA VOLTA)
# ---------------------------------------
st.set_page_config(page_title="Dashboard Vendite", layout="wide")

st.title("📊 Dashboard Vendite")

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
# TABS PRINCIPALI
# ---------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["🌍 Global Overview", "🏪 Per Negozio", "🌎 Per Stato", "✨ Extra"]
)

# =======================================
# TAB 1: OVERVIEW GLOBALE
# =======================================
with tab1:
    st.header("Overview Globale delle Vendite")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Negozi", df["store_nbr"].nunique())
    col2.metric("Prodotti", df["family"].nunique())
    col3.metric("Stati", df["state"].nunique())
    col4.metric("Righe dataset", len(df))

    st.markdown("---")

    st.subheader("Top 10 Prodotti più venduti")
    top_prod = (
        df.groupby("family")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    st.plotly_chart(
        px.bar(top_prod, x="sales", y="family", orientation="h"),
        use_container_width=True
    )

    st.subheader("Distribuzione vendite per negozio")
    sales_store = df.groupby("store_nbr")["sales"].sum().reset_index()
    st.plotly_chart(
        px.histogram(sales_store, x="sales", nbins=30),
        use_container_width=True
    )

# =======================================
# TAB 2: ANALISI PER NEGOZIO
# =======================================
with tab2:
    st.header("Analisi per Negozio")

    store = st.selectbox(
        "Seleziona negozio",
        sorted(df["store_nbr"].unique())
    )

    df_store = df[df["store_nbr"] == store]

    col1, col2, col3 = st.columns(3)
    col1.metric("Vendite totali", round(df_store["sales"].sum(), 2))
    col2.metric("Transazioni", len(df_store))
    col3.metric("Promo attive", df_store["onpromotion"].sum())

    st.subheader("Vendite per anno")
    sales_year = df_store.groupby("year")["sales"].sum().reset_index()
    st.plotly_chart(
        px.bar(sales_year, x="year", y="sales"),
        use_container_width=True
    )

# =======================================
# TAB 3: ANALISI PER STATO
# =======================================
with tab3:
    st.header("Analisi per Stato")

    state = st.selectbox(
        "Seleziona stato",
        sorted(df["state"].dropna().unique())
    )

    df_state = df[df["state"] == state]

    st.subheader("Vendite per anno")
    sales_year = df_state.groupby("year")["sales"].sum().reset_index()
    st.plotly_chart(
        px.bar(sales_year, x="year", y="sales"),
        use_container_width=True
    )

    st.subheader("Top 10 negozi nello stato")
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

# =======================================
# TAB 4: EXTRA / INSIGHTS
# =======================================
with tab4:
    st.header("Insights aggiuntivi")

    st.subheader("Heatmap vendite medie (mese vs giorno)")
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

    st.subheader("Vendite medie: Promo vs No Promo")
    promo_cmp = df.groupby("onpromotion")["sales"].mean().reset_index()
    st.plotly_chart(
        px.bar(promo_cmp, x="onpromotion", y="sales"),
        use_container_width=True
    )

    st.success("Dashboard pronta per il CEO 🚀")
