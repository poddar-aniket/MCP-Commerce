def generate_query_from_text(context):
    """
    Accepts either raw text (legacy) or structured_query dict.

    Priority order for the search string:
      1. reference_product  (for similar/cheaper intents)
      2. product_name       (clean, filler-stripped keywords for search intent)
      3. raw_query          (legacy fallback — includes full user sentence)
    """

    if isinstance(context, dict):
        text = (
            context.get("reference_product")
            or context.get("product_name")
            or context.get("raw_query")
            or ""
        )
        
        # Return the clean query ALONG with the dynamic constraints.
        return {
            "query": text.strip(),
            "min_price": context.get("min_price"),
            "max_price": context.get("max_price"),
            "condition": context.get("condition", "any")
        }
    
    # Legacy fallback if 'context' is just a raw string
    text = str(context) if context else ""
    return {
        "query": text.strip(),
        "min_price": None,
        "max_price": None,
        "condition": "any"
    }
