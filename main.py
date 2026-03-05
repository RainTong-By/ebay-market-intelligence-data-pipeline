import logging
import os
import sys
from datetime import datetime

# --- DYNAMIC PATH INJECTION ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import app_config as settings
from core.ebay_client import EbayClient       
from core.cloud_manager import CloudManager   
from core.data_processor import DataProcessor 

def run_adis_pipeline():
    """
    Orchestration logic for Phase 3: Pilot Run.
    Now collects both Live and Sold data for comprehensive price analysis.
    """
    # 1. Setup local logs
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # 2. Initialize core modules
    ebay = EbayClient()
    
    # CRITICAL: Manually passing project_id to solve "No project ID could be determined" error
    # Make sure settings.GCP_PROJECT_ID is set to 'project-adis-auction-484316' in your config
    gcp = CloudManager(project_id=settings.GCP_PROJECT_ID)
    processor = DataProcessor()

    logging.info("=== 🚀 ADIS Phase 3: Multi-Market Pipeline Start ===")

    for site_id in settings.TARGET_MARKETS:
        for keyword in settings.SEARCH_KEYWORDS:
            # Crawl both statuses to satisfy the 'Sale Outcome' requirement
            for mode in ["LIVE", "SOLD"]:
                try:
                    logging.info(f"Task: [Market: {site_id} | Keyword: {keyword} | Mode: {mode}]")

                    raw_payload = ebay.search_items(keyword=keyword, market_id=site_id, search_type=mode)

                    if raw_payload and 'itemSummaries' in raw_payload:
                        # Archive Raw JSON to GCS Data Lake
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{mode}_{site_id}_{keyword.replace(' ', '_')}_{timestamp}"
                        gcp.archive_to_gcs(data=raw_payload, filename=filename)

                        # Clean data and tag with 'status' (LIVE or SOLD)
                        processed_rows = processor.clean_listing_data(
                            raw_payload, site_id, keyword, status=mode
                        )
                        
                        # Stream to BigQuery
                        if processed_rows:
                            gcp.stream_to_bigquery(rows=processed_rows)
                            logging.info(f"✅ Synced {len(processed_rows)} {mode} records.")
                    else:
                        logging.warning(f"⏭️ No {mode} data for {keyword} in {site_id}.")

                except Exception as e:
                    logging.error(f"❌ Failure in task [{site_id}|{mode}]: {str(e)}")

    logging.info("=== ✨ ADIS Phase 3 Cycle Complete ===")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler("logs/adis_system.log"),
            logging.StreamHandler()
        ]
    )
    run_adis_pipeline()