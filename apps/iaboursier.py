import streamlit as st

# ⚠️ DOIT être la première commande Streamlit
st.set_page_config(page_title="IA Boursier", layout="wide")

import sys
import os
import pandas as pd
import yfinance as yf

# 🔧 permet de trouver le dossier core/
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.indicators import trend_score, volatility
from core.risk_engine import risk_score
from core.decision_engine import recommendation
from core.portfolio_engine import get_prices


# ----------------------------
# TITRE
# ----------------------------
st.title("📊 Copilote IA Boursier")

# ----------------------------
# MODE IA
# ----------------------------
mode = st.selectbox(
    "🎛️ Mode de recommandation",
    ["defensif", "equilibre", "dynamique"]
)

# ----------------------------
# UPLOAD PORTFOLIO
# ----------------------------
file = st.file_uploader("📥 Import portefeuille CSV", type=["csv"])

if file:

    df = pd.read_csv(file)

    st.subheader("📦 Portefeuille importé")
    st.dataframe(df)

    # ----------------------------
    # PRIX DU MARCHE
    # ----------------------------
    tickers = df["Ticker"].tolist()
    data = get_prices(tickers)

    latest_prices = data.iloc[-1]

    df["Prix_Actuel"] = df["Ticker"].map(latest_prices)
    df["Valeur"] = df["Quantité"] * df["Prix_Actuel"]
    df["Perf_%"] = ((df["Prix_Actuel"] - df["Prix_Achat"]) / df["Prix_Achat"]) * 100

    # ----------------------------
    # IA HYBRIDE
    # ----------------------------
    scores = []
    recos = []

    for t in tickers:
        hist = data[t].dropna()

        tr = trend_score(hist)
        vol = volatility(hist)
        perf = df[df["Ticker"] == t]["Perf_%"].values[0]

        score = risk_score(perf, vol) + tr
        scores.append(score)

        recos.append(recommendation(score, mode))

    df["Score_IA"] = scores
    df["Recommandation"] = recos

    # ----------------------------
    # VUE SIMPLE
    # ----------------------------
    st.subheader("🟢 Vue simple")

    col1, col2, col3 = st.columns(3)

    col1.metric("Valeur portefeuille", f"{df['Valeur'].sum():.2f} €")
    col2.metric("Perf moyenne", f"{df['Perf_%'].mean():.2f} %")
    col3.metric("Positions", len(df))

    st.dataframe(df[["Ticker", "Valeur", "Perf_%", "Recommandation"]])

    # ----------------------------
    # VUE AVANCEE
    # ----------------------------
    with st.expander("🔵 Vue avancée (IA détaillée)"):

        st.dataframe(df)

        st.write("📊 Lecture IA :")
        st.write("- Score IA = tendance + risque + performance")
        st.write("- Mode influence les décisions")
        st.write("- Volatilité impacte le risque")

else:
    st.info("📥 Importez un fichier CSV pour commencer")