"""Tela de Configurações do Git Foresight."""
import streamlit as st
from theme import load_css
from backend.database.repository_settings import (
    buscar_configuracoes_repositorio,
    salvar_configuracoes_repositorio,
)
from backend.database.repositories import buscar_repositorio_analisado

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


def _carregar_do_banco():
    repository_id = _obter_repository_id()
    user_id = st.session_state.get("user_id")

    if not repository_id or not user_id:
        return None

    dados = buscar_configuracoes_repositorio(
        repository_id,
        user_id,
    )

    if not dados:
        return None

    return {
        "cfg_provedor": "GitHub",
        "cfg_branch": dados["selected_branch"] or "main",
        "cfg_ignorados": dados["ignored_directories"],
        "cfg_commit": bool(dados["analyze_on_commit"]),
        "cfg_freq": dados["scan_frequency"],
        "cfg_horario": dados["scan_time"],
        "cfg_deps": bool(dados["scan_dependencies"]),
        "cfg_ia": bool(dados["update_ai_projections"]),
        "cfg_n_criticas": bool(dados["notify_critical"]),
        "cfg_n_score": bool(dados["notify_score_increase"]),
        "cfg_n_resumo": bool(dados["notify_weekly_summary"]),
        "cfg_n_sem_alertas": bool(dados["notify_no_alerts"]),
    }


def _aplicar_estado(dados):
    st.session_state.cfg_salvo = dict(dados)

    for chave, valor in dados.items():
        st.session_state[chave] = valor



def _iniciar_estado():
    repository_id = _obter_repository_id()

    if not repository_id:
        return False

    # Verifica se todas as configurações estão inicializadas.
    estado_incompleto = any(
        chave not in st.session_state
        for chave in DEFAULTS
    )

    # Recarrega se o repositório mudou ou se falta alguma configuração.
    if (
        st.session_state.get("cfg_repo_id") != repository_id
        or estado_incompleto
    ):
        dados = _carregar_do_banco()

        if dados is None:
            return False

        _aplicar_estado(dados)
        st.session_state.cfg_repo_id = repository_id

    return True

def _obter_repository_id():
    repository_id = st.session_state.get("repo_id")

    if repository_id:
        return repository_id

    user_id = st.session_state.get("user_id")

    if not user_id:
        return None

    repo = buscar_repositorio_analisado(user_id)

    if not repo:
        return None

    st.session_state.repo_id = repo["id"]
    st.session_state.repo_nome = repo["name"]
    st.session_state.repo_url = repo["url"]

    return repo["id"]

def _salvar():
    repository_id = st.session_state.get("repo_id")
    user_id = st.session_state.get("user_id")

    dados = {
        "selected_branch": st.session_state["cfg_branch"],
        "ignored_directories": st.session_state["cfg_ignorados"],
        "analyze_on_commit": st.session_state["cfg_commit"],
        "scan_frequency": st.session_state["cfg_freq"],
        "scan_time": st.session_state["cfg_horario"],
        "scan_dependencies": st.session_state["cfg_deps"],
        "update_ai_projections": st.session_state["cfg_ia"],
        "notify_critical": st.session_state["cfg_n_criticas"],
        "notify_score_increase": st.session_state["cfg_n_score"],
        "notify_weekly_summary": st.session_state["cfg_n_resumo"],
        "notify_no_alerts": st.session_state["cfg_n_sem_alertas"],
    }

    sucesso = salvar_configuracoes_repositorio(
        repository_id,
        user_id,
        dados,
    )

    if sucesso:
        st.session_state.cfg_salvo = {
            chave: st.session_state[chave]
            for chave in DEFAULTS
        }
        st.toast(
            "Configurações salvas.",
            icon=":material/check_circle:",
        )
    else:
        st.error("Não foi possível salvar as configurações.")


def _cancelar():
    dados = _carregar_do_banco()

    if dados:
        _aplicar_estado(dados)
        st.toast("Alterações descartadas.")
    else:
        st.error("Não foi possível recuperar as configurações.")

def _sincronizar():
    # TODO: chamar o serviço de sincronização do repositório
    st.toast("Sincronização iniciada.", icon=":material/sync:")


def _conectar_webhook():
    # TODO: abrir fluxo de cadastro do endpoint
    st.toast("Cadastro de webhook ainda não implementado.")

def _cabecalho(titulo: str, sub: str):
    _md(f'<div class="cfg-h">{titulo}</div><div class="cfg-sub">{sub}</div>')

def _toggle(titulo: str, desc: str, key: str, disabled=False):
    esq, dir_ = st.columns([4, 1.6], vertical_alignment="center")

    esq.markdown(
        _h(
            f'<div class="cfg-t">{titulo}</div>'
            f'<div class="cfg-d">{desc}</div>'
        ),
        unsafe_allow_html=True
    )

    dir_.toggle(
        titulo,
        key=f"toggle_{key}",
        label_visibility="collapsed",
        disabled=disabled
    )

def _integracao(icone: str, nome: str, desc: str, conectado: bool, acao=None):
    esq, dir_ = st.columns([5, 1.6], vertical_alignment="center")
    esq.markdown(_h(f"""
        <div class="cfg-int"><span class="cfg-ico">{icone}</span>
        <div><div class="cfg-t">{nome}</div><div class="cfg-d">{desc}</div></div></div>"""),
        unsafe_allow_html=True)
    if conectado:
        dir_.markdown('<div style="text-align:right"><span class="cfg-badge ok">Conectado</span></div>', unsafe_allow_html=True)
    else:
        dir_.button("Conectar", key=f"cfg_btn_{nome}", on_click=acao, width=True, disabled=True)


def _card_repositorio(repo: str):
    with st.container(key="cfg_card_repo"):
        _cabecalho("Repositório", "Repositório ativo e escopo da análise.")
        _md(f'''<div class="cfg-repo"><span class="cfg-mono">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                <circle cx="4" cy="3.5" r="1.8"/>
                <circle cx="12" cy="3.5" r="1.8"/>
                <circle cx="8" cy="12.5" r="1.8"/>
                <path d="M4 5.3v1.2c0 1 .8 1.5 1.8 1.5h4.4c1 0 1.8-.5 1.8-1.5V5.3M8 8v2.7"/>
            </svg>
            {repo}</span><span class="cfg-badge">Privado</span></div>''')
        c1, c2 = st.columns(2)
        c1.selectbox("Provedor", ["GitHub"], key="cfg_provedor")

        branches = list(BRANCHES)
        branch_atual = st.session_state["cfg_branch"]

        if branch_atual not in branches:
            branches.append(branch_atual)

        c2.selectbox(
            "Branch principal",
            branches,
            key="cfg_branch",
        )
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

        _toggle(
            "Analisar a cada novo commit",
            "Iniciar uma varredura ao receber alterações em main.",
            "cfg_commit",
            disabled=True
        )

        _md('<div class="cfg-hr"></div>')

        c1, c2 = st.columns(2)

        c1.selectbox(
            "Varredura completa",
            FREQUENCIAS,
            key="cfg_freq",
            disabled=True
        )

        c2.selectbox(
            "Horário (Brasília)",
            HORARIOS,
            key="cfg_horario",
            disabled=True
        )

        _toggle(
            "Verificar dependências e segredos",
            "Identificar pacotes vulneráveis e credenciais expostas.",
            "cfg_deps",
            disabled=True
        )

        _toggle(
            "Atualizar projeções de IA",
            "Recalcular a previsão de risco após cada varredura.",
            "cfg_ia",
            disabled=True
        )


def _card_notificacoes(email: str, canal: str):
    with st.container(key="cfg_card_notif"):
        _cabecalho("Notificações", "Escolha quais eventos devem gerar um alerta.")
        _toggle("Vulnerabilidades críticas e altas", "Avisar imediatamente por e-mail e Slack.", "cfg_n_criticas", disabled=True)
        _toggle("Aumento no score de risco", "Avisar quando o score subir 5 pontos ou mais.", "cfg_n_score", disabled=True)
        _toggle("Resumo semanal", "Receber tendências e recomendações por e-mail.", "cfg_n_resumo", disabled=True)
        _toggle("Varredura concluída sem alertas", "Enviar uma confirmação a cada análise.", "cfg_n_sem_alertas", disabled=True)
        _md(f'<div class="cfg-mail">✉ {email} • {canal}</div>')

def render(analysis=None, risk=None):
    # A sidebar e a topbar já são desenhadas pelo main() do app.py.
    load_css("base", "predictive", "settings")
    if not _iniciar_estado():
        st.warning(
            "Selecione um repositório antes de acessar as configurações."
        )
        return

    dados_repo = buscar_configuracoes_repositorio(
        st.session_state["repo_id"],
        st.session_state["user_id"],
    )

    repo = dados_repo["repo_nome"]
    email = st.session_state.get("user_email") or "E-mail não informado"
    canal = "Slack não configurado"

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

    txt, acoes = st.columns(2, gap="medium")
    txt.markdown(f'<div class="cfg-d" style="font-weight:600">As alterações se aplicam a {repo}.</div>', unsafe_allow_html=True)
    with acoes:
        b1, b2 = st.columns([1, 1.5])
        b1.button("Cancelar", key="cfg_cancel", on_click=_cancelar, width="stretch")
        b2.button("Salvar Alterações", key="cfg_save", type="primary", on_click=_salvar, width="stretch")