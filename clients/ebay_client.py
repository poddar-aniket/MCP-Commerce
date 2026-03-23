import os
import time
import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class EbayClient:
    """
    eBay client via Browse API.
    Fully environment-driven.
    """

    def __init__(self):
        self.app_id = os.getenv("EBAY_APP_ID")
        self.cert_id = os.getenv("EBAY_CERT_ID")

        if not self.app_id or not self.cert_id:
            raise RuntimeError("Missing required environment variables: EBAY_APP_ID and/or EBAY_CERT_ID")

        self.marketplace_id = os.getenv("EBAY_MARKETPLACE_ID", "EBAY_US")
        self.timeout = int(os.getenv("EBAY_TIMEOUT", "10"))

        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        self._access_token = None
        self._token_expiry = 0

    def _get_access_token(self) -> str:
        current_time = time.time()
        if self._access_token and current_time < self._token_expiry:
            return self._access_token

        token_url = "https://api.ebay.com/identity/v1/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        }

        response = self.session.post(
            token_url,
            auth=HTTPBasicAuth(self.app_id, self.cert_id),
            data=data,
            timeout=self.timeout
        )
        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data["access_token"]
        
        # Subtacting a 60 second buffer to be safe against expiration during request
        expires_in = int(token_data.get("expires_in", 7200))
        self._token_expiry = current_time + expires_in - 60

        return self._access_token

    def search(self, query: str, limit: int = 10) -> dict:
        token = self._get_access_token()
        
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": self.marketplace_id
        }
        params = {
            "q": query,
            "limit": limit
        }

        response = self.session.get(
            url,
            headers=headers,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        return response.json()
