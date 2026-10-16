import streamlit as st
from components.topbar import render_auth_topbar, render_auth_footer
from views.auth import restaurar_sessao, direcionar_usuario

def render():
    render_auth_topbar()

    st.title("Escolha seu Repositório")
    st.caption("Conecte um repositório para começar a análise de riscos.")

    with st.form("repo_form"):
        novo_repo = st.text_input(
            "URL do repositório",
            placeholder="https://github.com/usuario/repositorio"
        )

        enviar = st.form_submit_button(
            "Conectar",
            type="primary"
        )

    if enviar:
        if not novo_repo.strip():
            st.error("Informe um repositório.")
            return

        # Integraremos o salvamento no banco posteriormente.
        st.session_state.repositorio_conectado = novo_repo.strip()
        st.session_state.pagina = "overview"
        st.rerun()

    render_auth_footer()