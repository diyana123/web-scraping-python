import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class KeellsProductScraper:
    def __init__(self):
        self.CHROME_DRIVER_PATH = "drivers/chromedriver.exe"
        self.options = Options()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        service = Service(executable_path=self.CHROME_DRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=self.options)
        self.wait = WebDriverWait(self.driver, 25)  # Increased wait time

    def navigate_to_fresh_vegetables(self):
        """Navigate through the Keells website to reach the Fresh Vegetables section."""
        self.driver.get("https://www.keellssuper.com/welcome")
        time.sleep(7)  # Wait for the page to fully load

        try:
            # Click "Browse the Store"
            browse_button = self.wait.until(EC.element_to_be_clickable((By.ID, "welcome_browse_btn")))
            browse_button.click()
            time.sleep(5)

            # Click "Categories"
            categories_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "category_menu_btn_product_search")))
            categories_button.click()
            time.sleep(5)

            # Click "Vegetables"
            vegetables_button = self.wait.until(EC.element_to_be_clickable((By.ID, "dep_id_16")))
            vegetables_button.click()
            time.sleep(5)

            # Click "Fresh Vegetables"
            fresh_vegetables_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//li[text()='Fresh Vegetables']")))
            fresh_vegetables_button.click()
            time.sleep(7)  # Allow products to load

        except Exception as e:
            print("Error navigating the site:", e)
            self.driver.quit()
            return

    def scroll_until_all_products_loaded(self):
        """Continuously scroll until all products are loaded."""
        last_height = 0
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Allow more products to load

            # Get all product elements
            product_elements = self.driver.find_elements(By.CLASS_NAME, "product-card-name")
            print(f"Currently loaded products: {len(product_elements)}")  # Debugging info

            # Check if new products loaded
            new_height = len(product_elements)
            if new_height == last_height:  # Stop if no new products are loaded
                break
            last_height = new_height

    def scrape_products(self):
        """Scrape all product names and prices."""
        self.navigate_to_fresh_vegetables()
        self.scroll_until_all_products_loaded()

        try:
            # Extract product names
            product_names = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card-name")))

            # Extract product prices
            product_prices = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card-final-price")))

            products = []
            for name, price in zip(product_names, product_prices):
                product_name = name.text.strip()
                product_price = price.text.strip()
                products.append([product_name, product_price])

            # Save results to CSV
            with open('keells_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["name", "Price"])
                csv_writer.writerows(products)

            print(f"Scraped {len(products)} products. Saved to keells_products.csv.")

        except Exception as e:
            print("Error scraping products:", e)

        self.driver.quit()

# Run the scraper
# scraper = KeellsProductScraper()
# scraper.scrape_products()
