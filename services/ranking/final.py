def rank_results(results: list) -> list:
    """
    Rank marketplace results by:
    1. Lower price
    2. Higher rating (tie-breaker)
    """

    if not results:
        return []

    parsed_results = []
    for x in results:
        if hasattr(x, "model_dump"):
            parsed_results.append(x.model_dump())
        elif hasattr(x, "dict"):
            parsed_results.append(x.dict())
        else:
            parsed_results.append(dict(x) if hasattr(x, "__iter__") else x)

    ranked = sorted(
        parsed_results,
        key=lambda x: (
            x.get("price", float('inf')),
            -(x.get("rating") or 0)
        )
    )

    for index, item in enumerate(ranked, start=1):
        if isinstance(item, dict):
            item["rank"] = index

    return ranked
