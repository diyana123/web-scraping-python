import json
import traceback
import os
import pandas as pd
import logging
from fastapi import FastAPI
from helpers.helper import SeleniumHelper
from sources.Scrapper import UberEatsScraper
from sources.keels_supper import KeellsProductScraper
from sources.ican_mall import icanScraper
from sources.cargills import CargillsScraper

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

CSV_FILES = {
    "ican mall products.csv": "Ican Mall",
    "keells_products.csv": "Keells",
    "ubereats_products.csv": "Uber Eats",
    "cargills.csv": "Cargills"
}

MERGED_FILE = "merged_products.csv"

def scrape_products():
    """Runs all scrapers and merges data."""
    try:
        logger.info("Starting scraping process...")

        scrapers = [
            (UberEatsScraper(), "UberEats"),
            (KeellsProductScraper(), "Keells"),
            (CargillsScraper(), "Cargills"),
            (icanScraper(), "Ican Mall")
        ]

        for scraper, name in scrapers:
            logger.info(f"Scraping {name}...")
            scraper.scrape_products()
            logger.info(f"✅ {name} scraping complete.")

        merge_scraped_data()
        logger.info("✅ Scraping & Merging Done!")
        return True

    except Exception as e:
        logger.error(f"❌ Scraping Error: {e}")
        traceback.print_exc()
        return False

def merge_scraped_data():
    """Merges all scraped CSV files into one."""
    try:
        logger.info("Merging scraped CSV files...")
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
        logger.error(f"❌ Merging Error: {e}")
        traceback.print_exc()

@app.get("/products")
async def get_products():
    """Scrapes data on request and returns it."""
    logger.info("📢 Received API request to fetch products.")

    success = scrape_products()
    if not success:
        return {"error": "Scraping failed. Check logs for details."}

    if not os.path.exists(MERGED_FILE):
        return {"message": "Scraping in progress or failed. Try again later."}

    try:
        df = pd.read_csv(MERGED_FILE)
        if df.empty:
            return {"message": "No data available yet. Try again later."}
        return json.loads(df.to_json(orient="records"))
    except Exception as e:
        logger.error(f"❌ Error reading {MERGED_FILE}: {e}")
        traceback.print_exc()
        return {"error": str(e)}
