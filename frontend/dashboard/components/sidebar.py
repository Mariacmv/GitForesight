
import base64
import streamlit as st

from frontend.dashboard.paths import ASSETS_DIR


ITENS_MENU = [
    ("Visão Geral", ":material/grid_view:", "overview"),
    ("Heatmap de Risco", ":material/water_drop:", "heatmap"),
    ("Análise Preditiva", ":material/show_chart:", "predictive"),
]


@st.cache_data
def _logo_base64():
    return base64.b64encode(
        (ASSETS_DIR / "Logo.png").read_bytes()
    ).decode()


def render_sidebar():

    def _ir_para(pagina):
        st.session_state["pagina"] = pagina

    ativa = st.session_state.get("pagina", "overview")

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

        for nome, icone, pagina in ITENS_MENU:
            st.button(
                nome,
                icon=icone,
                key=f"nav_{pagina}",
                type="primary" if ativa == pagina else "secondary",
                on_click=_ir_para,
                args=(pagina,)
            )

        st.button(
            "Configurações",
            icon=":material/settings:",
            key="nav_config",
            type="primary" if ativa == "settings" else "secondary",
            on_click=_ir_para,
            args=("settings",)
        )

    return st.session_state.get("pagina", "overview")
