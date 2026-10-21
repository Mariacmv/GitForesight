import os
from datetime import datetime, timezone
from html import escape
from views.auth import restaurar_sessao

import requests
import streamlit as st

from backend.app.github import fetch_repo_stats, list_accounts, list_repos, fetch_many_stats
from components.cards import html_inline
from components.topbar import render_auth_footer, render_auth_topbar

ETAPAS = [
    "Escolher repositório",
    "Primeira análise",
    "Explorar resultados",
]

STATS_LIMIT = 30
LISTA_ALTURA = 440 #rolagem de repositórios

def _token():
    return st.session_state.get("github_token") or os.getenv("GITHUB_TOKEN")


def _num(n):
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
    if not _token():
        return None
    if "gh_contas" not in st.session_state:
        st.session_state.gh_contas = list_accounts(_token())
    return st.session_state.gh_contas

def _repos(conta):
    cache = st.session_state.setdefault("gh_repos", {})
    if conta["login"] not in cache:
        cache[conta["login"]] = list_repos(
            conta["login"], conta["type"] == "Usuário", _token()
        )
    return cache[conta["login"]]

def _detalhes(full_name):
    cache = st.session_state.setdefault("gh_detalhes", {})
    if full_name not in cache:
        cache[full_name] = fetch_repo_stats(full_name, _token())
    return cache[full_name]

def _stats(repos):
    cache = st.session_state.setdefault("gh_stats", {})
    faltam = [r["full_name"] for r in repos[:STATS_LIMIT] if r["full_name"] not in cache]
    if faltam:
        cache.update(fetch_many_stats(faltam, _token()))
    return cache

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
    contas = _contas()

    if contas is None:
        # Sem GitHub conectado: só repositórios públicos de uma conta digitada
        login = st.text_input(
            "Conta ou organização",
            placeholder="Digite o usuário ou a organização (repositórios públicos)",
            key="conta_texto",
        ).strip()
        return {"login": login, "type": "Usuário"} if login else None

    i = st.selectbox(
        "Conta ou organização",
        range(len(contas)),
        format_func=lambda i: f"{contas[i]['login']}  ·  {contas[i]['type']}",
        key="conta_sel",
    )
    return contas[i]

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
                info = _detalhes(nome)
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
        if conta is None:
            return
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