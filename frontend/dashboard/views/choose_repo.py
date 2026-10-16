import streamlit as st
from frontend.dashboard.components.cards import _html
from components.topbar import render_auth_topbar, render_auth_footer
from views.auth import restaurar_sessao, direcionar_usuario

def render():
    st.set_page_config(layout="wide")
    render_auth_topbar()

    # 1. Inicializa o estado do passo
    if "passo" not in st.session_state:
        st.session_state.passo = 1

    TOTAL_PASSOS = 3
    
    # Como passar o CSS do main.css para este arquivo de forma limpa:
    try:
        with open("main.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback caso mude o arquivo de lugar (mantém seu CSS antigo aqui por segurança)
        pass
    
    p = st.session_state.passo

    # 2. Renderização do Stepper
    html_stepper = f"""
        <div class="stepper-wrapper">
            <div class="steps-container">
                <div class="step-item {'active' if p >= 1 else 'inactive'}">
                    <div class="step-circle">1</div>
                    <div class="step-text">Escolher repositório</div>
                </div>
                <div class="step-item {'active' if p >= 2 else 'inactive'}">
                    <div class="step-circle">2</div>
                    <div class="step-text">Escolher branch</div>
                </div>
                <div class="step-item {'active' if p >= 3 else 'inactive'}">
                    <div class="step-circle">3</div>
                    <div class="step-text">Explorar resultados</div>
                </div>
            </div>
            <div class="step-counter">
                ETAPA {p} DE {TOTAL_PASSOS}
            </div>
        </div>
        """
    st.markdown(html_stepper, unsafe_allow_html=True)

    # 3. Controle de Telas (Movido o formulário para DENTRO do condicional do Passo 1)
    if st.session_state.passo == 1:
        st.title("Boas-vindas ao GitForesight.")
        st.caption("Qual repositório vamos analisar primeiro?")

        # O formulário agora só existe enquanto o usuário estiver no passo 1
        with st.form("repo_form"):
            novo_repo = st.text_input(
                "URL do repositório",
                placeholder="https://github.com/usuario/repositorio"
            )

            # Para deixar 100% de largura, usamos use_container_width=True
            enviar = st.form_submit_button( 
                "Conectar",
                key="envio_repo",
                type="primary",
                use_container_width=True 
            )

        if enviar:
            if not novo_repo.strip():
                st.error("Informe um repositório.")
                return

            # Guarda os dados na sessão
            st.session_state.repositorio_conectado = novo_repo.strip()
            
            # FAZ A TRANSIÇÃO: Muda para o Passo 2 e atualiza a interface
            st.session_state.passo = 2
            st.rerun()

    elif st.session_state.passo == 2:
        st.subheader("Escolher branch")
        st.info("Selecione a branch desejada para a análise.")
        
        st.markdown(_html(f"""
                <div class="panel-card">
                    criar o painel aqui
                </div>
        """), unsafe_allow_html=True)
        
        # Exemplo de botão para ir para o passo 3 (fora de formulário)
        if st.button("Avançar para Análise", type="primary", use_container_width=True):
            st.session_state.passo = 3
            st.rerun()

    elif st.session_state.passo == 3:
        st.subheader("Exploração de Resultados Finais")
        st.success("Tudo pronto! Visualize seus gráficos e relatórios gerados aqui.")
        
        # Botão opcional para reiniciar o fluxo
        if st.button("Analisar outro repositório", use_container_width=True):
            st.session_state.passo = 1
            st.rerun()

    render_auth_footer()