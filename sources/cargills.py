import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait  # Add this import
from selenium.webdriver.support import expected_conditions as EC  # Add this import

class CargillsScraper:
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
        url = "https://cargillsonline.com/Product/Vegetables?IC=MjM=&NC=VmVnZXRhYmxlcw==&srsltid=AfmBOoqxc5AcYbRlkDUdfIbdGAMnIoEHYsT4MwRV1kBowWWrotP3mH86"
        self.driver.get(url)
        time.sleep(5)  # Wait for initial page load

        collected_data = []
        while True:
            # Ensure all products are loaded on the current page
            self.load_all_products()

            # Extract product data
            collected_data.extend(self.extract_product_data())

            # Check if 'Next' button is available and clickable
            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[@class='pagination-next']//a"))
                )
                next_button.click()  # Click the 'Next' button to go to the next page
                time.sleep(5)  # Wait for products to load
            except Exception as e:
                print("No more pages or error while navigating:", e)
                break  # Exit the loop if no more pages are found

        # Save results to 'cargills.csv'
        with open('cargills.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["name", "Quantity", "Price"])  # Added Quantity column
            csv_writer.writerows(collected_data)

        print(f"✅ Scraped {len(collected_data)} products. Saved to cargills.csv.")

    def load_all_products(self):
        """ Scrolls until all products are loaded. """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 50  # Increase max attempts for more thorough scrolling

        while scroll_attempts < max_attempts:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Increased sleep time

            # Wait for new products to load
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "ng-binding"))
            )

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Stop if no new content is loaded

            last_height = new_height
            scroll_attempts += 1

    def extract_product_data(self):
        """ Extracts all product names, quantities, and prices. """
        collected_data = set()

        try:
            # Wait until all products are visible
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "ng-binding"))
            )

            # Find all product name elements
            product_names = self.driver.find_elements(By.XPATH, "//p[@class='ng-binding']")

            # Find all quantity elements (button with quantity)
            quantities = self.driver.find_elements(By.XPATH, "//button[@class='dropbtn1 ng-binding ng-scope']")

            # Find all price elements
            prices = self.driver.find_elements(By.XPATH, "//h4[@class='txtSmall ng-binding']")

            # Loop through products and extract name, quantity, and price
            for name_element, quantity_element, price_element in zip(product_names, quantities, prices):
                name = name_element.text.strip()
                quantity = quantity_element.text.strip() if quantity_element else "N/A"
                price = price_element.text.strip().replace("Rs. ", "").strip()  # Clean the price string

                if name and price and quantity:
                    collected_data.add((name, quantity, price))  # Add product only if valid

        except Exception as e:
            print(f"❌ Error extracting products: {e}")

        return collected_data

# Run the scraper
# scraper = UberEatsScraper()
# scraper.scrape_products()
