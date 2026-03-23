from core.mcp_server.tools.generate_query import generate_query_from_text
from services.search.amazon import search_amazon
from services.search.flipkart import search_flipkart
from services.ranking.final import rank_results


def main():
    user_input = "iPhone 14 128GB blue"

    # Step 1: generate product query
    product = generate_query_from_text(user_input)

    # Step 2: search marketplaces
    amazon_results = search_amazon(product)
    flipkart_results = search_flipkart(product)

    all_results = amazon_results + flipkart_results

    # Step 3: rank results
    ranked_results = rank_results(all_results)

    # Step 4: print output
    print("Final ranked results:\n")
    for item in ranked_results:
        print(item)


if __name__ == "__main__":
    main()
