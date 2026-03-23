from core.mcp_server.registry.tool_registry import TOOLS


def run_text_query(user_text: str) -> list:
    # Step 1: generate product query
    product = TOOLS["generate_query"](user_text)

    # Step 2: search marketplaces via registry
    results = []
    results.extend(TOOLS["search_amazon"](product))
    results.extend(TOOLS["search_flipkart"](product))

    # Step 3: rank results via registry
    ranked = TOOLS["rank_results"](results)

    return ranked


if __name__ == "__main__":
    output = run_text_query("iPhone 14 128GB blue")
    for item in output:
        print(item)
