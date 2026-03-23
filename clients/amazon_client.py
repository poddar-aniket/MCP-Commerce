import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AmazonClient:
    """
    Amazon US client via RapidAPI.
    Fully environment-driven.
    """

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.api_host = os.getenv(
            "AMAZON_API_HOST",
            "real-time-amazon-data.p.rapidapi.com"
        )

        self.country = os.getenv("AMAZON_COUNTRY", "US")
        self.domain = os.getenv("AMAZON_DOMAIN", "amazon.com")
        self.language = os.getenv("AMAZON_LANGUAGE", "en_US")
        self.timeout = int(os.getenv("AMAZON_TIMEOUT", "10"))

        if not self.api_key:
            raise RuntimeError("RAPIDAPI_KEY not set")

        self.base_url = f"https://{self.api_host}"

        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host,
        }

    def search(self, query: str) -> dict:
        url = f"{self.base_url}/search"

        params = {
            "query": query,
            "country": self.country,
            "domain": self.domain,
            "language": self.language,
            "page": "1",
        }

        response = self.session.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
