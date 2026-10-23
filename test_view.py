from frontend.dashboard.theme import load_css
from pathlib import Path
import sys
import streamlit as st
from frontend.dashboard.components.sidebar  import _logo_base64
import time
from html import escape

st.set_page_config(
    page_title="Git Foresight",
    layout="wide",
    initial_sidebar_state="collapsed",
)

RAIZ = Path(__file__).resolve().parent
DASHBOARD = RAIZ / "frontend" / "dashboard"

# Topbar do projeto (opcional): se não carregar, a prévia segue sem ela
sys.path.insert(0, str(DASHBOARD))
try:
    from frontend.dashboard.components.topbar import render_auth_topbar
except Exception:
    render_auth_topbar = None


# ===================== dados simulados =====================

INFO = {
    "full_name": "empresa/backend",
    "language": "Python",
    "private": True,
    "commits": 1847,
    "contributors": 12,
    "default_branch": "main",
    "branches": ["main", "develop"],
}

# (antes de rodar, em andamento, concluída)
ETAPAS = [
    ("Clonar o repositório", "Clonando o repositório...", "Repositório clonado"),
    ("Indexar histórico de commits", "Indexando histórico de commits...",
     "Indexação do histórico de commits concluída"),
    ("Gerar a base de dados", "Gerando a base de dados...", "Base de dados gerada"),
    ("Mapear contribuidores", "Mapeando contribuidores...",
     "Mapeamento de contribuidores concluído"),
    ("Calcular o risco por semana", "Calculando o risco por semana...",
     "Cálculo de risco concluído"),
    ("Identificar hotspots e módulos críticos",
     "Identificando hotspots e módulos críticos...",
     "Hotspots e módulos críticos identificados"),
]

PESOS = [10, 45, 10, 15, 10, 10]   # soma 100 (a indexação é a etapa mais demorada)

DEPOIS = [
    "Arquivos e módulos com maior concentração de alterações recentes.",
    "Contribuidores mais ativos e distribuição de commits no período analisado.",
    "Indicadores iniciais para revisão, refatoração e acompanhamento contínuo.",
]

ACHADOS = [
    "payment_gateway.py é o arquivo com mais alterações: 1.240 linhas alteradas em 18 commits.",
    "auth_service.py também se destaca: 845 linhas alteradas em 12 commits nos últimos 30 dias.",
    "12 contribuidores identificados até o momento, com 3 deles concentrando 62% das alterações.",
]

OPCOES = ["Pronta para iniciar", "Em andamento (68%)", "Animada", "Concluída"]

TITULOS = {
    "pronta": ("Pronto para iniciar a primeira análise",
               "Confira o repositório e a branch selecionados para iniciar a análise.",
               "Primeira análise pronta para iniciar", "AGUARDANDO"),
    "andamento": (f"Analisando {INFO['full_name']} · {INFO['default_branch']}",
                  "A primeira análise está em andamento. "
                  "Veja o progresso e os primeiros achados disponíveis.",
                  "Primeira análise em andamento", "PROCESSANDO"),
    "concluida": ("Primeira análise concluída",
                  "Os resultados já estão disponíveis para exploração.",
                  "Primeira análise concluída", "CONCLUÍDO"),
}

ICONE_BRANCH = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#818CF8" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="6" cy="5" r="2"/><circle cx="18" cy="5" r="2"/><circle cx="12" cy="19" r="2"/>'
    '<path d="M6 7v2a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3V7M12 12v5"/></svg>'
)


# ===================== CSS =====================

CSS_TELA = """
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stHeader"] { display: none !important; }

[data-testid="stMainBlockContainer"] {
    max-width: 1248px;
    padding-top: 96px !important;
    padding-bottom: 80px !important;
}

/* ----- Títulos da página ----- */
.pg-title {
    margin: 0 0 8px;
    color: #F8FAFC;
    font-family: 'Inter', sans-serif;
    font-size: 36px;
    font-weight: 600;
    line-height: 1.2;
}
.pg-sub {
    margin: 0 0 28px;
    color: #94A3B8;
    font-family: 'Inter', sans-serif;
    font-size: 16px;
}

/* ----- Stepper ----- */
.stepper-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0 0 24px;
    font-family: 'Inter', sans-serif;
}
.steps-container { display: flex; align-items: center; gap: 16px; }
.step-item { display: flex; align-items: center; gap: 10px; }
.step-item:not(:last-child)::after {
    content: "";
    width: 48px;
    height: 1px;
    margin-left: 6px;
    background: #334155;
}
.step-circle {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    border: 1px solid #334155;
    background: #1E293B;
    color: #94A3B8;
    font-size: 14px;
    font-weight: 600;
}
.step-text { color: #94A3B8; font-size: 15px; }
.step-item.current .step-circle,
.step-item.done .step-circle { background: #6366F1; border-color: #6366F1; color: #FFFFFF; }
.step-item.current .step-text,
.step-item.done .step-text { color: #F8FAFC; font-weight: 600; }
.step-counter {
    color: #818CF8;
    font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
    font-size: 12px;
    letter-spacing: 0.08em;
}

/* ----- Selo (AGUARDANDO / PROCESSANDO) ----- */
.step-badge {
    padding: 6px 10px;
    border-radius: 6px;
    background: rgba(99, 102, 241, 0.15);
    color: #818CF8;
    font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    white-space: nowrap;
}

/* ----- Cartão do repositório ----- */
.repo-card {
    background: #0B1220;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
    font-family: 'Inter', sans-serif;
}
.repo-card-label {
    color: #818CF8;
    font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}
.repo-card-name {
    color: #F8FAFC;
    font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 12px;
}
.repo-card-meta { color: #94A3B8; font-size: 12px; line-height: 1.7; }

/* ----- Cartão da esquerda ----- */
.st-key-first_card {
    background: #1E293B;
    border: 1px solid #6366F1;
    border-radius: 12px;
    padding: 24px;
}
.an-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}
.an-title { color: #F8FAFC; font-size: 18px; font-weight: 600; font-family: 'Inter', sans-serif; }
.an-label {
    margin-top: 4px;
    color: #E2E8F0;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
}
.an-divider { border-top: 1px solid #334155; margin: 12px 0; }

.st-key-first_card [data-baseweb="select"] > div {
    min-height: 44px;
    background: #0B1220;
    border: 1px solid #334155;
    border-radius: 8px;
}
.st-key-first_card button[kind^="primary"] {
    width: 100% !important;
    height: 48px;
}

/* ----- Cartão da direita ----- */
.st-key-analysis_card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
}
.an-head { display: flex; justify-content: space-between; align-items: center; }
.an-head-title { color: #F8FAFC; font-size: 18px; font-weight: 600; font-family: 'Inter', sans-serif; }

.an-panel {
    background: #0B1220;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
    font-family: 'Inter', sans-serif;
}
.an-panel-top { display: flex; justify-content: space-between; align-items: center; }
.an-panel-title { color: #F8FAFC; font-size: 13px; font-weight: 600; }
.an-pct {
    padding: 4px 8px;
    border-radius: 4px;
    background: rgba(99, 102, 241, 0.15);
    color: #818CF8;
    font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
    font-size: 11px;
}

.an-bar { height: 8px; margin: 12px 0 8px; border-radius: 4px; background: #334155; overflow: hidden; }
.an-bar-fill { height: 100%; background: #6366F1; }
.an-mono {
    color: #94A3B8;
    font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
    font-size: 10px;
}

.an-sub { display: flex; justify-content: space-between; align-items: center; margin-top: 16px; }
.an-sub-title { color: #F8FAFC; font-size: 13px; font-weight: 600; }
.an-tag {
    color: #818CF8;
    font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
}

.an-steps { margin-top: 8px; }
.an-step { display: flex; align-items: center; gap: 12px; margin: 10px 0; color: #94A3B8; font-size: 13px; }
.an-mark {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    border: 1px solid #334155;
    font-size: 10px;
}
.an-step.done { color: #E2E8F0; }
.an-step.done .an-mark { background: #22C55E; border-color: #22C55E; color: #FFFFFF; }
.an-step.current { color: #F8FAFC; }
.an-step.current .an-mark { border-color: #6366F1; color: #818CF8; }

.an-list { margin-top: 12px; color: #E2E8F0; font-size: 13px; line-height: 2; }
.an-list span { color: #22C55E; margin-right: 12px; }
.an-empty { color: #94A3B8; font-size: 12px; }
"""


# ===================== utilidades =====================

def _html(text):
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def _num(n):
    return f"{n:,}".replace(",", ".")


def _carregar_css():
    css_projeto = DASHBOARD / "styles" / "main.css"
    base = css_projeto.read_text(encoding="utf-8") if css_projeto.exists() else ""
    st.markdown(
        "<style>@import url('https://fonts.googleapis.com/css2?"
        "family=Inter:wght@400;500;600&display=swap');\n"
        f"{base}\n{CSS_TELA}</style>",
        unsafe_allow_html=True,
    )


# ===================== componentes =====================

def _stepper(passo):
    nomes = ["Escolher repositório", "Primeira análise", "Explorar resultados"]
    itens = ""
    for n, nome in enumerate(nomes, start=1):
        estado = "current" if n == passo else "done" if n < passo else "todo"
        itens += (
            f'<div class="step-item {estado}">'
            f'<div class="step-circle">{n}</div>'
            f'<div class="step-text">{nome}</div>'
            f'</div>'
        )

    st.markdown(_html(f"""
        <div class="stepper-wrapper">
            <div class="steps-container">{itens}</div>
            <div class="step-counter">ETAPA {passo} DE {len(nomes)}</div>
        </div>
    """), unsafe_allow_html=True)


def _card_repo(info, rotulo):
    visibilidade = "Privado" if info["private"] else "Público"
    st.markdown(_html(f"""
        <div class="repo-card">
            <div class="repo-card-label">{rotulo}</div>
            <div class="repo-card-name">{escape(info['full_name'])}</div>
            <div class="repo-card-meta">{escape(info['language'])} · {visibilidade}</div>
            <div class="repo-card-meta">{_num(info['commits'])} commits · {_num(info['contributors'])} contribuidores</div>
        </div>
    """), unsafe_allow_html=True)


def _painel_progresso(modo, concluidas, atual, pct, mono):
    itens = ""
    for i, (futuro, andamento, concluido) in enumerate(ETAPAS):
        if i in concluidas:
            marca, texto, estado = "✓", concluido, "done"
        elif modo == "andamento" and i == atual:
            marca, texto, estado = i + 1, andamento, "current"
        else:
            marca, texto, estado = i + 1, futuro, "todo"
        itens += (f'<div class="an-step {estado}"><span class="an-mark">{marca}</span>'
                  f'<span>{texto}</span></div>')

    if modo == "pronta":
        titulo, sub, tag = "Pronto para começar", "O que acontecerá na primeira análise", "ETAPAS PREVISTAS"
    elif modo == "andamento":
        titulo, sub = "Análise em andamento", "O que está sendo processado agora"
        tag = f"Etapa {atual + 1} de {len(ETAPAS)}"
    else:
        titulo, sub, tag = "Análise concluída", "O que foi processado", "TODAS AS ETAPAS"

    return _html(f"""
        <div class="an-panel">
            <div class="an-panel-top">
                <span class="an-panel-title">{titulo}</span>
                <span class="an-pct">{pct}%</span>
            </div>
            <div class="an-bar"><div class="an-bar-fill" style="width:{pct}%;"></div></div>
            <div class="an-mono">{escape(mono)}</div>
            <div class="an-sub"><span class="an-sub-title">{sub}</span>
                <span class="an-tag">{tag}</span></div>
            <div class="an-steps">{itens}</div>
        </div>
    """)


def _painel_achados(modo, achados):
    if modo == "pronta":
        titulo, tag, linhas = "O que você verá depois", "APÓS A ANÁLISE", DEPOIS
    elif modo == "andamento":
        titulo, tag, linhas = "Primeiros achados parciais", "RESULTADOS PARCIAIS", achados
    else:
        titulo, tag, linhas = "Principais achados", "RESULTADOS", achados

    if linhas:
        corpo = "".join(f"<div><span>✓</span>{escape(l)}</div>" for l in linhas)
    else:
        corpo = ('<div class="an-empty">Os primeiros achados aparecem assim que '
                 'o histórico for indexado.</div>')

    return _html(f"""
        <div class="an-panel" style="margin-top:20px;">
            <div class="an-panel-top"><span class="an-panel-title">{titulo}</span>
                <span class="an-tag">{tag}</span></div>
            <div class="an-list">{corpo}</div>
        </div>
    """)


# ===================== estados e animação =====================

def _estado_estatico(estado):
    """(modo, concluídas, etapa atual, %, texto mono, achados) de cada estado fixo."""
    total, contrib = INFO["commits"], INFO["contributors"]

    if estado == "Em andamento (68%)":
        feitos = int(total * 0.68)
        return ("andamento", {0, 1, 2}, 3, 68,
                f"{_num(feitos)} de {_num(total)} commits processados · "
                f"{contrib} contribuidores identificados", ACHADOS)

    if estado == "Concluída":
        return ("concluida", set(range(len(ETAPAS))), len(ETAPAS) - 1, 100,
                f"{_num(total)} de {_num(total)} commits processados · "
                f"{contrib} contribuidores identificados", ACHADOS)

    if estado == "Animada":
        return ("andamento", set(), 0, 0, "Preparando o clone do repositório...", [])

    return ("pronta", set(), 0, 0,
            "Nenhum commit processado · nenhum resultado disponível", [])


def _animar(ph_prog, ph_ach):
    total, contrib = INFO["commits"], INFO["contributors"]
    concluidas = set()

    for i, peso in enumerate(PESOS):
        base = sum(PESOS[:i])
        passos = max(2, peso // 5)

        for k in range(1, passos + 1):
            pct = int(base + peso * k / passos)
            feitos = int(total * pct / 100)
            mono = (f"{_num(feitos)} de {_num(total)} commits processados · "
                    f"{min(contrib, 1 + pct * contrib // 100)} contribuidores identificados")
            achados = ACHADOS[: min(len(ACHADOS), (i + 1) // 2)]

            ph_prog.markdown(_painel_progresso("andamento", concluidas, i, pct, mono),
                             unsafe_allow_html=True)
            ph_ach.markdown(_painel_achados("andamento", achados), unsafe_allow_html=True)
            time.sleep(0.25)

        concluidas.add(i)


def _iniciar():
    st.session_state.preview_estado = "Animada"


# ===================== página =====================

def render():
    _carregar_css()

    if render_auth_topbar:
        render_auth_topbar(mostrar_usuario=True)

    st.session_state.setdefault("preview_estado", OPCOES[0])
    estado = st.session_state.preview_estado

    modo, concluidas, atual, pct, mono, achados = _estado_estatico(estado)
    titulo, subtitulo, titulo_dir, selo = TITULOS[modo]
    rodando = modo != "pronta"

    _stepper(2)
    st.markdown(f'<div class="pg-title">{escape(titulo)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pg-sub">{escape(subtitulo)}</div>', unsafe_allow_html=True)

    col_esq, col_dir = st.columns([1, 2], gap="medium")

    with col_esq:
        with st.container(key="first_card"):
            st.markdown(
                '<div class="an-title-row"><span class="an-title">Sua primeira análise</span>'
                f'{ICONE_BRANCH}</div>',
                unsafe_allow_html=True,
            )
            _card_repo(INFO, "REPOSITÓRIO SELECIONADO")

            st.markdown(
                f'<div class="an-label">'
                f'{"Branch analisada" if rodando else "Branch selecionada"}</div>',
                unsafe_allow_html=True,
            )
            st.selectbox(
                "Branch", INFO["branches"],
                format_func=lambda b: f"{b}  (padrão)" if b == INFO["default_branch"] else b,
                key="preview_branch", label_visibility="collapsed", disabled=rodando,
            )

            st.markdown('<div class="an-divider"></div>', unsafe_allow_html=True)

            if not rodando:
                st.button("Iniciar primeira análise", key="iniciar_primeira",
                          type="primary", on_click=_iniciar)

    with col_dir:
        with st.container(key="analysis_card"):
            st.markdown(_html(f"""
                <div class="an-head"><div class="an-head-title">{titulo_dir}</div>
                    <span class="step-badge">{selo}</span></div>
            """), unsafe_allow_html=True)

            ph_prog = st.empty()
            ph_ach = st.empty()
            ph_prog.markdown(_painel_progresso(modo, concluidas, atual, pct, mono),
                             unsafe_allow_html=True)
            ph_ach.markdown(_painel_achados(modo, achados), unsafe_allow_html=True)

    # A animação roda depois de a tela estar desenhada e termina no estado "Concluída"
    if estado == "Animada":
        _animar(ph_prog, ph_ach)
        st.session_state.preview_estado = "Concluída"
        st.rerun()

    st.divider()
    with st.expander("Pré-visualização (somente desenvolvimento)", expanded=True):
        st.radio("Estado da tela", OPCOES, horizontal=True, key="preview_estado")
        st.caption(
            "Topbar do projeto: "
            + ("carregada." if render_auth_topbar else
               "não encontrada (confira frontend/dashboard/components/topbar.py).")
        )


render()