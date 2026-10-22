"""Tela de Configurações do Git Foresight."""
import streamlit as st

# Valores iniciais. Troque por leitura do seu banco/config do usuário.
DEFAULTS = {
    "cfg_provedor": "GitHub",
    "cfg_branch": "main",
    "cfg_ignorados": "node_modules/, .venv/, dist/",
    "cfg_commit": True,
    "cfg_freq": "Diariamente",
    "cfg_horario": "02:00",
    "cfg_deps": True,
    "cfg_ia": True,
    "cfg_n_criticas": True,
    "cfg_n_score": True,
    "cfg_n_resumo": True,
    "cfg_n_sem_alertas": False,
}
PROVEDORES = ["GitHub", "GitLab", "Bitbucket"]
BRANCHES = ["main", "master", "develop"]
FREQUENCIAS = ["A cada hora", "Diariamente", "Semanalmente"]
HORARIOS = [f"{h:02d}:00" for h in range(24)]


def _h(html: str) -> str:
    """Evita que o markdown trate indentação como código e linhas vazias como fim do HTML."""
    return "\n".join(l.strip() for l in html.splitlines() if l.strip())


def _md(html: str):
    st.markdown(_h(html), unsafe_allow_html=True)

def _iniciar_estado():
    if "cfg_salvo" not in st.session_state:
        st.session_state.cfg_salvo = dict(DEFAULTS)  # TODO: carregar do banco
    for k, v in st.session_state.cfg_salvo.items():
        st.session_state.setdefault(k, v)


def _salvar():
    st.session_state.cfg_salvo = {k: st.session_state[k] for k in DEFAULTS}
    # TODO: persistir no backend (ex.: salvar_configuracoes(user_id, st.session_state.cfg_salvo))
    st.toast("Configurações salvas.", icon=":material/check_circle:")


def _cancelar():
    for k, v in st.session_state.cfg_salvo.items():
        st.session_state[k] = v


def _sincronizar():
    # TODO: chamar o serviço de sincronização do repositório
    st.toast("Sincronização iniciada.", icon=":material/sync:")


def _conectar_webhook():
    # TODO: abrir fluxo de cadastro do endpoint
    st.toast("Cadastro de webhook ainda não implementado.")

def _cabecalho(titulo: str, sub: str):
    _md(f'<div class="cfg-h">{titulo}</div><div class="cfg-sub">{sub}</div>')


def _toggle(titulo: str, desc: str, key: str):
    esq, dir_ = st.columns([8, 1], vertical_alignment="center")
    esq.markdown(_h(f'<div class="cfg-t">{titulo}</div><div class="cfg-d">{desc}</div>'), unsafe_allow_html=True)
    dir_.toggle(titulo, key=key, label_visibility="collapsed")


def _integracao(icone: str, nome: str, desc: str, conectado: bool, acao=None):
    esq, dir_ = st.columns([5, 1.6], vertical_alignment="center")
    esq.markdown(_h(f"""
        <div class="cfg-int"><span class="cfg-ico">{icone}</span>
        <div><div class="cfg-t">{nome}</div><div class="cfg-d">{desc}</div></div></div>"""),
        unsafe_allow_html=True)
    if conectado:
        dir_.markdown('<div style="text-align:right"><span class="cfg-badge ok">Conectado</span></div>', unsafe_allow_html=True)
    else:
        dir_.button("Conectar", key=f"cfg_btn_{nome}", on_click=acao, use_container_width=True)


def _card_repositorio(repo: str):
    with st.container(key="cfg_card_repo"):
        _cabecalho("Repositório", "Repositório ativo e escopo da análise.")
        _md(f'<div class="cfg-repo"><span class="cfg-mono">⁘ {repo}</span><span class="cfg-badge">Privado</span></div>')
        c1, c2 = st.columns(2)
        c1.selectbox("Provedor", PROVEDORES, key="cfg_provedor")
        c2.selectbox("Branch principal", BRANCHES, key="cfg_branch")
        st.text_input("Diretórios ignorados", key="cfg_ignorados")
        _md('<div class="cfg-d">Os diretórios ignorados não entram no cálculo do score de risco.</div>')
        a, b = st.columns([1, 1], vertical_alignment="center")
        a.markdown('<span class="cfg-badge ok">Sincronizado há 10 min</span>', unsafe_allow_html=True)
        b.button("Sincronizar", key="cfg_sync", icon=":material/sync:", on_click=_sincronizar, use_container_width=True)


def _card_integracoes():
    with st.container(key="cfg_card_integ"):
        _cabecalho("Integrações", "Conecte ferramentas ao fluxo de monitoramento.")
        _integracao("GH", "GitHub", "Organização: empresa • Acesso autorizado", True)
        _integracao("#", "Slack", "Alertas enviados para #seguranca-backend", True)
        _integracao("⚭", "Webhook", "Envie eventos para um endpoint próprio.", False, _conectar_webhook)
        _md("""<div class="cfg-note">As integrações utilizam apenas as permissões necessárias para leitura e envio de alertas.
        <br><a href="https://github.com/settings/installations" target="_blank">Gerenciar permissões do GitHub</a></div>""")


def _card_varredura():
    with st.container(key="cfg_card_scan"):
        _cabecalho("Preferências de Varredura", "Controle a frequência e as verificações automáticas.")
        _toggle("Analisar a cada novo commit", "Iniciar uma varredura ao receber alterações em main.", "cfg_commit")
        c1, c2 = st.columns(2)
        c1.selectbox("Varredura completa", FREQUENCIAS, key="cfg_freq")
        c2.selectbox("Horário (Brasília)", HORARIOS, key="cfg_horario")
        _toggle("Verificar dependências e segredos", "Identificar pacotes vulneráveis e credenciais expostas.", "cfg_deps")
        _toggle("Atualizar projeções de IA", "Recalcular a previsão de risco após cada varredura.", "cfg_ia")


def _card_notificacoes(email: str, canal: str):
    with st.container(key="cfg_card_notif"):
        _cabecalho("Notificações", "Escolha quais eventos devem gerar um alerta.")
        _toggle("Vulnerabilidades críticas e altas", "Avisar imediatamente por e-mail e Slack.", "cfg_n_criticas")
        _toggle("Aumento no score de risco", "Avisar quando o score subir 5 pontos ou mais.", "cfg_n_score")
        _toggle("Resumo semanal", "Receber tendências e recomendações por e-mail.", "cfg_n_resumo")
        _toggle("Varredura concluída sem alertas", "Enviar uma confirmação a cada análise.", "cfg_n_sem_alertas")
        _md(f'<div class="cfg-mail">✉ {email} • {canal}</div>')

def render(analysis=None, risk=None):
    # A sidebar e a topbar já são desenhadas pelo main() do app.py.
    _iniciar_estado()

    # TODO: ligar estes valores ao contexto / usuário reais
    repo = st.session_state.get("repo_nome", "empresa/backend")
    email = st.session_state.get("user_email", "lucas.silva@empresa.com")
    canal = "#seguranca-backend"

    _md("""<div class="cfg-title">Configurações</div>
    <div class="cfg-sub" style="margin-bottom:6px">Defina como o Git Foresight monitora o repositório e avisa sua equipe.</div>""")

    esq, dir_ = st.columns(2, gap="medium")
    with esq:
        _card_repositorio(repo)
    with dir_:
        _card_integracoes()

    esq, dir_ = st.columns(2, gap="medium")
    with esq:
        _card_varredura()
    with dir_:
        _card_notificacoes(email, canal)

    txt, b1, b2 = st.columns([6, 1.1, 1.6], vertical_alignment="center")
    txt.markdown(f'<div class="cfg-d" style="font-weight:600">As alterações se aplicam a {repo}.</div>', unsafe_allow_html=True)
    b1.button("Cancelar", key="cfg_cancel", on_click=_cancelar, use_container_width=True)
    b2.button("Salvar Alterações", key="cfg_save", type="primary", on_click=_salvar, use_container_width=True)