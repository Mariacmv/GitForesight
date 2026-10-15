from views import account, banner, choose_repo
import streamlit as st

from views import auth
from views.auth import direcionar_usuario
from backend.database.connection import init_db

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
from views import heatmap, overview, predictive, settings, banner

TELAS = {
    "Visão Geral": overview.render,
    "Heatmap de Risco": heatmap.render,
    "Análise Preditiva": predictive.render,
    "Configurações": settings.render,
    "Apresentação da Aplicação": banner.render,
    "Conta de Usuário": account.render,
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
    init_db()

    if not st.session_state.autenticado:
        auth.render()
        return
    if "cookie_pendente" in st.session_state:
        auth.gravar_cookie(st.session_state.pop("cookie_pendente"))
        
    # Verifica qual tela deve aparecer
    if "pagina" not in st.session_state:
        direcionar_usuario(st.session_state.user_id)

    # Tela de seleção de repositório
    if st.session_state.pagina == "choose_repo":
        choose_repo.render()
        return

    ctx = get_context()
    analysis, risk = load_commits()

    tela = render_sidebar()
    render_topbar(ctx)

    TELAS[tela](analysis, risk)


if __name__ == "__main__":
    main()