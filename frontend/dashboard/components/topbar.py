import streamlit as st
from components.sidebar import _logo_base64
from html import escape
from textwrap import dedent

def render_topbar(ctx):

    repo = ctx["repo_ativo"]
    branch = ctx["branch"]
    last_scan = ctx["ultima_varredura"]
    user_name = ctx["usuario"]["nome"]
    avatar_url = ctx["usuario"]["avatar_url"]

    initials = "".join(p[0] for p in user_name.split()[:2]).upper()

    avatar = (
        f'<img src="{avatar_url}" alt="{user_name}">'
        if avatar_url else initials
    )

    html = f"""
    <div class="topbar">
        <div class="topbar-left">
            <div class="topbar-repo">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none"
                     stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                    <circle cx="4" cy="3.5" r="1.8"/>
                    <circle cx="12" cy="3.5" r="1.8"/>
                    <circle cx="8" cy="12.5" r="1.8"/>
                    <path d="M4 5.3v1.2c0 1 .8 1.5 1.8 1.5h4.4c1 0 1.8-.5 1.8-1.5V5.3M8 8v2.7"/>
                </svg>
                <span>{repo}</span>
                <svg width="10" height="10" viewBox="0 0 16 16" fill="none"
                     stroke="currentColor" stroke-width="2" stroke-linecap="round">
                    <path d="M4 6l4 4 4-4"/>
                </svg>
            </div>
            <div class="topbar-branch">
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none"
                     stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
                    <circle cx="4" cy="3.5" r="1.8"/>
                    <circle cx="4" cy="12.5" r="1.8"/>
                    <circle cx="12" cy="5.5" r="1.8"/>
                    <path d="M4 5.3v5.4M12 7.3c0 3-8 1.5-8 3.4"/>
                </svg>
                <span>{branch}</span>
            </div>
        </div>
        <div class="topbar-right">
            <div class="topbar-status">
                <span class="topbar-dot"></span>
                <span>Última varredura: {last_scan}</span>
            </div>
            <div class="topbar-avatar">{avatar}</div>
        </div>
    </div>
    """

    # Remove a indentação: o Markdown trata linhas com 4+ espaços como bloco de código
    html = " ".join(line.strip() for line in html.splitlines())

    st.markdown(
        html,
        unsafe_allow_html=True
    )
    

def render_auth_topbar(mostrar_usuario=False):
    avatar_html = ""

    if mostrar_usuario:
        nome = str(st.session_state.get("usuario") or "Usuário")
        avatar_url = st.session_state.get("avatar_url")
        iniciais = "".join(p[0] for p in nome.split()[:2]).upper() or "U"

        conteudo = (
            f'<img src="{escape(avatar_url)}" alt="{escape(nome)}">'
            if avatar_url else iniciais
        )

        avatar_html = (
            f'<span class="auth-vsep"></span>'
            f'<div class="auth-avatar">{conteudo}</div>'
        )

    html = f"""
    <div class="auth-topbar">
        <div class="auth-brand">
            <div class="auth-brand-logo">
                <img class="auth-brand-logo-img"
                     src="data:image/png;base64,{_logo_base64()}">
            </div>
            <div class="auth-brand-text">
                <div class="auth-brand-name">Git Foresight</div>
            </div>
        </div>

        <div class="auth-right">
            <a class="auth-help" href="mailto:suporte@gitforesight.com">
                Precisa de ajuda?
            </a>
            {avatar_html}
        </div>
    </div>
    """

    # Remove a indentação: sem isso o Markdown mostra o HTML como código
    html = " ".join(line.strip() for line in html.splitlines())
    st.markdown(html, unsafe_allow_html=True)

    if mostrar_usuario:
        if st.button("Meu perfil", key="avatar_click"):
            st.session_state.pagina = "account"
            st.session_state.tela_ativa = "Conta de Usuário"
            st.rerun()


def render_auth_footer():

    html = """
    <div class="auth-footer">
        <span>© 2026 Git Foresight</span>
        <span class="auth-footer-links">
            <a href="#">Política de Privacidade</a>
            <a href="#">Termos de Uso</a>
        </span>
    </div>
    """

    html = " ".join(line.strip() for line in html.splitlines())
    st.markdown(html, unsafe_allow_html=True)