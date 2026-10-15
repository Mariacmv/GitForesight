import streamlit as st
from components.topbar import render_auth_topbar, render_auth_footer
from views.auth import restaurar_sessao

def render():
    #para manter a sessão de login?
    if restaurar_sessao():
        st.rerun()
    render_auth_topbar()
    
    