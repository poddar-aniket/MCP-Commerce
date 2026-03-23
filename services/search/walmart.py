from pydantic import BaseModel
from clients.walmart_client import WalmartClient
from services.search.normalize_walmart import normalize_walmart_result

try:
    from core.schemas.models import MarketplaceResult
except ModuleNotFoundError:
    pass

def search_walmart(product: dict | BaseModel) -> list:
    """
    MCP Tool: Search Walmart marketplace via RapidAPI wrapper.
    """
    try:
        if isinstance(product, BaseModel):
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

        client = WalmartClient()
        response = client.search(query)
        
        results = normalize_walmart_result(response)
        return results

    except Exception:
        return []
