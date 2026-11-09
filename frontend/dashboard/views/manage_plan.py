from html import escape
import streamlit as st
from theme import load_css

def _svg(paths: str, size: int = 18) -> str:
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round">{paths}</svg>'
    )


IC_INFO = _svg('<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>')
IC_CHECK = _svg('<path d="M4 12.5l5 5L20 6.5"/>', 16)
IC_USERS = _svg(
    '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/>'
    '<path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14.2c2 .7 3.5 2.6 3.5 5.8"/>'
)
IC_BUILDING = _svg(
    '<rect x="4" y="3" width="12" height="18" rx="1.5"/>'
    '<path d="M16 9h3.5a.5.5 0 0 1 .5.5V21H16"/><path d="M8 7h4M8 11h4M8 15h4"/>'
)
IC_BOX = _svg('<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>')
IC_WARN = _svg('<path d="M12 3.5l9.5 16.5h-19L12 3.5z"/><path d="M12 10v4.5M12 17.2h.01"/>')

# ---------------------------------------------------------------- dados (exemplos)

PLANO = {
    "nome": "Plano Equipe",
    "descricao": "Escolha ilustrada para esta conta. Não representa assinatura ativa nem cobrança vigente.",
    "preco": "R$ 149",
    "unidade": "/ mês por equipe",
    "limites": ["Até 5 repositórios", "Até 10 pessoas"],
    "recursos": [
        "Histórico de commits e churn",
        "Hotspots e concentração de conhecimento",
        "Simulações hipotéticas de impacto",
        "Comparação de cenários e exportação",
    ],
}

# (ícone, nome, descrição, preço, unidade)
OPCOES = [
    (IC_USERS, "Equipe", "Até 5 repositórios e 10 pessoas", "R$ 149", "/ mês"),
    (IC_BUILDING, "Organização", "Repositórios e pessoas a combinar", "Sob consulta", "/ mês"),
    (IC_BOX, "Explorar", "1 repositório e 1 pessoa", "R$ 0", "/ mês"),
]

COBRANCA = [
    ("Forma", "Cartão de crédito"),
    ("Período", "Mensal"),
    ("Próximo vencimento", "15 de maio de 2026"),
    ("Valor previsto", "R$ 149,00"),
]

SITUACAO = [
    ("Status", "Exemplo ilustrativo"),
    ("Repositórios", "Até 5"),
    ("Pessoas", "Até 10"),
    ("Recursos", "Histórico, hotspots, simulações e exportação"),
]

# (data, valor, status)
TRANSACOES = [
    ("15/04/2026", "R$ 149,00", "Pendente"),
    ("15/03/2026", "R$ 149,00", "Pendente"),
    ("15/02/2026", "R$ 149,00", "Pendente"),
]

# ---------------------------------------------------------------- helpers


def _md(html: str):
    """Remove indentação e linhas vazias (o markdown trataria como bloco de código)."""
    limpo = "\n".join(l.strip() for l in html.splitlines() if l.strip())
    st.markdown(limpo, unsafe_allow_html=True)


def _demo(msg: str):
    st.toast(f"{msg} (demonstração, nenhuma ação real foi executada).")


def _linhas(pares) -> str:
    itens = "".join(
        f'<div class="gp-row"><span>{escape(k)}</span><b>{escape(v)}</b></div>' for k, v in pares
    )
    return f'<div class="gp-rows">{itens}</div>'


def _cabecalho_card(tag: str, titulo: str, descricao: str = "", vermelho: bool = False) -> str:
    cls = "gp-tag red" if vermelho else "gp-tag"
    desc = f'<div class="gp-desc">{escape(descricao)}</div>' if descricao else ""
    return f'<div class="{cls}">{escape(tag)}</div><div class="gp-title">{escape(titulo)}</div>{desc}'


# ---------------------------------------------------------------- cards


def _card_plano_escolhido():
    with st.container(key="gp_card_plano"):
        limites = "".join(f"<li>{escape(x)}</li>" for x in PLANO["limites"])
        recursos = "".join(f"<li>{IC_CHECK}{escape(x)}</li>" for x in PLANO["recursos"])
        _md(f"""
            <div class="gp-tag">PLANO ESCOLHIDO</div>
            <div class="gp-title lg">{escape(PLANO['nome'])}</div>
            <div class="gp-desc">{escape(PLANO['descricao'])}</div>
            <div class="gp-price">{escape(PLANO['preco'])}</div>
            <div class="gp-unit">{escape(PLANO['unidade'])}</div>
            <div class="gp-sep"></div>
            <div class="gp-lbl">Limites previstos</div>
            <ul class="gp-dots">{limites}</ul>
            <div class="gp-sep"></div>
            <div class="gp-lbl-mono">RECURSOS PREVISTOS</div>
            <ul class="gp-checks">{recursos}</ul>
        """)


def _card_alterar_plano():
    with st.container(key="gp_card_alterar"):
        opcoes = "".join(
            f'<div class="gp-opt"><div class="gp-opt-ic">{ic}</div>'
            f'<div class="gp-opt-body"><b>{escape(nome)}</b><span>{escape(desc)}</span></div>'
            f'<div class="gp-opt-price"><b>{escape(preco)}</b><span>{escape(un)}</span></div></div>'
            for ic, nome, desc, preco, un in OPCOES
        )
        _md(f"""
            {_cabecalho_card("ALTERAR PLANO", "Escolha uma nova proposta",
                             "Compare as opções disponíveis e ajuste a escolha para "
                             "repositórios, pessoas e recursos.")}
            <div class="gp-opts">{opcoes}</div>
        """)
        st.button(
            "Escolher plano", key="gp_btn_escolher", type="primary",
            use_container_width=True, on_click=_demo, args=("Escolher plano",),
        )


def _card_cobranca():
    with st.container(key="gp_card_cobranca"):
        _md(f"""
            {_cabecalho_card("DETALHES DE PAGAMENTO", "Informações de cobrança",
                             "Exemplo de dados para demonstração.")}
            {_linhas(COBRANCA)}
        """)
        st.button(
            "Atualizar pagamento", key="gp_btn_pagamento", type="primary",
            use_container_width=True, on_click=_demo, args=("Atualizar pagamento",),
        )


def _card_situacao():
    with st.container(key="gp_card_situacao"):
        _md(f"""
            {_cabecalho_card("SITUAÇÃO DO PLANO", PLANO["nome"],
                             "Exemplo ilustrativo para esta conta.")}
            {_linhas(SITUACAO)}
        """)


def _card_historico():
    with st.container(key="gp_card_historico"):
        itens = "".join(
            f'<div class="gp-tx"><div class="gp-tx-date">{escape(d)}</div>'
            '<div class="gp-tx-mid"><b>Cobrança mensal</b><span>Exemplo de demonstração</span></div>'
            f'<div class="gp-tx-end"><b>{escape(v)}</b><span>{escape(s)}</span></div></div>'
            for d, v, s in TRANSACOES
        )
        _md(f"""
            {_cabecalho_card("HISTÓRICO DE PAGAMENTO", "Transações recentes",
                             "Exemplo de registros para demonstração.")}
            <div class="gp-tx-list">{itens}</div>
        """)
        st.button(
            "Ver histórico completo", key="gp_btn_historico",
            use_container_width=True, on_click=_demo, args=("Ver histórico completo",),
        )


def _card_cancelar():
    with st.container(key="gp_card_cancelar"):
        _md(f"""
            {_cabecalho_card("CANCELAR ASSINATURA", "Encerrar assinatura",
                             "Esta ação é exemplificativa e não executa ação real. "
                             "Revise os impactos antes de confirmar.", vermelho=True)}
            <div class="gp-alert">{IC_WARN}<div>Atenção: esta ação pode afetar acesso a recursos,
            histórico e compartilhamento de dados.</div></div>
        """)
        st.button(
            "Cancelar assinatura", key="gp_btn_cancelar_assinatura", type="primary",
            use_container_width=True, on_click=_demo, args=("Cancelar assinatura",),
        )

def _cabecalho():
    _md(f"""
        <div class="gp-h1">Gerenciar plano</div>
        <div class="gp-lead">Revise o plano escolhido, acompanhe pagamentos, consulte histórico
        e acesse ações administrativas em uma única área.</div>
    """)


def _rodape():
    with st.container(key="gp_footer"):
        nota, cancelar, salvar = st.columns([3, 1, 1.6], gap="small", vertical_alignment="center")
        with nota:
            _md('<div class="gp-foot-note">As alterações se aplicam apenas à sua conta.</div>')
        with cancelar:
            st.button(
                "Cancelar", key="gp_btn_cancelar",
                use_container_width=True, on_click=_demo, args=("Cancelar",),
            )
        with salvar:
            st.button(
                "Salvar Alterações", key="gp_btn_salvar", type="primary",
                use_container_width=True, on_click=_demo, args=("Salvar Alterações",),
            )


def render_plan():
    load_css("base", "predictive", "manage_plan")
    with st.container(key="gp_page"):
        _cabecalho()
        with st.container(key="gp_grid"):
            with st.container(key="gp_row1"):      
                _card_plano_escolhido()
                _card_alterar_plano()
                _card_cobranca()
            with st.container(key="gp_row2"):
                _card_situacao()
                _card_historico()
                _card_cancelar()
        _rodape()