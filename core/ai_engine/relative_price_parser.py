import re
from typing import Optional


def extract_cheaper_than_reference(text: str) -> Optional[str]:
    """
    Extract reference product from phrases like:
    - cheaper than iphone 14
    - cheaper than this
    """

    text = text.lower()

    match = re.search(r"cheaper than (.+)", text)
    if match:
        return match.group(1).strip()

    return None
