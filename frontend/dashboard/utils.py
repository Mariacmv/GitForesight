from pathlib import Path
import streamlit as st

def render_topbar(repo="meu-repo", branch="main", status="Conectado"):
    st.markdown(
        f"""<div class="topbar">
<div class="topbar-left"><div class="topbar-repo">{repo}</div><div class="topbar-branch">{branch}</div></div>
<div class="topbar-right"><div class="topbar-status"><span class="topbar-dot"></span>{status}</div></div>
</div>""",
        unsafe_allow_html=True,
    )


def render_footbar():
    st.markdown(
        """<div class="footbar">
<div>© 2026 Sua Empresa</div>
<div>v1.0.0</div>
</div>""",
        unsafe_allow_html=True,
    )