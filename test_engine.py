from core.ai_engine.engine import AIEngine

engine = AIEngine()

print("\n--- Indexing dummy products ---")
dummy_products = [
    {"title": "iPhone 14 128GB Blue", "price": 70000},
    {"title": "Samsung Galaxy S21 128GB", "price": 55000},
    {"title": "OnePlus Nord 5G", "price": 30000},
    {"title": "Redmi Note 12", "price": 18000},
]
engine.retriever.index_products(dummy_products)

print("\n--- Similar under 60000 ---")
for r in engine.handle_input("show me similar cheaper phones under 60000"):
    print(r)

print("\n--- Cheaper than iPhone 14 ---")
for r in engine.handle_input("cheaper than iPhone 14"):
    print(r)

print("\n--- Ambiguous query (expected fallback or empty) ---")
print(engine.handle_input("similar phones cheaper than this"))
