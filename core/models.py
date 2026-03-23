from pydantic import BaseModel

class ParsedQuery(BaseModel):
    reasoning: str
    search_query: str
    min_price: float | None = None
    max_price: float | None = None
    condition: str = "new"
    suggestion: str | None = None
