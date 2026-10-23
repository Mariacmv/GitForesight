from html import escape

import streamlit as st

from paths import DATA_DIR   # precisa vir antes dos imports de backend (ajusta o sys.path)
from backend.app.analysis_summary import build_summary
from components.analysis_panels import repo_html
from components.results_panels import (
    ICONE_BRANCH,
    nota_html,
    preview_desfocado_html,
    proximos_html,
    resumo_html,
)
from backend.database.repositories import buscar_repositorio_usuario


def _ir_visao_geral():
    info = st.session_state.get("repo_info", {})
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("Sua sessão expirou. Entre novamente.")
        return

    repo = buscar_repositorio_usuario(user_id)

    if not repo or repo.get("url") != info.get("url"):
        st.error(
            "Não foi possível recuperar o repositório analisado."
        )
        return

    st.session_state.repositorio_conectado = repo
    st.session_state.pagina = "overview"
    st.session_state.tela_ativa = "Visão Geral"
    st.session_state.passo = 1
    st.session_state.analise = "pronta"


def _planos():
    st.toast("A página de planos ainda está em construção.")


def _analisar_outro():
    st.session_state.passo = 1
    st.session_state.analise = "pronta"


def render_resultados():
    info = st.session_state.repo_info
    branch = st.session_state.get("branch") or info["default_branch"]
    resumo = build_summary(DATA_DIR)

    st.markdown('<div class="pg-title">Primeira análise do repositório selecionado.</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="pg-sub">Com o contexto de {escape(info["full_name"])} · {escape(branch)}, '
        'esta é a prévia do que a análise encontrou: histórico, churn, hotspots e '
        'distribuição de conhecimento.</div>',
        unsafe_allow_html=True,
    )

    col_esq, col_dir = st.columns([1, 2], gap="medium")

    with col_esq:
        with st.container(key="first_card"):
            st.markdown(
                '<div class="an-title-row"><span class="an-title">Sua primeira análise</span>'
                f'{ICONE_BRANCH}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(repo_html(info, "REPOSITÓRIO SELECIONADO"), unsafe_allow_html=True)

            st.markdown('<div class="an-label">Branch analisada</div>', unsafe_allow_html=True)
            st.selectbox(
                "Branch", [branch],
                format_func=lambda b: f"{b}  (padrão)" if b == info.get("default_branch") else b,
                key=f"branch3_{info['full_name']}",
                label_visibility="collapsed", disabled=True,
            )
            st.caption("O histórico desta branch foi a base da análise.")

            st.markdown(proximos_html(), unsafe_allow_html=True)

            st.button("Conhecer planos e preços", key="res_planos", type="primary",
                      icon=":material/arrow_forward:", on_click=_planos)
            st.button("Ir para visão geral do plano", key="res_visao", on_click=_ir_visao_geral)
            st.button("Analisar outro repositório", key="res_outro", type="tertiary",
                      on_click=_analisar_outro)

            st.markdown(
                f'<div class="side-foot">{escape(info["full_name"])} · {escape(branch)}</div>',
                unsafe_allow_html=True,
            )

    with col_dir:
        with st.container(key="analysis_card"):
            st.markdown(
                '<div class="an-head"><div>'
                '<div class="an-head-title">Primeira análise</div>'
                '<div class="an-head-sub">Visão geral dos resultados desta etapa.</div>'
                '</div><span class="step-badge">ANÁLISE PRELIMINAR</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(resumo_html(resumo), unsafe_allow_html=True)
            st.markdown(preview_desfocado_html(), unsafe_allow_html=True)

    st.markdown(nota_html(), unsafe_allow_html=True)