
from pathlib import Path

import pandas as pd
import streamlit as st

from paths import DATA_DIR


def _get_data_dir(analysis_dir=None):
    if analysis_dir is None:
        return DATA_DIR

    return Path(analysis_dir)


@st.cache_data
def load_commits(analysis_dir=None):
    pasta = _get_data_dir(analysis_dir)

    analysis = pd.read_csv(pasta / "analysis.csv")
    risk = pd.read_csv(pasta / "risk.csv")

    return analysis, risk


@st.cache_data
def load_commit_log(analysis_dir=None):
    pasta = _get_data_dir(analysis_dir)

    df = pd.read_csv(pasta / "commits.csv")
    df["date"] = pd.to_datetime(df["date"], utc=True)

    return df


@st.cache_data
def load_file_changes(analysis_dir=None):
    pasta = _get_data_dir(analysis_dir)

    return pd.read_csv(pasta / "file_changes.csv")
