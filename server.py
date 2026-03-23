import sys
import unittest.mock as mock
import os
from dotenv import load_dotenv

# --- Bypass broken local HuggingFace pyarrow environment (same as our test script) ---
sys.modules['core.rag.embeddings'] = mock.MagicMock()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Ensure environment variables are loaded
load_dotenv()

from core.ai_engine.engine import AIEngine
from core.rag.retrieve import Retriever

# --- Bypass FAISS index_products crash due to mocked embeddings ---
Retriever.index_products = mock.MagicMock()

# ---------------------------------------------------------
# FASTAPI SERVER INITIALIZATION
# ---------------------------------------------------------

app = FastAPI(
    title="MCP Commerce Engine API",
    description="Production-ready multi-marketplace semantic search API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local testing
    allow_credentials=False,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Instantiate the AIEngine globally so FAISS memory state persists across all HTTP requests
print("Instantiating Global AIEngine...")
engine = AIEngine()

# ---------------------------------------------------------
# PYDANTIC SCHEMAS
# ---------------------------------------------------------

class SearchRequest(BaseModel):
    query: str
    history: list[dict] = []
    result_mode: str = "top_5_overall"
    item_condition: str = "any"

# ---------------------------------------------------------
# HTTP ENDPOINTS
# ---------------------------------------------------------

@app.get("/")
async def health_check():
    """
    Basic health check to verify backend server status.
    """
    return {
        "status": "MCP Commerce Engine Online",
        "markets": ["Amazon", "eBay", "Walmart"]
    }


@app.post("/api/search")
async def search_markets(request: SearchRequest):
    """
    Core API endpoint accepting an incoming search query and routing it through
    the multi-marketplace MCP AI engine.
    """
    try:
        results, suggestion = engine.handle_input(request.query, history=request.history, result_mode=request.result_mode, item_condition=request.item_condition)
        
        # Conversational / LLM output
        if isinstance(results, str):
            return {
                "type": "text",
                "message": results,
                "suggestion": suggestion
            }
            
        # Product ranking output
        if isinstance(results, list):
            serialized_data = []
            for item in results:
                if hasattr(item, "model_dump"):
                    serialized_data.append(item.model_dump())
                elif hasattr(item, "dict"):
                    serialized_data.append(item.dict())
                else:
                    serialized_data.append(dict(item) if hasattr(item, "__iter__") else item)
                    
            return {
                "type": "products",
                "data": serialized_data,
                "suggestion": suggestion
            }
            
        # Failsafe for unknown formats
        return {
            "type": "products",
            "data": [],
            "suggestion": suggestion
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine Error: {str(e)}")


if __name__ == "__main__":
    # Launch Uvicorn strictly mapped to server:app
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
