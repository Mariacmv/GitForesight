from pathlib import Path

import pandas as pd


# Diretório raiz do projeto GitForesight
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Pasta onde o backend salva os dados
DATA_DIR = BASE_DIR / "data"


def load_data():

    analysis_path = DATA_DIR / "analysis.csv"
    risk_path = DATA_DIR / "risk.csv"

    analysis = pd.read_csv(analysis_path)
    risk = pd.read_csv(risk_path)

    return analysis, risk