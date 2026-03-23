from core.mcp_server.tools.generate_query import generate_query_from_text
from core.mcp_server.tools.find_similar import find_similar_products
from services.search.amazon import search_amazon
from services.search.ebay import search_ebay
from services.search.walmart import search_walmart
from services.ranking.final import rank_results
from core.mcp_server.registry.tool_metadata import TOOL_METADATA


TOOLS = {
    "generate_query": generate_query_from_text,
    "search_amazon": search_amazon,
    "search_ebay": search_ebay,
    "search_walmart": search_walmart,
    "rank_results": rank_results,
    "find_similar_products": find_similar_products,
}


def list_tools():
    """
    Returns tool metadata for planners / inspection.
    """
    return TOOL_METADATA
