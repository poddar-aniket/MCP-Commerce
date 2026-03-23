import re
from typing import Optional


def extract_max_price(text: str) -> Optional[int]:
    """
    Extract a max price from user text.
    Supports:
    - under 50000
    - below 40k
    - less than 30000
    - 40k
    """

    text = text.lower()

    # under / below / less than <number>
    match = re.search(r"(under|below|less than)\s*(\d+)", text)
    if match:
        return int(match.group(2))

    # shorthand like 40k, 50k
    match = re.search(r"(\d+)\s*k", text)
    if match:
        return int(match.group(1)) * 1000

    return None
