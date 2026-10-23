#TELA ETAPA 2
import os
from html import escape

import streamlit as st

from paths import DATA_DIR   # precisa vir antes dos imports de backend (ajusta o sys.path)
from backend.app.analysis_state import TEXTO_PREPARANDO, Snapshot, snapshot_pronta
from frontend.dashboard.components.analysis_panels import achados_html, progresso_html, repo_html
from backend.services.github_token_storage import obter_token_github
from backend.database.repositories import marcar_repositorio_analisado, salvar_repositorio_usuario

ICONE_BRANCH = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#818CF8" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="6" cy="5" r="2"/><circle cx="18" cy="5" r="2"/><circle cx="12" cy="19" r="2"/>'
    '<path d="M6 7v2a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3V7M12 12v5"/></svg>'
)


def _titulos(info, branch):
    return {
        "pronta": ("Pronto para iniciar a primeira análise",
                   "Confira o repositório e a branch selecionados para iniciar a análise.",
                   "Primeira análise pronta para iniciar", "AGUARDANDO"),
        "andamento": (f"Analisando {info['full_name']} · {branch}",
                      "A primeira análise está em andamento. "
                      "Veja o progresso e os primeiros achados disponíveis.",
                      "Primeira análise em andamento", "PROCESSANDO"),
        "concluida": ("Primeira análise concluída",
                      "Os resultados já estão disponíveis para exploração.",
                      "Primeira análise concluída", "CONCLUÍDO"),
    }

def desenhar_tela(info, snap, branch, ao_iniciar=None, ao_voltar=None):
    """Desenha a tela inteira e devolve os espaços (progresso, achados) que podem ser
    redesenhados ao vivo com atualizar().

    ao_iniciar(chave_branch): chamado ao clicar em "Iniciar primeira análise".
    ao_voltar(): opcional, mostra "Trocar repositório" quando a análise ainda não começou.
    """
    rodando = snap.modo != "pronta"
    titulo, subtitulo, titulo_dir, selo = _titulos(info, branch)[snap.modo]

    st.markdown(f'<div class="pg-title">{escape(titulo)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pg-sub">{escape(subtitulo)}</div>', unsafe_allow_html=True)

    col_esq, col_dir = st.columns([1, 2], gap="medium")

    with col_esq:
        with st.container(key="first_card"):
            st.markdown(
                '<div class="an-title-row"><span class="an-title">Sua primeira análise</span>'
                f'{ICONE_BRANCH}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(repo_html(info, "REPOSITÓRIO SELECIONADO"), unsafe_allow_html=True)

            st.markdown(
                f'<div class="an-label">'
                f'{"Branch analisada" if rodando else "Branch selecionada"}</div>',
                unsafe_allow_html=True,
            )
            chave_branch = f"branch2_{info['full_name']}"
            st.selectbox(
                "Branch", info["branches"],
                index=info["branches"].index(branch) if branch in info["branches"] else 0,
                format_func=lambda b: f"{b}  (padrão)" if b == info["default_branch"] else b,
                key=chave_branch, label_visibility="collapsed", disabled=rodando,
            )

            st.markdown('<div class="an-divider"></div>', unsafe_allow_html=True)

            if not rodando:
                st.button("Iniciar primeira análise", key="iniciar_primeira",
                          type="primary", on_click=ao_iniciar, args=(chave_branch,))
                if ao_voltar:
                    st.button("Trocar repositório", key="voltar_passo1",
                              type="tertiary", on_click=ao_voltar)

    with col_dir:
        with st.container(key="analysis_card"):
            st.markdown(
                f'<div class="an-head"><div class="an-head-title">{escape(titulo_dir)}</div>'
                f'<span class="step-badge">{selo}</span></div>',
                unsafe_allow_html=True,
            )
            phs = (st.empty(), st.empty())

    atualizar(phs, snap)
    return phs


def atualizar(phs, snap):
    """Redesenha os dois painéis da direita com um novo Snapshot."""
    ph_progresso, ph_achados = phs
    ph_progresso.markdown(progresso_html(snap), unsafe_allow_html=True)
    ph_achados.markdown(achados_html(snap), unsafe_allow_html=True)

def _iniciar(chave_branch):
    st.session_state.branch = st.session_state[chave_branch]
    st.session_state.analise = "rodando"


def _voltar():
    st.session_state.passo = 1
    st.session_state.analise = "pronta"


def executar(info, branch, phs):
    from backend.app.pipeline import run_pipeline   # import tardio: só quem roda a análise precisa

    try:
        user_id = st.session_state.get("user_id")
        resultado = run_pipeline(
            info["url"], branch, DATA_DIR, token=obter_token_github(user_id),
            total_commits=info["commits"],
            on_update=lambda snap: atualizar(phs, snap),
        )
        if user_id:
            salvar_repositorio_usuario(user_id, info["full_name"], info["url"])
            marcar_repositorio_analisado(user_id, info["url"])
    except ValueError as e:
        st.session_state.erro_analise = str(e)
        st.session_state.analise = "pronta"
        st.rerun()
    except Exception as e:
        st.session_state.erro_analise = f"Não foi possível concluir a análise :"f"{type(e).__name__}: {e}"
        st.session_state.analise = "pronta"
        st.rerun()

    st.cache_data.clear()                       # o painel precisa ler os CSVs novos
    st.session_state.resultado_analise = resultado
    st.session_state.analise = "pronta"
    st.session_state.passo = 3
    st.rerun()


def render_primeira_analise():
    st.caption("DEBUG — Renderizando etapa 2")
    info = st.session_state.repo_info
    rodando = st.session_state.get("analise") == "rodando"
    branch = st.session_state.get("branch") or info["default_branch"]

    erro = st.session_state.pop("erro_analise", None)
    if erro:
        st.error(erro)

    snap = Snapshot(modo="andamento", mono=TEXTO_PREPARANDO) if rodando else snapshot_pronta()
    phs = desenhar_tela(info, snap, branch, ao_iniciar=_iniciar, ao_voltar=_voltar)

    # A análise roda depois de a tela estar desenhada, atualizando os painéis ao vivo
    if rodando:
        executar(info, branch, phs)