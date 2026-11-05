from paths import DATA_DIR   # precisa vir antes dos imports de backend
import streamlit as st
import textwrap

from backend.app.heatmap_data import build_heatmap
from components.heatmap_panels import cabecalho_detalhes_html, detalhes_html, heatmap_html
from frontend.dashboard.views.predictive import card_header

def _historico():
    st.toast("O histórico completo ainda está em construção.")


def render_heatmap():
    analysis_dir = st.session_state.get("analysis_dir")

    data_dir = analysis_dir or DATA_DIR

    itens = build_heatmap(data_dir)
    itens = sorted(itens, key=lambda i: i["score"], reverse=True)
    por_path = {i["path"]: i for i in itens}
    paths = list(por_path)

    if paths and st.session_state.get("heat_sel") not in por_path:
        st.session_state["heat_sel"] = paths[0]       # abre no arquivo de maior risco
    selecionado = st.session_state.get("heat_sel")

    col_esq, col_dir = st.columns([20, 10], gap="small")

    with col_esq:
        with st.container(key="heat_card"):
            st.markdown(
                card_header(
                    "Atividade por módulo",
                    "Últimos 90 dias",
                    tip=textwrap.dedent("""\
                        **Como interpretar o Heatmap de Risco**
                        
                        O Heatmap classifica os arquivos de acordo com indicadores extraídos do histórico de alterações do repositório.
                        
                        📈 **Score de risco**
                        
                        Pontuação de 0 a 100 calculada a partir do volume de alterações, da frequência de commits, da quantidade de contribuidores e da sensibilidade do arquivo. Quanto maior o score, maior a prioridade sugerida para revisão.
                        
                        ⊸ **Commits**
                        
                        Quantidade de commits distintos em que o arquivo aparece no histórico analisado. Alterações frequentes podem indicar maior atividade ou necessidade de revisão.
                        
                        𖦥 **Linhas alteradas, inserções e exclusões**
                        
                        Indicam o volume de mudanças registrado para o arquivo. Mudanças maiores podem exigir mais atenção durante a revisão, mas não significam necessariamente que exista uma vulnerabilidade.
                        
                        👥 **Contribuidores**
                        
                        Número de pessoas distintas associadas às alterações do arquivo. Ajuda a compreender como o trabalho está distribuído, mas não mede diretamente a qualidade do código.
                        
                        🛡️ **Arquivo sensível**
                        
                        Indica que o arquivo foi classificado como relacionado à segurança, por exemplo, um .env. Essa classificação depende dos dados e das regras utilizadas pelo analisador.
                        
                        ⚠️ **Fatores de risco**
                        
                        Explicam os critérios específicos que foram acionados para um arquivo, como muitas alterações, frequência elevada ou sensibilidade. Nem todo componente do score necessariamente aparece nessa lista.
                        
                        Importante: o score é um indicador heurístico calculado a partir do histórico. Não representa a probabilidade estatística de uma vulnerabilidade nem confirma que um arquivo seja vulnerável.
                        """)
                ),
                unsafe_allow_html=True,
            )
            st.markdown(heatmap_html(itens, selecionado), unsafe_allow_html=True)

    with col_dir:
        with st.container(key="file_card"):
            st.markdown(cabecalho_detalhes_html(), unsafe_allow_html=True)
            if paths:
                st.selectbox("Arquivo", paths, key="heat_sel", label_visibility="collapsed",
                             format_func=lambda p: p.split("/")[-1])
                st.markdown(detalhes_html(por_path[selecionado]), unsafe_allow_html=True)
                st.button("Ver Histórico Completo", key="heat_hist", type="primary",
                          on_click=_historico)
            else:
                st.markdown('<div class="an-empty">Selecione um arquivo para ver os detalhes.</div>',
                            unsafe_allow_html=True)