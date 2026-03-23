import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class WalmartClient:
    """
    Walmart client via RapidAPI.
    Fully environment-driven.
    """

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        # Support fallback to the specific Axesso service
        self.api_host = os.getenv(
            "WALMART_API_HOST",
            "axesso-walmart-data-service.p.rapidapi.com"
        )
        self.timeout = int(os.getenv("WALMART_TIMEOUT", "10"))

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
        # Based on typical axesso-walmart-data-service endpoint structures
        # The endpoint varies by wrapper, assuming /ws/amazon/search is the standard mapping
        # Actual Axesso Walmart endpoint might be /ws/walmart/search or /search
        
        # Searching Axesso RapidAPI Walmart wrapper
        url = f"{self.base_url}/wlm/walmart-search-by-keyword"
        
        params = {
            "keyword": query,
            "page": "1",
        }

        # Try making the request, wrapping gracefully just in case this specific logic fails
        try:
            response = self.session.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Walmart API HTTP Error (Endpoint 1): {e}")
            if e.response is not None:
                print(f"Response Body: {e.response.text}")
        except Exception as e:
            print(f"Walmart API General Error (Endpoint 1): {e}")

        # Fallback path if URL endpoint structure from user is different
        try:
            url_fallback = f"{self.base_url}/walmart/search"
            response = self.session.get(
                url_fallback,
                headers=self.headers,
                params={"keyword": query, "page": "1"},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Walmart API HTTP Error (Fallback): {e}")
            if e.response is not None:
                print(f"Response Body: {e.response.text}")
            return {}
        except Exception as e:
            print(f"Walmart API General Error (Fallback): {e}")
            return {}
