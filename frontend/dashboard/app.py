import streamlit as st

from views import auth

# set_page_config precisa ser a primeira chamada do Streamlit
st.set_page_config(
    page_title="Git Foresight",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.sidebar import render_sidebar
from components.topbar import render_topbar
from context import get_context
from data_loader import load_commits
from theme import load_css
from views import heatmap, overview, predictive, settings, apresentacao, conta

TELAS = {
    "Visão Geral": overview.render,
    "Heatmap de Risco": heatmap.render,
    "Análise Preditiva": predictive.render,
    "Configurações": settings.render,
    "Apresentação da Aplicação": apresentacao.render,
    "Conta de Usuário": conta.render,
    "Login": auth.render
}

if "tela_ativa" not in st.session_state:
    st.session_state.tela_ativa = "Visão Geral"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "cadastro"


def main():
    load_css()

    if not st.session_state.autenticado:
        auth.render()
        return
    if "cookie_pendente" in st.session_state:
        auth.gravar_cookie(st.session_state.pop("cookie_pendente"))

    ctx = get_context()
    analysis, risk = load_commits()

    tela = render_sidebar()
    render_topbar(ctx)

    TELAS[tela](analysis, risk)


if __name__ == "__main__":
    main()