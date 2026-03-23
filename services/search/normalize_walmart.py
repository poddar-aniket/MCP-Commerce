from pydantic import BaseModel

try:
    from core.schemas.models import MarketplaceResult
except ModuleNotFoundError:
    class MarketplaceResult(BaseModel):
        platform: str
        title: str
        price: float
        currency: str
        url: str

def normalize_walmart_result(raw_data: dict) -> list:
    """
    Normalizes the raw response from Walmart API into a list of MarketplaceResult.
    Handles data from various RapidAPI Walmart wrappers nesting.
    """
    if not isinstance(raw_data, dict):
        return []

    # RapidAPI Walmart wrappers return data in various nested structures
    items = raw_data.get("item", [])
    
    # Handle Axesso deeply nested pageProps structure
    if isinstance(items, dict):
        try:
            item_stacks = items.get("props", {}).get("pageProps", {}).get("initialData", {}).get("searchResult", {}).get("itemStacks", [])
            if item_stacks and isinstance(item_stacks, list):
                items = item_stacks[0].get("items", [])
        except Exception:
            pass

    if not items or not isinstance(items, list):
        items = raw_data.get("data", {}).get("items", [])
        
    if not isinstance(items, list):
        return []

    results = []
    for item in items:
        # Title extraction: look for "name", "title", or "productName"
        title = item.get("name") or item.get("title") or item.get("productName")
        
        # Price extraction: look for "price", "salePrice", or "offerPrice"
        price_raw = item.get("price") or item.get("salePrice") or item.get("offerPrice")
        
        # URL extraction: look for "productUrl" or "url" or construct fallback
        url = item.get("productUrl") or item.get("url")
        item_id = item.get("itemId") or item.get("id")
        
        if not url and item_id:
            url = f"https://www.walmart.com/ip/{item_id}"

        if not title or price_raw is None or not url:
            continue
            
        # Strip "$" signs and commas before casting to float
        try:
            if isinstance(price_raw, str):
                cleaned_price = price_raw.replace("$", "").replace(",", "").strip()
                price_float = float(cleaned_price)
            else:
                price_float = float(price_raw)
        except (ValueError, TypeError):
            continue

        result = MarketplaceResult(
            platform="Walmart",
            title=str(title),
            price=price_float,
            currency="USD",
            url=str(url)
        )
        results.append(result)

    return results
