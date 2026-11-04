import streamlit as st
from datetime import datetime


def get_context():
    repo = st.session_state.get("repo_sel")
    branch = st.session_state.get("branch")
    ultima_varredura = st.session_state.get("ultima_varredura")

    # Dados do usuário
    nome = st.session_state.get("user_name") or "Usuário"
    avatar_url = st.session_state.get("avatar_url")

    usuario = {
        "nome": nome,
        "avatar_url": avatar_url,
    }

    if isinstance(ultima_varredura, datetime):
        ultima_varredura = ultima_varredura.strftime(
            "%d/%m/%Y às %H:%M"
        )

    return {
        "repos": [repo] if repo else [],
        "repo_ativo": repo or "Nenhum repositório",
        "branch": branch or "Nenhuma branch",
        "ultima_varredura": ultima_varredura or "Nenhuma varredura realizada",
        "usuario": usuario,
    }