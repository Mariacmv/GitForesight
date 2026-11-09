import streamlit as st

from frontend.dashboard.paths import STYLES_DIR
from pathlib import Path

@st.cache_data
def ler_css(nome_arquivo):
    caminho = STYLES_DIR / nome_arquivo
    print("PROCURANDO EM:", STYLES_DIR)
    print("EXISTE?", STYLES_DIR.exists())
    if STYLES_DIR.exists():
        print("ARQUIVOS:", [p.name for p in STYLES_DIR.iterdir()])
    return caminho.read_text(encoding="utf-8")

def load_css(*names):
    css = "\n".join(
        (STYLES_DIR / f"{n}.css").read_text(encoding="utf-8") for n in names
    )
    print("CSS carregado:", names, len(css), "caracteres")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


