import streamlit as st
from components.cards import html_inline
import re

IDIOMAS = ["Português (Brasil)", "English (US)", "Español"]
FUSOS = [
    "Brasília (UTC−03:00)",
    "Manaus (UTC−04:00)",
    "Fernando de Noronha (UTC−02:00)",
    "UTC",
]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def indice(opcoes, valor):
    return opcoes.index(valor) if valor in opcoes else 0

def render_dados_pessoais(nome, cargo, email, idioma, fuso):
    with st.container(key="dados_card"):
        st.markdown(html_inline("""
            <div class="sess-title">Dados Pessoais</div>
            <div class="sess-sub">Esses dados aparecem nas atividades e nos relatórios da equipe.</div>
        """), unsafe_allow_html=True)

        col_nome, col_cargo = st.columns(2)
        col_nome.text_input("Nome completo", value=nome, key="dados_nome")
        col_cargo.text_input("Cargo", value=cargo, key="dados_cargo")

        st.text_input("E-mail profissional", value=email, key="dados_email")

        col_idioma, col_fuso = st.columns(2)
        col_idioma.selectbox(
            "Idioma", IDIOMAS, index=indice(IDIOMAS, idioma), key="dados_idioma"
        )
        col_fuso.selectbox(
            "Fuso horário", FUSOS, index=indice(FUSOS, fuso), key="dados_fuso"
        )

        st.caption("Ao alterar o e-mail, enviaremos um novo link de verificação.")


def salvar_dados_pessoais(email_atual, ao_salvar):
    """Lê os campos, valida e chama ao_salvar(dados). Use no botão de salvar da página."""
    nome = st.session_state.get("dados_nome", "").strip()
    cargo = st.session_state.get("dados_cargo", "").strip()
    email = st.session_state.get("dados_email", "").strip()

    erros = []
    if len(nome) < 3:
        erros.append("Informe seu nome completo.")
    if not EMAIL_RE.match(email):
        erros.append("Informe um e-mail válido.")

    if erros:
        for erro in erros:
            st.error(erro)
        return False

    ao_salvar({
        "nome": nome,
        "cargo": cargo,
        "email": email,
        "idioma": st.session_state["dados_idioma"],
        "fuso": st.session_state["dados_fuso"],
        "email_alterado": email.lower() != email_atual.lower(),
    })
    st.success("Dados atualizados.")
    return True