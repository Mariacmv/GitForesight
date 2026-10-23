"""
Estado da primeira análise.

Reúne tudo que NÃO é visual: as etapas, os pesos, o cálculo da porcentagem e o
"retrato" (Snapshot) do andamento que a tela desenha. Não importa o Streamlit,
então dá para testar no terminal.

Quem produz Snapshots: o pipeline real (backend/app/pipeline.py) e a prévia
com dados falsos (preview_etapa2.py). Quem consome: a tela
(frontend/dashboard/views/first_analysis.py).
"""
from dataclasses import dataclass, field

# A ordem das etapas é a mesma em que o pipeline as executa.
ETAPAS = [
    {"peso": 10, "futuro": "Clonar o repositório",
     "andamento": "Clonando o repositório...", "concluido": "Repositório clonado"},
    {"peso": 45, "futuro": "Indexar histórico de commits",
     "andamento": "Indexando histórico de commits...",
     "concluido": "Indexação do histórico de commits concluída"},
    {"peso": 10, "futuro": "Gerar a base de dados",
     "andamento": "Gerando a base de dados...", "concluido": "Base de dados gerada"},
    {"peso": 15, "futuro": "Mapear contribuidores",
     "andamento": "Mapeando contribuidores...",
     "concluido": "Mapeamento de contribuidores concluído"},
    {"peso": 10, "futuro": "Calcular o risco por semana",
     "andamento": "Calculando o risco por semana...", "concluido": "Cálculo de risco concluído"},
    {"peso": 10, "futuro": "Identificar hotspots e módulos críticos",
     "andamento": "Identificando hotspots e módulos críticos...",
     "concluido": "Hotspots e módulos críticos identificados"},
]  # os pesos somam 100; a indexação dos commits é a etapa mais demorada

TEXTO_PRONTA = "Nenhum commit processado · nenhum resultado disponível"
TEXTO_PREPARANDO = "Preparando o clone do repositório..."


# ---------- formatação ----------

def fmt_num(n):
    return f"{int(n):,}".replace(",", ".")


def plural(n, singular, plural_):
    return f"{fmt_num(n)} {singular if n == 1 else plural_}"


def texto_progresso(feitos, total, contribuidores=0):
    """Ex.: '1.257 de 1.847 commits processados · 12 contribuidores identificados'."""
    if total and total > 0:
        texto = f"{fmt_num(feitos)} de {fmt_num(total)} commits processados"
    else:
        texto = f"{fmt_num(feitos)} commits processados"

    if contribuidores:
        texto += " · " + plural(
            contribuidores, "contribuidor identificado", "contribuidores identificados"
        )
    return texto


# ---------- porcentagem ----------

def calcular_pct(concluidas, atual, fracao=0.0):
    """Etapas concluídas somam o peso inteiro; a etapa atual soma o peso x fração feita."""
    pct = sum(ETAPAS[i]["peso"] for i in concluidas)
    if atual not in concluidas and 0 <= atual < len(ETAPAS):
        pct += ETAPAS[atual]["peso"] * max(0.0, min(1.0, fracao))
    return int(min(100, pct))


# ---------- o retrato que a tela desenha ----------

@dataclass
class Snapshot:
    modo: str = "pronta"                       # "pronta", "andamento" ou "concluida"
    concluidas: set = field(default_factory=set)
    atual: int = 0                             # índice da etapa em execução
    pct: int = 0
    mono: str = TEXTO_PRONTA                   # linha pequena abaixo da barra
    achados: list = field(default_factory=list)


def snapshot_pronta():
    return Snapshot()


class AnalysisTracker:
    """Acompanha a análise e gera Snapshots. Usado pelo pipeline e pela prévia."""

    def __init__(self, total_commits=0, contribuidores=0):
        self.total = total_commits
        self.contribuidores = contribuidores
        self.concluidas = set()
        self.atual = 0
        self.fracao = 0.0
        self.feitos = 0
        self.achados = []

    def iniciar(self, i):
        self.atual = i
        self.fracao = 0.0

    def avancar(self, fracao, feitos=None):
        self.fracao = fracao
        if feitos is not None:
            self.feitos = feitos

    def concluir(self, i):
        self.concluidas.add(i)
        self.fracao = 1.0
        if len(self.concluidas) == len(ETAPAS):
            self.feitos = self.total

    @property
    def terminou(self):
        return len(self.concluidas) == len(ETAPAS)

    def snapshot(self):
        if self.feitos > 0:
            mono = texto_progresso(self.feitos, self.total, self.contribuidores)
        else:
            mono = TEXTO_PREPARANDO

        return Snapshot(
            modo="concluida" if self.terminou else "andamento",
            concluidas=set(self.concluidas),
            atual=self.atual,
            pct=calcular_pct(self.concluidas, self.atual, self.fracao),
            mono=mono,
            achados=list(self.achados),
        )