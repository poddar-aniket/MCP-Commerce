import json
import os
from dotenv import load_dotenv

load_dotenv()

from clients.walmart_client import WalmartClient

def main():
    print("Testing Walmart Client API...")
    try:
        client = WalmartClient()
        response = client.search("laptop")
        print("\n--- RAW API RESPONSE ---")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error during Walmart API call: {e}")

if __name__ == "__main__":
    main()
