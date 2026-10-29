from html import escape


def info_tip(text: str, side: str = "right") -> str:
    """Retorna o HTML do ícone (?) com balão. side: 'right' ou 'left'."""
    return (
        f'<span class="gf-tip gf-tip--{side}" tabindex="0" aria-label="Ajuda">'
        f'<span class="gf-tip-icon">?</span>'
        f'<span class="gf-tip-bubble" role="tooltip">{escape(text)}</span>'
        f"</span>"
    )