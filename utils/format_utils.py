# Utility functions for formatting values


def format_currency(value):
    """Return value formatted as Paraguayan Guaraní currency.

    Examples
    --------
    >>> format_currency(1234)
    'Gs 1.234'
    """
    formatted = f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"Gs {formatted}"
