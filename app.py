# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------
st.set_page_config(page_title="Dashboard Vendite", layout="wide")

# ---------------------------------------
# FUNZIONE PER CARICARE DATI
# ---------------------------------------
@st.cache_data
def load_data(path="parte_1.csv"):
    df = pd.read_csv(path, parse_dates=["date"])
    
    # Se mancano alcune colonne, le calcoliamo
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.dayofweek + 1  # 1=Lun ... 7=Dom
    return df

# Carica dataset
df = load_data("parte_1.csv")

# ---------------------------------------
# TABS PRINCIPALI
# ---------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Global Overview", "Per Negozio", "Per Stato", "Extra/Surprise"])

# =======================================
# PESTAÑA 1: Vista globale
# =======================================
with tab1:
    st.header("Overview Globale delle Vendite")
    
    # a) Conteggio generale
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Numero totale negozi", df["store_nbr"].nunique())
    col2.metric("Numero totale prodotti (SKU distinti)", df["family"].nunique())
    col3.metric("Stati coperti", df["state"].nunique())
    months = sorted(df["date"].dt.to_period("M").unique())
    col4.metric("Mesi nel dataset", f"{months[0]} → {months[-1]}")
    
    st.markdown("---")
    
    # b) Analisi media e ranking
    st.subheader("Top 10 Prodotti più venduti")
    top_prod = df.groupby("family").agg(times_sold=("family","count")).sort_values("times_sold", ascending=False).head(10).reset_index()
    fig_top_prod = px.bar(top_prod, x="times_sold", y="family", orientation="h", labels={"times_sold":"Numero vendite", "family":"Prodotto"})
    st.plotly_chart(fig_top_prod, use_container_width=True)
    
    st.subheader("Distribuzione vendite per negozio")
    sales_by_store = df.groupby("store_nbr")["sales"].sum().reset_index()
    fig_sales_store = px.histogram(sales_by_store, x="sales", nbins=30, title="Distribuzione vendite per negozio")
    st.plotly_chart(fig_sales_store, use_container_width=True)
    
    st.subheader("Top 10 negozi con vendite in promozione")
    promo_by_store = df[df["onpromotion"]==1].groupby("store_nbr")["sales"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_top_promo = px.bar(promo_by_store, x="sales", y="store_nbr", orientation="h", labels={"sales":"Vendite promo", "store_nbr":"Negozio"})
    st.plotly_chart(fig_top_promo, use_container_width=True)
    
    st.markdown("---")
    
    # c) Analisi di stagionalità
    st.subheader("Stagionalità delle vendite")
    dow = df.groupby("day_of_week")["sales"].mean().reset_index()
    dow["day_name"] = dow["day_of_week"].map({1:"Mon",2:"Tue",3:"Wed",4:"Thu",5:"Fri",6:"Sat",7:"Sun"})
    fig_dow = px.bar(dow, x="day_name", y="sales", title="Vendite medie per giorno della settimana")
    st.plotly_chart(fig_dow, use_container_width=True)
    
    weekly = df.groupby("week")["sales"].mean().reset_index()
    fig_week = px.line(weekly, x="week", y="sales", title="Vendite medie per settimana dell'anno")
    st.plotly_chart(fig_week, use_container_width=True)
    
    monthly = df.groupby("month")["sales"].mean().reset_index()
    fig_month = px.bar(monthly, x="month", y="sales", title="Vendite medie per mese")
    st.plotly_chart(fig_month, use_container_width=True)

# =======================================
# PESTAÑA 2: Analisi per negozio
# =======================================
with tab2:
    st.header("Analisi per negozio")
    store_selected = st.selectbox("Seleziona negozio", sorted(df["store_nbr"].unique()))
    df_store = df[df["store_nbr"]==store_selected]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Vendite totali", round(df_store["sales"].sum(),2))
    col2.metric("Numero righe (transazioni)", df_store.shape[0])
    col3.metric("Prodotti in promozione", df_store["onpromotion"].sum())
    
    st.subheader("Vendite per anno")
    sales_year = df_store.groupby("year")["sales"].sum().reset_index()
    fig_sales_year = px.bar(sales_year, x="year", y="sales", title="Vendite per anno")
    st.plotly_chart(fig_sales_year, use_container_width=True)

# =======================================
# PESTAÑA 3: Analisi per stato
# =======================================
with tab3:
    st.header("Analisi per stato")
    state_selected = st.selectbox("Seleziona stato", sorted(df["state"].dropna().unique()))
    df_state = df[df["state"]==state_selected]
    
    st.subheader("Transazioni per anno")


# ---------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------
st.set_page_config(page_title="Dashboard Vendite", layout="wide")

# ---------------------------------------
# FUNZIONE PER CARICARE DATI
# ---------------------------------------
@st.cache_data
def load_data(path="parte_1.csv"):
    df = pd.read_csv(path, parse_dates=["date"])
    
    # Se mancano alcune colonne, le calcoliamo
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.dayofweek + 1  # 1=Lun ... 7=Dom
    return df

# Carica dataset
df = load_data("parte_1.csv")

# ---------------------------------------
# TABS PRINCIPALI
# ---------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Global Overview", "Per Negozio", "Per Stato", "Extra/Surprise"])

# =======================================
# PESTAÑA 1: Vista globale
# =======================================
with tab1:
    st.header("Overview Globale delle Vendite")
    
    # a) Conteggio generale
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Numero totale negozi", df["store_nbr"].nunique())
    col2.metric("Numero totale prodotti (SKU distinti)", df["family"].nunique())
    col3.metric("Stati coperti", df["state"].nunique())
    months = sorted(df["date"].dt.to_period("M").unique())
    col4.metric("Mesi nel dataset", f"{months[0]} → {months[-1]}")
    
    st.markdown("---")
    
    # b) Analisi media e ranking
    st.subheader("Top 10 Prodotti più venduti")
    top_prod = df.groupby("family").agg(times_sold=("family","count")).sort_values("times_sold", ascending=False).head(10).reset_index()
    fig_top_prod = px.bar(top_prod, x="times_sold", y="family", orientation="h", labels={"times_sold":"Numero vendite", "family":"Prodotto"})
    st.plotly_chart(fig_top_prod, use_container_width=True)
    
    st.subheader("Distribuzione vendite per negozio")
    sales_by_store = df.groupby("store_nbr")["sales"].sum().reset_index()
    fig_sales_store = px.histogram(sales_by_store, x="sales", nbins=30, title="Distribuzione vendite per negozio")
    st.plotly_chart(fig_sales_store, use_container_width=True)
    
    st.subheader("Top 10 negozi con vendite in promozione")
    promo_by_store = df[df["onpromotion"]==1].groupby("store_nbr")["sales"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_top_promo = px.bar(promo_by_store, x="sales", y="store_nbr", orientation="h", labels={"sales":"Vendite promo", "store_nbr":"Negozio"})
    st.plotly_chart(fig_top_promo, use_container_width=True)
    
    st.markdown("---")
    
    # c) Analisi di stagionalità
    st.subheader("Stagionalità delle vendite")
    dow = df.groupby("day_of_week")["sales"].mean().reset_index()
    dow["day_name"] = dow["day_of_week"].map({1:"Mon",2:"Tue",3:"Wed",4:"Thu",5:"Fri",6:"Sat",7:"Sun"})
    fig_dow = px.bar(dow, x="day_name", y="sales", title="Vendite medie per giorno della settimana")
    st.plotly_chart(fig_dow, use_container_width=True)
    
    weekly = df.groupby("week")["sales"].mean().reset_index()
    fig_week = px.line(weekly, x="week", y="sales", title="Vendite medie per settimana dell'anno")
    st.plotly_chart(fig_week, use_container_width=True)
    
    monthly = df.groupby("month")["sales"].mean().reset_index()
    fig_month = px.bar(monthly, x="month", y="sales", title="Vendite medie per mese")
    st.plotly_chart(fig_month, use_container_width=True)

# =======================================
# PESTAÑA 2: Analisi per negozio
# =======================================
with tab2:
    st.header("Analisi per negozio")
    store_selected = st.selectbox("Seleziona negozio", sorted(df["store_nbr"].unique()))
    df_store = df[df["store_nbr"]==store_selected]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Vendite totali", round(df_store["sales"].sum(),2))
    col2.metric("Numero righe (transazioni)", df_store.shape[0])
    col3.metric("Prodotti in promozione", df_store["onpromotion"].sum())
    
    st.subheader("Vendite per anno")
    sales_year = df_store.groupby("year")["sales"].sum().reset_index()
    fig_sales_year = px.bar(sales_year, x="year", y="sales", title="Vendite per anno")
    st.plotly_chart(fig_sales_year, use_container_width=True)

# =======================================
# PESTAÑA 3: Analisi per stato
# =======================================
with tab3:
    st.header("🌎 Analisi per stato")
    state_selected = st.selectbox("Seleziona stato", sorted(df["state"].dropna().unique()))
    df_state = df[df["state"]==state_selected]
    
    st.subheader("Transazioni per anno")
    trans_year = df_state.groupby("year")["transactions"].sum().reset_index()
    fig_trans_year = px.bar(trans_year, x="year", y="transactions", title="Transazioni per anno")
    st.plotly_chart(fig_trans_year, use_container_width=True)
    
    st.subheader("Top negozi per vendite")
    top_stores = df_state.groupby("store_nbr")["sales"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_top_stores = px.bar(top_stores, x="sales", y="store_nbr", orientation="h", title="Top negozi per vendite")
    st.plotly_chart(fig_top_stores, use_container_width=True)
    
    st.subheader("Prodotto più venduto nello stato")
    top_product = df_state.groupby("family")["sales"].sum().idxmax()
    st.success(f"Prodotto più venduto: {top_product}")

# =======================================
# PESTAÑA 4: Extra / Surprise
# =======================================
with tab4:
    st.header("✨ Insights aggiuntivi")
    st.markdown("Heatmap vendite medie per giorno della settimana e mese")
    pivot = df.groupby(["month","day_of_week"])["sales"].mean().reset_index()
    pivot_table = pivot.pivot(index="day_of_week", columns="month", values="sales")
    fig_heat = px.imshow(pivot_table, labels=dict(x="Mese", y="Giorno settimana", color="Vendite medie"))
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown("Confronto vendite medie: OnPromotion vs OffPromotion")
    promo_cmp = df.groupby("onpromotion")["sales"].mean().reset_index()
    fig_promo_cmp = px.bar(promo_cmp, x="onpromotion", y="sales", labels={"onpromotion":"OnPromotion (0/1)", "sales":"Vendite medie"})
    st.plotly_chart(fig_promo_cmp, use_container_width=True)
    
    st.write("Puoi aggiungere qui altre analisi sorprendenti per il CEO!")


    trans_year = df_state.groupby("year")["transactions"].sum().reset_index()
    fig_trans_year = px.bar(trans_year, x="year", y="transactions", title="Transazioni per anno")
    st.plotly_chart(fig_trans_year, use_container_width=True)
    
    st.subheader("Top negozi per vendite")
    top_stores = df_state.groupby("store_nbr")["sales"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_top_stores = px.bar(top_stores, x="sales", y="store_nbr", orientation="h", title="Top negozi per vendite")
    st.plotly_chart(fig_top_stores, use_container_width=True)
    
    st.subheader("Prodotto più venduto nello stato")
    top_product = df_state.groupby("family")["sales"].sum().idxmax()
    st.success(f"Prodotto più venduto: {top_product}")

# =======================================
# PESTAÑA 4: Extra / Surprise
# =======================================
with tab4:
    st.header("✨ Insights aggiuntivi")
    st.markdown("Heatmap vendite medie per giorno della settimana e mese")
    pivot = df.groupby(["month","day_of_week"])["sales"].mean().reset_index()
    pivot_table = pivot.pivot(index="day_of_week", columns="month", values="sales")
    fig_heat = px.imshow(pivot_table, labels=dict(x="Mese", y="Giorno settimana", color="Vendite medie"))
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown("Confronto vendite medie: OnPromotion vs OffPromotion")
    promo_cmp = df.groupby("onpromotion")["sales"].mean().reset_index()
    fig_promo_cmp = px.bar(promo_cmp, x="onpromotion", y="sales", labels={"onpromotion":"OnPromotion (0/1)", "sales":"Vendite medie"})
    st.plotly_chart(fig_promo_cmp, use_container_width=True)
    
    st.write("Puoi aggiungere qui altre analisi sorprendenti per il CEO!")

