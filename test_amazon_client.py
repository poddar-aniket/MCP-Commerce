from dotenv import load_dotenv
load_dotenv()

from clients.amazon_client import AmazonClient
from services.search.normalize import normalize_product


def main():
    client = AmazonClient()
    query = "iPhone 14 128GB"

    print("\n--- RAW AMAZON RESPONSE (trimmed) ---\n")
    response = client.search(query)

    print("Top-level keys:", list(response.keys()))

    data = response.get("data", {})
    products = data.get("products", [])

    print(f"\nNumber of products returned: {len(products)}\n")

    print("\n--- NORMALIZED PRODUCTS ---\n")

    normalized = []

    for item in products[:5]:
        product = normalize_product(
            platform="Amazon",
            title=item.get("product_title"),
            price=item.get("product_price"),
            rating=item.get("product_star_rating"),
            reviews_count=item.get("product_num_ratings"),
            url=item.get("product_url"),
        )

        if product:
            normalized.append(product)
            print(product)
        else:
            print("❌ Dropped product due to normalization failure")

    print(f"\nNormalized products count: {len(normalized)}")


if __name__ == "__main__":
    main()
