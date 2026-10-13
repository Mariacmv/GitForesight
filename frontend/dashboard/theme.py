import streamlit as st

from paths import STYLES_DIR


def load_css():
    css = (STYLES_DIR / "main.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


