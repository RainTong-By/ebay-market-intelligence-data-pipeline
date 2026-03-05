import os

# ›=================================================================
# GOOGLE CLOUD PLATFORM (GCP) CONFIGURATION
# =================================================================
# Project and Table details as verified in your BigQuery console
CP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCS_RAW_BUCKET = os.getenv("GS_BUCKET_NAME")
BQ_DATASET = os.getenv("BQ_DATASET")
BQ_TABLE = os.getenv("BQ_TABLE")BQ_FULL_TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}" if GCP_PROJECT_ID else NoneABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

# =================================================================
# EBAY API AUTHENTICATION (PRODUCTION MODE)
# =================================================================
# CRITICAL: We are now moving from "SANDBOX" to "PRODUCTION"
EBAY_ENV = "PRODUCTION"

# Your validated Production Credentials from the eBay Developer Portal
EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")
EBAY_DEV_ID = os.getenv("EBAY_DEV_ID")

# =================================================================
# INGESTION PARAMETERS (LIVE MARKET DATA)
# =================================================================
# Filter to ensure we only capture Auction-style listings
AUCTION_FILTER = "buyingOptions:{AUCTION}"

# Global Market IDs we are monitoring
TARGET_MARKETS = [
    "EBAY_US", "EBAY_GB", "EBAY_AU", "EBAY_DE", 
    "EBAY_FR", "EBAY_IT", "EBAY_CA"
]

# Keywords for live market analysis (Production has much more data)
SEARCH_KEYWORDS = [
    "iPhone 15 Pro", 
    "Rolex Submariner", 
    "Sony PS5", 
    "Leica Camera", 
    "MacBook M3"
]

# =================================================================
# OPERATIONAL SETTINGS
# =================================================================
LOG_DIR = "logs"
# Ensuring the log file reflects the production status
LOG_FILE = os.path.join(LOG_DIR, "adis_system_production.log")

# Create log directory if it doesn't exist during config load
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)