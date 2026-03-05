# eBay Market Intelligence & Data Pipeline

A robust Python-based data engineering tool designed to monitor global eBay auction markets and stream high-fidelity listing data into **Google BigQuery** for real-time analytics.

## 🚀 Key Features
- **Multi-Market Monitoring**: Tracks auction-style listings across 8+ global regions (US, GB, AU, DE, etc.).
- **Cloud Integration**: Automated data flow from raw API ingestion to **Google Cloud Storage (GCS)** and **BigQuery**.
- **Production-Ready Architecture**: Features modular design, environment-based configuration, and comprehensive logging.
- **Data Processor**: Includes custom logic for cleaning and formatting raw JSON into analytical-ready schemas.

## 🛠 Tech Stack
- **Language**: Python 3.13+
- **APIs**: eBay Production API (Finding/Browse)
- **Cloud**: Google Cloud Platform (BigQuery, GCS)
- **Tools**: `python-dotenv`, `requests`, `google-cloud-sdk`

## 📦 Installation & Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/ebay-market-intelligence.git](https://github.com/yourusername/ebay-market-intelligence.git)