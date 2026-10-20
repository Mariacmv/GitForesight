import os
from datetime import datetime, timezone
from html import escape
from views.auth import restaurar_sessao

import requests
import streamlit as st
from backend.database.repositories import (
    salvar_instalacoes_github,
    listar_instalacoes_github_usuario,
)
from backend.services.github_installation import (
    listar_instalacoes_usuario,
    listar_repositorios_instalacao,
)
from components.cards import html_inline
from components.topbar import render_auth_footer, render_auth_topbar

from backend.services.github_installation import (
    listar_instalacoes_usuario,
    listar_repositorios_instalacao,
    obter_detalhes_repositorio,
)

ETAPAS = [
    "Escolher repositório",
    "Primeira análise",
    "Explorar resultados",
]

STATS_LIMIT = 30
LISTA_ALTURA = 440 #rolagem de repositórios

def _num(n):
    if n is None:
        return "—"

    return f"{n:,}".replace(",", ".")


def _tempo_relativo(iso):
    if not iso:
        return "—"
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    minutos = int((datetime.now(timezone.utc) - dt).total_seconds() // 60)
    if minutos < 60:
        return f"há {max(minutos, 1)} min"
    if minutos < 1440:
        return f"há {minutos // 60} h"
    dias = minutos // 1440
    return f"há {dias} dia" if dias == 1 else f"há {dias} dias"

def _ir_passo(n):
    st.session_state.passo = n

def _selecionar(full_name):
    st.session_state.repo_sel = full_name

def _concluir():
    st.session_state.onboarding_concluido = True
    

def _contas():
    """Atualiza as instalações confirmadas pelo GitHub."""
    user_id = st.session_state.get("user_id")
    user_token = st.session_state.get("github_user_token")

    if not user_id or not user_token:
        return []

    try:
        instalacoes = listar_instalacoes_usuario(user_token)
        salvar_instalacoes_github(user_id, instalacoes)

        # A resposta da API é a fonte atual da autorização.
        return instalacoes

    except requests.RequestException:
        st.error(
            "Não foi possível consultar suas instalações do GitHub. "
            "Tente novamente."
        )
        return []


def _repos(conta):
    """Lista os repositórios autorizados para uma instalação."""
    installation_id = conta["installation_id"]

    cache = st.session_state.setdefault("gh_repos", {})

    if installation_id not in cache:
        cache[installation_id] = listar_repositorios_instalacao(
            installation_id
        )

    return cache[installation_id]


def _stats(repos):
    """A listagem do App ainda não inclui métricas de commits."""
    return {}


def _detalhes(full_name, conta):
    cache = st.session_state.setdefault("gh_detalhes", {})
    installation_id = conta["installation_id"]
    chave = f"{installation_id}:{full_name}"

    if chave not in cache:
        cache[chave] = obter_detalhes_repositorio(
            installation_id,
            full_name,
        )

    return cache[chave]

def _stepper(passo):
    itens = ""
    for n, nome in enumerate(ETAPAS, start=1):
        estado = "current" if n == passo else "done" if n < passo else "todo"
        simbolo = "✓" if estado == "done" else n
        itens += (
            f'<div class="step-item {estado}">'
            f'<div class="step-circle">{simbolo}</div>'
            f'<div class="step-text">{nome}</div>'
            f'</div>'
        )

    st.markdown(html_inline(f"""
        <div class="stepper-wrapper">
            <div class="steps-container">{itens}</div>
            <div class="step-counter">ETAPA {passo} DE {len(ETAPAS)}</div>
        </div>
    """), unsafe_allow_html=True)

def _cabecalho(passo, descricao, selo):
    st.markdown(html_inline(f"""
        <div class="step-head">
            <div>
                <div class="step-title">Etapa {passo} · {ETAPAS[passo - 1]}</div>
                <div class="step-desc">{descricao}</div>
            </div>
            <span class="step-badge">{selo}</span>
        </div>
    """), unsafe_allow_html=True)

def _card_repo(info, rotulo):
    visibilidade = "Privado" if info["private"] else "Público"
    st.markdown(html_inline(f"""
        <div class="repo-card">
            <div class="repo-card-label">{rotulo}</div>
            <div class="repo-card-name">{escape(info['full_name'])}</div>
            <div class="repo-card-meta">{escape(info['language'])} · {visibilidade}</div>
            <div class="repo-card-meta">{_num(info['commits'])} commits · {_num(info['contributors'])} contribuidores</div>
        </div>
    """), unsafe_allow_html=True)

def _linha_repo(r, selecionado, stats):
    tag = "Privado" if r["private"] else "Público"
    desc = escape(r["description"] or "Sem descrição")

    meta = f'<span><i class="lang-dot"></i>{escape(r["language"])}</span>'
    if stats.get("commits") is not None:
        meta += f'<span>{_num(stats["commits"])} commits</span>'
    if stats.get("contributors") is not None:
        meta += f'<span>{_num(stats["contributors"])} contribuidores</span>'
    meta += f'<span>Atualizado {_tempo_relativo(r["pushed_at"])}</span>'

    return html_inline(f"""
        <div class="repo-row {'selected' if selecionado else ''}">
            <span class="repo-radio"></span>
            <div class="repo-row-body">
                <div class="repo-row-top">
                    <span class="repo-row-name">{escape(r['full_name'])}</span>
                    <span class="repo-tag">{tag}</span>
                </div>
                <div class="repo-row-desc">{desc}</div>
                <div class="repo-row-meta">{meta}</div>
            </div>
            {'<span class="repo-check">✓</span>' if selecionado else ''}
        </div>
    """)


def _seletor_conta():
    instalacoes = _contas()

    if not st.session_state.get("github_user_token"):
        st.warning(
            "Para selecionar repositórios privados ou autorizados "
            "pela GitHub App, entre com sua conta GitHub."
        )
        return None

    if not instalacoes:
        st.info(
            "Para analisar seus repositórios, primeiro autorize "
            "o GitForesight na sua conta GitHub."
        )
        #BOTÃO DE CONECTAR REPOSITÓRIOS
        # st.link_button(
        #     "Conectar meus repositórios",
        #     st.secrets["GITHUB_INSTALL_URL"],
        # )

        return None

    indice = st.selectbox(
        "Conta ou organização",
        range(len(instalacoes)),
        format_func=lambda i: (
            f"{instalacoes[i]['account_login']} · "
            f"{instalacoes[i]['account_type']}"
        ),
        key="conta_instalacao_sel",
    )

    return instalacoes[indice]


def processar_retorno_instalacao():
    params = st.query_params

    installation_id = params.get("installation_id")
    setup_action = params.get("setup_action")

    if not installation_id or setup_action not in ("install", "update"):
        return False

    # Remove os parâmetros para evitar processamento repetido.
    st.query_params.clear()

    # Invalida o cache anterior de repositórios.
    st.session_state.pop("gh_repos", None)

    # Retorna à seleção de repositórios.
    if st.session_state.get("autenticado"):
        st.session_state["pagina"] = "choose_repo"
        st.session_state["passo"] = 1

    st.rerun()


def _lista(conta):
    busca = st.text_input(
        "Buscar", key="repo_busca", label_visibility="collapsed",
        placeholder="Buscar por nome de repositório...",
    ).strip().lower()

    repos, stats = [], {}
    if conta is None:
        pass
    else:
        try:
            with st.spinner("Buscando repositórios..."):
                repos = _repos(conta)
                stats = _stats(repos)
        except ValueError as e:
            st.error(str(e))
        except requests.RequestException:
            st.error("Não foi possível consultar o GitHub. Verifique sua conexão.")

    filtrados = [r for r in repos if busca in r["full_name"].lower()]
    nomes = [r["full_name"] for r in filtrados]

    if st.session_state.get("repo_sel") not in nomes:
        st.session_state.repo_sel = nomes[0] if nomes else None

    st.markdown(html_inline(f"""
        <div class="repo-list-head">
            <span>{len(filtrados)} repositório{'s' if len(filtrados) != 1 else ''}</span>
            <span>Atualização recente ↓</span>
        </div>
    """), unsafe_allow_html=True)

    # Área com rolagem própria
    with st.container(height=LISTA_ALTURA, border=False, key="repo_list"):
        for i, r in enumerate(filtrados):
            with st.container(key=f"repo_row_{i}"):
                st.markdown(
                    _linha_repo(r, r["full_name"] == st.session_state.repo_sel,
                                stats.get(r["full_name"], {})),
                    unsafe_allow_html=True,
                )
                st.button(
                    f"Selecionar {r['full_name']}", key=f"pick_{i}",
                    on_click=_selecionar, args=(r["full_name"],),
                )

        if conta is not None and not filtrados:
            st.caption("Nenhum repositório encontrado.")

    nome = st.session_state.get("repo_sel")

    col_botao, col_dica = st.columns([1, 1], vertical_alignment="center")

    with col_botao:
        continuar = st.button(
            "Continuar para a primeira análise", key="continuar_analise",
            type="primary", icon=":material/arrow_forward:", disabled=not nome,
        )

    with col_dica:
        st.markdown(
            '<div class="repo-list-foot">Não encontrou o projeto? '
            'Confira a conta ou organização selecionada.</div>',
            unsafe_allow_html=True,
        )

    if continuar:
        try:
            with st.spinner("Consultando o repositório..."):
                info = _detalhes(nome, conta)
        except ValueError as e:
            st.error(str(e))
            return
        except requests.RequestException:
            st.error("Não foi possível consultar o GitHub. Verifique sua conexão.")
            return

        st.session_state.repo_info = info
        st.write(info)
        st.session_state.branch = info["default_branch"]
        st.session_state.passo = 2
        st.rerun()

def _etapa_1():
    with st.container(key="repo_picker"):
        conta = _seletor_conta()
        _lista(conta)


def _etapa_2():
    info = st.session_state.repo_info

    _cabecalho(2, "Escolha a branch e inicie a análise do histórico.", "PRIMEIRA ANÁLISE")
    _card_repo(info, "REPOSITÓRIO SELECIONADO")

    branch = st.selectbox(
        "Branch para análise",
        info["branches"],
        index=info["branches"].index(st.session_state.get("branch", info["default_branch"])),
        format_func=lambda b: f"{b}  (padrão)" if b == info["default_branch"] else b,
        key=f"branch_{info['full_name']}",
    )
    st.caption("O histórico desta branch será a base da análise proposta.")

    # TODO: clonar o repositório e rodar coleta -> dataset -> analyzer -> risk
    # (com st.status mostrando o progresso) antes de avançar.
    if st.button("Iniciar análise", key="iniciar_analise", type="primary",
                 icon=":material/arrow_forward:"):
        st.session_state.branch = branch
        st.session_state.passo = 3
        st.rerun()

    st.button("Trocar repositório", key="voltar_passo1",
              on_click=_ir_passo, args=(1,))

def _etapa_3():
    info = st.session_state.repo_info

    _cabecalho(3, "Veja uma prévia do que a análise entrega e siga para o painel.",
               "PRÉVIA ILUSTRATIVA")
    _card_repo(info, "REPOSITÓRIO ANALISADO")

    st.markdown(html_inline("""
        <div class="check-list">
            <div><span>✓</span>Histórico de commits e churn disponíveis para o plano Explorar</div>
            <div><span>✓</span>Hotspots e concentração de conhecimento visíveis no dashboard</div>
            <div><span>✓</span>Leitura dos achados no dashboard para entender o contexto do projeto</div>
        </div>
    """), unsafe_allow_html=True)

    st.caption("Prévia ilustrativa · Os achados detalhados serão exibidos no painel.")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Conhecer planos e preços", key="ver_planos", type="primary",
                     icon=":material/arrow_forward:"):
            st.toast("A página de planos ainda está em construção.")
    with col_b:
        st.button("Ir para visão geral do plano", key="ir_painel", on_click=_concluir)

    st.button("Analisar outro repositório", key="reiniciar",
              on_click=_ir_passo, args=(1,))

def render():
    if restaurar_sessao():
        st.rerun()
    render_auth_topbar(mostrar_usuario=True)

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] { display: none !important; }

        [data-testid="stMainBlockContainer"] {
            max-width: 1248px;
            padding-top: 96px !important;
            padding-bottom: 112px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "passo" not in st.session_state:
        st.session_state.passo = 1

    if st.session_state.passo > 1 and "repo_info" not in st.session_state:
        st.session_state.passo = 1

    passo = st.session_state.passo

    _stepper(passo)
    st.title("Boas-vindas ao GitForesight.")

    if passo == 1:
        _etapa_1()
    else:
        with st.container(key="step_card"):
            {2: _etapa_2, 3: _etapa_3}[passo]()

    render_auth_footer()