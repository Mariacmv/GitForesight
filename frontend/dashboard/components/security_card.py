import streamlit as st

from components.cards import html_inline   # use o mesmo import que você usa nos outros cards

ICONE_CHAVE = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M2 18v3c0 .6.4 1 1 1h4v-3h3v-3h2l1.4-1.4a6.5 6.5 0 1 0-4-4Z"/>'
    '<circle cx="16.5" cy="7.5" r=".5" fill="currentColor"/></svg>'
)
ICONE_ESCUDO = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>'
    '<path d="m9 12 2 2 4-4"/></svg>'
)
ICONE_CADEADO = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>'
    '<path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
)


def _item(icone, cor, titulo, descricao, badge=None, badge_ativo=True):
    badge_html = ""
    if badge:
        classe = "sec-badge" if badge_ativo else "sec-badge sec-badge-off"
        badge_html = f'<span class="{classe}">{badge}</span>'

    return html_inline(f"""
        <div class="sec-icon" style="color:{cor};">{icone}</div>
        <div class="sec-head"><span class="sec-title">{titulo}</span>{badge_html}</div>
        <div class="sec-desc">{descricao}</div>
    """)


def render_seguranca(dias_desde_troca, dois_fatores, ao_alterar_senha, ao_gerenciar, ao_ver_codigos):
    with st.container(key="seguranca_card"):
        st.markdown(html_inline("""
            <div class="sess-title">Segurança</div>
            <div class="sess-sub">Proteja o acesso à sua conta.</div>
        """), unsafe_allow_html=True)

        col_senha, col_2fa, col_rec = st.columns(3, gap="medium")

        with col_senha:
            st.markdown(_item(ICONE_CHAVE, "#818CF8", "Senha de acesso",
                              f"Última alteração<br>há {dias_desde_troca} dias."),
                        unsafe_allow_html=True)
            st.button("Alterar Senha", key="sec_senha", on_click=ao_alterar_senha)

        with col_2fa:
            st.markdown(_item(ICONE_ESCUDO, "#22C55E", "Duas etapas",
                              "Código solicitado em<br>cada novo acesso.",
                              badge="Ativada" if dois_fatores else "Desativada",
                              badge_ativo=dois_fatores),
                        unsafe_allow_html=True)
            st.button("Gerenciar", key="sec_2fa", on_click=ao_gerenciar)

        with col_rec:
            st.markdown(_item(ICONE_CADEADO, "#818CF8", "Recuperação",
                              "Guarde seus códigos em um local<br>seguro."),
                        unsafe_allow_html=True)
            st.button("Ver Códigos", key="sec_codigos", on_click=ao_ver_codigos)

        st.markdown(html_inline("""
            <div class="sec-divider"></div>
            <div class="sec-foot">Nunca compartilhe sua senha ou seus códigos de autenticação com a equipe.</div>
        """), unsafe_allow_html=True)