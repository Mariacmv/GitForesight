import streamlit as st
from datetime import datetime


def get_context():
    repo = st.session_state.get("repo_sel")
    branch = st.session_state.get("branch")
    ultima_varredura = st.session_state.get("ultima_varredura")

    usuario = st.session_state.get("usuario")

    # Garante o formato esperado pela topbar.
    if isinstance(usuario, dict):
        usuario = {
            "nome": usuario.get("nome") or "Usuário",
            "avatar_url": usuario.get("avatar_url"),
        }
    elif isinstance(usuario, str):
        usuario = {
            "nome": usuario or "Usuário",
            "avatar_url": None,
        }
    else:
        usuario = {
            "nome": "Usuário",
            "avatar_url": None,
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