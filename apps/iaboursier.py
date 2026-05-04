import streamlit as st

# ⚠️ Première commande Streamlit
st.set_page_config(page_title="IA Boursier V2", layout="wide")

import sys
import os
import pandas as pd

# accès dossier racine
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.indicators import trend_score, volatility
from core.risk_engine import risk_score
from core.decision_engine import recommendation
from core.portfolio_engine import get_prices

# ---------------------------------
# TITRE
# ---------------------------------
st.title("📊 Copilote IA Boursier — V2")

st.caption("Analyse portefeuille • pondération réelle • récupération de cash • IA hybride")

# ---------------------------------
# SIDEBAR
# ---------------------------------
with st.sidebar:
    st.header("⚙️ Paramètres")

    mode = st.selectbox(
        "🎛️ Mode IA",
        ["defensif", "equilibre", "dynamique"]
    )

    cash_target = st.selectbox(
        "💰 Objectif cash à récupérer",
        [0, 250, 500, 1000, 2000],
        index=0
    )

# ---------------------------------
# UPLOAD
# ---------------------------------
file = st.file_uploader("📥 Importer votre portefeuille CSV", type=["csv"])

if not file:
    st.info("Importez un fichier CSV avec colonnes : Ticker, Quantité, Prix_Achat")
    st.stop()

# ---------------------------------
# LECTURE CSV
# ---------------------------------
df = pd.read_csv(file)

required_cols = {"Ticker", "Quantité", "Prix_Achat"}
if not required_cols.issubset(df.columns):
    st.error("Le fichier doit contenir : Ticker, Quantité, Prix_Achat")
    st.stop()

# nettoyage simple
df["Ticker"] = df["Ticker"].astype(str).str.upper().str.strip()
df["Quantité"] = pd.to_numeric(df["Quantité"], errors="coerce")
df["Prix_Achat"] = pd.to_numeric(df["Prix_Achat"], errors="coerce")
df = df.dropna()

# ---------------------------------
# PRIX MARCHÉ
# ---------------------------------
tickers = df["Ticker"].tolist()

with st.spinner("📡 Récupération des cours..."):
    data = get_prices(tickers)

# si un seul ticker
if len(tickers) == 1:
    data = pd.DataFrame(data)

latest_prices = data.iloc[-1]

# ---------------------------------
# CALCULS
# ---------------------------------
df["Prix_Actuel"] = df["Ticker"].map(latest_prices)
df = df.dropna(subset=["Prix_Actuel"])

df["Valeur"] = df["Quantité"] * df["Prix_Actuel"]
df["Investi"] = df["Quantité"] * df["Prix_Achat"]
df["Gain_€"] = df["Valeur"] - df["Investi"]
df["Perf_%"] = ((df["Prix_Actuel"] - df["Prix_Achat"]) / df["Prix_Achat"]) * 100

total = df["Valeur"].sum()
df["Poids_%"] = (df["Valeur"] / total) * 100

# ---------------------------------
# IA HYBRIDE
# ---------------------------------
scores = []
recos = []
vols = []
trends = []

for t in df["Ticker"]:
    hist = data[t].dropna()

    tr = trend_score(hist)
    vol = volatility(hist)

    perf = df.loc[df["Ticker"] == t, "Perf_%"].values[0]

    score = risk_score(perf, vol) + tr

    trends.append(tr)
    vols.append(vol)
    scores.append(score)
    recos.append(recommendation(score, mode))

df["Trend"] = trends
df["Volatilité"] = vols
df["Score_IA"] = scores
df["Recommandation"] = recos

# ---------------------------------
# KPIs
# ---------------------------------
st.subheader("📌 Synthèse")

c1, c2, c3, c4 = st.columns(4)

c1.metric("💼 Valeur totale", f"{total:,.2f} €")
c2.metric("💸 Investi", f"{df['Investi'].sum():,.2f} €")
c3.metric("📈 Gain total", f"{df['Gain_€'].sum():,.2f} €")
c4.metric("📦 Positions", len(df))

# ---------------------------------
# ALLOCATION
# ---------------------------------
st.subheader("📊 Allocation réelle")

alloc = df[["Ticker", "Valeur", "Poids_%"]].sort_values("Poids_%", ascending=False)

st.dataframe(
    alloc.style.format({
        "Valeur": "{:,.2f} €",
        "Poids_%": "{:.2f}%"
    }),
    use_container_width=True
)

st.bar_chart(alloc.set_index("Ticker")["Poids_%"])

# ---------------------------------
# ALERTES
# ---------------------------------
st.subheader("⚠️ Alertes portefeuille")

heavy = df[df["Poids_%"] > 15]
micro = df[df["Poids_%"] < 1]

if not heavy.empty:
    st.warning("Positions concentrées (>15%) : " + ", ".join(heavy["Ticker"]))

if not micro.empty:
    st.info("Micro-lignes (<1%) : " + ", ".join(micro["Ticker"]))

if heavy.empty and micro.empty:
    st.success("Allocation équilibrée.")

# ---------------------------------
# TABLEAU PRINCIPAL
# ---------------------------------
st.subheader("🧠 Analyse IA")

view = df[[
    "Ticker",
    "Valeur",
    "Poids_%",
    "Perf_%",
    "Gain_€",
    "Score_IA",
    "Recommandation"
]].sort_values("Valeur", ascending=False)

st.dataframe(
    view.style.format({
        "Valeur": "{:,.2f} €",
        "Poids_%": "{:.2f}%",
        "Perf_%": "{:.2f}%",
        "Gain_€": "{:,.2f} €"
    }),
    use_container_width=True
)

# ---------------------------------
# RECUP CASH INTELLIGENTE
# ---------------------------------
if cash_target > 0:
    st.subheader(f"💰 Plan IA pour récupérer {cash_target} €")

    # ordre logique :
    # 1 micro lignes
    # 2 recommandations réduire/sortir
    # 3 plus grosses pondérations

    cash_df = df.copy()

    priority = []

    for _, row in cash_df.iterrows():
        score = 0

        if row["Poids_%"] < 1:
            score += 5

        if "Sortir" in row["Recommandation"]:
            score += 4

        if "Réduire" in row["Recommandation"]:
            score += 3

        score += row["Poids_%"] / 5

        priority.append(score)

    cash_df["Priority"] = priority
    cash_df = cash_df.sort_values("Priority", ascending=False)

    selected = []
    running = 0

    for _, row in cash_df.iterrows():
        if running >= cash_target:
            break

        selected.append(row)
        running += row["Valeur"]

    if selected:
        plan = pd.DataFrame(selected)[[
            "Ticker",
            "Valeur",
            "Poids_%",
            "Recommandation"
        ]]

        st.dataframe(
            plan.style.format({
                "Valeur": "{:,.2f} €",
                "Poids_%": "{:.2f}%"
            }),
            use_container_width=True
        )

        st.success(f"Cash estimé récupérable : {running:,.2f} €")

# ---------------------------------
# DETAILS
# ---------------------------------
with st.expander("🔵 Vue avancée"):
    st.dataframe(df, use_container_width=True)
