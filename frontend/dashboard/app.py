import streamlit as st

# set_page_config precisa ser a primeira chamada do Streamlit
st.set_page_config(
    page_title="Git Foresight",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.sidebar import render_sidebar
from components.topbar import render_topbar
from context import get_context
from data_loader import load_data
from theme import load_css
from views import heatmap, overview, predictive, settings

TELAS = {
    "Visão Geral": overview.render,
    "Heatmap de Risco": heatmap.render,
    "Análise Preditiva": predictive.render,
    "Configurações": settings.render,
}

if "tela_ativa" not in st.session_state:
    st.session_state.tela_ativa = "Visão Geral"


def main():
    load_css()

    ctx = get_context()
    analysis, risk = load_data()

    tela = render_sidebar()
    render_topbar(ctx)

    TELAS[tela](analysis, risk)


if __name__ == "__main__":
    main()