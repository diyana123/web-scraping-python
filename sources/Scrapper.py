import csv
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class OTCProductScraper:

    def __init__(self, obj):
        self.selenium_helper = obj
        self.CHROME_DRIVER_PATH = "./drivers/chromedriver"
        self.options = Options()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        service = Service(executable_path=self.CHROME_DRIVER_PATH)
        driver = Chrome(service=service, options=self.options)
        self.driver = driver

    def scrape_urls(self):
        url_set = set()  # Use a set to store unique URLs

        page_numbers = 43
        for i in range(1, page_numbers):
            url = f"https://powertool.lk/shop/page/{i}/"
            self.driver.get(url)
            time.sleep(5)
            WebDriverWait(self.driver, 5)

            a_elements = self.driver.find_elements(By.XPATH, "//ul[@class='products products list-unstyled row g-0 row-cols-2 row-cols-md-3 row-cols-lg-3 row-cols-xl-3 row-cols-xxl-5']//a[@class='woocommerce-LoopProduct-link woocommerce-loop-product__link']")

            for a_element in a_elements:
                href = a_element.get_attribute('href')
                if href:  # If href is not None
                    url_set.add(href)

        self.driver.quit()  # Quit the WebDriver once URLs are scraped

        # Save unique URLs to a CSV file
        with open('urls.csv', 'w', newline='') as csvfile:
            url_writer = csv.writer(csvfile)
            url_writer.writerow(['URL'])
            for url in url_set:
                url_writer.writerow([url])

        return list(url_set)  # Convert set back to list for consistent return type

# Example usage:
scraper = OTCProductScraper(None)
urls = scraper.scrape_urls()
print(f"Scraped {len(urls)} unique URLs. Saved to urls.csv.")
