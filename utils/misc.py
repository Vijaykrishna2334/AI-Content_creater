def ensure_list(x):
    """Return x as a list. If x is None, return empty list. If x is already a list, return it."""
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]
