import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def render_risk_chart(risk):

    data = risk.copy()  # copia os dados

    data["week"] = pd.to_datetime(
        data["week"]
    )

    fig, ax = plt.subplots(
        figsize=(10, 4)
    )

    # plotagem dos dados principais
    ax.plot(
        data["week"],
        data["risk_score"],
        marker="o",
        color="#1f77b4",  # Força uma cor azul sólida na linha
        zorder=5          # Garante que a linha fique por CIMA de qualquer elemento de fundo
    )

    ax.set_title(
        "Evolução do Score de Risco"
    )

    ax.set_xlabel("Semana")
    ax.set_ylabel("Score de risco")

    ax.set_ylim(0, 100)

    valores_linhas = [20, 40, 60, 80]  # Define em quais alturas do gráfico as linhas devem aparecer
    for valor in valores_linhas:
        ax.axhline(
            y=valor, 
            color="#888888",   # Um cinza médio visível tanto em temas claros quanto escuros
            linestyle="--",    # Estilo tracejado
            linewidth=0.8,     # Espessura da linha
            alpha=0.4,         # Opacidade ideal
            zorder=1           # Desenha no fundo, atrás do gráfico de linhas azul
        )

    # Configura os marcadores de texto do eixo Y para bater com as linhas criadas
    ax.set_yticks([0, 20, 40, 60, 80, 100])

    fig.tight_layout()

    st.pyplot(fig)
