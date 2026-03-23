from typing import Optional


def resolve_reference_price(
    retriever,
    reference_text: str,
) -> Optional[int]:
    """
    Resolve the price of a reference product using RAG memory.
    Returns the price of the closest matching product.
    """

    if not reference_text:
        return None

    # Use existing similarity search
    results = retriever.find_similar(reference_text)

    if not results:
        return None

    # Take the top match as reference
    price = results[0].get("price")

    if isinstance(price, (int, float)):
        return int(price)

    return None
