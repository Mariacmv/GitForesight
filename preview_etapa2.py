"""
Prévia da etapa 2 (Primeira análise) com dados simulados.

Rode da raiz do projeto (a pasta que contém backend/, data/ e frontend/):
    streamlit run preview_etapa2.py

Este arquivo só fornece dados falsos e a animação. Quem desenha é a mesma view
da tela real (views/first_analysis.py), então o que você ajusta aqui vale lá.
"""
import sys
import time
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Git Foresight",
    layout="wide",
    initial_sidebar_state="collapsed",
)

RAIZ = Path(__file__).resolve().parent
DASHBOARD = RAIZ / "frontend" / "dashboard"
sys.path.insert(0, str(RAIZ))        # para importar backend/
sys.path.insert(0, str(DASHBOARD))   # para importar components/ e views/

from backend.app.analysis_state import ETAPAS, AnalysisTracker, calcular_pct, snapshot_pronta
from views.first_analysis import atualizar, desenhar_tela

# Topbar do projeto (opcional): se não carregar, a prévia segue sem ela
try:
    from components.topbar import render_auth_topbar
except Exception:
    render_auth_topbar = None

# Achados calculados a partir do histórico real do repositório (opcional)
try:
    from backend.app.insights import count_contributors, partial_findings
except Exception:
    count_contributors = partial_findings = None


# ===================== dados simulados =====================

# Usado SÓ se nenhum repositório foi escolhido na etapa 1 (st.session_state.repo_info)
DEMO_INFO = {
    "full_name": "empresa/backend",
    "language": "Python",
    "private": True,
    "commits": 1847,
    "contributors": 12,
    "default_branch": "main",
    "branches": ["main", "develop"],
}

OPCOES = ["Pronta para iniciar", "Em andamento (68%)", "Animada", "Concluída"]

# Regras só desta página: sem sidebar e com espaço para a topbar fixa
CSS_PAGINA = """
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
"""


def _carregar_css():
    estilos = DASHBOARD / "styles"
    base = (estilos / "main.css").read_text(encoding="utf-8") if (estilos / "main.css").exists() else ""

    # Se o CSS da tela ainda não foi colado no main.css, usa o arquivo separado
    extra = estilos / "primeira_analise.css"
    if ".an-panel" not in base and extra.exists():
        base += "\n" + extra.read_text(encoding="utf-8")

    st.markdown(
        "<style>@import url('https://fonts.googleapis.com/css2?"
        "family=Inter:wght@400;500;600&display=swap');\n"
        f"{base}\n{CSS_PAGINA}</style>",
        unsafe_allow_html=True,
    )


def _stepper(passo):
    nomes = ["Escolher repositório", "Primeira análise", "Explorar resultados"]
    itens = ""
    for n, nome in enumerate(nomes, start=1):
        estado = "current" if n == passo else "done" if n < passo else "todo"
        itens += (f'<div class="step-item {estado}"><div class="step-circle">{n}</div>'
                  f'<div class="step-text">{nome}</div></div>')
    st.markdown(
        f'<div class="stepper-wrapper"><div class="steps-container">{itens}</div>'
        f'<div class="step-counter">ETAPA {passo} DE {len(nomes)}</div></div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _ler_analise(assinatura):
    """Achados da última análise gravada em data/. `assinatura` renova o cache quando muda."""
    arquivo = RAIZ / "data" / "file_changes.csv"
    if not arquivo.exists() or partial_findings is None:
        return {"achados": [], "contribuidores": None, "commits": None}

    files = pd.read_csv(arquivo)
    commits_csv = RAIZ / "data" / "commits.csv"
    return {
        "achados": partial_findings(files),
        "contribuidores": count_contributors(files),
        "commits": len(pd.read_csv(commits_csv)) if commits_csv.exists() else None,
    }


def _dados():
    arquivo = RAIZ / "data" / "file_changes.csv"
    return _ler_analise(arquivo.stat().st_mtime if arquivo.exists() else 0)


def _info(dados):
    info = st.session_state.get("repo_info")
    if info:
        return info

    demo = dict(DEMO_INFO)
    if dados["commits"]:
        demo["commits"] = dados["commits"]
    if dados["contribuidores"]:
        demo["contributors"] = dados["contribuidores"]
    return demo


# ===================== estados simulados =====================

def _snapshot(estado, info, contrib, achados):
    total = info["commits"]
    t = AnalysisTracker(total, contrib)

    if estado == "Em andamento (68%)":
        for i in range(3):
            t.concluir(i)
        t.iniciar(3)
        t.avancar(0.2, feitos=int(total * 0.68))     # 65% das etapas feitas + 20% da quarta = 68%
        t.achados = achados
        return t.snapshot()

    if estado == "Concluída":
        for i in range(len(ETAPAS)):
            t.concluir(i)
        t.achados = achados
        return t.snapshot()

    if estado == "Animada":
        t.iniciar(0)
        return t.snapshot()

    return snapshot_pronta()


def _animar(phs, info, contrib, achados):
    total = info["commits"]
    t = AnalysisTracker(total, 0)

    for i, etapa in enumerate(ETAPAS):
        t.iniciar(i)
        passos = max(2, etapa["peso"] // 5)

        for k in range(1, passos + 1):
            fracao = k / passos
            pct = calcular_pct(t.concluidas, i, fracao)

            t.avancar(fracao, feitos=int(total * pct / 100))
            t.contribuidores = min(contrib, 1 + pct * contrib // 100) if contrib else 0
            t.achados = achados[: int(len(achados) * i / (len(ETAPAS) - 1))]   # aparecem aos poucos

            atualizar(phs, t.snapshot())
            time.sleep(0.25)

        t.concluir(i)


def _iniciar(_chave_branch):
    st.session_state.preview_estado = "Animada"


# ===================== página =====================

def render():
    _carregar_css()

    if render_auth_topbar:
        render_auth_topbar(mostrar_usuario=True)

    dados = _dados()
    info = _info(dados)
    branch = st.session_state.get("branch") or info["default_branch"]
    contrib = dados["contribuidores"] or info["contributors"]

    st.session_state.setdefault("preview_estado", OPCOES[0])
    estado = st.session_state.preview_estado

    _stepper(2)
    phs = desenhar_tela(info, _snapshot(estado, info, contrib, dados["achados"]),
                        branch, ao_iniciar=_iniciar)

    # A animação roda depois de a tela estar desenhada e termina no estado "Concluída"
    if estado == "Animada":
        _animar(phs, info, contrib, dados["achados"])
        st.session_state.preview_estado = "Concluída"
        st.rerun()

    st.divider()
    with st.expander("Pré-visualização (somente desenvolvimento)", expanded=True):
        st.radio("Estado da tela", OPCOES, horizontal=True, key="preview_estado")

        origem = ("repositório escolhido na etapa 1"
                  if st.session_state.get("repo_info") else "exemplo (nenhum repositório escolhido)")
        achados_ok = ("calculados a partir de data/file_changes.csv"
                      if dados["achados"] else "indisponíveis (rode uma análise para gerar data/)")
        st.caption(
            f"Repositório: {origem}. Achados: {achados_ok}. "
            "Topbar do projeto: "
            + ("carregada." if render_auth_topbar else
               "não encontrada (confira frontend/dashboard/components/topbar.py).")
        )


render()