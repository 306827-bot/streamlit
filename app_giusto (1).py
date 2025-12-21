import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# -------------------------------------------------------------
# CONFIGURAZIONE STREAMLIT
# -------------------------------------------------------------
st.set_page_config(page_title="Dashboard Vendite - Azienda Alimentare",
                   layout="wide")

st.sidebar.header("Caricamento dati")

# -------------------------------------------------------------
# CARICA AUTOMATICAMENTE TUTTI I CSV IN /data
# -------------------------------------------------------------

data_folder = Path(__file__).parent / "data"
csv_files = list(data_folder.glob("*.csv"))

if not csv_files:
    st.error("❌ Nessun CSV trovato nella cartella /data. Aggiungi i file prima di continuare.")
    st.stop()


# -------------------------------------------------------------
# FUNZIONE CHE NORMALIZZA OGNI DATAFRAME
# -------------------------------------------------------------
def load_and_normalize(path):
    df = pd.read_csv(path, parse_dates=["date"])

    # Aggiungo colonne utili
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    if "week" not in df.columns:
        df["week"] = df["date"].dt.isocalendar().week

    if "day_of_week" not in df.columns:
        df["day_of_week"] = df["date"].dt.day_name()

    return df


# -------------------------------------------------------------
# CARICA + CONCATENA TUTTI I CSV
# -------------------------------------------------------------
@st.cache_data(ttl=1800)
def load_all_csv(files):
    dfs = []
    for f in files:
        try:
            df = load_and_normalize(f)
            dfs.append(df)
        except Exception as e:
            st.warning(f"⚠️ Errore leggendo {f.name}: {e}")

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


# Bottone per ricaricare
if st.sidebar.button("🔄 Ricarica dati"):
    st.cache_data.clear()
    st.experimental_rerun()

# Caricamento effettivo
df = load_all_csv(csv_files)

if df.empty:
    st.error("❌ I file CSV sono vuoti o impossibili da leggere.")
    st.stop()

st.success(f"📁 Caricati {len(csv_files)} file CSV → Totale righe: {len(df):,}")


# -------------------------------------------------------------
# FUNZIONI KPI E ANALISI
# -------------------------------------------------------------
def top_n_products(df, n=10, by="sales", agg="sum"):
    if agg == "sum":
        tmp = df.groupby("family")[by].sum().reset_index().sort_values(by, ascending=False).head(n)
    else:
        tmp = df.groupby("family")[by].mean().reset_index().sort_values(by, ascending=False).head(n)
    return tmp


def mean_sales_by_period(df, period="month"):
    if period == "month":
        return df.groupby("month")["sales"].mean().reset_index().sort_values("month")
    elif period == "week":
        return df.groupby("week")["sales"].mean().reset_index().sort_values("week")
    elif period == "day_of_week":
        order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        return df.groupby("day_of_week")["sales"].mean().reindex(order).reset_index()
    return pd.DataFrame()


# -------------------------------------------------------------
# INTERFACCIA PRINCIPALE
# -------------------------------------------------------------
st.title("Dashboard Vendite - Azienda Alimentare")
st.markdown("Questa app mostra i KPI richiesti dalla consegna (4 pestanas).")

# Info lato sidebar
st.sidebar.write(f"📅 Anni disponibili: {sorted(df['year'].unique())}")

# Tabs richieste dalla consegna
tab1, tab2, tab3, tab4 = st.tabs([
    "Panoramica (Pestaña 1)",
    "Per Negozio (Pestaña 2)",
    "Per Stato (Pestaña 3)",
    "Extra (Pestaña 4)"
])


# =============================================================
# PESTAÑA 1
# =============================================================
with tab1:
    st.header("1) Visualizzazione globale delle vendite")

    # KPI
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Negozi unici", df["store_nbr"].nunique())
    with col2:
        st.metric("Prodotti (famiglie)", df["family"].nunique())
    with col3:
        st.metric("Stati", df["state"].nunique())
    with col4:
        months = sorted(df["date"].dt.to_period("M").unique().astype(str))
        st.metric("Intervallo mesi", f"{months[0]} → {months[-1]}")

    st.markdown("---")
    st.subheader("b) Analisi (Top & distribuzioni)")

    # Top10 prodotti
    st.markdown("### Top 10 prodotti per sales (somma)")
    top10 = top_n_products(df, 10, "sales", "sum")
    st.plotly_chart(px.bar(top10, x="family", y="sales"), use_container_width=True)

    # Distribuzione vendite per store
    st.markdown("### Distribuzione vendite per negozio")
    sales_per_store = df.groupby("store_nbr")["sales"].sum().reset_index()
    st.plotly_chart(px.histogram(sales_per_store, x="sales"), use_container_width=True)

    # Promozioni
    st.markdown("### Top 10 negozi per vendite in promozione")
    promo = df[df["onpromotion"] > 0]
    promo_rank = promo.groupby("store_nbr")["sales"].sum().reset_index().sort_values("sales", ascending=False).head(10)
    st.plotly_chart(px.bar(promo_rank, x="store_nbr", y="sales"), use_container_width=True)

    st.markdown("---")
    st.subheader("c) Estacionalità")

    mean_by_day = mean_sales_by_period(df, "day_of_week")
    st.plotly_chart(px.bar(mean_by_day, x="day_of_week", y="sales"), use_container_width=True)

    mean_by_week = mean_sales_by_period(df, "week")
    st.plotly_chart(px.line(mean_by_week, x="week", y="sales", markers=True), use_container_width=True)

    mean_by_month = mean_sales_by_period(df, "month")
    st.plotly_chart(px.line(mean_by_month, x="month", y="sales", markers=True), use_container_width=True)



# =============================================================
# PESTAÑA 2
# =============================================================
with tab2:
    st.header("2) Visualizzazione per negozio (store_nbr)")

    store_list = sorted(df["store_nbr"].unique())
    sel_store = st.selectbox("Seleziona store:", store_list)

    df_store = df[df["store_nbr"] == sel_store]

    # Vendite per anno
    st.subheader("Vendite per anno")
    yearly = df_store.groupby("year")["sales"].sum().reset_index()
    st.plotly_chart(px.bar(yearly, x="year", y="sales"), use_container_width=True)

    # Prodotti venduti
    st.subheader("Prodotti venduti")
    if "transactions" in df.columns:
        st.metric("Transazioni totali", df_store["transactions"].sum())
    else:
        st.metric("Righe dataset (proxy)", len(df_store))

    # Promo vendute
    st.subheader("Prodotti in promozione venduti")
    if "transactions" in df.columns:
        promo_trans = df_store[df_store["onpromotion"] > 0]["transactions"].sum()
        st.metric("Transazioni promo", promo_trans)
    else:
        promo_sales = df_store[df_store["onpromotion"] > 0]["sales"].sum()
        st.metric("Sales promo (proxy)", promo_sales)



# =============================================================
# PESTAÑA 3
# =============================================================
with tab3:
    st.header("3) Visualizzazione per stato (state)")

    state_list = sorted(df["state"].unique())
    sel_state = st.selectbox("Seleziona stato:", state_list)

    df_state = df[df["state"] == sel_state]

    # Transazioni per anno
    st.subheader("Transazioni per anno")
    if "transactions" in df.columns:
        yearly = df_state.groupby("year")["transactions"].sum().reset_index()
        st.plotly_chart(px.bar(yearly, x="year", y="transactions"), use_container_width=True)

    # Top store
    st.subheader("Top 10 negozi per vendite")
    store_rank = df_state.groupby("store_nbr")["sales"].sum().reset_index().sort_values("sales", ascending=False).head(10)
    st.plotly_chart(px.bar(store_rank, x="store_nbr", y="sales"), use_container_width=True)

    # Prodotto top
    st.subheader("Prodotto più venduto")
    prod_rank = df_state.groupby("family")["sales"].sum().reset_index().sort_values("sales", ascending=False)
    if len(prod_rank) > 0:
        st.write(f"Il prodotto più venduto è **{prod_rank.iloc[0]['family']}**.")



# =============================================================
# PESTAÑA 4
# =============================================================
with tab4:
    st.header("4) Insight aggiuntivi")

    st.write("Qui puoi aggiungere grafici avanzati.")
    if "cluster" in df.columns:
        cl = df.groupby("cluster")["sales"].mean().reset_index()
        st.plotly_chart(px.bar(cl, x="cluster", y="sales"), use_container_width=True)
    else:
        st.info("Aggiungi la colonna 'cluster' nei CSV per abilitare questa analisi.")


