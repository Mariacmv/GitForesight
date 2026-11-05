
import sys
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))


st.set_page_config(
    page_title="Git Foresight",
    layout="wide",
    initial_sidebar_state="expanded"
)


from router import navegar

from views import auth
from paths import DATA_DIR

from backend.database.connection import init_db
from backend.services.github_callback import processar_callback
from backend.services.github_token_storage import obter_token_github
from backend.services.github_oauth import buscar_usuario_github

from backend.database.repositories import (
    migrar_repositorios,
    buscar_repositorio_analisado,
    buscar_ultima_analise_usuario,
)

from views.auth import direcionar_usuario
from views.choose_repo import processar_retorno_instalacao

from theme import load_css


# Migração das tabelas de repositórios.
migrar_repositorios()


def main():

    load_css()
    init_db()

    # 1. Detecta o retorno da instalação da GitHub App.
    processar_retorno_instalacao()

    # 2. Processa o callback OAuth.
    callback_processado = processar_callback()

    usuario_github = st.session_state.pop(
        "github_usuario_pendente",
        None
    )

    # 3. OAuth concluído: define a sessão e a página.
    if usuario_github is not None:

        user_id = usuario_github["id"]

        auth._entrar(
            user_id,
            usuario_github["name"],
            usuario_github["email"],
            metodo_login="github",
        )

        st.session_state["avatar_url"] = (
            usuario_github.get("avatar_url")
        )

        # Mantém a sessão após o retorno externo do GitHub.
        st.session_state["cookie_pendente"] = (
            auth.issue_remember_token(user_id)
        )

        st.session_state["pagina"] = "choose_repo"
        st.session_state["passo"] = 1

        st.session_state.pop(
            "retorno_instalacao_pendente",
            None
        )

        st.session_state.pop(
            "installation_id_pendente",
            None
        )

    # Interrompe se o callback foi processado,
    # mas não entregou um usuário autenticado.
    if callback_processado and usuario_github is None:
        return

    # 4. Interpreta atalhos recebidos pela URL.
    if st.query_params.get("precos") == "1":
        st.session_state["pagina"] = "pricing"
        del st.query_params["precos"]

    if st.query_params.get("entrar") == "1":
        st.session_state["pagina"] = "login"
        st.session_state["auth_view"] = "login"
        st.session_state["mostrar_banner"] = False

        del st.query_params["entrar"]

    # 5. Restaura a sessão local, se necessário.
    if not st.session_state.get("autenticado", False):

        sessao_restaurada = auth.restaurar_sessao()

        print(
            "DEBUG — Cookie disponível:",
            bool(st.context.cookies.get("gf_remember"))
        )

        print(
            "DEBUG — Retorno pendente:",
            st.session_state.get("retorno_instalacao_pendente")
        )

        if not sessao_restaurada:

            if st.session_state.get("retorno_instalacao_pendente"):
                st.session_state["pagina"] = "login"
                st.session_state["auth_view"] = "login"
                st.session_state["mostrar_banner"] = False

    # 6. Recupera o usuário autenticado.
    autenticado = st.session_state.get("autenticado", False)
    user_id = st.session_state.get("user_id")

    if autenticado:

        if user_id is None:
            st.error(
                "Não foi possível recuperar a sessão do usuário."
            )
            return

        # Recupera o token GitHub antes da navegação.
        if not st.session_state.get("github_user_token"):

            token = obter_token_github(user_id)

            if token:
                st.session_state["github_user_token"] = token
                
                # Recupera o perfil do GitHub quando a sessão é restaurada.
        token = st.session_state.get("github_user_token")

        if token and not st.session_state.get("avatar_url"):
            try:
                perfil = buscar_usuario_github(token)
                st.session_state["avatar_url"] = perfil.get("avatar_url")

            except Exception as e:
                print("DEBUG — Erro ao recuperar avatar:", e)

        # Recupera o último repositório analisado.
        if not st.session_state.get("repo_sel"):
            repo = buscar_repositorio_analisado(user_id)

            if repo:
                st.session_state["repo_sel"] = repo["name"]
                st.session_state["repo_url"] = repo["url"]

                st.session_state["branch"] = (
                    repo.get("selected_branch")
                )

                st.session_state["ultima_varredura"] = (
                    repo.get("last_analysis_at")
                )

        # Recupera a última análise salva do usuário.
        if not st.session_state.get("analysis_id"):

            analise = buscar_ultima_analise_usuario(user_id)

            if analise:
                st.session_state["analysis_id"] = analise["id"]

                st.session_state["analysis_dir"] = (
                    DATA_DIR / analise["artifact_dir"]
                )

                st.session_state["repo_sel"] = (
                    analise["repository_name"]
                )

                st.session_state["repo_url"] = (
                    analise["repository_url"]
                )

                st.session_state["branch"] = analise["branch"]

                st.session_state["ultima_varredura"] = (
                    analise["analyzed_at"]
                )

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

        # 7. Resolve o retorno da instalação da GitHub App.
        if st.session_state.get("retorno_instalacao_pendente"):

            if st.session_state.get("github_user_token"):

                st.session_state["pagina"] = "choose_repo"
                st.session_state["passo"] = 1

                st.session_state.pop(
                    "retorno_instalacao_pendente",
                    None
                )

                st.session_state.pop(
                    "installation_id_pendente",
                    None
                )

            else:
                st.info(
                    "É necessário conectar novamente sua conta GitHub "
                    "para consultar os repositórios autorizados."
                )

                st.session_state["pagina"] = "login"
                st.session_state["auth_view"] = "login"

                auth.render()
                return

        # 8. Grava o cookie pendente.
        if "cookie_pendente" in st.session_state:

            token_cookie = st.session_state.pop("cookie_pendente")
            auth.gravar_cookie(token_cookie)

        # 9. Define a página inicial do usuário.
        if "pagina" not in st.session_state:
            direcionar_usuario(user_id)

    else:

        # Usuário sem sessão: página inicial pública.
        if "pagina" not in st.session_state:
            st.session_state["pagina"] = "banner"
    print(
        "DEBUG — Avatar URL:",
        st.session_state.get("avatar_url")
    )

    # 10. Centraliza a renderização das páginas.
    navegar()


if __name__ == "__main__":
    main()
