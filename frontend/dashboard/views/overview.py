import streamlit as st

from components.cards import (
    render_metrics,
    render_heatmap_card,
    render_alerts_card,
)
from data_loader import load_commit_log, load_file_changes
from backend.app.predictive import build_predictive
from frontend.dashboard.views.predictive import render_projection_card
from theme import load_css
from backend.app.permissions import has_permission

def iniciar_nova_analise():
    chaves = (
        "repo_sel",
        "repo_url",
        "repo_id",
        "repo_info",
        "branch",
        "analysis_id",
        "analysis_dir",
        "ultima_varredura",
        "analise",
    )

    for chave in chaves:
        st.session_state.pop(chave, None)

    st.session_state["pagina"] = "choose_repo"
    st.session_state["passo"] = 1
    st.session_state["nova_analise_em_andamento"] = True

def render(analysis, risk):
    load_css("base", "predictive", "overview")
    user_id = st.session_state.get("user_id")
    pode_simular = (
        has_permission(user_id, "simulations")
        if user_id
        else False
    )
    col_titulo, col_botao = st.columns(
        [4, 1],
        vertical_alignment="center",
    )

    with col_botao:
        st.button(
            "Nova análise",
            key="btn_nova_analise",
            icon=":material/add:",
            type="primary",
            use_container_width=True,
            on_click=iniciar_nova_analise,
        )
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
            if pode_simular:
                render_projection_card(
                    data,
                    key="card_projection_overview",
                )
            else:
                with st.container(key="premium_projection_overview"):
                    render_projection_card(
                        data,
                        key="card_projection_overview",
                    )

                st.markdown(
                    """
                    <div class="premium-projection-overlay">
                        <span>Disponível no plano Equipe ou superior</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info(data["message"])

    with col_right:
        render_alerts_card(commits)