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
 
# Dados fictícios (placeholders)
# KPIS = [ #Resumo calculado pelo backend
#     {
#         "label": "Score de risco",
#         "badge": "Atual",
#         "value": "72/100",
#         "color": ORANGE,
#         "foot": "12 vulnerabilidades críticas abertas",
#         "forecast": False,
#     },
#     {
#         "label": "Em +50 commits",
#         "badge": "Previsão",
#         "value": "84/100",
#         "color": INDIGO_SOFT,
#         "foot": "+12 pontos no cenário de continuidade",
#         "forecast": True,
#     },
#     {
#         "label": "Com ações de IA",
#         "badge": "Previsão",
#         "value": "58/100",
#         "color": GREEN,
#         "foot": "Correções aplicadas • simulação",
#         "forecast": True,
#     },
#     {
#         "label": "Base analisada",
#         "badge": "Atual",
#         "value": "1.847",
#         "color": TEXT,
#         "foot": "Commits • cobertura atual de testes: 89%",
#         "forecast": False,
#     },
# ]
 
# PROJECTION = pd.DataFrame( #Projeção dos próximos 50 commits
#     {
#         "commits": [0, 10, 20, 30, 40, 50],
#         "continuidade": [72, 75, 77, 77, 80, 84],
#         "com_acoes": [72, 70, 66, 62, 59, 58],
#         "faixa_min": [72, 74, 75, 74, 77, 79],
#         "faixa_max": [72, 76, 79, 81, 85, 89],
#     }
# )
 
# TRENDS = [ #Interpretação do histórico
#     "Autenticação: 47 commits em 90 dias e 3 falhas reincidentes.",
#     "Pagamentos: 34 commits no período.",
#     "Cobertura de testes atual: 89%.",
# ]
 
# FACTORS = [ #Indicadores efetivamente identificados
#     {
#         "severity": RED,
#         "file": "auth_service.py",
#         "title": "Dependência desatualizada e entrada sem sanitização",
#         "meta": "jsonwebtoken@8.5.1 • handler de login, linha 142",
#     },
#     {
#         "severity": RED,
#         "file": "payment_gateway.py",
#         "title": "Credenciais expostas no módulo de transações",
#         "meta": "Chaves de API no código • exige rotação dos segredos",
#     },
#     {
#         "severity": ORANGE,
#         "file": "auth_service.py",
#         "title": "Complexidade elevada e código duplicado",
#         "meta": "Complexidade ciclomática: 34 • 3 ocorrências",
#     },
# ]
 
# RECOMMENDATIONS = [ #Recomendações derivadas das evidências
#     {
#         "title": "Atualizar dependências de autenticação",
#         "desc": "Atualizar jsonwebtoken para v9.0.0 ou superior e validar regressões.",
#     },
#     {
#         "title": "Validar entradas e proteger segredos",
#         "desc": "Adicionar Joi ou Zod ao login e rotacionar as chaves de pagamento.",
#     },
#     {
#         "title": "Reforçar testes nos módulos prioritários",
#         "desc": "Cobrir cenários de falha de autenticação e de transações.",
#     },
# ]

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
            "value": "—",
            "color": INDIGO_SOFT,
            "foot": "Modelo preditivo em desenvolvimento",
            "forecast": True,
        },
        {
            "label": "Com ações corretivas",
            "badge": "Simulação",
            "value": "—",
            "color": GREEN,
            "foot": "Cenário ainda não calculado",
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

    for col, kpi in zip(st.columns(4), kpis):
        badge_cls = (
            "gf-badge forecast"
            if kpi["forecast"]
            else "gf-badge"
        )

        col.markdown(
            f'<div class="gf-kpi">'
            f'<div class="gf-kpi-head">'
            f'<span>{kpi["label"].upper()}</span>'
            f'<span class="{badge_cls}">{kpi["badge"].upper()}</span>'
            f'</div>'
            f'<div class="gf-kpi-value" style="color:{kpi["color"]}">'
            f'{kpi["value"]}</div>'
            f'<div class="gf-kpi-foot">{kpi["foot"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
 
def _projection_chart() -> alt.LayerChart:
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
        values=[20, 40, 60, 80, 100],
        labelColor=MUTED,
        gridColor=BORDER,
        gridDash=[3, 3],
        domain=False,
        ticks=False,
        title=None,
    )
    y_scale = alt.Scale(domain=[20, 100])
 
    band = (
        alt.Chart(PROJECTION)
        .mark_area(color=INDIGO, opacity=0.18)
        .encode(x=x, y=alt.Y("faixa_min:Q", scale=y_scale, axis=y_axis), y2="faixa_max:Q")
    )
    continuity = (
        alt.Chart(PROJECTION)
        .mark_line(color=INDIGO, strokeDash=[6, 4], strokeWidth=2)
        .encode(x=x, y=alt.Y("continuidade:Q", scale=y_scale))
    )
    with_actions = (
        alt.Chart(PROJECTION)
        .mark_line(color=GREEN, strokeDash=[6, 4], strokeWidth=2)
        .encode(x=x, y=alt.Y("com_acoes:Q", scale=y_scale))
    )
    last = PROJECTION.tail(1)
    labels = alt.Chart(last).mark_text(
        dy=-10, fontWeight="bold", fontSize=11, color=INDIGO_SOFT
    ).encode(x=x, y="continuidade:Q", text=alt.value("84")) + alt.Chart(last).mark_text(
        dy=14, fontWeight="bold", fontSize=11, color=GREEN
    ).encode(x=x, y="com_acoes:Q", text=alt.value("58"))
 
    return (
        (band + continuity + with_actions + labels)
        .properties(height=240)
        .configure(background="rgba(0,0,0,0)")
        .configure_view(stroke=None)
    )
 
 
def _projection_card(data) -> None:
    with st.container(border=True):
        card_header(
            "Projeção do Score de Risco",
            "Próximos 50 commits • estimativa, não resultado de varredura.",
        )
        st.altair_chart(_projection_chart(), use_container_width=True, theme=None)
        st.markdown(
            card_header(
                "Projeção do Score de Risco",
                "Próximos 50 commits",
            ),
            unsafe_allow_html=True,
        )
    if data["projection"] is None:
        with st.container(border=True):
            st.markdown(
                card_header(
                    "Projeção do Score de Risco",
                    "Próximos 50 commits",
                ),
                unsafe_allow_html=True,
            )

            st.info("A projeção ainda não foi calculada.")

        return
 
def _trends_card() -> None:
    with st.container(border=True):
        card_header("Tendências e Contexto", "Sinais atuais que orientam a previsão.")
        #items = "".join(f'<div class="gf-trend-item">• {t}</div>' for t in TRENDS)
        st.markdown(
            card_header(
                "Projeção do Score de Risco",
                "Próximos 50 commits",
            ),
            unsafe_allow_html=True,
        )
 
 
def _factors_card() -> None:
    with st.container(border=True):
        card_header(
            "Principais Fatores de Risco",
            "Evidências atuais consideradas pelo modelo.",
        )
        # html = "".join(
        #     f'<div class="gf-factor"><span class="gf-dot" style="background:{f["severity"]}"></span>'
        #     f'<div><div class="gf-file">{f["file"]}</div>'
        #     f'<div class="gf-factor-title">{f["title"]}</div>'
        #     f'<div class="gf-factor-meta">{f["meta"]}</div></div></div>'
        #     for f in FACTORS
        # )
        st.markdown(
            card_header(
                "Projeção do Score de Risco",
                "Próximos 50 commits",
            ),
            unsafe_allow_html=True,
        )
 
 
def _recommendations_card() -> None:
    with st.container(border=True, key="card_reco"):
        card_header(
            "Recomendações de IA",
            "Ações sugeridas • revise com sua equipe antes de aplicar.",
        )
        # html = "".join(
        #     f'<div class="gf-reco"><span class="gf-num">{i:02d}</span>'
        #     f'<div><div class="gf-reco-title">{r["title"]}</div>'
        #     f'<div class="gf-reco-desc">{r["desc"]}</div></div></div>'
        #     for i, r in enumerate(RECOMMENDATIONS, start=1)
        # )
        st.markdown(
            card_header(
                "Projeção do Score de Risco",
                "Próximos 50 commits",
            ),
            unsafe_allow_html=True,
        )
 
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

    st.write("")
    _kpis(data)
    st.write("")

    col_chart, col_trends = st.columns([2.1, 1])

    with col_chart:
        _projection_card(data)

    with col_trends:
        _trends_card(data)

    col_factors, col_reco = st.columns([1.35, 1])

    with col_factors:
        _factors_card(data)

    with col_reco:
        _recommendations_card(data)
 