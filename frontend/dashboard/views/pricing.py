"""Tela de Preços do Git Foresight (proposta de planos, conceitual)."""
from html import escape
from components.sidebar import _logo_base64
import streamlit as st

GITHUB_URL = "https://github.com/Mariacmv/GitForesight"
README_URL = f"{GITHUB_URL}#readme"

PLANOS = [
    {
        "key": "explorar",
        "nome": "Explorar",
        "tag": "PROPOSTA",
        "desc": "Para estudos e projetos individuais.",
        "preco": "R$ 0",
        "unidade": "/ mês",
        "botao": "Explorar proposta gratuita",
        "destaque": False,
        "resumo": "1 repositório · 1 pessoa",
        "recursos": [
            "Histórico de commits e churn",
            "Hotspots e concentração de conhecimento",
            "Leitura dos achados no dashboard",
        ],
    },
    {
        "key": "equipe",
        "nome": "Equipe",
        "tag": "PARA EQUIPES",
        "desc": "Para discutir riscos com quem mantém o código.",
        "preco": "R$ 149",
        "unidade": "/ mês por equipe",
        "botao": "Considerar plano Equipe",
        "destaque": True,
        "resumo": "Até 5 repositórios · 10 pessoas",
        "recursos": [
            "Toda a base de análise do Explorar",
            "Simulações hipotéticas de impacto",
            "Comparação de cenários e exportação",
        ],
    },
    {
        "key": "organizacao",
        "nome": "Organização",
        "tag": "PROPOSTA",
        "desc": "Para contextos com múltiplas equipes.",
        "preco": "Sob consulta",
        "unidade": "escopo a definir",
        "botao": "Discutir necessidades",
        "destaque": False,
        "resumo": "Repositórios e pessoas a combinar",
        "recursos": [
            "Todos os recursos propostos de Equipe",
            "Visão consolidada entre repositórios",
            "Escopo ajustado à organização",
        ],
    },
]

# (escopo, explorar, equipe, organização)
TABELA = [
    ("Valor mensal sugerido", "R$ 0", "R$ 149 / equipe", "Sob consulta"),
    ("Repositórios", "1", "Até 5", "A combinar"),
    ("Pessoas no espaço de trabalho", "1", "Até 10", "A combinar"),
    ("Histórico, churn e hotspots", "Previsto", "Previsto", "Previsto"),
    ("Concentração de conhecimento", "Previsto", "Previsto", "Previsto"),
    ("Simulação e comparação de cenários", "Não proposto", "Previsto", "Previsto"),
    ("Exportação de relatórios", "Não proposto", "Previsto", "Previsto"),
    ("Visão entre repositórios", "Não proposto", "Não proposto", "Previsto"),
]

IC_BRANCH = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="7" r="2"/>'
    '<path d="M6 7v10M18 9c0 5-6 4-12 8"/></svg>'
)
IC_USERS = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/>'
    '<path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14.2c2 .7 3.5 2.6 3.5 5.8"/></svg>'
)
IC_BUILDING = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="4" y="3" width="12" height="18" rx="1.5"/><path d="M16 9h3.5a.5.5 0 0 1 .5.5V21H16"/>'
    '<path d="M8 7h4M8 11h4M8 15h4"/></svg>'
)
IC_INFO = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>'
)
IC_SHIELD = (
    '<svg width="30" height="30" viewBox="0 0 32 32" fill="none">'
    '<rect x="1" y="1" width="30" height="30" rx="8" fill="#1d2147" stroke="#6366f1" stroke-width="1.5"/>'
    '<path d="M16 7l7 3v5c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9v-5l7-3z" fill="none" '
    'stroke="#a5b4fc" stroke-width="1.8" stroke-linejoin="round"/>'
    '<path d="M16 12v5M16 20h.01" stroke="#a5b4fc" stroke-width="1.8" stroke-linecap="round"/></svg>'
)

CONTEXTOS = [
    (IC_BRANCH, "Quero investigar um projeto",
     "Explorar é a proposta de entrada para estudar o histórico de um repositório, "
     "individualmente.", "EXPLORAR"),
    (IC_USERS, "Quero discutir com a equipe",
     "Equipe propõe cenários e relatórios para até 10 pessoas, em até 5 repositórios.",
     "EQUIPE"),
    (IC_BUILDING, "Tenho múltiplas equipes",
     "Organização propõe uma visão entre repositórios, com volume e condições a combinar.",
     "ORGANIZAÇÃO"),
]

FAQ = [
    ("Esses preços já estão em vigor?",
     "Não. R$ 0 para Explorar, R$ 149 por mês por equipe e Organização sob consulta são "
     "valores sugeridos para discussão. O projeto acadêmico está em desenvolvimento e não "
     "oferece contratação nesta proposta."),
    ("Como seria a cobrança do plano Equipe?",
     "A proposta é uma mensalidade de R$ 149 por equipe, para até 5 repositórios e 10 "
     "pessoas — não por pessoa. Meios de pagamento, tributos e regras de renovação ainda "
     "precisam ser definidos."),
    ("Existe plano anual ou desconto?",
     "Não há preço anual, desconto ou período de teste definido. O comparativo usa apenas "
     "a referência mensal para evitar condições ainda não validadas."),
    ("O que acontece se eu precisar de mais repositórios?",
     "O plano Organização propõe negociar repositórios, pessoas e condições conforme o "
     "escopo. Não há cobrança excedente ou migração automática definida; cancelamento e "
     "mudança de plano também dependem de validação."),
]

NAV = [
    ("Planos propostos", "#"),
    ("Compare o escopo", "#"),
    ("Encontre seu ponto de partida", "#"),
    ("Antes de escolher", "#")
]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --pr-bg:      #0b1120;
    --pr-card:    #1a2236;
    --pr-card-hi: #1e2745;
    --pr-field:   #131b2e;
    --pr-border:  #2a3550;
    --pr-text:    #f1f5f9;
    --pr-body:    #aab4c8;
    --pr-muted:   #7b869e;
    --pr-accent:  #6366f1;
    --pr-soft:    #a5b4fc;
    --pr-sans:    'Plus Jakarta Sans', 'Inter', system-ui, sans-serif;
    --pr-mono:    'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}

/* ---------- Estrutura da página (sem sidebar, largura de leitura) ---------- */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

[data-testid="stMainBlockContainer"] {
    max-width: 1248px !important;
    padding: 0 2rem 2rem !important;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: 0; }

/* ---------- Barra de navegação ---------- */
/* barra de navegação */
.pr-nav {
    position: relative;
    display: flex; align-items: center; justify-content: space-between;
    height: 70px;
    font-family: var(--pr-sans);
}
.pr-nav::after {
    content: ""; position: absolute; bottom: 0; left: 50%;
    width: 100vw; transform: translateX(-50%);
    border-bottom: 1px solid var(--pr-border); pointer-events: none;
}

/* link ativo (na imagem é branco e em negrito) */
.pr-links a.on { color: var(--pr-text); font-weight: 700; }

/* seções */
.pr-section { position: relative; padding: 54px 0 46px; }
.pr-section::before,
.pr-section-end::after {
    content: ""; position: absolute; left: 50%;
    width: 100vw; transform: translateX(-50%);
    border-top: 1px solid var(--pr-border); pointer-events: none;
}
.pr-section::before { top: 0; }
.pr-section-end::after { bottom: 0; }

/* evita barra de rolagem horizontal por causa do 100vw */
[data-testid="stMain"] { overflow-x: hidden; }

/* ---------- Hero ---------- */
.pr-hero { text-align: center; padding: 54px 0 34px; font-family: var(--pr-sans); }
.pr-pill {
    display: inline-block; padding: 5px 12px; border-radius: 6px;
    background: var(--pr-card-hi); color: var(--pr-soft);
    font: 500 .66rem var(--pr-mono); letter-spacing: .06em;
}
.pr-h1 { margin: 22px 0 18px; color: var(--pr-text); font-size: 3.1rem;
         font-weight: 700; line-height: 1.1; letter-spacing: -.02em; }
.pr-h1 span { color: var(--pr-soft); }
.pr-lead { max-width: 640px; margin: 0 auto; color: var(--pr-body);
           font-size: 1rem; line-height: 1.7; }

.pr-notice {
    display: flex; gap: 14px; align-items: center; margin: 14px 0 34px;
    padding: 14px 18px; border-left: 3px solid var(--pr-accent); border-radius: 4px;
    background: #171d3f; font-family: var(--pr-sans);
}
.pr-notice svg { color: var(--pr-soft); flex-shrink: 0; }
.pr-notice b  { display: block; color: var(--pr-text); font-size: .85rem; }
.pr-notice span { color: var(--pr-muted); font-size: .72rem; }

/* ---------- Cabeçalhos de seção ---------- */
.pr-eyebrow { color: var(--pr-soft); font: 500 .68rem var(--pr-mono); letter-spacing: .08em; }
.pr-h2 { margin: 10px 0 8px; color: var(--pr-text); font: 700 1.9rem var(--pr-sans);
         letter-spacing: -.01em; }
.pr-sub { color: var(--pr-body); font: 400 .9rem var(--pr-sans); margin-bottom: 26px; }
.pr-section { padding: 54px 0 46px; border-top: 1px solid var(--pr-border); }

.pr-bar { display: flex; justify-content: space-between; align-items: center;
          color: var(--pr-muted); font: 400 .72rem var(--pr-mono); margin-bottom: 26px; }
.pr-bar .pr-pill { margin-right: 10px; padding: 3px 9px; }

/* ---------- Cards de plano ---------- */
[class*="st-key-pr_plan_"] {
    background: var(--pr-card);
    border: 1px solid var(--pr-border);
    border-radius: 14px;
    padding: 28px 26px 24px;
    gap: 0 !important;
    height: 100%;
}
.st-key-pr_plan_equipe {
    background: var(--pr-card-hi);
    border: 2px solid var(--pr-accent);
    box-shadow: 0 0 0 1px rgba(99,102,241,.25), 0 14px 40px rgba(99,102,241,.12);
}
.pr-plan-head { display: flex; justify-content: space-between; align-items: center; }
.pr-plan-name { color: var(--pr-text); font: 600 1.35rem var(--pr-sans); }
.pr-plan-tag  { color: var(--pr-muted); font: 500 .62rem var(--pr-mono); letter-spacing: .06em; }
.pr-plan-desc { margin: 22px 0 36px; color: var(--pr-body); font: 400 .82rem var(--pr-sans); }
.pr-price { color: var(--pr-text); font: 700 2.5rem var(--pr-sans); letter-spacing: -.02em; line-height: 1.1; }
.pr-unit  { color: var(--pr-muted); font: 400 .78rem var(--pr-sans); margin: 6px 0 20px; }

[class*="st-key-pr_plan_"] button {
    min-height: 44px; border-radius: 8px; font-weight: 600; font-size: .85rem;
    background: transparent; border: 1px solid var(--pr-border); color: var(--pr-text);
}
[class*="st-key-pr_plan_"] button:hover { border-color: var(--pr-accent); color: #fff; }
[class*="st-key-pr_plan_"] button[kind="primary"] { background: var(--pr-accent); border-color: var(--pr-accent); }
[class*="st-key-pr_plan_"] button[kind="primary"]:hover { background: #7c7ff5; }

.pr-feat { margin-top: 22px; padding-top: 20px; border-top: 1px solid var(--pr-border); font-family: var(--pr-sans); }
.pr-feat-sum { color: var(--pr-text); font-size: .82rem; font-weight: 600; }
.pr-feat-lbl { margin: 10px 0 14px; color: var(--pr-soft); font: 500 .6rem var(--pr-mono); letter-spacing: .08em; }
.pr-feat ul { list-style: none; margin: 0; padding: 0; }
.pr-feat li { position: relative; padding: 0 0 0 26px; margin-bottom: 14px;
              color: #d5dbe8; font-size: .8rem; line-height: 1.4; }
.pr-feat li::before { content: "✓"; position: absolute; left: 0; top: 0; color: var(--pr-soft); font-weight: 700; }
.pr-disc { text-align: center; color: var(--pr-muted); font: 400 .72rem var(--pr-sans); margin: 28px 0 8px; }

/* ---------- Tabela comparativa ---------- */
.pr-table-wrap { overflow-x: auto; border: 1px solid var(--pr-border); border-radius: 12px; background: var(--pr-card); }
.pr-table { width: 100%; border-collapse: collapse; font-family: var(--pr-sans); }
.pr-table th, .pr-table td { padding: 14px 24px; text-align: center; font-size: .8rem; color: var(--pr-body); }
.pr-table th:first-child, .pr-table td:first-child { text-align: left; color: var(--pr-text); }
.pr-table thead th { color: var(--pr-text); font-weight: 600; padding: 18px 24px; background: #1c2540; }
.pr-table tbody td { border-top: 1px solid var(--pr-border); }
.pr-table .eq { color: var(--pr-soft); }
.pr-table thead th.eq { color: var(--pr-soft); }
.pr-table td.no { color: var(--pr-muted); }

/* ---------- Pontos de partida ---------- */
.pr-ctx-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.pr-ctx { padding: 24px; border: 1px solid var(--pr-border); border-radius: 12px; background: var(--pr-card); font-family: var(--pr-sans); }
.pr-ctx svg { color: var(--pr-soft); }
.pr-ctx h3 { margin: 16px 0 10px; color: var(--pr-text); font-size: 1.1rem; font-weight: 600; }
.pr-ctx p  { margin: 0 0 14px; color: var(--pr-muted); font-size: .8rem; line-height: 1.7; }
.pr-ctx span { color: var(--pr-soft); font: 500 .62rem var(--pr-mono); letter-spacing: .08em; }

/* ---------- FAQ ---------- */
.pr-faq-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 60px; font-family: var(--pr-sans); }
.pr-faq-grid .pr-h2 { font-size: 1.9rem; line-height: 1.2; }
.pr-faq-side p { color: var(--pr-body); font-size: .82rem; line-height: 1.7; margin: 0 0 18px; }
.pr-faq-side p.sm { color: var(--pr-muted); font-size: .72rem; }
.pr-faq details { padding: 18px 0; border-bottom: 1px solid var(--pr-border); }
.pr-faq details:first-child { padding-top: 0; }
.pr-faq summary { cursor: pointer; list-style: none; display: flex; justify-content: space-between;
                  color: var(--pr-text); font-size: .88rem; font-weight: 600; }
.pr-faq summary::-webkit-details-marker { display: none; }
.pr-faq summary::after { content: "+"; color: var(--pr-soft); font-size: 1.1rem; line-height: 1; }
.pr-faq details[open] summary::after { content: "−"; }
.pr-faq details p { margin: 10px 0 0; color: var(--pr-muted); font-size: .8rem; line-height: 1.7; }

/* ---------- CTA final ---------- */
.st-key-pr_cta {
    margin-top: 40px; padding: 36px 40px;
    background: var(--pr-card); border: 1px solid var(--pr-border); border-radius: 14px;
}
.pr-cta-lbl { color: var(--pr-soft); font: 500 .62rem var(--pr-mono); letter-spacing: .08em; }
.pr-cta-title { margin: 12px 0 12px; color: var(--pr-text); font: 600 1.9rem var(--pr-sans); }
.pr-cta-txt { color: var(--pr-body); font: 400 .85rem/1.7 var(--pr-sans); max-width: 640px; }
.st-key-pr_cta button, .st-key-pr_cta a[data-testid="stBaseLinkButton-secondary"] {
    min-height: 46px; border-radius: 8px; font-weight: 600; font-size: .85rem;
}
.st-key-pr_cta button[kind="primary"] { background: var(--pr-accent); border-color: var(--pr-accent); }

/* ---------- Rodapé ---------- */
.pr-foot { display: flex; justify-content: space-between; align-items: flex-end;
           margin-top: 38px; font-family: var(--pr-sans); }
.pr-foot small { display: block; margin-top: 10px; color: var(--pr-muted); font-size: .72rem; }
.pr-foot a { color: var(--pr-soft); font: 500 .75rem var(--pr-mono); text-decoration: none; }
.pr-foot .r { text-align: right; }

@media (max-width: 900px) {
    .pr-links a:not(.pr-readme) { display: none; }
    .pr-h1 { font-size: 2.1rem; }
    .pr-ctx-grid, .pr-faq-grid { grid-template-columns: 1fr; gap: 20px; }
}
</style>
"""

def _h(html: str) -> str:
    """Remove indentação e linhas vazias (o markdown trataria como bloco de código)."""
    return "\n".join(l.strip() for l in html.splitlines() if l.strip())


def _md(html: str):
    st.markdown(_h(html), unsafe_allow_html=True)

def _secao_cabecalho(eyebrow: str, titulo: str, sub: str):
    return (
        f'<div class="pr-eyebrow">{eyebrow}</div>'
        f'<div class="pr-h2">{titulo}</div>'
        f'<div class="pr-sub">{sub}</div>'
    )

def _escolher_repositorio():
    st.session_state.pop("pagina_publica", None)
    st.session_state["mostrar_banner"] = False
    if st.session_state.get("autenticado"):
        st.session_state["pagina"] = "choose_repo"
        st.session_state["passo"] = 1

def _aviso_plano(nome: str):
    st.toast(f"Plano {nome}: proposta conceitual, sem contratação disponível.")

# def _nav():
#     links = "".join(
#         f'<a class="{"on" if i == len(NAV) - 1 else ""}" href="{href}">{escape(txt)}</a>'
#         for i, (txt, href) in enumerate(NAV)
#     )
#     _md(f"""
#         <div class="pr-nav">
#             <div class="pr-brand">{IC_SHIELD}<span>Git Foresight</span></div>
#             <div class="pr-links">
#                 {links}
#                 <a class="pr-readme" href="{README_URL}" target="_blank" rel="noopener">Ler o README ↗</a>
#             </div>
#         </div>
#     """)
def _nav(publico: bool = False):
    entrar = '<a class="gf-btn pri" href="/?entrar=1" target="_self">Entrar</a>' if publico else ""
    _md(f"""
    <header class="gf-nav"><div class="gf-wrap">
      <a class="gf-brand" href="/" target="_self">
        <img class="auth-brand-logo-img" src="data:image/png;base64,{_logo_base64()}">
        <div class="auth-brand-text">
          <div class="auth-brand-name">Git Foresight</div>
        </div>
      </a>
      <nav>
        <a href="/#planos" target="_self">Planos propostos</a>
        <a href="/#tabela" target="_self">Compare o escopo</a>
        <a href="/#contextos" target="_self">Encontre seu ponto de partida</a>
        <a href="/#faq" target="_self">Antes de escolher</a>        
        <a class="gf-btn sec" href="{README_URL}" target="_blank" rel="noopener">Ler o README ↗</a>
        {entrar}
      </nav>
    </div></header>
    """)

def _hero():
    _md(f"""
        <div class="pr-hero">
            <span class="pr-pill">PROJETO ACADÊMICO · EM DESENVOLVIMENTO</span>
            <div class="pr-h1">Uma proposta para cada <span>escala de projeto.</span></div>
            <div class="pr-lead">Do primeiro repositório à discussão em equipe. Compare uma proposta
            de acesso à análise histórica, aos hotspots e às simulações de impacto.</div>
        </div>
        <div class="pr-notice">
            {IC_INFO}
            <div><b>Proposta de planos — valores e condições sujeitos a validação</b>
            <span>Conceito comercial, não uma oferta vigente. Recursos e limites propostos;
            contratação e pagamento não estão disponíveis.</span></div>
        </div>
    """)


def _card_plano(p: dict):
    with st.container(key=f"pr_plan_{p['key']}"):
        _md(f"""
            <div class="pr-plan-head">
                <span class="pr-plan-name">{escape(p['nome'])}</span>
                <span class="pr-plan-tag">{escape(p['tag'])}</span>
            </div>
            <div class="pr-plan-desc">{escape(p['desc'])}</div>
            <div class="pr-price">{escape(p['preco'])}</div>
            <div class="pr-unit">{escape(p['unidade'])}</div>
        """)
        st.button(
            p["botao"],
            key=f"pr_btn_{p['key']}",
            type="primary" if p["destaque"] else "secondary",
            use_container_width=True,
            on_click=_aviso_plano,
            args=(p["nome"],),
        )
        itens = "".join(f"<li>{escape(r)}</li>" for r in p["recursos"])
        _md(f"""
            <div class="pr-feat">
                <div class="pr-feat-sum">{escape(p['resumo'])}</div>
                <div class="pr-feat-lbl">RECURSOS PREVISTOS</div>
                <ul>{itens}</ul>
            </div>
        """)


def _planos():
    _md("""
        <div class="pr-bar">
            <span>01 / PLANOS PROPOSTOS</span>
            <span><span class="pr-pill">MENSAL</span>Sem compromisso anual definido</span>
        </div>
    """)
    cols = st.columns(3, gap="large")
    for col, plano in zip(cols, PLANOS):
        with col:
            _card_plano(plano)
    _md('<div class="pr-disc">Em todos os planos, simular não é prever o futuro. '
        'As estimativas apoiam a decisão e precisam de contexto.</div>')


def _tabela():
    linhas = ""
    for escopo, a, b, c in TABELA:
        def cel(v, eq=False):
            cls = " ".join(x for x in ("eq" if eq else "", "no" if v == "Não proposto" else "") if x)
            return f'<td class="{cls}">{escape(v)}</td>'
        linhas += f"<tr><td>{escape(escopo)}</td>{cel(a)}{cel(b, True)}{cel(c)}</tr>"

    _md(f"""
        <div class="pr-section">
            {_secao_cabecalho("02 / COMPARE O ESCOPO", "O que muda em cada plano?",
                "Uma mesma base de análise, com diferentes escalas e possibilidades. "
                "Tudo abaixo faz parte da proposta, não de recursos já disponíveis.")}
            <div class="pr-table-wrap">
            <table class="pr-table">
                <thead><tr><th>Escopo proposto</th><th>Explorar</th>
                <th class="eq">Equipe</th><th>Organização</th></tr></thead>
                <tbody>{linhas}</tbody>
            </table>
            </div>
        </div>
    """)


def _contextos():
    cards = "".join(
        f'<div class="pr-ctx">{icone}<h3>{escape(t)}</h3><p>{escape(d)}</p>'
        f'<span>{escape(rot)} →</span></div>'
        for icone, t, d, rot in CONTEXTOS
    )
    _md(f"""
        <div class="pr-section">
            {_secao_cabecalho("03 / ENCONTRE SEU PONTO DE PARTIDA", "Escolha pelo contexto, não só pelo volume.",
                "O número de repositórios importa. A forma como sua equipe pretende usar os achados também.")}
            <div class="pr-ctx-grid">{cards}</div>
        </div>
    """)


def _faq():
    itens = "".join(
        f"<details{' open' if i >= 0 else ''}><summary>{escape(q)}</summary><p>{escape(a)}</p></details>"
        for i, (q, a) in enumerate(FAQ)
    )
    _md(f"""
        <div class="pr-section pr-section-end">
            <div class="pr-faq-grid">
                <div class="pr-faq-side">
                    <div class="pr-eyebrow">04 / ANTES DE ESCOLHER</div>
                    <div class="pr-h2">Sem surpresas. Sem promessas antecipadas.</div>
                    <p>O que já pode ser comparado e o que ainda precisa ser definido sobre a proposta comercial.</p>
                    <p class="sm">O README é a fonte para o escopo técnico. Planos e preços são uma
                    exploração conceitual desta interface.</p>
                </div>
                <div class="pr-faq">{itens}</div>
            </div>
        </div>
    """)


def _cta():
    with st.container(key="pr_cta"):
        txt, acoes = st.columns([2.6, 1], gap="large", vertical_alignment="center")
        with txt:
            _md("""
                <div class="pr-cta-lbl">DO PLANO À PRIMEIRA PERGUNTA</div>
                <div class="pr-cta-title">Comece pelo seu repositório.</div>
                <div class="pr-cta-txt">Explore a experiência proposta de escolha do projeto ou conheça
                a ideia no README. Nenhuma contratação é realizada aqui.</div>
            """)
        with acoes:
            st.button(
                "Escolher repositório",
                key="pr_cta_repo",
                type="primary",
                icon=":material/arrow_forward:",
                icon_position="right",
                use_container_width=True,
                on_click=_escolher_repositorio,
            )
            st.link_button(
                "Conhecer o projeto no GitHub",
                GITHUB_URL,
                icon=":material/north_east:",
                icon_position="right",
                use_container_width=True,
            )


def _rodape():
    _md(f"""
        <div class="pr-foot">
            <div>
                <div class="pr-brand">{IC_SHIELD}<span>Git Foresight</span></div>
                <small>Projeto acadêmico em desenvolvimento · Proposta comercial conceitual</small>
            </div>
            <div class="r">
                <a href="{GITHUB_URL}" target="_blank" rel="noopener">github.com/Mariacmv/GitForesight ↗</a>
                <small>Valores, limites e recursos sujeitos à validação.</small>
            </div>
        </div>
    """)

def _voltar():
    st.session_state["pagina"] = st.session_state.pop("pagina_anterior", None) or "choose_repo"

def render():
    st.markdown(CSS, unsafe_allow_html=True)
    _nav()
    _hero()
    _planos()
    _tabela()
    _contextos()
    _faq()
    _cta()
    _rodape()
    #_voltar()