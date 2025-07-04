import re


def sanitize_text_in(text: str) -> str:
    """
    Sanitiza o texto de entrada para garantir que ele esteja em
    um formato adequado para armazenamento ou processamento. Esta função remove
    caracteres indesejados, converte o texto para minúsculas,
    remove espaços extras e formata o texto.

    Args:
        text (str): O texto a ser sanitizado.
    Returns:
        str: O texto sanitizado.
    """
    sanitized = text.lower()
    sanitized = sanitized.strip()
    sanitized = re.sub(r'[?!]', '', sanitized)
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized


def sanitize_text_out(text: str) -> str:
    """
    Sanitiza o texto de saída para garantir que ele esteja em
    um formato adequado para exibição. Esta função remove caracteres
    indesejados, converte o texto para title, remove espaços extras
    e formata o texto.

    Args:
        text (str): O texto a ser sanitizado.

    Returns:
        str: O texto sanitizado.
    """
    sanitized = text.strip()
    sanitized = re.sub(r'\s+', ' ', sanitized)
    sanitized = sanitized.title()
    return sanitized
