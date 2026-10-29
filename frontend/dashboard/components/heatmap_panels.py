"""
Componentes visuais do Heatmap de Risco.

Cada função recebe dados prontos e devolve HTML. Não importam o Streamlit nem
calculam risco: os itens vêm de backend/app/heatmap_data.py.
"""
from html import escape

from backend.app.analysis_state import plural
from components.results_panels import _inline

NIVEIS = {
    "critico": ("Crítico", "#EF4444", ">80"),
    "alto": ("Alto", "#F97316", "60-80"),
    "medio": ("Médio", "#EAB308", "35-60"),
    "baixo": ("Baixo", "#22C55E", "<35"),
}

ICONE_FECHAR = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/></svg>'
)

ICONE_BARRAS = (
    '<svg width="24" height="16" viewBox="0 0 24 16" fill="#6366F1">'
    '<rect x="1" y="11" width="3" height="4" rx="1"/><rect x="7" y="8" width="3" height="7" rx="1"/>'
    '<rect x="13" y="4" width="3" height="11" rx="1"/><rect x="19" y="0" width="3" height="15" rx="1"/></svg>'
)


def nivel_por_score(score):
    if score > 80:
        return "critico"
    if score >= 60:
        return "alto"
    if score >= 35:
        return "medio"
    return "baixo"


def _fmt(n):
    return f"{n:,}".replace(",", ".")


def _peso(item):
    return max(item.get("commits") or 1, 1) * max(item["score"], 1)


# ---------- treemap ----------

def _pior(linha, lado):
    s = sum(linha)
    return max(max(lado * lado * a / (s * s), (s * s) / (lado * lado * a)) for a in linha)


def treemap(itens, peso, w=100.0, h=100.0):
    """Treemap 'squarified'. Devolve [(item, x, y, w, h)] em % do retângulo."""
    itens = sorted(itens, key=peso, reverse=True)
    if not itens:
        return []
    total = sum(peso(i) for i in itens)
    areas = [peso(i) / total * w * h for i in itens]
    saida = []

    def distribuir(idx, x, y, w, h):
        if idx >= len(itens):
            return
        lado = min(w, h)
        linha, j = [], idx
        while j < len(itens):
            nova = linha + [areas[j]]
            if linha and _pior(nova, lado) > _pior(linha, lado):
                break
            linha, j = nova, j + 1
        soma = sum(linha)
        if w >= h:                      # coluna à esquerda
            cw, cy = soma / h, y
            for k, a in enumerate(linha):
                ch = a / cw
                saida.append((itens[idx + k], x, cy, cw, ch))
                cy += ch
            distribuir(j, x + cw, y, w - cw, h)
        else:                           # faixa no topo
            rh, cx = soma / w, x
            for k, a in enumerate(linha):
                cw = a / rh
                saida.append((itens[idx + k], cx, y, cw, rh))
                cx += cw
            distribuir(j, x, y + rh, w, h - rh)

    distribuir(0, 0.0, 0.0, w, h)
    return saida


def _bloco(item, x, y, w, h, selecionado):
    nome, cor, _ = NIVEIS[nivel_por_score(item["score"])]
    arquivo = escape(item["path"].split("/")[-1])
    area = w * h
    classe = "hm-tile sel" if selecionado else "hm-tile"

    if area >= 1500:      # bloco grande: cabeçalho com selo + metadados
        meta = []
        if item.get("commits") is not None:
            meta.append(f"Frequência: {plural(item['commits'], 'commit', 'commits')}")
        if item.get("loc") is not None:
            meta.append(f"Tamanho: {_fmt(item['loc'])} LOC")
        if item.get("falhas"):
            meta.append("Status: " + plural(item["falhas"], "falha reincidente", "falhas reincidentes"))
        corpo = (
            f'<div class="hm-head"><b class="hm-name big">{arquivo}</b>'
            f'<span class="hm-badge">{nome.upper()} ({item["score"]:.0f})</span></div>'
            + "".join(f"<div class='hm-meta'>{escape(m)}</div>" for m in meta)
        )
    elif area >= 400:     # bloco médio: nome + volume
        meta = []
        if item.get("loc") is not None:
            meta.append(f"{_fmt(item['loc'])} LOC")
        if item.get("commits") is not None:
            meta.append(plural(item["commits"], "commit", "commits"))
        corpo = (f'<b class="hm-name">{arquivo}</b>'
                 f'<div class="hm-meta">{escape(" · ".join(meta))}</div>')
    else:                 # bloco pequeno: nome + score
        corpo = (f'<b class="hm-name">{arquivo}</b>'
                 f'<div class="hm-meta">Score: {item["score"]:.0f}</div>')

    return (
        f'<div class="hm-cell" style="left:{x:.3f}%;top:{y:.3f}%;width:{w:.3f}%;height:{h:.3f}%;">'
        f'<div class="{classe}" style="--c:{cor};" title="{escape(item["path"])}">{corpo}</div></div>'
    )


def heatmap_html(itens, selecionado):
    if not itens:
        return '<div class="an-empty">Nenhum arquivo analisado. Execute a análise para gerar o heatmap.</div>'

    blocos = "".join(
        _bloco(i, x, y, w, h, i["path"] == selecionado)
        for i, x, y, w, h in treemap(itens, _peso)
    )
    legenda = "".join(
        f'<span><i style="background:{cor}"></i>{nome} ({faixa})</span>'
        for nome, cor, faixa in NIVEIS.values()
    )
    return _inline(f"""
        <div class="hm-map">{blocos}</div>
        <div class="hm-legend"><b>Escala de Gravidade de Risco:</b>{legenda}</div>
    """)


# ---------- painel de detalhes ----------

def _secao(titulo, valor):
    return f'<div class="fd-sec"><div class="fd-label">{titulo}</div>{valor}</div>'


def detalhes_html(item):
    nome, cor, _ = NIVEIS[nivel_por_score(item["score"])]
    cab = (
        f'<div class="fd-file">{escape(item["path"].split("/")[-1])}</div>'
        f'<div class="fd-tags"><span class="fd-sev" style="--c:{cor};">Severidade: {nome}</span>'
        + (f'<span class="fd-mod">{escape(item["modulo"])}</span>' if item.get("modulo") else "")
        + "</div>"
    )

    secoes = []
    if item.get("commits") is not None:
        txt = plural(item["commits"], "commit", "commits")
        if item.get("janela_dias"):
            txt += f" nos últimos {item['janela_dias']} dias"
        secoes.append(_secao("FREQUÊNCIA DE ALTERAÇÕES",
                             f'<div class="fd-val row">{escape(txt)}{ICONE_BARRAS}</div>'))
    if item.get("falhas"):
        txt = plural(item["falhas"], "falha reincidente", "falhas reincidentes")
        secoes.append(_secao("HISTÓRICO DE FALHAS", f'<div class="fd-val danger">{escape(txt)}</div>'))
    if item.get("ultima_mod_dias") is not None:
        d = item["ultima_mod_dias"]
        quando = "hoje" if d == 0 else f"{plural(d, 'dia', 'dias')} atrás"
        autor = f" por <b>{escape(item['ultima_mod_autor'])}</b>" if item.get("ultima_mod_autor") else ""
        secoes.append(_secao("ÚLTIMA MODIFICAÇÃO", f'<div class="fd-val">{quando}{autor}</div>'))
    if item.get("contribuidores"):
        txt = plural(item["contribuidores"], "desenvolvedor ativo", "desenvolvedores ativos")
        secoes.append(_secao("CONTRIBUIDORES", f'<div class="fd-val">{escape(txt)}</div>'))

    html = cab + '<div class="fd-block">' + "".join(secoes) + "</div>"

    if item.get("fatores"):
        lis = "".join(
            f'<li style="--c:{NIVEIS[f.get("nivel", "alto")][1]};">{escape(f["texto"])}</li>'
            for f in item["fatores"]
        )
        html += (f'<div class="fd-block"><div class="fd-label">PRINCIPAIS FATORES DE RISCO</div>'
                 f'<ul class="fd-list">{lis}</ul></div>')

    if item.get("recomendacoes"):
        lis = "".join(f"<div>• {escape(r)}</div>" for r in item["recomendacoes"])
        html += f'<div class="fd-ai"><div class="fd-ai-title">RECOMENDAÇÕES IA</div>{lis}</div>'

    return _inline(html)


def cabecalho_detalhes_html():
    return f'<div class="an-title-row"><span class="an-title">Detalhes do Arquivo</span>{ICONE_FECHAR}</div>'