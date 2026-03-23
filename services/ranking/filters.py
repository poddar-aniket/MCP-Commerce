def filter_by_max_price(products: list[dict], max_price: int) -> list[dict]:
    """
    Return products priced <= max_price.
    Safe, deterministic, and side-effect free.
    """
    filtered = []

    for product in products:
        price = product.get("price")

        if isinstance(price, (int, float)) and price <= max_price:
            filtered.append(product)

    return filtered

def filter_cheaper_than(products: list[dict], reference_price: int) -> list[dict]:
    """
    Return products priced strictly less than the reference price.
    """
    filtered = []

    for product in products:
        price = product.get("price")

        if isinstance(price, (int, float)) and price < reference_price:
            filtered.append(product)

    return filtered
