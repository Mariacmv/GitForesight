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
from views.choose_repo import processar_retorno_instalacao
from backend.services.github_token_storage import (
    obter_token_github,
)

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
if "mostrar_banner" not in st.session_state:
    st.session_state.mostrar_banner = True
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "cadastro"




def main():
    load_css()
    init_db()

    # 1. Detecta o retorno da instalação.
    processar_retorno_instalacao()

    # 2. Processa o callback OAuth.
    callback_processado = processar_callback()
    print("DEBUG — Callback processado:", callback_processado)

    usuario_github = st.session_state.pop(
        "github_usuario_pendente",
        None
    )
    print("DEBUG — Usuário recebido do callback:", bool(usuario_github))

    # 3. OAuth concluído: define a sessão e a página.
    if usuario_github is not None:
        user_id = usuario_github["id"]

        auth._entrar(
            user_id,
            usuario_github["name"],
            usuario_github["email"],
        )
        print("DEBUG — Autenticado:", st.session_state.get("autenticado"))
        print("DEBUG — User ID:", st.session_state.get("user_id"))

        # Mantém a sessão após o retorno externo do GitHub.
        st.session_state["cookie_pendente"] = (
            auth.issue_remember_token(user_id)
        )

        st.session_state["pagina"] = "choose_repo"
        st.session_state["passo"] = 1
        print("DEBUG — Página definida:", st.session_state["pagina"])

        st.session_state.pop("retorno_instalacao_pendente", None)
        st.session_state.pop("installation_id_pendente", None)

    if callback_processado:
        return

    # 4. Restaura a sessão local, se necessário.
    if not st.session_state.get("autenticado", False):
        print("DEBUG — Sessão não autenticada")
        sessao_restaurada = auth.restaurar_sessao()
        print("DEBUG — Sessão restaurada:", sessao_restaurada)
        print(
            "DEBUG — Cookie disponível:",
            bool(st.context.cookies.get("gf_remember"))
        )
        print(
            "DEBUG — Retorno pendente:",
            st.session_state.get("retorno_instalacao_pendente")
        )
        if not auth.restaurar_sessao():
            if st.session_state.get("retorno_instalacao_pendente"):
                st.session_state["mostrar_banner"] = False
                st.session_state["auth_view"] = "login"
                auth.render()
                return

            if st.query_params.get("entrar") == "1":
                st.session_state["mostrar_banner"] = False
                del st.query_params["entrar"]

            if st.session_state.get("mostrar_banner", True):
                banner.render(None, None, publico=True)
                return

            auth.render()
            return

    user_id = st.session_state.get("user_id")

    if user_id is None:
        st.error("Não foi possível recuperar a sessão do usuário.")
        return

    # 5. Recupera o token GitHub antes do roteamento.
    if not st.session_state.get("github_user_token"):
        token = obter_token_github(user_id)

        if token:
            st.session_state["github_user_token"] = token
            
    print(
        "DEBUG — Retorno pendente:",
        st.session_state.get("retorno_instalacao_pendente")
    )

    print(
        "DEBUG — Token recuperado do banco:",
        bool(st.session_state.get("github_user_token"))
    )

    print(
        "DEBUG — Página atual:",
        st.session_state.get("pagina")
    )

    # 6. Se o retorno da instalação está pendente,
    # prioriza a tela de seleção de repositórios.
    if st.session_state.get("retorno_instalacao_pendente"):
        if st.session_state.get("github_user_token"):
            st.session_state["pagina"] = "choose_repo"
            st.session_state["passo"] = 1
            print("DEBUG — Antes do roteamento")
            print("DEBUG — Autenticado:", st.session_state.get("autenticado"))
            print("DEBUG — Página:", st.session_state.get("pagina"))
            st.session_state.pop("retorno_instalacao_pendente", None)
            st.session_state.pop("installation_id_pendente", None)
        else:
            st.info(
                "É necessário conectar novamente sua conta GitHub "
                "para consultar os repositórios autorizados."
            )
            auth.render()
            return

    # 7. Grava o cookie pendente.
    # if "cookie_pendente" in st.session_state:
    #     auth.gravar_cookie(
    #         st.session_state.pop("cookie_pendente")
    #     )

    # 8. Define a página inicial.
    if "pagina" not in st.session_state:
        direcionar_usuario(user_id)

    pagina = st.session_state.get("pagina")
    print("DEBUG — Entrou no roteamento:", pagina)

    if pagina == "choose_repo":
        print("DEBUG — Chamando choose_repo.render()")
        st.session_state.setdefault("passo", 1)
        choose_repo.render()
        print("DEBUG — Retornou de choose_repo.render()")
        return

    if pagina == "account":
        account.render()
        return

    # 9. Dashboard.
    ctx = get_context()
    analysis, risk = load_commits()

    tela = render_sidebar()
    render_topbar(ctx)

    TELAS[tela](analysis, risk)


if __name__ == "__main__":
    main()