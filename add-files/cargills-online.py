import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
            # Extract data from the current page
            collected_data.extend(self.extract_product_data())

            # Find the next page button
            next_page_button = self.get_next_page_button()
            if next_page_button:
                self.driver.execute_script("arguments[0].click();", next_page_button)
                time.sleep(5)  # Wait for new page to load
            else:
                break  # No more pages left

        # Save results
        with open('cargills.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Product Name", "Quantity", "Price"])
            csv_writer.writerows(collected_data)

        print(f"✅ Scraped {len(collected_data)} products. Saved to cargills.csv.")
        self.driver.quit()

    def get_next_page_button(self):
        """Finds the next page button and returns it if available."""
        try:
            # Locate pagination links
            pagination_links = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'pagination-page')]/a")

            # Get current active page
            active_page_element = self.driver.find_element(By.XPATH, "//li[contains(@class, 'pagination-page') and contains(@class, 'active')]")
            active_page = int(active_page_element.text.strip())

            # Find the next available page
            for link in pagination_links:
                try:
                    page_number = int(link.text.strip())
                    if page_number > active_page:
                        return link  # Return the next page button
                except ValueError:
                    continue  # Skip non-numeric values

            return None  # No next page found
        except Exception:
            return None  # If pagination does not exist

    def extract_product_data(self):
        """ Extracts all product names, quantities, and prices. """
        collected_data = []

        try:
            # Wait until products are visible
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
                price = price_element.text.strip().replace("Rs. ", "").strip()

                if name and price and quantity:
                    collected_data.append((name, quantity, price))  # Add product only if valid

        except Exception as e:
            print(f"❌ Error extracting products: {e}")

        return collected_data

# Run the scraper
# scraper = CargillsScraper()
# scraper.scrape_products()
