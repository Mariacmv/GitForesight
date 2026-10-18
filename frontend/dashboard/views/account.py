from html import escape

import streamlit as st

from components.cards import html_inline
from components.dados_card import render_dados_pessoais, salvar_dados_pessoais
from components.security_card import render_seguranca
from components.sidebar import render_sidebar
from components.topbar import render_auth_topbar

CAMPOS_DADOS = ["dados_nome", "dados_cargo", "dados_email", "dados_idioma", "dados_fuso"]

ICONE_DESKTOP = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="2" y="3" width="20" height="14" rx="2"/>'
    '<path d="M8 21h8M12 17v4"/></svg>'
)
ICONE_LAPTOP = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="4" y="4" width="16" height="12" rx="2"/>'
    '<path d="M2 20h20"/></svg>'
)

def render_profile_card(nome, email, avatar_url, papel, organizacao, repositorio):
    iniciais = "".join(p[0] for p in nome.split()[:2]).upper() or "U"

    foto = (
        f'<img src="{escape(avatar_url)}" alt="{escape(nome)}">'
        if avatar_url else iniciais
    )

    with st.container(key="profile_card"):
        st.markdown(html_inline(f"""
            <div class="pc-title">Perfil</div>

            <div class="pc-header">
                <div class="pc-avatar">{foto}</div>
                <div>
                    <div class="pc-name">{escape(nome)}</div>
                    <div class="pc-email">{escape(email)}</div>
                </div>
            </div>

            <div class="pc-badges">
                <span class="pc-badge pc-badge-primary">{escape(papel)}</span>
                <span class="pc-badge pc-badge-success">E-mail verificado</span>
            </div>

            <div class="pc-divider"></div>

            <div class="pc-label">ORGANIZAÇÃO</div>
            <div class="pc-value">{escape(organizacao)}</div>
            <div class="pc-mono">{escape(repositorio)}</div>
        """), unsafe_allow_html=True)

        st.button("Alterar Foto", key="pc_alterar_foto", icon=":material/photo_camera:")


def render_sessoes(sessoes, ao_encerrar, ao_encerrar_outras):
    with st.container(key="sessions_card"):
        st.markdown(html_inline("""
            <div class="sess-title">Sessões Ativas</div>
            <div class="sess-sub">Dispositivos conectados à sua conta.</div>
        """), unsafe_allow_html=True)

        for i, s in enumerate(sessoes):
            if i > 0:
                st.markdown('<div class="sess-divider"></div>', unsafe_allow_html=True)

            icone = ICONE_LAPTOP if s.get("tipo") == "laptop" else ICONE_DESKTOP

            col_nome, col_acao = st.columns([3, 1], vertical_alignment="center")

            with col_nome:
                st.markdown(html_inline(f"""
                    <div class="sess-name">{icone}<span>{escape(s['dispositivo'])}</span></div>
                """), unsafe_allow_html=True)

            with col_acao:
                if s["atual"]:
                    st.markdown('<div class="sess-badge">Atual</div>', unsafe_allow_html=True)
                else:
                    st.button("Encerrar", key=f"sess_link_{s['id']}",
                              on_click=ao_encerrar, args=(s["id"],))

            st.markdown(html_inline(f"""
                <div class="sess-meta">{escape(s['local'])} • {escape(s['ip'])}</div>
                <div class="sess-meta">{escape(s['ultimo_acesso'])}</div>
            """), unsafe_allow_html=True)

        st.markdown('<div class="sess-divider"></div>', unsafe_allow_html=True)

        st.button("Encerrar Outras Sessões", key="sess_all", on_click=ao_encerrar_outras)

        st.markdown(
            '<div class="sess-foot">Não reconhece um dispositivo? '
            'Encerre a sessão e altere sua senha.</div>',
            unsafe_allow_html=True,
        )


# ---------- ações da página ----------

def _cancelar():
    # Apagar as chaves faz os campos voltarem aos valores cadastrados
    for chave in CAMPOS_DADOS:
        st.session_state.pop(chave, None)


def _gravar(dados):
    # TODO: gravar no banco (update_user) e, se dados["email_alterado"], enviar verificação
    st.session_state.usuario = dados["nome"]
    st.session_state.email = dados["email"]


def _aviso(texto):
    return lambda: st.toast(texto)


# ---------- página ----------

def render():
    render_auth_topbar(mostrar_usuario=True)
    render_sidebar()

    usuario = {
        "nome": st.session_state.get("usuario") or "Usuário",
        "email": st.session_state.get("email") or "",
        "cargo": "Engenheiro de Software",       # TODO: vir do banco
        "idioma": "Português (Brasil)",          # TODO: vir do banco
        "fuso": "Brasília (UTC−03:00)",          # TODO: vir do banco
    }

    sessoes = [   # TODO: vir do banco
        {"id": 1, "dispositivo": "Chrome • macOS", "tipo": "desktop", "atual": True,
         "local": "São Paulo, Brasil", "ip": "189.42.18.102", "ultimo_acesso": "Ativo agora"},
        {"id": 2, "dispositivo": "Firefox • Windows", "tipo": "laptop", "atual": False,
         "local": "São Paulo, Brasil", "ip": "189.42.18.108",
         "ultimo_acesso": "Último acesso há 2 horas"},
    ]

    st.title("Minha Conta")
    st.caption("Gerencie seu perfil, seus dados pessoais e a segurança do seu acesso.")

    col_esq, col_dir = st.columns([1, 2], gap="medium")

    with col_esq:
        render_profile_card(
            nome=usuario["nome"],
            email=usuario["email"],
            avatar_url=st.session_state.get("avatar_url"),
            papel="Administrador",
            organizacao="Empresa • Engenharia",
            repositorio="empresa/backend",
        )
        render_sessoes(
            sessoes,
            ao_encerrar=lambda sid: st.toast(f"Encerrar sessão {sid}: em construção"),
            ao_encerrar_outras=_aviso("Encerrar outras sessões: em construção"),
        )

    with col_dir:
        render_dados_pessoais(
            nome=usuario["nome"],
            cargo=usuario["cargo"],
            email=usuario["email"],
            idioma=usuario["idioma"],
            fuso=usuario["fuso"],
        )
        render_seguranca(
            dias_desde_troca=30,
            dois_fatores=True,
            ao_alterar_senha=_aviso("Alterar senha: em construção"),
            ao_gerenciar=_aviso("Duas etapas: em construção"),
            ao_ver_codigos=_aviso("Códigos de recuperação: em construção"),
        )

    with st.container(key="conta_rodape"):
        col_nota, col_cancelar, col_salvar = st.columns(
            [3, 1, 1.6],
            gap="small",
            vertical_alignment="center"
        )

        col_nota.markdown(
            '<div class="conta-note">As alterações se aplicam apenas à sua conta.</div>',
            unsafe_allow_html=True,
        )

        col_cancelar.button(
            "Cancelar",
            key="conta_cancelar",
            on_click=_cancelar
        )

        salvou = col_salvar.button(
            "Salvar Alterações",
            key="conta_salvar",
            type="primary"
        )