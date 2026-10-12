from backend.app.simulation import prepare, ORPHAN_THRESHOLD


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