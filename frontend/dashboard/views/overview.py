import streamlit as st

from components.cards import (
    render_metrics,
    render_heatmap_card,
    render_alerts_card,
)
from data_loader import load_commit_log, load_file_changes
from backend.app.predictive import build_predictive
from frontend.dashboard.views.predictive import render_projection_card


def render(analysis, risk):
    commits = load_commit_log()
    files = load_file_changes()

    render_metrics(analysis, risk)
    st.write("")

    # Primeira linha: Heatmap em largura total
    render_heatmap_card(risk)

    st.write("")

    # Segunda linha: Projeção e alertas
    col_left, col_right = st.columns([1.15, 1])

    with col_left:
        data = build_predictive(analysis, risk)

        if data["status"] == "ok":
            render_projection_card(data, key="card_projection_overview")
        else:
            st.info(data["message"])

    with col_right:
        render_alerts_card(commits)