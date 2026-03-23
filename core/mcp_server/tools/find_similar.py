def find_similar_products(retriever, query: str, k: int = 3) -> list:
    """
    MCP Tool: Find semantically similar products using RAG.
    """
    return retriever.find_similar(query, k)
