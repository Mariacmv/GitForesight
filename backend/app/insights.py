import pandas as pd

from backend.app.simulation import prepare, ORPHAN_THRESHOLD


# ---------- concentração de conhecimento (sem alterações) ----------

def knowledge_concentration(file_changes):
    df = prepare(file_changes)

    por_pessoa = df.groupby("person")["weight"].sum()
    principal = por_pessoa.idxmax()
    participacao = por_pessoa.max() / por_pessoa.sum()

    por_arquivo = df.pivot_table(
        index="path", columns="person", values="weight",
        aggfunc="sum", fill_value=0,
    )
    dominancia = por_arquivo.max(axis=1) / por_arquivo.sum(axis=1)

    return {
        "pessoa": principal,
        "participacao": float(participacao),
        "arquivos_dono_unico": int((dominancia >= ORPHAN_THRESHOLD).sum()),
        "arquivos_total": len(por_arquivo),
    }


# ---------- achados da primeira análise ----------

def _fmt(n):
    return f"{int(n):,}".replace(",", ".")


def _plural(n, singular, plural):
    return f"{_fmt(n)} {singular if n == 1 else plural}"


def _como_df(file_changes):
    """Aceita um DataFrame (CSV lido ou montado pelo pipeline) ou a lista bruta do collector."""
    if isinstance(file_changes, pd.DataFrame):
        return file_changes
    return pd.DataFrame(file_changes)


def count_contributors(file_changes):
    """Quantidade de pessoas distintas (autores unificados pelos ALIASES da simulação)."""
    df = prepare(_como_df(file_changes))
    return int(df["person"].nunique()) if not df.empty else 0


def partial_findings(file_changes, max_items=4):
    """Frases do bloco "Primeiros achados parciais".

    Aceita o DataFrame de alterações por arquivo ou a lista bruta do collector.
    """
    df = _como_df(file_changes)
    if df.empty:
        return []

    df = prepare(df)
    if df.empty:
        return []

    achados = []

    # 1 e 2: arquivos com mais linhas alteradas
    por_arquivo = (
        df.groupby("path")
        .agg(commits=("hash", "nunique"), linhas=("changes", "sum"))
        .sort_values(["linhas", "commits"], ascending=False)
    )
    for pos, (caminho, r) in enumerate(por_arquivo.head(2).iterrows()):
        inicio = (f"{caminho} é o arquivo com mais alterações"
                  if pos == 0 else f"{caminho} também se destaca")
        achados.append(
            f"{inicio}: {_plural(r['linhas'], 'linha alterada', 'linhas alteradas')} "
            f"em {_plural(r['commits'], 'commit', 'commits')}."
        )

    # 3: concentração das alterações entre as pessoas
    por_pessoa = df.groupby("person")["weight"].sum().sort_values(ascending=False)
    n = len(por_pessoa)
    if n == 1:
        achados.append(
            f"1 contribuidor identificado: {por_pessoa.index[0]} fez 100% das alterações."
        )
    elif n <= 3:
        achados.append(
            f"{n} contribuidores identificados, e {por_pessoa.index[0]} concentra "
            f"{por_pessoa.iloc[0] / por_pessoa.sum():.0%} das alterações."
        )
    else:
        top3 = por_pessoa.head(3).sum() / por_pessoa.sum()
        achados.append(
            f"{n} contribuidores identificados, com 3 deles concentrando "
            f"{top3:.0%} das alterações."
        )

    # 4: arquivos sensíveis (só aparece se existirem)
    sensiveis = df[df["is_security"].astype(str).str.lower() == "true"]
    if not sensiveis.empty:
        exemplo = sensiveis["path"].value_counts().index[0]
        achados.append(
            f"{_plural(sensiveis['path'].nunique(), 'arquivo sensível alterado', 'arquivos sensíveis alterados')}"
            f", como {exemplo}."
        )

    return achados[:max_items]