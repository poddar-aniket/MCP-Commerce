from core.ai_engine.engine import AIEngine

engine = AIEngine()

# First call: normal product search (this INDEXES results into RAG)
engine.handle_input("iPhone 14 128GB blue")

# Second call: semantic similarity search using embeddings
similar = engine.retriever.find_similar(
    "cheaper phones like iPhone",
    k=3
)

print("\nSimilar products:\n")
for item in similar:
    print(item)
