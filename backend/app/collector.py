from pathlib import Path

from git import Repo

SENSITIVE_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "settings.py",
    "config.py",
    "security.py",
    "auth.py",
    "authentication.py",
    "authorization.py",
    "permissions.py",
}

SENSITIVE_DIRECTORIES = {
    "auth",
    "authentication",
    "authorization",
    "security",
    "secrets",
    "credentials",
    "config",
}

SENSITIVE_EXTENSIONS = {
    ".pem",
    ".key",
    ".crt",
    ".p12",
    ".pfx",
    ".conf",
    ".cfg",
}


def _is_sensitive(file_path):
    """
        Confere se o arquivo está na lista de arquivos sensíveis
    """
    
    path = Path(file_path)
    file_name = path.name.lower()
    extension = path.suffix.lower()
    path_parts = {part.lower() for part in path.parts}

    return (
        file_name in SENSITIVE_FILE_NAMES
        or extension in SENSITIVE_EXTENSIONS
        or bool(path_parts & SENSITIVE_DIRECTORIES)
    )


def collect_commits(repository_path):
    repository = Repo(repository_path)

    commits = []
    file_changes = []

    for commit in repository.iter_commits(): #confere cada commit realizado
        files_changed = []
        security_files_changed = 0

        insertions = 0
        deletions = 0

        if commit.parents: #compara o commit atual com o commit pai
            parent = commit.parents[0]
            diff = parent.diff(commit, create_patch=True)

            for item in diff:
                file_path = item.b_path or item.a_path

                if not file_path:
                    continue
                # MUDEI AQUI
                change_type = (
                    "A" if item.new_file else #added
                    "D" if item.deleted_file else #deleted
                    "R" if item.renamed_file else #renamed
                    "M" #modified
                )
                old_path = item.rename_from if item.renamed_file else ""
                # ATÉ AQUI

                files_changed.append(file_path) #pega os arquivos identificados que sofreram alterações

                is_sensitive = _is_sensitive(file_path) #verifica se são sensíveis
                if is_sensitive:
                    security_files_changed += 1

                file_ins = 0
                file_del = 0

                try:
                    patch = item.diff.decode("utf-8", errors="ignore")

                    for line in patch.splitlines():
                        if line.startswith("+") and not line.startswith("+++"):
                            file_ins += 1
                        elif line.startswith("-") and not line.startswith("---"):
                            file_del += 1

                except Exception:
                    pass

                insertions += file_ins
                deletions += file_del

                file_changes.append({
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "date": commit.committed_datetime,
                    "path": file_path,
                    "module": Path(file_path).parts[0] if len(Path(file_path).parts) > 1 else "(raiz)",
                    "change_type": change_type, # mudei aqui
                    "old_path": old_path, # mudei aqui
                    "insertions": file_ins,
                    "deletions": file_del,
                    "changes": file_ins + file_del,
                    "is_security": is_sensitive,
                    "email": commit.author.email,
                })

        commits.append({
            "hash": commit.hexsha,
            "author": commit.author.name,
            "date": commit.committed_datetime,
            "message": commit.message.strip(),
            "files_changed": files_changed,
            "files_count": len(files_changed),
            "security_files_changed": security_files_changed,
            "insertions": insertions,
            "deletions": deletions,
            "changes": insertions + deletions,
            "email": commit.author.email,
        })

    return commits, file_changes