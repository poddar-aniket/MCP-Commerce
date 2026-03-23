from services.ranking.final import rank_results


def test_rank_by_price():
    results = [
        {
            "platform": "Amazon",
            "price": 60000,
            "rating": 4.5,
            "currency": "INR",
            "url": "https://amazon.in"
        },
        {
            "platform": "Flipkart",
            "price": 58000,
            "rating": 4.3,
            "currency": "INR",
            "url": "https://flipkart.com"
        }
    ]

    ranked = rank_results(results)

    assert ranked[0]["platform"] == "Flipkart"
    assert ranked[0]["rank"] == 1
