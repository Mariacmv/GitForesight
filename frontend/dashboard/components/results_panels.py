"""
Componentes visuais da etapa 3 (prévia dos resultados).

Cada função recebe dados prontos e devolve HTML. Não importam o Streamlit nem
calculam nada: o resumo vem de backend/app/analysis_summary.py.
"""
from html import escape

from backend.app.analysis_state import plural

ICONE_BRANCH = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#818CF8" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="6" cy="5" r="2"/><circle cx="18" cy="5" r="2"/><circle cx="12" cy="19" r="2"/>'
    '<path d="M6 7v2a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3V7M12 12v5"/></svg>'
)

ICONE_INFO = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'
)


def _inline(texto):
    """Tira a indentação: o Markdown trataria linhas com 4+ espaços como código."""
    return " ".join(linha.strip() for linha in texto.splitlines() if linha.strip())


def linhas_resumo(r):
    """As três frases do painel, montadas só com o que foi encontrado."""
    linhas = []

    # 1) risco e arquivos sensíveis
    if r["score"] is not None:
        risco = (
            f"Risco da última semana analisada: "
            f"{r['score']:.0f}/100 ({r['nivel']})"
        )
    else:
        risco = "Score de risco indisponível"
    n = r["arquivos_sensiveis"]
    sensiveis = (plural(n, "arquivo sensível alterado", "arquivos sensíveis alterados")
                 if n else "nenhum arquivo sensível alterado")
    linhas.append(f"{risco} · {sensiveis}")

    # 2) volume e concentração
    partes = []
    if r["commits"] is not None:
        partes.append(plural(r["commits"], "commit analisado", "commits analisados"))
    if r["contribuidores"]:
        partes.append(plural(r["contribuidores"], "contribuidor", "contribuidores"))
    if r["pessoa"]:
        partes.append(f"{r['pessoa']} concentra {r['participacao']:.0%} das alterações")
    if partes:
        linhas.append(" · ".join(partes))

    # 3) arquivos mais alterados
    itens = [
        f"{t['path']} ({plural(t['linhas'], 'linha alterada', 'linhas alteradas')}"
        f" · {plural(t['commits'], 'commit', 'commits')})"
        for t in r["top_arquivos"]
    ]
    if itens:
        titulo = "Arquivo mais alterado" if len(itens) == 1 else "Arquivos mais alterados"
        linhas.append(f"{titulo}: " + " e ".join(itens))

    return linhas


def resumo_html(r):
    linhas = linhas_resumo(r)

    if r["score"] is None and r["commits"] is None and not r["top_arquivos"]:
        corpo = ('<div class="an-empty">Nenhum resultado encontrado. '
                 'Execute a análise para gerar os dados.</div>')
    else:
        corpo = "".join(f"<div><span>✓</span>{escape(l)}</div>" for l in linhas)

    return _inline(f"""
        <div class="an-panel">
            <div class="an-list" style="margin-top:0;">{corpo}</div>
        </div>
    """)


def proximos_html():
    return _inline("""
        <div class="next-list">
            <div class="next-label">O QUE VEM A SEGUIR</div>
            <div><span>✓</span>Examinar histórico, churn e hotspots</div>
            <div><span>✓</span>Explorar a distribuição de conhecimento</div>
        </div>
    """)


def preview_desfocado_html():
    """Silhueta desfocada da Visão Geral: só formas, sem números nem textos inventados."""
    cores = ["#EF4444", "#F97316", "#EAB308", "#22C55E", "#22C55E", "#F97316"]
    tiles = "".join(
        f'<div class="blur-tile" style="border-color:{c};"><i></i><i></i></div>' for c in cores
    )
    alertas = "".join(
        '<div class="blur-alert"><b></b><i></i><u></u></div>' for _ in range(2)
    )

    return _inline(f"""
        <div class="res-blur">
            <div class="res-blur-inner">
                <div class="blur-col">
                    <div class="blur-title"></div>
                    <div class="blur-grid">{tiles}</div>
                </div>
                <div class="blur-col">
                    <div class="blur-title"></div>
                    <svg viewBox="0 0 300 110" preserveAspectRatio="none" class="blur-chart">
                        <polyline points="0,95 40,70 80,85 120,45 160,60 200,30 240,40 300,10"
                                  fill="none" stroke="#6366F1" stroke-width="3"/>
                    </svg>
                    {alertas}
                </div>
            </div>
            <div class="res-overlay">Veja os resultados completos na Visão geral</div>
        </div>
    """)


def nota_html():
    return _inline(f"""
        <div class="res-note">{ICONE_INFO}
            <span>Prévia baseada no histórico real do repositório. Os valores são estimativas
            e as simulações não são previsões determinísticas.</span>
        </div>
    """)