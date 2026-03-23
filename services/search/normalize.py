import re


def _parse_price(price):
    """
    Normalize prices into int INR.
    Accepts strings like '₹54,790' or '54790'.
    """

    if price is None:
        return None

    if isinstance(price, (int, float)):
        return int(price)

    if isinstance(price, str):
        cleaned = price.replace("₹", "").replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None

    return None


def normalize_product(
    *,
    platform: str,
    title: str,
    price,
    rating=None,
    reviews_count=None,
    url=None,
):
    # ---------- Title ----------
    if not title or not isinstance(title, str):
        return None

    title = title.strip()
    if not title:
        return None

    # ---------- Price ----------
    price = _parse_price(price)
    if price is None:
        return None

    # ---------- Rating ----------
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = None

    # ---------- Reviews ----------
    if not isinstance(reviews_count, int):
        reviews_count = None

    # ---------- URL ----------
    if not isinstance(url, str):
        url = None

    return {
        "platform": platform,
        "title": title,
        "price": price,
        "currency": "USD",
        "rating": rating,
        "reviews_count": reviews_count,
        "url": url,
    }
