from google.cloud import storage, bigquery
from config import app_config as settings
import json
import logging

class CloudManager:
    """
    Manages communication with Google Cloud Services (GCS and BigQuery).
    Updated in Phase 3 to support explicit project_id injection for better stability.
    """
    # Modified __init__ to accept project_id, defaulting to settings if not provided
    def __init__(self, project_id=None):
        """
        Initializes GCP clients for Storage and BigQuery.
        :param project_id: Optional project ID to override configuration settings.
        """
        self.project_id = project_id or settings.GCP_PROJECT_ID
        
        # Explicitly passing project ID to clients resolves "No project ID determined" warnings
        self.storage_client = storage.Client(project=self.project_id)
        self.bq_client = bigquery.Client(project=self.project_id)
        
        logging.info(f"☁️ CloudManager initialized for project: {self.project_id}")

    def archive_to_gcs(self, data, filename):
        """
        Uploads raw JSON payloads to the specified GCS data lake bucket.
        """
        try:
            bucket = self.storage_client.bucket(settings.GCS_RAW_BUCKET)
            blob = bucket.blob(f"raw_ingestion/{filename}.json")
            blob.upload_from_string(
                data=json.dumps(data),
                content_type='application/json'
            )
            # Using logging instead of print for professional production logs
            logging.info(f"📦 [GCS] Data archived to {filename}.json")
        except Exception as e:
            logging.error(f"❌ [GCS] Archival Failed: {str(e)}")

    def stream_to_bigquery(self, rows):
        """
        Streams processed records directly into the BigQuery analytical table.
        """
        table_id = f"{self.project_id}.{settings.BQ_DATASET}.{settings.BQ_TABLE}"
        
        try:
            errors = self.bq_client.insert_rows_json(table_id, rows)
            
            if not errors:
                logging.info(f"📊 [BQ] Successfully streamed {len(rows)} records.")
                return True
            else:
                logging.error(f"❌ [BQ] Insertion Errors: {errors}")
                return False
        except Exception as e:
            logging.error(f"❌ [BQ] BigQuery Stream Failed: {str(e)}")
            return False