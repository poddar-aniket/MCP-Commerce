TOOL_METADATA = {
    "generate_query": {
        "description": "Normalize user text into a structured product query",
        "input": "string (user text)",
        "output": "ProductQuery (schemas/product.json)"
    },
    "search_amazon": {
        "description": "Search Amazon marketplace for a product",
        "input": "ProductQuery",
        "output": "List[MarketplaceResult]"
    },
    "search_ebay": {
        "description": "Search eBay marketplace for a product",
        "input": "ProductQuery",
        "output": "List[MarketplaceResult]"
    },
    "search_walmart": {
        "description": "Search Walmart marketplace for a product",
        "input": "ProductQuery",
        "output": "List[MarketplaceResult]"
    },
    "rank_results": {
        "description": "Rank marketplace results by price and rating",
        "input": "List[MarketplaceResult]",
        "output": "List[RankedMarketplaceResult]"
    },
    "find_similar_products": {
        "description": "Find semantically similar products using vector embeddings",
        "input": "string (similarity query)",
        "output": "List[MarketplaceResult]"
    }

}
