import base64

import streamlit as st

from paths import ASSETS_DIR

ITENS_MENU = [
    ("Visão Geral",       ":material/grid_view:"),
    ("Heatmap de Risco",  ":material/water_drop:"),
    ("Análise Preditiva", ":material/show_chart:"),
]


@st.cache_data
def _logo_base64():
    return base64.b64encode((ASSETS_DIR / "Logo.png").read_bytes()).decode()


def render_sidebar():

    def _ir_para(tela):
        st.session_state.tela_ativa = tela

    ativa = st.session_state.tela_ativa

    with st.sidebar:

        st.markdown(
            f"""
            <div class="sidebar-brand">
                <div class="sidebar-logo">
                    <img src="data:image/png;base64,{_logo_base64()}">
                </div>
                <span class="sidebar-title">Git Foresight</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        for nome, icone in ITENS_MENU:
            st.button(
                nome,
                icon=icone,
                key=f"nav_{nome}",
                type="primary" if ativa == nome else "secondary",
                on_click=_ir_para,
                args=(nome,)
            )

        # Precisa ser o ÚLTIMO elemento dentro da sidebar
        st.button(
            "Configurações",
            icon=":material/settings:",
            key="nav_config",
            type="primary" if ativa == "Configurações" else "secondary",
            on_click=_ir_para,
            args=("Configurações",)
        )

    return st.session_state.tela_ativa