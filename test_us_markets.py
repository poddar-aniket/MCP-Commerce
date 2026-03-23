import sys
import unittest.mock as mock

# --- Bypass broken local HuggingFace pyarrow environment ---
sys.modules['core.rag.embeddings'] = mock.MagicMock()

import os
from dotenv import load_dotenv

load_dotenv()

from core.ai_engine.engine import AIEngine
from core.rag.retrieve import Retriever

# --- Bypass FAISS crashing due to mocked vector embeddings ---
Retriever.index_products = mock.MagicMock()

def main():
    print("Initializing AI Engine with US Marketplaces...")
    engine = AIEngine()
    
    query = "laptop"
    print(f"Executing Query: '{query}'")
    
    results = engine.handle_input(query)
    
    if not results:
        print("No results returned.")
        return

    print("\n--- Top Results ---")
    
    # We display up to 10 results
    for i, item in enumerate(results[:10], start=1):
        try:
            # Assuming item is a Pydantic RankedResult object
            platform = item.platform
            title = item.title
            price = item.price
            
            # Optionally format the title if it's too long
            short_title = title[:60] + "..." if len(title) > 60 else title
            
            print(f"Rank {i}: [{platform}] {short_title} - ${price}")
        except AttributeError:
            # Fallback if it behaves like a dict unexpectedly
            platform = item.get("platform", "Unknown")
            title = item.get("title", "Unknown")
            price = item.get("price", 0)
            short_title = title[:60] + "..." if len(title) > 60 else title
            print(f"Rank {i}: [{platform}] {short_title} - ${price}")
            
if __name__ == "__main__":
    main()
