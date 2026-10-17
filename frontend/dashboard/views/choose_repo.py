from html import escape

import requests
import streamlit as st

from backend.app.github import fetch_repo_info
from components.cards import _html
from components.topbar import render_auth_footer, render_auth_topbar

ETAPAS = [
    "Enviar link do repositório",
    "Escolher branch e iniciar análise",
    "Prévia dos resultados",
]


def _num(n):
    return f"{n:,}".replace(",", ".")


def _ir_passo(n):
    st.session_state.passo = n


def _concluir():
    st.session_state.onboarding_concluido = True


def _stepper(passo):
    itens = ""
    for n, nome in enumerate(ETAPAS, start=1):
        estado = "current" if n == passo else "done" if n < passo else "todo"
        simbolo = "✓" if estado == "done" else n
        itens += (
            f'<div class="step-item {estado}">'
            f'<div class="step-circle">{simbolo}</div>'
            f'<div class="step-text">{nome}</div>'
            f'</div>'
        )

    st.markdown(_html(f"""
        <div class="stepper-wrapper">
            <div class="steps-container">{itens}</div>
            <div class="step-counter">ETAPA {passo} DE {len(ETAPAS)}</div>
        </div>
    """), unsafe_allow_html=True)


def _cabecalho(passo, descricao, selo):
    st.markdown(_html(f"""
        <div class="step-head">
            <div>
                <div class="step-title">Etapa {passo} · {ETAPAS[passo - 1]}</div>
                <div class="step-desc">{descricao}</div>
            </div>
            <span class="step-badge">{selo}</span>
        </div>
    """), unsafe_allow_html=True)


def _card_repo(info, rotulo):
    visibilidade = "Privado" if info["private"] else "Público"
    st.markdown(_html(f"""
        <div class="repo-card">
            <div class="repo-card-label">{rotulo}</div>
            <div class="repo-card-name">{escape(info['full_name'])}</div>
            <div class="repo-card-meta">{escape(info['language'])} · {visibilidade}</div>
            <div class="repo-card-meta">{_num(info['commits'])} commits · {_num(info['contributors'])} contribuidores</div>
        </div>
    """), unsafe_allow_html=True)


def _etapa_1():
    _cabecalho(1, "Cole o link do repositório que você quer analisar.", "ESTADO INICIAL")

    with st.form("repo_form", border=False):
        url = st.text_input(
            "URL do repositório",
            label_visibility="collapsed",
            placeholder="Cole o link do repositório...",
        )
        enviar = st.form_submit_button("Enviar link e continuar", type="primary")

    if enviar:
        if not url.strip():
            st.error("Informe um repositório.")
            return

        try:
            with st.spinner("Consultando o repositório..."):
                info = fetch_repo_info(url)
        except ValueError as e:
            st.error(str(e))
            return
        except requests.RequestException:
            st.error("Não foi possível consultar o GitHub. Verifique sua conexão.")
            return

        st.session_state.repo_info = info
        st.session_state.passo = 2
        st.rerun()


def _etapa_2():
    info = st.session_state.repo_info

    _cabecalho(2, "Com o repositório recebido, escolha a branch e inicie a análise.",
               "SELEÇÃO DA BRANCH")
    _card_repo(info, "REPOSITÓRIO RECEBIDO")

    branch = st.selectbox(
        "Branch para análise",
        info["branches"],
        format_func=lambda b: f"{b}  (padrão)" if b == info["default_branch"] else b,
        key="branch_sel",
    )
    st.caption("O histórico desta branch será a base da análise.")

    if st.button("Iniciar análise", key="iniciar_analise", type="primary",
                 icon=":material/arrow_forward:"):
        st.session_state.branch = branch
        st.session_state.passo = 3
        st.rerun()

    st.button("Trocar repositório", key="voltar_passo1",
              on_click=_ir_passo, args=(1,))


def _etapa_3():
    info = st.session_state.repo_info

    _cabecalho(3, "Veja uma prévia do que a análise entrega e siga para o painel.",
               "PRÉVIA ILUSTRATIVA")
    _card_repo(info, "REPOSITÓRIO ANALISADO")

    st.markdown(_html("""
        <div class="check-list">
            <div><span>✓</span>Histórico de commits e churn disponíveis para o plano Explorar</div>
            <div><span>✓</span>Hotspots e concentração de conhecimento visíveis no dashboard</div>
            <div><span>✓</span>Leitura dos achados no dashboard para entender o contexto do projeto</div>
        </div>
    """), unsafe_allow_html=True)

    st.caption("Prévia ilustrativa · Os achados detalhados serão exibidos no painel.")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Conhecer planos e preços", key="ver_planos", type="primary",
                     icon=":material/arrow_forward:"):
            st.toast("A página de planos ainda está em construção.")
    with col_b:
        st.button("Ir para visão geral do plano", key="ir_painel", on_click=_concluir)

    st.button("Analisar outro repositório", key="reiniciar",
              on_click=_ir_passo, args=(1,))


def render():
    render_auth_topbar()

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] { display: none !important; }

        [data-testid="stMainBlockContainer"] {
            max-width: 1248px;
            padding-top: 112px !important;
            padding-bottom: 112px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "passo" not in st.session_state:
        st.session_state.passo = 1

    # Se a sessão perdeu o repositório, volta ao começo
    if st.session_state.passo > 1 and "repo_info" not in st.session_state:
        st.session_state.passo = 1

    passo = st.session_state.passo

    _stepper(passo)
    st.title("Boas-vindas ao GitForesight.")
    st.caption("Qual repositório vamos analisar primeiro?")

    with st.container(key="step_card"):
        {1: _etapa_1, 2: _etapa_2, 3: _etapa_3}[passo]()

    render_auth_footer()