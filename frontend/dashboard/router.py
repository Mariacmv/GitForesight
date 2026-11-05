
import streamlit as st

from views import (
    account,
    banner,
    choose_repo,
    auth,
    heatmap,
    overview,
    predictive,
    settings,
    pricing,
)

from components.sidebar import render_sidebar
from components.topbar import render_topbar
from components.user_menu import (
    render_menu_usuario,
    iniciais_do_usuario,
)

from context import get_context
from data_loader import load_commits
from frontend.dashboard.components.heatmap_page import render_heatmap


PAGINAS_PUBLICAS = {
    "banner": banner.render,
    "pricing": pricing.render,
}

PAGINAS_AUTENTICACAO = {
    "login": "login",
    "register": "cadastro",
}

PAGINAS_PRIVADAS = {
    "choose_repo": choose_repo.render,
    "account": account.render,
    "heatmap": render_heatmap,
}

PAGINAS_DASHBOARD = {
    "overview": overview.render,
    "predictive": predictive.render,
    "settings": settings.render,
}

def renderizar_layout_privado():
    ctx = get_context()

    pagina = render_sidebar()

    render_topbar(ctx)
    render_menu_usuario()

    return pagina

def renderizar_pagina_publica(pagina):
    render = PAGINAS_PUBLICAS.get(pagina)

    if render is None:
        return False

    if pagina == "banner":
        render(None, None, publico=True)
    else:
        render()

    return True

def renderizar_autenticacao(pagina):
    auth_view = PAGINAS_AUTENTICACAO.get(pagina)

    if auth_view is None:
        return False

    st.session_state.setdefault("auth_view", auth_view)
    st.session_state["mostrar_banner"] = False

    auth.render()
    return True

def renderizar_pagina_privada(pagina):

    if not st.session_state.get("autenticado", False):
        st.session_state["pagina"] = "login"
        st.session_state["auth_view"] = "login"
        st.session_state["mostrar_banner"] = False

        auth.render()
        return

    if pagina == "choose_repo":
        st.session_state.setdefault("passo", 1)
        choose_repo.render()
        return

    pagina = renderizar_layout_privado()

    if pagina == "account":
        account.render()

    elif pagina == "heatmap":
        render_heatmap()

    else:
        analysis_dir = st.session_state.get("analysis_dir")

        analysis, risk = load_commits(analysis_dir)

        renderizar_dashboard(pagina, analysis, risk)

def renderizar_dashboard(pagina, analysis, risk):

    render = PAGINAS_DASHBOARD.get(
        pagina,
        overview.render
    )

    render(analysis, risk)


def navegar():

    pagina = st.session_state.get("pagina", "banner")

    if renderizar_pagina_publica(pagina):
        return

    if renderizar_autenticacao(pagina):
        return

    renderizar_pagina_privada(pagina)
