import streamlit as st
import html as html_lib
import numpy as np
import pandas as pd

from backend.app.insights import knowledge_concentration
from data_loader import load_commit_log, load_file_changes
from backend.app.hotspot import calculate_hotspots

ICON_ALERT = (
    '<svg width="16" height="14" viewBox="0 0 16 14" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<path d="M7.67839 5.00911V7.67578M7.67839 10.3424H7.68505M14.1653 11.0093'
        'L8.832 1.67593C8.71571 1.47073 8.54707 1.30006 8.34328 1.18131C8.13949 1.06256 '
        '7.90786 1 7.672 1C7.43614 1 7.2045 1.06256 7.00071 1.18131C6.79693 1.30006 '
        '6.62829 1.47073 6.512 1.67593L1.17866 11.0093C1.06112 11.2128 0.999483 11.4439 '
        '1 11.6789C1.00052 11.914 1.06318 12.1448 1.18163 12.3478C1.30007 12.5509 '
        '1.4701 12.719 1.67446 12.8352C1.87883 12.9513 2.11027 13.0114 2.34533 13.0093'
        'H13.012C13.2459 13.009 13.4757 12.9472 13.6782 12.8301C13.8807 12.713 '
        '14.0488 12.5447 14.1657 12.342C14.2825 12.1394 14.344 11.9095 14.344 11.6756'
        'C14.3439 11.4417 14.2823 11.2119 14.1653 11.0093Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
    '</svg>'
)

ICON_PROTECT = (
    '<svg width="13" height="16" viewBox="0 0 13 16" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<path d="M6.3328 5.00013V7.66688M6.3328 10.3336H6.33947M11.6656 8.33387C11.6656 '
    '11.6673 9.3325 13.334 6.55944 14.3007C6.41423 14.3499 6.2565 14.3476 6.11282 '
    '14.2941C3.3331 13.334 1 11.6673 1 8.33387V3.66705C1 3.49024 1.07023 3.32066 1.19524 '
    '3.19563C1.32025 3.0706 1.48981 3.00036 1.6666 3.00036C2.9998 3.00036 4.6663 2.20034 '
    '5.82618 1.18697C5.96741 1.0663 6.14705 1 6.3328 1C6.51855 1 6.69819 1.0663 6.83942 1.18697C8.00597 '
    '2.20701 9.6658 3.00036 10.999 3.00036C11.1758 3.00036 11.3453 3.0706 11.4704 3.19563C11.5954 '
    '3.32066 11.6656 3.49024 11.6656 3.66705V8.33387Z" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
    '</svg>'
)

ICON_DATA = (
    '<svg width="14" height="16" viewBox="0 0 14 16" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<path d="M13 3.00016C13 4.10482 10.3137 '
    '5.00032 7 5.00032C3.68629 5.00032 1 4.10482 1 3.00016M13 3.00016C13 '
    '1.8955 10.3137 1 7 1C3.68629 1 1 1.8955 1 '
    '3.00016M13 3.00016V12.3342C13 12.8647 12.3679 13.3735 11.2426 13.7486C10.1174 14.1237 8.5913 '
    '14.3344 7 14.3344C5.4087 14.3344 3.88258 14.1237 2.75736 13.7486C1.63214 13.3735 '
    '1 12.8647 1 12.3342V3.00016M1 7.6672C1 8.19768 1.63214 8.70642 2.75736 '
    '9.08153C3.88258 9.45663 5.4087 9.66736 7 9.66736C8.5913 9.66736 10.1174 9.45663 '
    '11.2426 9.08153C12.3679 8.70642 13 8.19768 13 7.6672" '
    'stroke="#6366F1" stroke-width="2" stroke-linecap="round"/>'
    '</svg>'
)

ICON_CHECK = (
    '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<path d="M14.1991 6.33561C14.5036 7.8298 14.2866 '
    '9.38322 13.5843 10.7368C12.8821 12.0904 11.737 13.1623 10.3401 13.7738C8.9432 14.3853 '
    '7.37886 14.4995 5.90797 14.0972C4.43709 13.6949 3.14857 12.8005 2.25729 11.5632C1.36601 '
    '10.3259 0.925853 8.82043 1.01021 7.29786C1.09458 5.77529 1.69836 4.32767 2.72087 3.19639C3.74339 '
    '2.06511 5.12283 1.31856 6.62915 1.08124C8.13547 0.843922 9.67763 1.13018 10.9984 '
    '1.89227M5.66536 7.00195L7.66536 9.00195L14.332 2.33529" '
    'stroke="#22C55E" stroke-width="2" stroke-linecap="round"/>'
    '</svg>'
)


def render_metrics(analysis, risk, commits=None, files=None):

    commits = load_commit_log() if commits is None else commits
    files = load_file_changes() if files is None else files

    # Card 1: hotspots
    hotspots = calculate_hotspots(files)

    n_hotspots = (
        int(hotspots["is_hotspot"].sum())
        if not hotspots.empty
        else 0
    )

    # Card 2: score de risco da semana mais recente
    current_risk = float(risk.sort_values("week")["risk_score"].iloc[-1])

    # Card 4: concentração de conhecimento
    conc = knowledge_concentration(files)
    if conc["participacao"] >= 0.5:
        cor_conc = "#EF4444"
    elif conc["participacao"] >= 0.3:
        cor_conc = "#F97316"
    else:
        cor_conc = "#22C55E"

    cards = [    
        {
            "title": "HOTSPOTS IDENTIFICADOS",
            "value": str(n_hotspots),
            "description": (
                f"{n_hotspots} de {len(hotspots)} arquivos "
                "com alta exposição histórica"
            ),
            "icon": ICON_ALERT,
            "color": "#EF4444"
        },
        {"title": "SCORE DE RISCO",
            "value": f"{current_risk:.0f}/100",
            "description": "Risco da semana mais recente",
            "icon": ICON_PROTECT, 
            "color": "#F97316"
        },
        {"title": "COMMITS ANALISADOS",
            "value": str(len(commits)),
            "description": "Commits no histórico",
            "icon": ICON_DATA, 
            "color": "#6366F1"
        },
        {"title": "CONCENTRAÇÃO DE CONHECIMENTO",
            "value": f"{conc['participacao']:.0%}",
            "description": (f"{conc['pessoa']} · {conc['arquivos_dono_unico']} de "
                        f"{conc['arquivos_total']} arquivos com dono único"),
            "icon": ICON_CHECK, 
            "color": "#22C55E"
        },
    ]

    cards_html = '<div class="metrics-container">'

    for card in cards:
        cards_html += (
            f'<div class="metric-card">'
            f'<div class="metric-header">'
            f'<div class="metric-title">{card["title"]}</div>'
            f'<div class="metric-icon" '
            f'style="color:{card["color"]}; '
            f'background:{card["color"]}1A;">'
            f'{card["icon"]}'
            f'</div>'
            f'</div>'
            f'<div class="metric-value">{card["value"]}</div>'
            f'<div class="metric-description">'
            f'{card["description"]}'
            f'</div>'
            f'</div>'
        )

    cards_html += '</div>'

    st.markdown(cards_html, unsafe_allow_html=True)
    
    

LEVELS = {
    "CRÍTICO":  "#EF4444",  # Vermelho
    "ALTO":     "#F97316",  # Laranja
    "MODERADO": "#EAB308",  # Amarelo
    "BAIXO":    "#22C55E",  # Verde
}


def _html(text):
    """Tira a indentação para o Markdown não tratar o HTML como código."""
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def _badge(level):
    color = LEVELS[level]
    return (
        f'<span class="badge" style="color:{color};'
        f'background:{color}26;border:1px solid {color}55;">{level}</span>'
    )


def risk_level(score):
    """Classifica o índice histórico de risco (0–100)."""

    if score >= 70:
        return "CRÍTICO"

    if score >= 40:
        return "ALTO"

    if score >= 20:
        return "MODERADO"

    return "BAIXO"


def _relative(ts):
    minutes = int((pd.Timestamp.now(tz="UTC") - ts).total_seconds() // 60)
    if minutes < 60:   return f"Há {max(minutes, 1)} min"
    if minutes < 1440: return f"Há {minutes // 60} h"
    return f"Há {minutes // 1440} d"


def render_heatmap_card(risk, top=8):
    df = risk.assign(week=pd.to_datetime(risk["week"]))
    df = df.sort_values("risk_score", ascending=False).head(top)

    tiles = ""
    for _, r in df.iterrows():
        level = risk_level(r["risk_score"])
        color = LEVELS[level]
        linhas = f'{int(r["total_changes"]):,}'.replace(",", ".")
        tiles += (
            f'<div class="heat-tile" style="border-color:{color};">'
            f'<div class="heat-top"><span class="mono">Semana {r["week"]:%d/%m/%y}</span>'
            f'{_badge(level)}</div>'
            f'<div class="heat-loc">{linhas} linhas · {int(r["commits"])} commits · '
            f'score {r["risk_score"]:.0f}</div>'
            f'</div>'
        )

    st.markdown(_html(f"""
        <div class="panel-card">
            <div class="panel-title">Heatmap de Risco por Semana</div>
            <div class="panel-sub">Semanas ordenadas pelo score de risco.</div>
            <div class="heat-grid">{tiles}</div>
        </div>
    """), unsafe_allow_html=True)


def render_trend_card(risk, n_hist=12, n_future=4):
    df = risk.assign(week=pd.to_datetime(risk["week"])).sort_values("week")
    values = df["risk_score"].astype(float).tail(n_hist).to_numpy()

    slope, future = 0.0, np.array([])
    if len(values) >= 2:
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        future = np.clip(
            intercept + slope * np.arange(len(values), len(values) + n_future), 0, 100
        )

    w, h, pad = 300, 100, 8
    step = (w - 2 * pad) / max(len(values) + len(future) - 1, 1)

    def y(v):
        return h - pad - (v / 100) * (h - 2 * pad)   # escala fixa 0-100

    hist = " ".join(f"{pad + i * step:.1f},{y(v):.1f}" for i, v in enumerate(values))
    proj = " ".join(
        f"{pad + (len(values) - 1 + i) * step:.1f},{y(v):.1f}"
        for i, v in enumerate(np.concatenate([[values[-1]], future]))
    )

    direcao = "subindo" if slope > 0.5 else "caindo" if slope < -0.5 else "estável"

    st.markdown(_html(f"""
        <div class="panel-card">
            <div class="panel-title"><span style="color:#818CF8;">✦</span> Tendência do Score de Risco</div>
            <div class="panel-sub">Histórico recente e projeção linear das próximas {n_future} semanas. Tendência: {direcao}.</div>
            <svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" class="trend-svg">
                <polyline points="{hist}" fill="none" stroke="#6366F1" stroke-width="2"
                          vector-effect="non-scaling-stroke" stroke-linejoin="round" stroke-linecap="round"/>
                <polyline points="{proj}" fill="none" stroke="#818CF8" stroke-width="2"
                          stroke-dasharray="4 4" vector-effect="non-scaling-stroke"/>
            </svg>
        </div>
    """), unsafe_allow_html=True)


def render_alerts_card(commits, limit=4):
    df = commits.copy()
    grande = df["changes"].quantile(0.9)

    alerts = []
    for _, c in df.iterrows():
        if c["security_files_changed"] > 0:
            level, motivo = "ALTO", "Arquivo de segurança alterado"
        elif c["changes"] >= grande and c["changes"] > 0:
            level, motivo = "MODERADO", f'Alteração grande ({int(c["changes"])} linhas)'
        else:
            continue
        resumo = str(c["message"]).splitlines()[0][:70]
        alerts.append((c["date"], c["author"], f"{motivo}: {resumo}", level))

    alerts = sorted(alerts, key=lambda a: a[0], reverse=True)[:limit]

    rows = ""
    for date, author, desc, level in alerts:
        color = LEVELS[level]
        rows += (
            f'<div class="alert-row">'
            f'<span class="alert-dot" style="background:{color};"></span>'
            f'<div class="alert-body"><div class="mono">{html_lib.escape(str(author))}</div>'
            f'<div class="alert-desc">{html_lib.escape(desc)}</div></div>'
            f'{_badge(level)}<span class="alert-time">{_relative(date)}</span>'
            f'</div>'
        )

    if not rows:
        rows = '<div class="alert-desc">Nenhum alerta no histórico.</div>'

    st.markdown(_html(f"""
        <div class="panel-card">
            <div class="panel-title">Alertas Recentes</div>
            <div class="alerts">{rows}</div>
        </div>
    """), unsafe_allow_html=True)