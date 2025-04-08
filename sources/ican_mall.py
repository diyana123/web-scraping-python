import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class icanScraper:
    def __init__(self):
        self.CHROME_DRIVER_PATH = "drivers/chromedriver.exe"
        self.options = Options()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        # self.options.add_argument('--headless')  # Uncomment for headless mode
        self.service = Service(executable_path=self.CHROME_DRIVER_PATH)
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def scrape_products(self):
        url = "https://icanmall.lk/services/iCan%20Fresh?type=vegetables-912"
        self.driver.get(url)
        time.sleep(5)  # Wait for initial page load

        self.load_all_products()  # Ensure all products are loaded

        collected_data = self.extract_product_data()  # Extract product details

        self.driver.quit()

        # Save results to CSV
        with open('ican mall products.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["name", "Price"])
            csv_writer.writerows(collected_data)

        print(f"✅ Scraped {len(collected_data)} products. Saved to products.csv.")

    def load_all_products(self):
        """ Scrolls until all products are loaded. """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 50  # Increase max attempts for more thorough scrolling

        while scroll_attempts < max_attempts:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Increased sleep time

            # Wait for new products to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "va-card__content"))
            )

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Stop if no new content is loaded

            last_height = new_height
            scroll_attempts += 1

    def extract_product_data(self):
        """ Extracts all product names and prices. """
        collected_data = set()

        try:
            # Wait until all products are visible
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "va-card__content"))
            )

            # Find all product name elements
            product_names = self.driver.find_elements(By.CLASS_NAME, "va-card__content.item-name")

            # Find all price elements
            price_containers = self.driver.find_elements(By.CLASS_NAME, "va-card__content.price-container")

            # Loop through products and extract name and price
            for name_element, price_element in zip(product_names, price_containers):
                name = name_element.text.strip()
                # Extract the price
                price_labels = price_element.find_elements(By.CLASS_NAME, "price-label")
                price = "".join([label.text.strip() for label in price_labels if label.text.strip()])


    # Ensure that the Red onion product is captured
                if "Red onion" in name or "Onion Big" in name:
                    print(f"Found Red onion Product: {name}, Price: {price}")
                if "carrot" in name.lower() or "ginger" in name.lower():
                    print(f"✅ Found {name} - {price}")
                if name and price:
                    collected_data.add((name, price))  # Add product only if valid

        except Exception as e:
            print(f"❌ Error extracting products: {e}")

        return collected_data

# Run the scraper
# scraper = UberEatsScraper()
# scraper.scrape_products()
