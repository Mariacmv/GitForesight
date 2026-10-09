import streamlit as st


def render_metrics(analysis, risk):

    total_commits = int(analysis["commits"].sum())
    current_risk = float(risk["risk_score"].iloc[-1])
    security_files = int(
        analysis["security_files_changed"].sum()
    )
    contributors = int(
        analysis["contributors"].sum()
    )

    cards = [
        {
            "title": "VULNERABILIDADES CRÍTICAS",
            "value": str(total_commits),
            "description": "Commits encontrados no histórico",
            "icon": "▣",
            "color": "#6366F1"
        },
        {
            "title": "SCORE DE RISCO",
            "value": f"{current_risk:.0f}/100",
            "description": "Risco atual do repositório",
            "icon": "◇",
            "color": "#F97316"
        },
        {
            "title": "COMMITS ANALISADOS",
            "value": str(security_files),
            "description": "Arquivos relacionados à segurança",
            "icon": "▤",
            "color": "#6366F1"
        },
        {
            "title": "COBERTURA DE TESTES",
            "value": str(contributors),
            "description": "Contribuidores identificados",
            "icon": "✓",
            "color": "#22C55E"
        }
    ]

    st.markdown(
        """
    <style>
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        width: 100%;
    }

    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        min-height: 125px;
    }

    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
    }

    .metric-title {
        color: #94A3B8;
        font-size: 11px;
        font-weight: 600;
    }

    .metric-icon {
        width: 30px;
        height: 30px;
        border-radius: 7px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .metric-value {
        color: #F8FAFC;
        font-size: 27px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .metric-description {
        color: #94A3B8;
        font-size: 11px;
    }
    </style>
    """,
        unsafe_allow_html=True
    )

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

    st.markdown(
        cards_html,
        unsafe_allow_html=True
    )