import streamlit as st

def abrir_conta():
    atual = st.session_state.get("pagina")
    if atual != "account":
        st.session_state["pagina_anterior"] = atual
    st.session_state["pagina"] = "account"

def voltar_da_conta():
    st.session_state["pagina"] = st.session_state.pop("pagina_anterior", None) or "heatmap"  # sua página padrão

def render_menu_usuario(iniciais: str = "U"):
    with st.container(key="topbar_user"):
        with st.popover(iniciais):
            st.button("Minha conta", key="menu_conta", icon=":material/person:",
                      on_click=abrir_conta, use_container_width=True)
            st.button("Voltar", icon=":material/arrow_back:", on_click=voltar_da_conta)
            
def iniciais_do_usuario() -> str:
    nome = (st.session_state.get("user_name") or "").strip()
    if not nome:
        email = st.session_state.get("user_email") or "U"
        return email[0].upper()
    partes = nome.split()
    if len(partes) == 1:
        return partes[0][0].upper()
    return (partes[0][0] + partes[-1][0]).upper()