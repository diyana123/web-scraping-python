import traceback
import os
import pandas as pd
import logging
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from helpers.helper import SeleniumHelper
from sources.Scrapper import UberEatsScraper
from sources.keels_supper import KeellsProductScraper
from sources.ican_mall import icanScraper
from sources.cargills import CargillsScraper

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

def scrape_products():
    try:
        # Initialize and run the UberEatsScraper
        ubereats_scraper = UberEatsScraper()
        logger.info("Starting UberEats scraping...")
        ubereats_scraper.scrape_products()
        logger.info("UberEats scraping finished.")

        keells_scraper = KeellsProductScraper()
        logger.info("Starting Keells scraping...")
        keells_scraper.scrape_products()
        logger.info("Keells scraping finished.")

        cargills = CargillsScraper()
        logger.info("Starting Cargills scraping...")
        cargills.scrape_products()
        logger.info("Cargills scraping finished.")

        ican_mall = icanScraper()
        logger.info("Starting Ican Mall scraping...")
        ican_mall.scrape_products()
        logger.info("Ican Mall scraping finished.")

        # Define CSV file paths
        files = {
            "ican mall products.csv": "Ican Mall",
            "keells_products.csv": "Keells",
            "ubereats_products.csv": "Uber Eats",
            "cargills.csv": "Cargills"
        }

        # Read and merge CSV files
        merged_data = []

        for file_name, shop_name in files.items():
            if os.path.exists(file_name):
                df = pd.read_csv(file_name)
                logger.info(f"Read {len(df)} rows from {file_name}.")
                df["Shop"] = shop_name  # Add shop name
                merged_data.append(df)
            else:
                logger.warning(f"Error: {file_name} does not exist.")

        # Combine all dataframes into one
        if merged_data:
            merged_data = pd.concat(merged_data, ignore_index=True)
            # Save to a new CSV file
            merged_data.to_csv("merged_shops.csv", index=False)
            logger.info("✅ Merged CSV files into 'merged_shops.csv'.")
        else:
            logger.warning("No data to merge.")

    except Exception as e:
        logger.error(f"❌ Error in scrape_products: {e}")
        traceback.print_exc()

# Initialize scheduler
scheduler = BackgroundScheduler()

def job_listener(event):
    if event.exception:
        logger.error(f"❌ Error in job: {event}")
    else:
        logger.info(f"✅ Job executed successfully: {event}")

# Schedule the scraping task every hour
scheduler.add_job(scrape_products, 'interval', hours=1)

# Add listener to capture job success and failure events
scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

# Start the scheduler
scheduler.start()

@app.get("/")
async def root():
    return {"message": "FastAPI is running with scheduled scraping every hour!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
