from pydantic import BaseModel
from clients.ebay_client import EbayClient
from services.search.normalize_ebay import normalize_ebay_result

try:
    from core.schemas.models import MarketplaceResult
except ModuleNotFoundError:
    # Fallback if models.py is not available in the environment
    pass

def search_ebay(product: dict | BaseModel) -> list:
    """
    MCP Tool: Search eBay marketplace.
    """
    try:
        if isinstance(product, BaseModel):
            # Try to get as dict if it's a Pydantic model (v1 or v2)
            if hasattr(product, "model_dump"):
                product_data = product.model_dump()
            elif hasattr(product, "dict"):
                product_data = product.dict()
            else:
                product_data = dict(product)
        elif isinstance(product, dict):
            product_data = product
        else:
            return []

        query = product_data.get("query") or product_data.get("raw_query")
        
        if not query or not isinstance(query, str):
            return []

        client = EbayClient()
        response = client.search(query)
        
        results = normalize_ebay_result(response)
        return results

    except Exception:
        return []
