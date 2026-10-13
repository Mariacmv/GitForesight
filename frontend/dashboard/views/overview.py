import streamlit as st

from components.cards import (
    render_metrics,
    render_heatmap_card,
    render_trend_card,
    render_alerts_card,
)
from data_loader import load_commit_log, load_file_changes


def render(analysis, risk):
    commits = load_commit_log()
    files = load_file_changes()

    render_metrics(analysis, risk)
    st.write("")

    col_left, col_right = st.columns([1.15, 1])

    with col_left:
        render_heatmap_card(risk)

    with col_right:
        render_trend_card(risk)
        render_alerts_card(commits)