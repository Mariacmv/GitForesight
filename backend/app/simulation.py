import pandas as pd


# E-mail -> pessoa. Adicione aqui quem aparecer com mais de um e-mail.
ALIASES = {
    "142021465+RafaPrattes@users.noreply.github.com": "Rafaela Prates",
    "142036250+lucianaliebl@users.noreply.github.com": "Luciana Liebl",
    "lucianaliebl@gmail.com": "Luciana Liebl",
    "143636716+Larissa-Kailane@users.noreply.github.com": "Larissa Kailane",
    "larissakailanelv@gmail.com": "Larissa Kailane",
}

# Pastas de configuração que não representam código do produto
IGNORED_MODULES = {".cursor", ".vscode", ".github", ".idea"}

ORPHAN_THRESHOLD = 0.80   # a partir de 80% das mudanças, não há segundo mantenedor

MIN_FILES_MODULE = 3

def prepare(file_changes):
    """Unifica autores, segue renomeações, remove pastas de editor e arquivos apagados."""
    df = file_changes.copy()
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.sort_values("date")

    # Segue renomeações: o histórico do nome antigo passa para o nome novo
    if "old_path" in df.columns:
        moves = df[(df["change_type"] == "R") & df["old_path"].notna()]
        rename_map = dict(zip(moves["old_path"], moves["path"]))

        def resolve(path):
            seen = set()
            while path in rename_map and path not in seen:
                seen.add(path)
                path = rename_map[path]
            return path

        df["path"] = df["path"].map(resolve)

    # Módulo recalculado a partir do caminho final
    df["module"] = df["path"].map(lambda p: p.split("/")[0] if "/" in p else "(raiz)")

    chave = df["email"] if "email" in df.columns else df["author"]
    df["person"] = chave.map(ALIASES).fillna(df["author"])

    df = df[~df["module"].isin(IGNORED_MODULES)]
    df["weight"] = df["changes"].clip(lower=1)

    # Descarta arquivos cuja última alteração foi a exclusão
    ultimo = df.groupby("path")["change_type"].last()
    existentes = ultimo[ultimo != "D"].index
    return df[df["path"].isin(existentes)]


def _level(knowledge_share, orphan_ratio, orphan_security):
    # Limites sugeridos: ajuste conforme o que sua equipe considerar crítico
    if orphan_security > 0 or knowledge_share >= 0.5:
        return "CRÍTICO"
    if knowledge_share >= 0.3 or orphan_ratio >= 0.3:
        return "ALTO"
    if knowledge_share >= 0.15 or orphan_ratio >= 0.1:
        return "MÉDIO"
    return "BAIXO"


def simulate_departure(df, person):
    """Cenário: 'e se <person> sair do projeto?'. Recebe o resultado de prepare()."""
    por_arquivo = df.pivot_table(
        index="path", columns="person", values="weight",
        aggfunc="sum", fill_value=0,
    )
    if person not in por_arquivo.columns:
        raise ValueError(f"Pessoa não encontrada: {person}")

    total = por_arquivo.sum(axis=1)
    share = por_arquivo[person] / total

    afetados = share[share > 0].index
    orfaos = share[share >= ORPHAN_THRESHOLD].index

    meta = df.drop_duplicates("path", keep="last").set_index("path")[["module", "is_security"]]
    meta_afet = meta.loc[afetados]
    meta_orf = meta.loc[orfaos]

    # Módulos críticos: têm arquivo de segurança órfão, ou metade dos arquivos órfãos
    arquivos_por_modulo = meta["module"].value_counts()
    orfaos_por_modulo = meta_orf["module"].value_counts()
    criticos = [
        m for m, n in orfaos_por_modulo.items()
        if n / arquivos_por_modulo[m] >= 0.5
        or meta_orf[(meta_orf["module"] == m)]["is_security"].any()
    ]

    criticos = [
        m for m, n in orfaos_por_modulo.items()
        if arquivos_por_modulo[m] >= MIN_FILES_MODULE
        and n / arquivos_por_modulo[m] >= 0.5
        or meta_orf[meta_orf["module"] == m]["is_security"].any()
    ]

    knowledge_share = float(por_arquivo[person].sum() / total.sum())
    orphan_ratio = len(orfaos) / len(meta)
    orphan_security = int(meta_orf["is_security"].sum())

    sec_modulos = meta_orf[meta_orf["is_security"]]["module"]
    if len(sec_modulos):
        principal = sec_modulos.value_counts().idxmax()
    elif len(orfaos_por_modulo):
        principal = orfaos_por_modulo.idxmax()
    else:
        principal = None

    return {
        "pessoa": person,
        "participacao_no_codigo": round(knowledge_share, 3),
        "arquivos_afetados": len(afetados),
        "arquivos_sem_segundo_mantenedor": len(orfaos),
        "arquivos_seguranca_orfaos": orphan_security,
        "modulos_afetados": sorted(meta_afet["module"].unique()),
        "modulos_criticos": sorted(criticos),
        "principal_area": principal,
        "risco": _level(knowledge_share, orphan_ratio, orphan_security),
        "lista_orfaos": sorted(orfaos),
    }


def simulate_all(df):
    """Compara o cenário de saída de cada pessoa (base para a comparação de cenários)."""
    resultados = [simulate_departure(df, p) for p in df["person"].unique()]
    return pd.DataFrame(resultados).drop(columns="lista_orfaos")

