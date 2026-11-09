import re, html
import streamlit as st
from components.topbar import render_auth_topbar, render_auth_footer
import base64
from backend.app.auth import (
    create_user, verify_user, request_password_reset, reset_password,
    issue_remember_token, user_from_remember_token,
)
from backend.database.repositories import buscar_repositorio_usuario, buscar_repositorio_analisado
import streamlit.components.v1 as components
from backend.services.github_callback import iniciar_oauth
from pathlib import Path
from theme import load_css

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
HERO_PATH = Path("C:/Users/maria/OneDrive/Área de Trabalho/GitForesight/frontend/assets/auth_hero.jpg")

def _label(texto):
    st.markdown(f'<div class="auth-label">{texto}</div>', unsafe_allow_html=True)

_HERO_CACHE = {}

def _hero_b64():
    if "b64" not in _HERO_CACHE:                      # só guarda se achou o arquivo
        base = Path(__file__).resolve().parent
        for p in (base / "assets" / "auth_hero.jpg",
                  base.parent / "assets" / "auth_hero.jpg",
                  Path(HERO_PATH)):
            if p.exists():
                _HERO_CACHE["b64"] = base64.b64encode(p.read_bytes()).decode()
                break
    return _HERO_CACHE.get("b64", "")


def _hero():
    b64 = _hero_b64()
    if b64:
        st.html("<style>:root{--auth-hero:url('data:image/jpeg;base64,"
                f"{b64}');}}</style>")
    else:
        st.caption("⚠️ assets/auth_hero.jpg não encontrado")
    st.html('<div class="auth-hero" style="min-height:1px"></div>')

def _auto_fit():
    components.html(
        """
        <script>
        const P = window.parent, D = P.document;

        function fit() {
            const card = D.querySelector('.st-key-auth_card');
            if (!card) return;
            const root = D.documentElement;
            root.style.setProperty('--auth-zoom', '1');          // mede no tamanho real

            // alinha "Esqueceu a senha?" com o rótulo "Senha"
            const lbl = D.querySelector('.st-key-login_senha [data-testid="stWidgetLabel"]');
            const forgot = D.querySelector('.st-key-form_forgot');
            const form = D.querySelector('.st-key-auth_card [data-testid="stForm"]');
            if (lbl && forgot && form) {
                const l = lbl.getBoundingClientRect();
                const f = form.getBoundingClientRect();
                const fh = forgot.getBoundingClientRect().height;
                root.style.setProperty('--forgot-top',
                    (l.top - f.top + (l.height - fh) / 2).toFixed(1) + 'px');
            }

            const h = card.getBoundingClientRect().height;
            const top = D.querySelector('.auth-topbar');
            const foot = D.querySelector('.auth-footer');
            const avail = P.innerHeight
                - (top ? top.offsetHeight : 56)
                - (foot ? foot.offsetHeight : 48) - 24;
            const z = Math.max(0.6, Math.min(1, avail / h));
            root.style.setProperty('--auth-zoom', z.toFixed(3));
        }

        if (P.__gfFit) P.removeEventListener('resize', P.__gfFit);
        P.__gfFit = fit;
        P.addEventListener('resize', fit);
        fit();
        [60, 250, 700].forEach(t => setTimeout(fit, t));
        </script>
        """,
        height=0,
    )
    
def _header(icone, titulo, subtitulo):
    st.markdown(
        f'<div class="auth-head">{icone}<h2>{titulo}</h2></div>'
        f'<p class="auth-sub">{subtitulo}</p>',
        unsafe_allow_html=True,
    )

def _secure():
    st.markdown(
        f'<div class="auth-secure">{ICON_SHIELD}'
        '<span>Conexão segura • Autenticação em duas etapas disponível</span></div>',
        unsafe_allow_html=True,
    )

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

def _alternativas():
    """GitHub e SSO lado a lado (economiza altura e deixa tudo maior)."""
    b64_icon = base64.b64encode(ICON_SSO.encode("utf-8")).decode("utf-8")
    st.html(f'<style>:root {{ --sso-icon-url: url("data:image/svg+xml;base64,{b64_icon}"); }}</style>')

    with st.container(key="auth_alt"):
        c1, c2 = st.columns(2, gap="small")
        with c1:
            botao_github()
        with c2:
            st.button("Entrar com SSO da Empresa", key="auth_sso", use_container_width=True)

    st.caption("SSO: acesso gerenciado pela organização. "
               "Para obter uma conta, fale com o administrador.")
    
ICON_LOCK = (
    '<div class="auth-card-icon">'
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#818CF8" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="4" y="11" width="16" height="10" rx="2"/>'
    '<path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg></div>'
)

ICON_SHIELD = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#22C55E" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>'
)

def _ir_para(view):
    st.session_state.auth_view = view


def _entrar(user_id, name, email, metodo_login=None):
    st.session_state.autenticado = True
    st.session_state.user_id = user_id

    st.session_state.user_name = name
    st.session_state.user_email = email

    # Mantém compatibilidade com partes antigas do projeto.
    st.session_state.usuario = name
    st.session_state.email = email

    if metodo_login:
        st.session_state.metodo_login = metodo_login

    
def botao_github():
    if "github_oauth_url" not in st.session_state:
        st.session_state.github_oauth_url = iniciar_oauth()

    url = html.escape(
        st.session_state.github_oauth_url,
        quote=True
    )

    st.markdown(
        f"""
        <div class="auth-github">
            <a href="{url}" target="_self">
                Continuar com GitHub
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

def _cadastro():
    _header(ICON_REG_LOGIN, "Crie sua conta no Git Foresight",
            "Comece a explorar os riscos do seu repositório.")

    with st.form("form_cadastro", border=False):
        c1, c2 = st.columns(2, gap="small")
        nome = c1.text_input("Nome completo", key="cadastro_nome",
                             placeholder="Seu nome completo")
        email = c2.text_input("E-mail profissional", key="cadastro_email",
                              placeholder="voce@empresa.com")

        c3, c4 = st.columns(2, gap="small")
        senha = c3.text_input("Senha", type="password", key="cadastro_senha",
                              placeholder="Crie uma senha")
        
        confirma = c4.text_input("Confirmar senha", type="password",
                                 key="cadastro_confirma_senha",
                                 placeholder="Digite a senha novamente")

        enviar = st.form_submit_button("Criar conta",
                                       icon=":material/arrow_forward:", type="primary")

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
            try:
                user_id = create_user(nome.strip(), email.strip(), senha)
            except ValueError as erro:
                st.error(str(erro))
            else:
                _entrar(user_id, nome.strip(), email.strip())
                direcionar_usuario(user_id)
                st.rerun()

    st.markdown('<div class="auth-divider"><span>ou continue com</span></div>',
                unsafe_allow_html=True)
    _alternativas()

    with st.container(key="auth_login_row"):
        col_texto, col_link = st.columns(2, vertical_alignment="center")
        with col_texto:
            st.markdown("Já tem uma conta?")
        with col_link:
            st.button("Entrar", key="auth_to_login",
                      on_click=_ir_para, args=("login",), type="tertiary")
    _secure()


def _login():
    _header(ICON_REG_LOGIN, "Entre no Git Foresight",
            "Acesse o console de risco da sua equipe.")

    with st.form("form_login", border=False):
        email = st.text_input("E-mail profissional", key="login_email",
                              placeholder="voce@empresa.com")
        senha = st.text_input("Senha", type="password", key="login_senha",
                              placeholder="Digite sua senha")
        lembrar = st.checkbox("Manter conectado neste dispositivo", key="login_lembrar")
        # "Entrar" precisa vir ANTES no código: é ele que responde ao Enter
        enviar = st.form_submit_button("Entrar", type="primary",
                                       icon=":material/arrow_forward:",
                                       use_container_width=True)
        # posicionado por CSS na linha do rótulo "Senha"
        esqueceu = st.form_submit_button("Esqueceu a senha?", key="form_forgot",
                                         type="tertiary")

    if esqueceu:
        st.session_state.auth_view = "recuperar"
        st.rerun()

    if enviar:
        user = verify_user(email.strip(), senha)
        if user is None:
            st.error("E-mail ou senha incorretos.")
        else:
            if lembrar:
                st.session_state.cookie_pendente = issue_remember_token(user["id"])
            _entrar(user["id"], user["name"], user["email"])
            direcionar_usuario(user["id"])   # já faz o st.rerun()

    st.markdown('<div class="auth-divider"><span>ou continue com</span></div>',
                unsafe_allow_html=True)
    _alternativas()

    with st.container(key="auth_login_row"):
        col_texto, col_link = st.columns(2, vertical_alignment="center")
        with col_texto:
            st.markdown("Não tem uma conta?")
        with col_link:
            st.button("Cadastrar-se", key="auth_to_cadastro",
                      on_click=_ir_para, args=("cadastro",), type="tertiary")

    _secure()
    
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
        _entrar(user["id"], user["name"], user["email"])
        return True
    return False

def direcionar_usuario(user_id):

    # Se existe um fluxo de seleção em andamento, preserva-o.
    if st.session_state.get("pagina") == "choose_repo":
        return

    analisado = buscar_repositorio_analisado(user_id)

    if analisado:
        st.session_state.pagina = "overview"
        st.session_state.repositorio_conectado = analisado

    else:
        conectado = buscar_repositorio_usuario(user_id)

        st.session_state.pagina = "choose_repo"
        st.session_state.repositorio_conectado = conectado

        if conectado:
            st.session_state.repo_sel = conectado["name"]

    st.rerun()

def render():
    load_css("chrome", "auth")
    if restaurar_sessao():
        st.rerun()
    render_auth_topbar()

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    view = st.session_state.auth_view
    telas = {"cadastro": _cadastro, "login": _login,
             "recuperar": _recuperar, "redefinir": _redefinir}

    with st.container(key="auth_card"):
        if view in ("login", "cadastro"):
            col_img, col_form = st.columns([456, 512], gap="small")
            with col_img:
                _hero()
            with col_form:
                telas[view]()
        else:
            telas[view]()

    # if view == "login":
    #     _secure()   # a função do "Conexão segura" da resposta anterior

    render_auth_footer()
    _auto_fit()