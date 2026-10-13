import streamlit as st


def get_context():
    """
    Ponto único de dados da barra superior.
    Quando o backend existir, só o corpo desta função muda.
    """
    repos = ["empresa/backend", "empresa/frontend"]

    repo_ativo = st.session_state.get("repo_ativo", repos[0])
    if repo_ativo not in repos:
        repo_ativo = repos[0]

    return {
        "repos": repos,
        "repo_ativo": repo_ativo,
        "branch": "main",
        "ultima_varredura": "Há 10 min",
        "usuario": {"nome": "Maria Silva", "avatar_url": None},
    }