import json
import traceback
import os
import pandas as pd
import logging
import threading
import time
from fastapi import FastAPI
from helpers.helper import SeleniumHelper
from sources.Scrapper import UberEatsScraper
from sources.ican_mall import icanScraper
from sources.cargills import CargillsScraper
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or your domain/IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_FILES = {
    "ican mall products.csv": "ican_mall",
    "ubereats_products.csv": "uber",
    "cargills.csv": "cargills"
}
MERGED_FILE = "merged_products.csv"

def scrape_products():
    try:
        logger.info("🔄 Starting scraping process...")

        scrapers = [
            (UberEatsScraper(), "uber"),
            (CargillsScraper(), "cargills"),
            (icanScraper(), "ican_mall")
        ]

        for scraper, name in scrapers:
            logger.info(f"🕷 Scraping {name}...")
            scraper.scrape_products()
            logger.info(f"✅ {name} scraping complete.")

        merge_scraped_data()
        logger.info("✅ All scraping and merging done!")
    except Exception as e:
        logger.error(f"❌ Scraping error: {e}")
        traceback.print_exc()

def merge_scraped_data():
    try:
        logger.info("🔗 Merging scraped CSV files...")
        dataframes = []

        for file_name, source in CSV_FILES.items():
            if os.path.exists(file_name):
                df = pd.read_csv(file_name)
                df["Source"] = source
                dataframes.append(df)
            else:
                logger.warning(f"⚠️ File not found: {file_name}")

        if dataframes:
            merged_df = pd.concat(dataframes, ignore_index=True)
            merged_df.to_csv(MERGED_FILE, index=False)
            logger.info(f"✅ Merged file saved as {MERGED_FILE}")
        else:
            logger.warning("⚠️ No data to merge.")
    except Exception as e:
        logger.error(f"❌ Merge error: {e}")
        traceback.print_exc()

@app.get("/merged-products")
async def get_merged_products():
    try:
        if not os.path.exists(MERGED_FILE):
            return {"message": "Scraping not complete yet."}
        df = pd.read_csv(MERGED_FILE)
        return json.loads(df.to_json(orient="records"))
    except Exception as e:
        logger.error(f"❌ Error loading merged file: {e}")
        traceback.print_exc()
        return {"error": str(e)}

# Background thread for automatic scraping
def scheduler_loop(interval_minutes=60):
    while True:
        scrape_products()
        time.sleep(interval_minutes * 60)

# Start background scraping thread on app launch
threading.Thread(target=scheduler_loop, daemon=True).start()
