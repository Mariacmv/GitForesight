import altair as alt
import pandas as pd
import streamlit as st
from theme import load_css
from components.info_tip import info_tip
from backend.app.predictive import build_predictive
from paths import DATA_DIR

# Paleta
BG_CARD = "#141b2d"
BORDER = "#26304a"
TEXT = "#f1f5f9"
MUTED = "#8b97b1"
INDIGO = "#6366f1"
INDIGO_SOFT = "#a5b4fc"
ORANGE = "#f97316"
GREEN = "#22c55e"
RED = "#ef4444"

def card_header(title: str, subtitle: str = "", tip: str | None = None) -> str:
    sub = f'<p class="gf-card-sub">{subtitle}</p>' if subtitle else ""
    tip_html = info_tip(tip, side="down") if tip else ""
    return (
        f'<div class="gf-card-head">'
        f'<div><p class="gf-card-title">{title}</p>{sub}</div>'
        f"{tip_html}"
        f"</div>"
    )
 
 
def _header() -> None:
    left, right = st.columns([5, 1.3], vertical_alignment="center")
    with left:
        st.markdown(
            '<p class="gf-title">Análise Preditiva</p>'
            '<p class="gf-subtitle">Antecipe a evolução do risco e priorize ações '
            "antes dos próximos commits.</p>",
            unsafe_allow_html=True,
        )
    with right:
        st.button(
            "Exportar Análise",
            icon=":material/download:",
            use_container_width=True,
            key="predictive_export",
        )
 
 
def _kpis(data) -> None:
    current = data["current"]
    projection = data["projection"]

    last_projection = (
        projection.iloc[-1]
        if projection is not None and not projection.empty
        else None
    )

    variation = current["variation"]

    if variation is None:
        variation_text = "Sem comparação anterior"
    else:
        variation_text = (
            f"{variation:+.2f} pontos em relação ao registro anterior"
        )

    kpis = [
        {
            "label": "Score de risco",
            "badge": "Histórico",
            "value": f'{current["score"]:.2f}/100',
            "color": ORANGE,
            "foot": variation_text,
            "forecast": False,
        },
        {
            "label": "Em +50 commits",
            "badge": "Previsão",
            "value": (
                f'{last_projection["continuidade"]:.2f}/100'
                if last_projection is not None
                else "—"
            ),
            "color": INDIGO_SOFT,
            "foot": "Cenário de manutenção do risco atual",
            "forecast": True,
        },
        {
            "label": "Com ações corretivas",
            "badge": "Simulação",
            "value": (
                f'{last_projection["com_acoes"]:.2f}/100'
                if last_projection is not None
                else "—"
            ),
            "color": GREEN,
            "foot": "Redução hipotética de 20% nos indicadores",
            "forecast": True,
        },
        {
            "label": "Base analisada",
            "badge": "Histórico",
            "value": str(current["commits"]),
            "color": TEXT,
            "foot": "Commits registrados no histórico de risco",
            "forecast": False,
        },
    ]

    cards_html = "".join(
        f'<div class="gf-kpi">'
        f'<div class="gf-kpi-head">'
        f'<span>{kpi["label"].upper()}</span>'
        f'<span class="{"gf-badge forecast" if kpi["forecast"] else "gf-badge"}">'
        f'{kpi["badge"].upper()}</span>'
        f'</div>'
        f'<div class="gf-kpi-value" style="color:{kpi["color"]}">{kpi["value"]}</div>'
        f'<div class="gf-kpi-foot">{kpi["foot"]}</div>'
        f'</div>'
        for kpi in kpis
    )

    st.markdown(
        f'<div class="gf-kpi-grid">{cards_html}</div>',
        unsafe_allow_html=True,
    )
    

def _projection_chart(projection: pd.DataFrame):

    x = alt.X(
        "commits:Q",
        title=None,
        scale=alt.Scale(domain=[0, 50], nice=False),
        axis=alt.Axis(
            values=[0, 10, 20, 30, 40, 50],
            labelExpr="datum.value == 0 ? 'Atual' : '+' + datum.value",
            labelColor=MUTED,
            grid=False,
            domain=False,
            ticks=False,
        ),
    )

    y_axis = alt.Axis(
        values=[0, 20, 40, 60, 80, 100],
        labelColor=MUTED,
        gridColor=BORDER,
        gridDash=[3, 3],
        domain=False,
        ticks=False,
        title=None,
    )

    y_scale = alt.Scale(domain=[0, 100])

    band = (
        alt.Chart(projection)
        .mark_area(color=INDIGO, opacity=0.18)
        .encode(
            x=x,
            y=alt.Y("faixa_min:Q", scale=y_scale, axis=y_axis),
            y2="faixa_max:Q",
        )
    )

    continuity = (
        alt.Chart(projection)
        .mark_line(color=INDIGO, strokeDash=[6, 4], strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y("continuidade:Q", scale=y_scale),
        )
    )

    with_actions = (
        alt.Chart(projection)
        .mark_line(color=GREEN, strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y("com_acoes:Q", scale=y_scale),
        )
    )

    last = projection.tail(1)

    labels = (
        alt.Chart(last)
        .mark_text(
            dy=-12,
            fontWeight="bold",
            fontSize=11,
            color=INDIGO_SOFT,
        )
        .encode(
            x=x,
            y="continuidade:Q",
            text=alt.Text("continuidade:Q", format=".2f"),
        )
        +
        alt.Chart(last)
        .mark_text(
            dy=14,
            fontWeight="bold",
            fontSize=11,
            color=GREEN,
        )
        .encode(
            x=x,
            y="com_acoes:Q",
            text=alt.Text("com_acoes:Q", format=".2f"),
        )
    )

    return (
        (band + continuity + with_actions + labels)
        .properties(height=240)
        .configure(background="rgba(0,0,0,0)")
        .configure_view(stroke=None)
    )

 

def render_projection_card(data: dict, key="card_projection") -> None:
    with st.container(border=True, key=key):
        st.markdown(
            card_header(
                "Projeção do Score de Risco",
                "Próximos 50 commits • simulação heurística.",
                "Mostra a continuidade e os cenários simulados",
            ),
            unsafe_allow_html=True,
        )

        projection = data["projection"]

        if projection is None or projection.empty:
            st.info("A projeção ainda não foi calculada.")
            return

        st.altair_chart(
            _projection_chart(projection),
            use_container_width=True,
            theme=None,
        )

        st.caption(
            "Continuidade: risco atual mantido. "
            "Ações preventivas: redução hipotética de 20% nos indicadores. "
            "A faixa representa uma análise de sensibilidade, "
            "não um intervalo de confiança estatístico."
        )

 

def _trends_card(data) -> None:

    with st.container(border=True, key="card_trends"):

        st.markdown(
            card_header(
                "Tendências e Contexto",
                "Indicadores extraídos do histórico analisado.",
                "Resume o histórico e as variações observadas",
            ),
            unsafe_allow_html=True,
        )

        trends = data["trends"]

        if not trends:
            st.info("Nenhuma tendência disponível.")
            return

        html = "".join(
            f'<div class="gf-trend-item">• {trend}</div>'
            for trend in trends
        )

        st.markdown(html, unsafe_allow_html=True)

        st.caption(data["current"]["trend"])

 
 
def _factors_card(data) -> None:
    with st.container(border=True, key="card_factors"):
        st.markdown(
            card_header(
                "Principais Fatores de Risco",
                "Apresenta os indicadores que mais contribuem para o risco",
            ),
            unsafe_allow_html=True,
        )

        factors = data.get("factors", [])

        if not factors:
            st.info("Nenhum fator de risco disponível.")
            return

        for factor in factors:
            col_info, col_score = st.columns([3, 1])

            with col_info:
                st.markdown(f"**{factor['name']}**")
                st.caption(factor["description"])

            with col_score:
                st.metric(
                    label="Contribuição",
                    value=f"{factor['contribution']:.2f} pts",
                )

            st.progress(
                min(factor["contribution"] / 100, 1.0)
            )


def _recommendations_card(data) -> None:
    with st.container(border=True, key="card_reco"):
        st.markdown(
            card_header(
                "Recomendações de IA",
                "Ações sugeridas • revise com sua equipe antes de aplicar.",
            ),
            unsafe_allow_html=True,
        )
        # TODO: renderizar a lista de recomendações aqui

        note, action = st.columns([2, 1], vertical_alignment="center")
        note.markdown(
            '<span class="gf-disclaimer">Redução de risco simulada, não garantida.</span>',
            unsafe_allow_html=True,
        )
        action.button(
            "Criar Plano de Ação",
            type="primary",
            use_container_width=True,
            key="predictive_create_plan",
        )

# Entrada da view
def render(analysis, risk):
    load_css()
    data = build_predictive(analysis, risk)

    _header()

    if data["status"] != "ok":
        st.warning(data["message"])
        return

    _kpis(data)

    col_chart, col_trends = st.columns([2.1, 1])

    with col_chart:
        render_projection_card(data)

    with col_trends:
        _trends_card(data)

    col_factors, col_reco = st.columns([1.35, 1])

    with col_factors:
        _factors_card(data)

    with col_reco:
        _recommendations_card(data)
 