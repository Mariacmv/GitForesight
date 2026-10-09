import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def render_risk_chart(risk):

    data = risk.copy()

    data["week"] = pd.to_datetime(
        data["week"]
    )

    fig, ax = plt.subplots(
        figsize=(10, 4)
    )

    ax.plot(
        data["week"],
        data["risk_score"],
        marker="o"
    )

    ax.set_title(
        "Evolução do Score de Risco"
    )

    ax.set_xlabel("Semana")
    ax.set_ylabel("Score de risco")

    ax.set_ylim(0, 100)

    ax.grid(
        alpha=0.2
    )

    fig.tight_layout()

    st.pyplot(fig)