"""
Componentes visuais da primeira análise.

Cada função recebe dados prontos (info do repositório ou Snapshot) e devolve
uma string HTML. Não importam o Streamlit nem calculam nada: quem usa decide
onde desenhar (st.markdown, st.empty().markdown...).
"""
from html import escape

from backend.app.analysis_state import ETAPAS, fmt_num

DEPOIS = [
    "Arquivos e módulos com maior concentração de alterações recentes.",
    "Contribuidores mais ativos e distribuição de commits no período analisado.",
    "Indicadores iniciais para revisão, refatoração e acompanhamento contínuo.",
]


def _inline(texto):
    """Tira a indentação: o Markdown trataria linhas com 4+ espaços como código."""
    return " ".join(linha.strip() for linha in texto.splitlines() if linha.strip())


def repo_html(info, rotulo):
    visibilidade = {True: "Privado", False: "Público"}.get(info.get("private"), "—")
    return _inline(f"""
        <div class="repo-card">
            <div class="repo-card-label">{rotulo}</div>
            <div class="repo-card-name">{escape(info['full_name'])}</div>
            <div class="repo-card-meta">{escape(info.get('language') or '—')} · {visibilidade}</div>
            <div class="repo-card-meta">{fmt_num(info.get('commits', 0))} commits · {fmt_num(info.get('contributors', 0))} contribuidores</div>
        </div>
    """)


def progresso_html(snap):
    itens = ""
    for i, etapa in enumerate(ETAPAS):
        if i in snap.concluidas:
            marca, texto, estado = "✓", etapa["concluido"], "done"
        elif snap.modo == "andamento" and i == snap.atual:
            marca, texto, estado = i + 1, etapa["andamento"], "current"
        else:
            marca, texto, estado = i + 1, etapa["futuro"], "todo"
        itens += (f'<div class="an-step {estado}"><span class="an-mark">{marca}</span>'
                  f'<span>{texto}</span></div>')

    if snap.modo == "pronta":
        titulo, sub, tag = "Pronto para começar", "O que acontecerá na primeira análise", "ETAPAS PREVISTAS"
    elif snap.modo == "andamento":
        titulo, sub = "Análise em andamento", "O que está sendo processado agora"
        tag = f"Etapa {snap.atual + 1} de {len(ETAPAS)}"
    else:
        titulo, sub, tag = "Análise concluída", "O que foi processado", "TODAS AS ETAPAS"

    return _inline(f"""
        <div class="an-panel">
            <div class="an-panel-top">
                <span class="an-panel-title">{titulo}</span>
                <span class="an-pct">{snap.pct}%</span>
            </div>
            <div class="an-bar"><div class="an-bar-fill" style="width:{snap.pct}%;"></div></div>
            <div class="an-mono">{escape(snap.mono)}</div>
            <div class="an-sub"><span class="an-sub-title">{sub}</span>
                <span class="an-tag">{tag}</span></div>
            <div class="an-steps">{itens}</div>
        </div>
    """)


def achados_html(snap):
    if snap.modo == "pronta":
        titulo, tag, linhas = "O que você verá depois", "APÓS A ANÁLISE", DEPOIS
    elif snap.modo == "andamento":
        titulo, tag, linhas = "Primeiros achados parciais", "RESULTADOS PARCIAIS", snap.achados
    else:
        titulo, tag, linhas = "Principais achados", "RESULTADOS", snap.achados

    if linhas:
        corpo = "".join(f"<div><span>✓</span>{escape(l)}</div>" for l in linhas)
    elif snap.modo == "concluida":
        corpo = '<div class="an-empty">Nenhum achado disponível para este repositório.</div>'
    else:
        corpo = ('<div class="an-empty">Os primeiros achados aparecem assim que '
                 'o histórico for indexado.</div>')

    return _inline(f"""
        <div class="an-panel" style="margin-top:20px;">
            <div class="an-panel-top"><span class="an-panel-title">{titulo}</span>
                <span class="an-tag">{tag}</span></div>
            <div class="an-list">{corpo}</div>
        </div>
    """)