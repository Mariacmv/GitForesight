import base64
from pathlib import Path

import streamlit as st
from streamlit_option_menu import option_menu

from data_loader import load_data
from components.cards import render_metrics

st.set_page_config(
    page_title="Git Foresight",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo
logo = (
    Path(r"C:\Users\maria\OneDrive\Área de Trabalho\GitForesight")
    / "frontend"
    / "assets"
    / "Logo.png"
)

with open(logo, "rb") as image_file:
    encoded_logo = base64.b64encode(image_file.read()).decode()

if "tela_ativa" not in st.session_state:
    st.session_state.tela_ativa = "Visão Geral"

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarUserContent"] {
            background-color: #0B1220 !important;
        }
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(255,255,255,0.05);
        }

        /* Sidebar sem rolagem */
        section[data-testid="stSidebar"] > div {
            height: 100vh;
            overflow: hidden !important;
            padding-top: 0 !important;
        }
        [data-testid="stSidebarHeader"] {
            display: none;
        }
        [data-testid="stSidebarUserContent"] {
            padding-top: 0.5rem !important;
            padding-bottom: 0 !important;
            height: 100vh;
            overflow: hidden !important;
        }
        section[data-testid="stSidebar"] *::-webkit-scrollbar { display: none; }
        section[data-testid="stSidebar"] * { scrollbar-width: none; }

        /* Marca */
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0 8px 16px 8px;
        }
        .sidebar-logo {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            background: rgba(95, 92, 229, 0.15);
            border: 1px solid rgba(95, 92, 229, 0.5);
            border-radius: 8px;
        }
        .sidebar-title {
            font-family: 'Inter', sans-serif;
            color: #F1F5F9;
            font-size: 14px;
            font-weight: 600;
        }

        /* Configurações no rodapé, alinhado com os itens do menu */
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
            gap: 2px !important;
        }

        /* Conteúdo */
        .main .block-container {
            padding: 2rem !important;
        }
        
        /* Ajustes sidebar para combinar com o cabeçalho */
        section[data-testid="stSidebar"] {
            width: 260px !important;
            min-width: 260px !important;
        }

        /* Esconde o header padrão do Streamlit */
        [data-testid="stHeader"] {
            display: none;
        }

        /* Alinha a marca da sidebar com a altura da barra (56px) */
        .sidebar-brand {
            height: 56px;
            padding: 0 8px;
            margin-bottom: 8px;
        }
        [data-testid="stSidebarUserContent"] {
            padding-top: 0 !important;
        }

        /* Abre espaço para a barra no conteúdo */
        .main .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-top: 5rem !important;
        }

        /*  TOPBAR  */
        .topbar {
            position: fixed;
            top: 0;
            left: 260px;
            right: 0;
            height: 56px;
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            background-color: #0B1220;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            font-family: 'Inter', sans-serif;
        }
        .topbar-left,
        .topbar-right {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .topbar-repo {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #CBD5E1;
            font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
            font-size: 12.5px;
            font-weight: 600;
        }
        .topbar-repo svg {
            color: #94A3B8;
        }
        .topbar-branch {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 3px 9px;
            color: #CBD5E1;
            font-family: ui-monospace, 'SFMono-Regular', Consolas, monospace;
            font-size: 12px;
            font-weight: 600;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 6px;
        }
        .topbar-branch svg {
            color: #7C79F2;
        }
        .topbar-status {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #94A3B8;
            font-size: 12px;
        }
        .topbar-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #22C55E;
            box-shadow: 0 0 6px rgba(34,197,94,0.7);
        }
        .topbar-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 600;
            background: linear-gradient(135deg, #5F5CE5, #8B5CF6);
            border: 1px solid rgba(255,255,255,0.15);
        }
        .topbar-avatar img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        /* Espaçamento entre itens */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 2px !important;
        }

        /* TODOS os botões da sidebar: mesmo estilo */
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
            width: 100% !important;
            min-height: 0 !important;
            padding: 8px 12px !important;
            background: transparent !important;
            background-color: transparent !important;
            color: #94A3B8 !important;
            border: none !important;
            outline: none !important;
            border-radius: 6px !important;
            box-shadow: none !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            font-weight: 400 !important;
            transition: background-color 0.2s ease, color 0.2s ease !important;
        }

    </style>
    """,
    unsafe_allow_html=True
)

ITENS_MENU = [
    ("Visão Geral",       ":material/grid_view:"),
    ("Heatmap de Risco",  ":material/water_drop:"),
    ("Análise Preditiva", ":material/show_chart:"),
]

def render_sidebar():

    def _ir_para(tela):
        st.session_state.tela_ativa = tela

    ativa = st.session_state.tela_ativa

    with st.sidebar:

        st.markdown(
            f"""
            <div class="sidebar-brand">
                <div class="sidebar-logo">
                    <img src="data:image/png;base64,{encoded_logo}">
                </div>
                <span class="sidebar-title">Git Foresight</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        for nome, icone in ITENS_MENU:
            st.button(
                nome,
                icon=icone,
                key=f"nav_{nome}",
                type="primary" if ativa == nome else "secondary",
                on_click=_ir_para,
                args=(nome,)
            )

        # Precisa ser o ÚLTIMO elemento dentro da sidebar
        st.button(
            "Configurações",
            icon=":material/settings:",
            key="nav_config",
            type="primary" if ativa == "Configurações" else "secondary",
            on_click=_ir_para,
            args=("Configurações",)
        )

    return st.session_state.tela_ativa

def render_overview(analysis, risk):

    render_metrics(
        analysis,
        risk
    )

def render_heatmap(analysis, risk):

    st.info(
        "O heatmap será conectado aos indicadores "
        "de risco dos módulos."
    )

def render_predictive_analysis(risk):

    st.title("Análise Preditiva")

    st.info(
        "A análise preditiva será implementada "
        "após a construção do histórico de risco."
    )

def render_settings():

    st.title("Configurações")

    st.info(
        "As configurações do GitForesight serão "
        "implementadas nesta seção."
    )

def render_topbar(ctx):

    repo = ctx["repo_ativo"]
    branch = ctx["branch"]
    last_scan = ctx["ultima_varredura"]
    user_name = ctx["usuario"]["nome"]
    avatar_url = ctx["usuario"]["avatar_url"]

    initials = "".join(p[0] for p in user_name.split()[:2]).upper()

    avatar = (
        f'<img src="{avatar_url}" alt="{user_name}">'
        if avatar_url else initials
    )

    html = f"""
    <div class="topbar">
        <div class="topbar-left">
            <div class="topbar-repo">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none"
                     stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                    <circle cx="4" cy="3.5" r="1.8"/>
                    <circle cx="12" cy="3.5" r="1.8"/>
                    <circle cx="8" cy="12.5" r="1.8"/>
                    <path d="M4 5.3v1.2c0 1 .8 1.5 1.8 1.5h4.4c1 0 1.8-.5 1.8-1.5V5.3M8 8v2.7"/>
                </svg>
                <span>{repo}</span>
                <svg width="10" height="10" viewBox="0 0 16 16" fill="none"
                     stroke="currentColor" stroke-width="2" stroke-linecap="round">
                    <path d="M4 6l4 4 4-4"/>
                </svg>
            </div>
            <div class="topbar-branch">
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none"
                     stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
                    <circle cx="4" cy="3.5" r="1.8"/>
                    <circle cx="4" cy="12.5" r="1.8"/>
                    <circle cx="12" cy="5.5" r="1.8"/>
                    <path d="M4 5.3v5.4M12 7.3c0 3-8 1.5-8 3.4"/>
                </svg>
                <span>{branch}</span>
            </div>
        </div>
        <div class="topbar-right">
            <div class="topbar-status">
                <span class="topbar-dot"></span>
                <span>Última varredura: {last_scan}</span>
            </div>
            <div class="topbar-avatar">{avatar}</div>
        </div>
    </div>
    """

    # Remove a indentação: o Markdown trata linhas com 4+ espaços como bloco de código
    html = " ".join(line.strip() for line in html.splitlines())

    st.markdown(html, unsafe_allow_html=True)

def get_context():
    repos = ["empresa/backend", "empresa/frontend"]

    repo_ativo = st.session_state.get("repo_ativo", repos[0])
    if repo_ativo not in repos:
        repo_ativo = repos[0]

    return {
        "repos": repos,
        "repo_ativo": repo_ativo,
        "branch": "main",
        "ultima_varredura": "Há 10 min",
        "usuario": {
            "nome": "Maria Silva",
            "avatar_url": None,
        },
    }
    """
    Para pegar informações do backend, será preciso: from backend.repos import list_repos, get_repo_info, get_current_user
    Depois montar o request
    Modifica o repositório utilizado: analysis, risk = load_data(ctx["repo_ativo"])
    E adaptar o load_data para filtrar por ele
    """
    

def main():

    ctx = get_context()

    analysis, risk = load_data()

    tela = render_sidebar()

    render_topbar(ctx)

    if tela == "Visão Geral":
        render_overview(analysis, risk)

    elif tela == "Heatmap de Risco":
        render_heatmap(analysis, risk)

    elif tela == "Análise Preditiva":
        render_predictive_analysis(risk)

    elif tela == "Configurações":
        render_settings()

if __name__ == "__main__":
    main()