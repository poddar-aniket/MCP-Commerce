import os
import json
from dotenv import load_dotenv

load_dotenv()

from clients.ebay_client import EbayClient


def main():
    try:
        # Initialize client (will raise RuntimeError if env vars are missing)
        client = EbayClient()
        print("✅ Client initialized successfully.")
    except RuntimeError as e:
        print(f"❌ Initialization failed: {e}")
        print("Please ensure EBAY_APP_ID and EBAY_CERT_ID are set in your .env file.")
        return

    query = "iPhone 14 128GB"
    limit = 3

    print(f"\nSearching for: '{query}' with limit: {limit} ...")

    try:
        # Since it's a dumb pipe, this returns the raw un-normalized JSON dictionary 
        response = client.search(query, limit=limit)
        
        print("\n--- RAW EBAY RESPONSE ---\n")
        # Pretty-print the raw JSON response
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"\n❌ Search failed: {e}")


if __name__ == "__main__":
    main()
