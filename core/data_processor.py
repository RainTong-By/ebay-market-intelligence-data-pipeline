from datetime import datetime
import json
import logging

class DataProcessor:
    """
    [Phase 3] High-Fidelity Data Processor
    Combines legacy descriptive richness with new analytical status tagging.
    """
    
    @staticmethod
    def clean_listing_data(raw_json, market_id, keyword, status="LIVE"):
        """
        Transforms raw eBay API JSON into a professional, flat structure for BigQuery.
        Includes error handling for missing fields to prevent pipeline crashes.
        """
        processed_records = []
        items = raw_json.get("itemSummaries", [])
        
        # Consistent timestamp for the entire batch synchronization
        ingestion_time = datetime.utcnow().isoformat()

        for item in items:
            try:
                # 1. Price Extraction (Current vs. Marketing/Original)
                price_info = item.get("price", {})
                current_val = float(price_info.get("value", 0.0))
                currency = price_info.get("currency", "USD")
                
                # Fetching the 'Original/Starting' price to restore legacy richness
                marketing_info = item.get("marketingPrice", {})
                original_val = marketing_info.get("originalPrice", {}).get("value")
                original_price = float(original_val) if original_val else 0.0

                # 2. Descriptive Richness (Restoring Subtitles/Snippets)
                # eBay summaries often store details in subtitle or shortDescription
                description = (
                    item.get("subtitle") or 
                    item.get("shortDescription") or 
                    "No detailed description provided"
                )

                # 3. Seller & Shipping Context
                shipping_info = item.get("shippingOptions", [{}])[0]
                shipping_cost = shipping_info.get("shippingCost", {}).get("value", 0.0)

                # --- CONSOLIDATED RECORD STRUCTURE ---
                record = {
                    "item_id": item.get("itemId"),
                    "title": item.get("title"),
                    "description": description,                  # Restored!
                    "current_price": current_val,
                    "original_price": original_price,            # Restored!
                    "currency": currency,
                    "bid_count": int(item.get("bidCount", 0)), 
                    "listing_status": status,                    # Added for Phase 3 SQL
                    "market_id": market_id,
                    "location": item.get("location", {}).get("country", "Unknown"),
                    "condition": item.get("condition", "N/A"),
                    "shipping_cost": float(shipping_cost),
                    "search_keyword": keyword,
                    "ingestion_timestamp": ingestion_time,
                    "item_url": item.get("itemWebUrl")
                }
                
                processed_records.append(record)
                
            except Exception as e:
                logging.error(f"Failed to process item {item.get('itemId', 'Unknown')}: {e}")
                continue
            
        return processed_records