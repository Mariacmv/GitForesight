import sys, requests
from pathlib import Path
import streamlit as st 

# Caminho absoluto até GitForesight
ROOT_DIR = Path(__file__).resolve().parents[2]

# Adiciona a raiz do projeto aos caminhos do Python
sys.path.insert(0, str(ROOT_DIR))

# Teste de importação


# set_page_config precisa ser a primeira chamada do Streamlit
st.set_page_config(
    page_title="Git Foresight",
    layout="wide",
    initial_sidebar_state="expanded"
)

#from backend.app.insights import knowledge_concentration
from views import account, banner, choose_repo, auth, heatmap, overview, predictive, settings
from views.auth import direcionar_usuario
from backend.database.connection import init_db
from components.sidebar import render_sidebar
from components.topbar import render_topbar
from context import get_context
from data_loader import load_commits
from theme import load_css
from backend.services.github_callback import processar_callback
from backend.services.github_installation import (
    listar_instalacoes_usuario
)
from frontend.dashboard.views.choose_repo import processar_retorno_instalacao

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
    
    processar_retorno_instalacao()
    
    # Processa o retorno da autorização do GitHub
    callback_processado = processar_callback()

    # Verifica se o callback entregou um usuário autenticado
    usuario_github = st.session_state.pop(
        "github_usuario_pendente",
        None
    )

    if usuario_github is not None:
        auth._entrar(
            usuario_github["id"],
            usuario_github["name"],
            usuario_github["email"],
            metodo_login="github",
        )

        st.session_state.pagina = "choose_repo"
        st.rerun()

    # Se houve erro ou cancelamento, interrompe esta execução
    if callback_processado:
        return

    if not st.session_state.get("autenticado", False):
        if auth.restaurar_sessao():
            direcionar_usuario(st.session_state.user_id)
            return

        auth.render()
        return
    #BOTÃO DE TESTAR INSTALAÇÕES
    # if st.session_state.get("github_user_token"):
    #     if st.button("Testar instalações GitHub"):
    #         try:
    #             instalacoes = listar_instalacoes_usuario(
    #                 st.session_state.github_user_token
    #             )

    #             for instalacao in instalacoes:
    #                 st.write({
    #                     "Conta": instalacao["account_login"],
    #                     "Instalação": instalacao["installation_id"],
    #                 })

    #         except requests.HTTPError:
    #             st.error(
    #                 "Não foi possível consultar as instalações. "
    #                 "Verifique a autorização do GitHub."
    #             )

    if "cookie_pendente" in st.session_state:
        auth.gravar_cookie(st.session_state.pop("cookie_pendente"))
        
    # Verifica qual tela deve aparecer
    if "pagina" not in st.session_state:
        direcionar_usuario(st.session_state.user_id)

    # Tela de seleção de repositório
    if st.session_state.pagina == "choose_repo":
        choose_repo.render()
        return
    
    if st.session_state.pagina == "account":
        account.render()
        return

    ctx = get_context()
    analysis, risk = load_commits()

    tela = render_sidebar()
    render_topbar(ctx)

    TELAS[tela](analysis, risk)


if __name__ == "__main__":
    main()