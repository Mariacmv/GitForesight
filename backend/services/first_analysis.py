#o backend não importa streamlit !!!!!!!!!!!!!!!!!!!!!!!!!! REGRA NA HORA DE REESTRUTURAR
#Ele recebe tudo por parâmetro e avisa a tela por um callback. Assim ele pode ser testado sem abrir o app.

"""Orquestra a primeira análise e controla o estado do progresso.

Não importa Streamlit: recebe tudo por parâmetro e avisa a tela por callback.
"""
from dataclasses import dataclass, field
from typing import Callable, Optional

from backend.app.pipeline import STAGES, run_pipeline

ETAPAS = STAGES

# Quanto cada etapa pesa na barra (soma 100); a coleta é a mais demorada
PESOS = {"clone": 10, "collect": 60, "dataset": 10, "analyze": 8, "risk": 7, "hotspots": 5}


class AnalysisError(Exception):
    """Falha na análise, com mensagem pronta para mostrar ao usuário."""


@dataclass
class ProgressState:
    concluidas: set = field(default_factory=set)
    atual: int = 0
    frac: float = 0.0                       # fração da etapa atual (0 a 1)
    commits_feitos: int = 0
    commits_total: Optional[int] = None     # None = ainda não começou a contar
    achados: list = field(default_factory=list)

    @property
    def pct(self) -> int:
        pct = sum(PESOS[ETAPAS[i]] for i in self.concluidas)
        if self.atual not in self.concluidas:
            pct += PESOS[ETAPAS[self.atual]] * self.frac
        return int(pct)


def executar_analise(url, branch, data_dir, token,
                     ao_atualizar: Callable[[ProgressState], None]):
    """Roda o pipeline e chama ao_atualizar(estado) a cada mudança.

    Retorna o resultado do pipeline. Em caso de falha, levanta AnalysisError.
    """
    estado = ProgressState()

    def on_stage(i, status):
        if status == "start":
            estado.atual, estado.frac = i, 0.0
        else:
            estado.concluidas.add(i)
        ao_atualizar(estado)

    def on_progress(feito, total):
        estado.commits_feitos, estado.commits_total = feito, total
        estado.frac = feito / total if total else 1.0
        ao_atualizar(estado)

    def on_findings(achados):
        estado.achados = achados
        ao_atualizar(estado)

    ao_atualizar(estado)
    try:
        return run_pipeline(
            url, branch, data_dir, token=token,
            on_stage=on_stage, on_progress=on_progress, on_findings=on_findings,
        )
    except ValueError as e:
        raise AnalysisError(str(e)) from e
    except Exception as e:
        raise AnalysisError(
            f"Não foi possível concluir a análise: "
            f"{type(e).__name__}: {e}"
        ) from e