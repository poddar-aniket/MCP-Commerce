def deduplicate_products(products: list[dict]) -> list[dict]:
    """
    Deduplicate products by (platform, title), preserving order.
    """
    seen = set()
    unique = []

    for p in products:
        key = (p.get("platform"), p.get("title"))
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique
    