def sanitize_markdown(text: str) -> str:
    """
    Sanitizes a string for use in MarkdownV2.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
