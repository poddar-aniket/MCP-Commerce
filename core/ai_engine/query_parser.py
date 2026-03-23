import re
from typing import Optional, Dict


# ─────────────────────────────────────────────────────────────
# FILLER / PRICE STRIPPING
# ─────────────────────────────────────────────────────────────

# Price range patterns  (e.g. "between $400 and $800", "under 800", "in the range 400 to 800")
_PRICE_RANGE_RE = re.compile(
    r"("
    r"between\s*[$₹]?\s*\d+[k]?\s*(?:and|to|-)\s*[$₹]?\s*\d+[k]?"
    r"|in\s+the\s+range\s*[$₹]?\s*\d+[k]?\s*(?:to|-|and)\s*[$₹]?\s*\d+[k]?"
    r"|(?:under|below|above|over|upto|within|less\s+than|more\s+than)\s*[$₹]?\s*\d+[k]?"
    r"|[$₹]\s*\d+[k]?\s*(?:to|-|and)\s*[$₹]?\s*\d+[k]?"
    r")",
    re.IGNORECASE,
)

# Conversational filler patterns
_FILLER_RE = re.compile(
    r"\b("
    r"i\s+(?:want|need|would\s+like|'d\s+like)\s+(?:to\s+(?:buy|get|purchase|have|order)|a|an)?"
    r"|(?:looking|searching|hunt(?:ing)?)\s+for"
    r"|(?:can\s+you|could\s+you|please|hey|hi|hello)\s*"
    r"|(?:find|show|get|give)\s+(?:me\s+)?"
    r"|(?:a|an|the)\s+(?=\S)"
    r"|(?:some|good|best|cheap|affordable|nice|new|latest|top)\s+(?=[A-Za-z])"
    r"|(?:recommend(?:ations?)?|suggest(?:ions?)?)"
    r"|(?:i'm|i\s+am)\s+(?:looking\s+for|interested\s+in|searching\s+for)"
    r"|(?:what\s+is\s+the|what's\s+the)\s+(?:best|cheapest|price\s+of)?"
    r")",
    re.IGNORECASE,
)

# Currency symbols + stray punctuation left after stripping
_CLEANUP_RE = re.compile(r"[$₹,;:!?]|(\d+\s*\$)")


def _extract_product_keywords(raw: str) -> Optional[str]:
    """
    Returns a clean, API-ready search string by:
    1. Stripping price range expressions.
    2. Stripping conversational filler phrases.
    3. Removing stray currency symbols & punctuation.
    """
    text = _PRICE_RANGE_RE.sub("", raw)
    text = _FILLER_RE.sub("", text)
    text = _CLEANUP_RE.sub("", text)
    # Collapse multiple spaces
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text if text else None

def parse_query(query: str) -> Dict[str, Optional[object]]:
    raw_query = query
    q = query.lower().strip()

    intent = "search"
    max_price = None
    reference_product = None
    product_name = None

    # ---------- Intent detection ----------
    cheaper_patterns = [
        r"cheaper than",
        r"less expensive than",
        r"lower priced than",
        r"budget alternative to",
    ]

    similar_patterns = [
        r"similar to",
        r"like",
        r"same as",
        r"comparable to",
    ]

    alternative_patterns = [
        r"alternatives to",
        r"instead of",
        r"other than",
        r"competitors of",
    ]

    def contains_any(patterns):
        return any(re.search(p, q) for p in patterns)

    if contains_any(cheaper_patterns):
        intent = "cheaper"
    elif contains_any(similar_patterns):
        intent = "similar"
    elif contains_any(alternative_patterns):
        intent = "alternatives"

    # ---------- Max price extraction ----------
    price_patterns = [
        r"under\s*₹?\s*(\d+(?:,\d+)?k?)",
        r"below\s*₹?\s*(\d+(?:,\d+)?k?)",
        r"less than\s*₹?\s*(\d+(?:,\d+)?k?)",
        r"upto\s*₹?\s*(\d+(?:,\d+)?k?)",
        r"within\s*₹?\s*(\d+(?:,\d+)?k?)",
    ]

    prices = []
    for pattern in price_patterns:
        for match in re.findall(pattern, q):
            val = match.replace(",", "")
            if val.endswith("k"):
                prices.append(int(val[:-1]) * 1000)
            else:
                prices.append(int(val))

    if prices:
        max_price = min(prices)

    # ---------- Reference product extraction ----------
    ref_patterns = [
        r"cheaper than (.+)",
        r"less expensive than (.+)",
        r"lower priced than (.+)",
        r"budget alternative to (.+)",
        r"similar to (.+)",
        r"comparable to (.+)",
        r"same as (.+)",
        r"alternatives to (.+)",
        r"instead of (.+)",
        r"other than (.+)",
        r"competitors of (.+)",
        r"like (.+)",
    ]

    for pattern in ref_patterns:
        match = re.search(pattern, q)
        if match:
            ref = match.group(1)

            ref = re.split(
                r" under | below | less than | upto | within ", ref
            )[0]

            ref = re.sub(
                r"\b(something|anything|phones|mobiles|laptops|products)\b",
                "",
                ref,
            )

            reference_product = ref.strip() or None
            break

    # ---------- Product name extraction (search intent only) ----------
    if intent == "search":
        product_name = _extract_product_keywords(q) or None

    # ---------- VALIDITY ENFORCEMENT ----------
    valid = True

    if intent == "search" and not product_name:
        valid = False

    if intent in {"similar", "cheaper", "alternatives"} and not reference_product:
        valid = False

    return {
        "intent": intent,
        "product_name": product_name,
        "reference_product": reference_product,
        "max_price": max_price,
        "platforms": ["amazon", "flipkart"],
        "raw_query": raw_query,
        "valid": valid,
    }
