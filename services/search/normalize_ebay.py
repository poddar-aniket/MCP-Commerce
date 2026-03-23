from pydantic import BaseModel

# Try to import MarketplaceResult, if not available, create a dummy one for type hinting or handle accordingly
try:
    from core.schemas.models import MarketplaceResult
except ModuleNotFoundError:
    class MarketplaceResult(BaseModel):
        platform: str
        title: str
        price: float
        currency: str
        url: str

def normalize_ebay_result(raw_data: dict) -> list[MarketplaceResult]:
    """
    Normalizes the raw response from eBay Browse API into a list of MarketplaceResult.
    """
    if not isinstance(raw_data, dict):
        return []

    item_summaries = raw_data.get("itemSummaries", [])
    if not isinstance(item_summaries, list):
        return []

    results = []
    for item in item_summaries:
        title = item.get("title")
        price_val = item.get("price", {}).get("value")
        url = item.get("itemWebUrl")

        if not title or not price_val or not url:
            continue
            
        try:
            price_float = float(price_val)
        except (ValueError, TypeError):
            continue

        result = MarketplaceResult(
            platform="eBay",
            title=str(title),
            price=price_float,
            currency="USD",
            url=str(url)
        )
        results.append(result)

    return results
