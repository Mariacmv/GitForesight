import streamlit as st
from html import escape


def abrir_conta():
    atual = st.session_state.get("pagina", "overview")

    if atual != "account":
        st.session_state["pagina_anterior"] = atual

    st.session_state["pagina"] = "account"


def voltar_da_conta():
    pagina_anterior = st.session_state.pop(
        "pagina_anterior", "overview"
    )

    paginas_validas = {
        "overview", "heatmap", "predictive", "settings"
    }

    if pagina_anterior not in paginas_validas:
        pagina_anterior = "overview"

    st.session_state["pagina"] = pagina_anterior


def iniciais_do_usuario():
    nome = (
        st.session_state.get("user_name")
        or st.session_state.get("usuario")
        or ""
    ).strip()

    if not nome:
        email = (
            st.session_state.get("user_email")
            or st.session_state.get("email")
            or "U"
        )
        return email[0].upper()

    partes = nome.split()

    if len(partes) == 1:
        return partes[0][0].upper()

    return (partes[0][0] + partes[-1][0]).upper()


def render_menu_usuario():
    iniciais = iniciais_do_usuario()

    with st.container(key="topbar_user"):
        st.button(
            iniciais,
            key="botao_avatar_usuario",
            help="Minha conta",
            on_click=abrir_conta
        )

    # st.markdown(
    #     """
    #     <style>
    #     .st-key-topbar_user {
    #         position: fixed;
    #         top: 7px;
    #         right: 24px;
    #         width: 32px;
    #         height: 32px;
    #         z-index: 1002;
    #     }

    #     .st-key-topbar_user button {
    #         width: 32px;
    #         min-width: 32px;
    #         height: 32px;
    #         min-height: 32px;
    #         padding: 0;
    #         opacity: 0;
    #         cursor: pointer;
    #         border-radius: 50%;
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )