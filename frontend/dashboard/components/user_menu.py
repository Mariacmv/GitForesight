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
    avatar_url = st.session_state.get("avatar_url")

    # Aceita somente imagens servidas por HTTPS.
    if not isinstance(avatar_url, str) or not avatar_url.startswith("https://"):
        avatar_url = None

    with st.container(key="topbar_user"):
        with st.popover(iniciais, help="Abrir menu do usuário"):
            st.button(
                "Minha conta",
                key="menu_conta",
                icon=":material/person:",
                on_click=abrir_conta,
                use_container_width=True
            )

            st.button(
                "Voltar",
                key="menu_voltar",
                icon=":material/arrow_back:",
                on_click=voltar_da_conta,
                use_container_width=True
            )

    # Estilização do botão que abre o popover.
    imagem_css = (
        f'background-image: url("{escape(avatar_url)}");'
        if avatar_url else ""
    )

    st.markdown(
        f"""
        <style>
        .st-key-topbar_user {{
            position: fixed;
            top: 6px;
            right: 24px;
            z-index: 1002;
        }}

        .st-key-topbar_user button {{
            width: 32px;
            min-width: 32px;
            height: 32px;
            min-height: 32px;
            padding: 0;
            border-radius: 50%;
            overflow: hidden;
            background-color: #5F5CE5;
            background-image: none;
            background-size: cover;
            background-position: center;
            border: 1px solid rgba(255,255,255,0.15);
            color: white;
            font-size: 11px;
            font-weight: 600;
            {imagem_css}
        }}

        .st-key-topbar_user button p {{
            color: white;
            font-size: 11px;
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )