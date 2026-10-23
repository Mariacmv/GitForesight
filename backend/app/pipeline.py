"""
Pipeline da primeira análise: clona o repositório e roda
coleta -> dataset -> análise semanal -> risco -> hotspots.

Executa as etapas e informa o progresso

Fluxo de análise:
Usuário escolhe main, por exemplo.
A view envia "main" ao pipeline.
O pipeline clona o repositório selecionando essa branch.
O collector percorre o histórico da HEAD desse clone.
"""
import os
import shutil
import stat
import tempfile
from contextlib import contextmanager
from pathlib import Path

import pandas as pd
from git import Repo
from git.exc import GitCommandError

from backend.app.analysis_state import AnalysisTracker
from backend.app.analyzer import analyze_commits
from backend.app.collector import collect_commits
from backend.app.dataset import create_dataset
from backend.app.insights import (
    count_contributors,
    knowledge_concentration,
    partial_findings,
)
from backend.app.risk import calculate_risk


def _auth_url(url, token):
    if token and url.startswith("https://"):
        return url.replace("https://", f"https://x-access-token:{token}@", 1)
    return url


def _force_remove(func, path, _exc):
    # No Windows, os arquivos do .git são somente leitura e o rmtree falha
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _cleanup(path):
    try:
        shutil.rmtree(path, onexc=_force_remove)      # Python 3.12+
    except TypeError:
        shutil.rmtree(path, onerror=_force_remove)    # versões anteriores


@contextmanager
def _etapa(tracker, indice, push):
    """Marca a etapa como em execução e, se terminar sem erro, como concluída."""
    tracker.iniciar(indice)
    push()
    yield
    tracker.concluir(indice)
    push()


def run_pipeline(url, branch, data_dir, token=None, total_commits=0, on_update=None):
    tracker = AnalysisTracker(total_commits)

    def push():
        if on_update:
            on_update(tracker.snapshot())

    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    commits_csv = str(data_dir / "commits.csv")
    files_csv = str(data_dir / "file_changes.csv")
    analysis_csv = str(data_dir / "analysis.csv")
    risk_csv = str(data_dir / "risk.csv")

    tmp = Path(tempfile.mkdtemp(prefix="gitforesight_"))
    try:
        with _etapa(tracker, 0, push):                                    # clonar
            try:
                Repo.clone_from(_auth_url(url, token), str(tmp / "repo"), branch=branch) #recebe a branch
            except GitCommandError:
                # Não repassa a mensagem original: ela pode conter o token na URL
                raise ValueError(
                    "Não foi possível clonar o repositório. Verifique se a branch "
                    "existe e se você tem acesso a ele."
                ) from None

        with _etapa(tracker, 1, push):                                    # coletar
            def on_progress(feitos, total):
                tracker.total = total
                tracker.avancar(feitos / total if total else 1.0, feitos=feitos)
                push()

            commits, file_changes = collect_commits(
                tmp / "repo", on_progress=on_progress
            )

        with _etapa(tracker, 2, push):                                    # dataset
            create_dataset(commits, file_changes,
                           output_path=commits_csv, file_changes_path=files_csv)
            files_df = pd.DataFrame(file_changes)
            if not files_df.empty:
                tracker.contribuidores = count_contributors(files_df)
                tracker.achados = partial_findings(files_df)

        with _etapa(tracker, 3, push):                                    # contribuidores
            analyze_commits(commits_csv, analysis_csv)

        with _etapa(tracker, 4, push):                                    # risco
            calculate_risk(analysis_csv, risk_csv)

        with _etapa(tracker, 5, push):                                    # hotspots
            concentracao = None if files_df.empty else knowledge_concentration(files_df)

        return {"commits": len(commits), "concentracao": concentracao}
    finally:
        _cleanup(tmp)