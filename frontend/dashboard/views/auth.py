import re
import streamlit as st
from components.topbar import render_auth_topbar, render_auth_footer
import base64
from backend.app.auth import (
    create_user, verify_user, request_password_reset, reset_password,
    issue_remember_token, user_from_remember_token,
)
import streamlit.components.v1 as components

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _label(texto):
    st.markdown(f'<div class="auth-label">{texto}</div>', unsafe_allow_html=True)

ICON_SSO = (
    '<svg width="14" height="12" viewBox="0 0 14 12" fill="none" '
    'xmlns="http://www.w3.org/2000/svg"> '
    '<path d="M4 0.900391H9.33398C9.44896 0.900391 9.55934 '
    '0.94607 9.64062 1.02734C9.72169 1.10852 9.76749 1.21832 9.76758 1.33301V3.56641H12.001C12.1159 3.56641 '
    '12.2263 3.61212 12.3076 3.69336C12.3889 3.77463 12.4346 3.8851 12.4346 4V10.667C12.4345 10.7817 '
    '12.3886 10.8915 12.3076 10.9727C12.2263 11.0539 12.1159 11.0996 12.001 11.0996H1.33301C1.21819 11.0995 '
    '1.10852 11.0538 1.02734 10.9727C0.946142 10.8915 0.900477 10.7818 0.900391 10.667V6C0.900391 5.8851 '
    '0.946066 5.77463 1.02734 5.69336C1.10849 5.6124 1.21834 5.56652 1.33301 5.56641H3.56641V1.33301C3.56649 1.21842 '
    '3.61242 1.1085 3.69336 1.02734C3.77456 0.946146 3.88514 0.900475 4 0.900391Z" '
    'stroke="white" stroke-width="1.8" stroke-linecap="round"/> '
    '</svg>'
)

ICON_REG_LOGIN = (
    '<div class="auth-card-icon">'
    '<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"> '
    '<rect x="0.5" y="0.5" width="39" height="39" rx="7.5" stroke="#6366F1" stroke-opacity="0.25098"/> '
    '<path d="M13.0547 26.2513C13.0546 25.182 13.3632 24.1353 13.9433 23.237C14.5234 22.3387 '
    '15.3504 21.6268 16.3251 21.1868C17.2998 20.7469 18.3807 20.5975 19.4382 '
    '20.7567C20.4957 20.9159 21.4847 21.3768 22.2867 22.0842M24.8621 22.7784V26.9456M26.9458 24.862H22.7785M22.0839 '
    '17.2222C22.0839 19.14 20.5291 20.6948 18.6111 20.6948C16.6932 20.6948 15.1384 19.14 15.1384 '
    '17.2222C15.1384 15.3043 16.6932 13.7495 18.6111 13.7495C20.5291 13.7495 22.0839 15.3043 22.0839 17.2222Z" '
    'stroke="#6366F1" stroke-width="1.8" stroke-linecap="round"/> '
    '</svg>'
    '</div>'
)

GITHUB = (
    '<style>'
        'div[data-testid="stElementContainer"] button[id="auth_github"] {'
            'border: 1px solid var(--st-border-color, #d3d3d3) !important;'
            'border-radius: 0.5rem !important;'
            
            'font-family: var(--st-font) !important;'
            'color: var(--st-text-color, #31333F) !important;'
            'background-color: var(--st-background-color, #FFFFFF) !important;'

            'padding: 10px 16px !important;'
            'font-weight: 500 !important;'

            'width: 100% !important;'
            'height: auto !important;'

            'opacity: 1 !important;'
            'cursor: not-allowed !important;}'
        'div[data-testid="stElementContainer"] button[id="auth_github"]:disabled {'
            'background-color: var(--st-secondary-background-color, #f0f2f6) !important;}'
    '</style>'
)

def _ir_para(view):
    st.session_state.auth_view = view

def _entrar(nome, email):
    st.session_state.usuario = {"nome": nome, "email": email}
    st.session_state.autenticado = True

def _cadastro():
    st.markdown(ICON_REG_LOGIN, unsafe_allow_html=True)
    
    st.markdown("#### Crie sua conta no Git Foresight")
    st.caption("Comece a explorar os riscos do seu repositório.")
    
    st.markdown(GITHUB,unsafe_allow_html=True)

    st.button("Continuar com GitHub", key="auth_github", disabled=False) # HABILITAR PARA FUNCIONAR

    st.markdown(
        '<div class="auth-divider"><span>ou cadastre-se com e-mail</span></div>',
        unsafe_allow_html=True,
    )

    with st.form("form_cadastro", border=False):
        nome = st.text_input("Nome completo", placeholder="Seu nome completo")
        email = st.text_input("E-mail profissional", placeholder="voce@empresa.com")
        senha = st.text_input("Senha", type="password", placeholder="Crie uma senha")
        st.caption("Prefira uma senha longa, com letras, números e símbolos.")
        confirma = st.text_input(
            "Confirmar senha", type="password",
            placeholder="Digite a senha novamente",
        )
        enviar = st.form_submit_button(
            "Criar conta", icon=":material/arrow_forward:", type="primary"
        )

    if enviar:
        erros = []
        if len(nome.strip()) < 3:
            erros.append("Informe seu nome completo.")
        if not EMAIL_RE.match(email.strip()):
            erros.append("Informe um e-mail válido.")
        if len(senha) < 8:
            erros.append("A senha deve ter pelo menos 8 caracteres.")
        if senha != confirma:
            erros.append("As senhas não coincidem.")

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            _entrar(nome.strip(), email.strip())
            st.rerun()

    # Colunas externas para centralizar no layout
    col_esq, col_centro, col_dir = st.columns([1, 2, 1])

    with col_centro:

        # Colunas internas para texto + botão
        col_texto, col_link = st.columns(
            [3, 1],
            vertical_alignment="center"
        )

        with col_texto:
            st.markdown(
                '<p style="margin:0; white-space:nowrap;">Já tem uma conta?</p>',
                unsafe_allow_html=True
            )

        with col_link:
            st.button(
                "Entrar",
                key="auth_to_login",
                on_click=_ir_para,
                args=("login",)
            )

    st.divider()
    
    b64_icon = base64.b64encode(ICON_SSO.encode("utf-8")).decode("utf-8")
    st.html(
    f"""
        <style>
        :root {{
            --sso-icon-url: url("data:image/svg+xml;base64,{b64_icon}");
        }}
        </style>
        """
    )
    st.button("Entrar com SSO da Empresa", key="auth_sso", disabled=False)
    st.caption("Seu acesso é gerenciado pela organização. Para obter uma conta, fale com o administrador.")

def _login():
    st.markdown("## Entre no Git Foresight")
    st.caption("Acesse o console de risco da sua equipe.")

    st.button("Continuar com GitHub", key="auth_github", disabled=False)
    st.markdown(
        '<div class="auth-divider"><span>ou entre com e-mail</span></div>',
        unsafe_allow_html=True,
    )

    with st.form("form_login", border=False):
            _label("E-mail profissional")
            email = st.text_input("E-mail profissional", key="login_email", label_visibility="collapsed", placeholder="voce@empresa.com")
            # "Senha" e "Esqueceu a senha?" na mesma linha
            st.markdown(
                '<div class="auth-label-row">'
                '<span class="auth-label">Senha</span>'
                '<a class="auth-link" href="?view=recuperar" target="_self">Esqueceu a senha?</a>'
                '</div>',
                unsafe_allow_html=True,
            )
            senha = st.text_input("Senha", type="password", key="login_senha", label_visibility="collapsed", placeholder="Digite sua senha")
            
            enviar = st.form_submit_button(
                "Entrar", icon=":material/arrow_forward:", type="primary"
            )

    # Manter conectado
    lembrar = st.checkbox("Manter conectado neste dispositivo", key="login_lembrar")

    if st.button("Entrar", key="login_entrar", type="primary", icon=":material/arrow_forward:"):
        user = verify_user(email.strip(), senha)
        if user is None:
            st.error("E-mail ou senha incorretos.")
        else:
            if lembrar:
                st.session_state.cookie_pendente = issue_remember_token(user["id"])
            _entrar(user["name"], user["email"])
            st.rerun()

    st.divider()

    b64_icon = base64.b64encode(ICON_SSO.encode("utf-8")).decode("utf-8")
    st.html(
        f"""
            <style>
            :root {{
                --sso-icon-url: url("data:image/svg+xml;base64,{b64_icon}");
            }}
            </style>
        """
    )
    st.button("Entrar com SSO da Empresa", key="auth_sso", disabled=False)
    st.caption("Seu acesso é gerenciado pela organização. "
               "Para obter uma conta, fale com o administrador.")
    
    #colocar o conexão segura
    
def _recuperar():
    st.markdown("## Recuperar senha")
    st.caption("Informe seu e-mail para receber o código de redefinição.")
    email = st.text_input("E-mail profissional", key="rec_email")

    if st.button("Enviar código", key="rec_enviar", type="primary"):
        token = request_password_reset(email.strip())
        if token:
            # MODO DEMONSTRAÇÃO: não há servidor de e-mail, então o código sai no terminal.
            # Em produção, envie por e-mail (smtplib ou um serviço) e remova esta linha.
            print(f"[DEMO] código de redefinição para {email}: {token}")
        # Mesma mensagem nos dois casos, para não revelar quais e-mails existem
        st.success("Se o e-mail estiver cadastrado, enviamos o código.")

    st.button("Já tenho o código", key="rec_tem_codigo",
              on_click=_ir_para, args=("redefinir",))
    st.button("Voltar ao login", key="rec_voltar",
              on_click=_ir_para, args=("login",))

def _redefinir():
    st.markdown("## Nova senha")
    codigo = st.text_input("Código recebido", key="red_codigo")
    nova = st.text_input("Nova senha", type="password", key="red_nova")
    confirma = st.text_input("Confirmar senha", type="password", key="red_conf")

    if st.button("Redefinir senha", key="red_ok", type="primary"):
        if len(nova) < 8:
            st.error("A senha deve ter pelo menos 8 caracteres.")
        elif nova != confirma:
            st.error("As senhas não coincidem.")
        elif reset_password(codigo.strip(), nova):
            st.success("Senha alterada. Faça login com a nova senha.")
            st.button("Ir para o login", key="red_login",
                      on_click=_ir_para, args=("login",))
        else:
            st.error("Código inválido ou expirado.")
            
def gravar_cookie(token, dias=30):
    components.html(
        f"<script>window.parent.document.cookie = "
        f"'gf_remember={token}; max-age={dias * 86400}; path=/; SameSite=Lax';"
        f"</script>",
        height=0,
    )


def restaurar_sessao():
    token = st.context.cookies.get("gf_remember")
    user = user_from_remember_token(token) if token else None
    if user:
        _entrar(user["name"], user["email"])
        return True
    return False

def render():
    if restaurar_sessao():
        st.rerun()
    render_auth_topbar()

    st.markdown(
        """
        <style>
        /* Tela sem sidebar nem barra padrão do Streamlit */
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] { display: none !important; }

        /* Abre espaço para a barra (80px) e o rodapé (80px) */
        [data-testid="stMainBlockContainer"] {
            padding-top: 112px !important;
            padding-bottom: 112px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="auth_card"):
        view = st.session_state.auth_view
        {"cadastro": _cadastro, "login": _login,
        "recuperar": _recuperar, "redefinir": _redefinir}[view]()

    render_auth_footer()