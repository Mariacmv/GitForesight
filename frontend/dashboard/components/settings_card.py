from html import escape
import streamlit as st
from components.cards import html_inline

def render_plano_card(ao_gerenciar):
    """
    Renderiza o card de plano idêntico à referência visual enviada.
    """
    with st.container(key="plano_card"):
        st.markdown(html_inline("""
            <div class="plano-container-vertical">
                <div class="plano-titulo-principal">Plano</div>
                <div class="plano-descricao-topo">Consulte ou altere o plano escolhido para sua conta.</div>
                
                <div class="plano-secao-atual">
                    <div class="plano-label-atual">Plano atual</div>
                    <div class="plano-texto-comercial">Acesse as opções comerciais disponíveis para sua conta.</div>
                </div>
            </div>
        """), unsafe_allow_html=True)

        # Botão nativo do Streamlit estruturado para o design da imagem
        st.button(
            "Gerenciar plano", 
            key="plano_gerenciar_btn",
            on_click=ao_gerenciar
        )

        st.markdown(html_inline("""
            <div class="plano-rodape-nota">
                Revise a proposta comercial e ajuste a escolha do plano quando necessário.
            </div>
        """), unsafe_allow_html=True)
