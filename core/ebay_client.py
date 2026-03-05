import requests
import base64
import logging
import os
import time
from dotenv import load_dotenv
from config import app_config as settings

# Load environment variables
load_dotenv()

class EbayClient:
    """
    EbayClient handles automated OAuth2 authentication and data retrieval.
    It supports fetching both active auctions (LIVE) and completed transactions (SOLD).
    """
    def __init__(self):
        self.client_id = settings.EBAY_CLIENT_ID
        self.client_secret = settings.EBAY_CLIENT_SECRET
        self.env = settings.EBAY_ENV
        
        # Determine API endpoints based on environment (Sandbox vs Production)
        if self.env == "PRODUCTION":
            self.base_url = "https://api.ebay.com/"
            self.auth_url = "https://api.ebay.com/identity/v1/oauth2/token"
        else:
            self.base_url = "https://api.sandbox.ebay.com/"
            self.auth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
            
        # Initialize the access token automatically to avoid manual entry
        self.access_token = self._get_oauth_token()

    def _get_oauth_token(self):
        """
        Automated OAuth2 Client Credentials flow. 
        Ensures the system stays online without manual token updates.
        """
        logging.info(f"🔄 Requesting fresh OAuth token for {self.env}...")
        try:
            # Base64 encode the Client ID and Secret for Basic Auth
            auth_str = f"{self.client_id}:{self.client_secret}"
            encoded_auth = base64.b64encode(auth_str.encode()).decode()

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_auth}"
            }
            
            payload = {
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope"
            }

            response = requests.post(self.auth_url, headers=headers, data=payload)
            
            if response.status_code == 200:
                logging.info("✅ OAuth Token acquired successfully.")
                return response.json().get("access_token")
            else:
                logging.error(f"❌ OAuth Failure: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logging.error(f"❌ Exception during token retrieval: {str(e)}")
            return None

    def search_items(self, keyword, market_id="EBAY_US", search_type="LIVE"):
        """
        Primary search function for ADIS Phase 3.
        :param search_type: "LIVE" for active auctions, "SOLD" for completed price analysis.
        """
        if not self.access_token:
            self.access_token = self._get_oauth_token()

        search_endpoint = f"{self.base_url}buy/browse/v1/item_summary/search"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-EBAY-C-MARKETPLACE-ID": market_id
        }

        # Construct filters according to Luck's requirement for price intelligence
        # LIVE: Monitoring current auction heat
        # SOLD: Establishing final sale price benchmarks
        filter_query = "buyingOptions:{AUCTION}"
        if search_type == "SOLD":
            filter_query = "buyingOptions:{AUCTION},conditions:{SOLD}"

        params = {
            "q": keyword,
            "filter": filter_query,
            "limit": 20
        }

        # Retry logic to handle network instability (e.g., SSLError, connection reset)
        for attempt in range(3):
            try:
                response = requests.get(search_endpoint, headers=headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    logging.warning("🔑 Token expired. Refreshing...")
                    self.access_token = self._get_oauth_token()
                    headers["Authorization"] = f"Bearer {self.access_token}"
                else:
                    logging.warning(f"⚠️ API Error ({response.status_code}) for {market_id}")
            except Exception as e:
                logging.warning(f"Network jitter on attempt {attempt+1}. Retrying...")
                time.sleep(2)
        
        return None