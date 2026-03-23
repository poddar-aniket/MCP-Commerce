from clients.amazon_client import AmazonClient
from services.search.normalize import normalize_product


def search_amazon(product: dict) -> list[dict]:
    """
    MCP Tool: Search Amazon marketplace.
    Amazon-specific field mapping happens here.
    """

    query = product.get("query") or product.get("raw_query")
    if not query or not isinstance(query, str):
        return []

    try:
        client = AmazonClient()
        raw_data = client.search(product.get("query"))
        print(f"\n[DEBUG] RAW AMAZON API JSON: {raw_data}\n")

        data = raw_data.get("data", {})
        items = data.get("products", [])

        if not isinstance(items, list):
            return []

        results = []

        for item in items[:5]:
            normalized = normalize_product(
                platform="Amazon",
                title=item.get("product_title"),
                price=item.get("product_price"),
                rating=item.get("product_star_rating"),
                reviews_count=item.get("product_num_ratings"),
                url=item.get("product_url"),
            )

            if normalized:
                results.append(normalized)

        return results

    except Exception as e:
        print(f"\n🚨 AMAZON ERROR: {str(e)}\n")
        return []
