import pandas as pd
import streamlit as st

from paths import DATA_DIR


@st.cache_data
def load_commits():
    # Mantém o seu corpo original: devolve analysis, risk
    analysis = pd.read_csv(DATA_DIR / "analysis.csv")
    risk = pd.read_csv(DATA_DIR / "risk.csv")
    return analysis, risk


@st.cache_data
def load_commit_log():
    df = pd.read_csv(DATA_DIR / "commits.csv")
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df


@st.cache_data
def load_file_changes():
    return pd.read_csv(DATA_DIR / "file_changes.csv")