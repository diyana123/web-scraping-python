import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class UberEatsScraper:
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
        url = "https://www.ubereats.com/lk/store/celeste-daily-colombo-05/TxX4NHBQStyKXNuu-OHwAA/4f15f834-7050-4adc-8a5c-dbaef8e1f000/d1f27d52-fbf5-447d-b4bf-1e82bc07648b?ps=1&scats=d1f27d52-fbf5-447d-b4bf-1e82bc07648b&scatsubs=9108ea5b-f133-41ca-834c-624d39e6c535"
        self.driver.get(url)
        time.sleep(5)  # Wait for initial page load

        self.load_all_products()  # Ensure all products are loaded

        collected_data = self.extract_product_data()  # Extract product details

        self.driver.quit()

        # Save results to CSV
        with open('ubereats_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Price", "Product Name"])
            csv_writer.writerows(collected_data)

        print(f"✅ Scraped {len(collected_data)} products. Saved to ubereats_products.csv.")

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
              EC.presence_of_all_elements_located((By.XPATH, "//span[@data-testid='rich-text']"))
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
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//span[@data-testid='rich-text']"))
            )

            product_elements = self.driver.find_elements(By.XPATH, "//span[@data-testid='rich-text']")

            for i in range(0, len(product_elements) - 1, 2):  # Every 2 elements (Name, Price)
                name = product_elements[i].text.strip()
                price = product_elements[i + 1].text.strip().replace("LKR", "").strip()


                # Ignore unwanted lines
                if "38, Iswari Road, Colombo 5,  Sri Lanka" in name or "Celeste Daily" in name:
                      continue  # Skip these lines
#                 #Remove "celeste daily-SKU xxxx"
#                 name = re.sub(r" - Celeste Daily - SKU \d+", "", name)


                # Ensure that the tomatoes product is captured
                if "Tomato" in name or "tomato" in name:
                    print(f"Found Tomato Product: {name}, Price: {price}")

                if name and price:
                    collected_data.add((name, price))  # Add product only if valid


        except Exception as e:
            print(f"❌ Error extracting products: {e}")

        return collected_data

# Run the scraper
# scraper = UberEatsScraper()
# scraper.scrape_products()
