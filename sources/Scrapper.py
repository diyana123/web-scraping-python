# import csv
# import time
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver import Chrome
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
#
# class OTCProductScraper:
#
#     def __init__(self, obj):
#         self.selenium_helper = obj
#         self.CHROME_DRIVER_PATH = "./drivers/chromedriver"
#         self.options = Options()
#         self.options.add_argument('--disable-blink-features=AutomationControlled')
#         self.options.add_argument('--ignore-certificate-errors')
#         self.options.add_argument('--ignore-ssl-errors')
#         service = Service(executable_path=self.CHROME_DRIVER_PATH)
#         driver = Chrome(service=service, options=self.options)
#         self.driver = driver
#
#     def scrape_urls(self):
#         url_set = set()  # Use a set to store unique URLs
#
#         page_numbers = 43
#         for i in range(1, page_numbers):
#             url = f"https://powertool.lk/shop/page/{i}/"
#             self.driver.get(url)
#             time.sleep(5)
#             WebDriverWait(self.driver, 5)
#
#             a_elements = self.driver.find_elements(By.XPATH, "//ul[@class='products products list-unstyled row g-0 row-cols-2 row-cols-md-3 row-cols-lg-3 row-cols-xl-3 row-cols-xxl-5']//a[@class='woocommerce-LoopProduct-link woocommerce-loop-product__link']")
#
#             for a_element in a_elements:
#                 href = a_element.get_attribute('href')
#                 if href:  # If href is not None
#                     url_set.add(href)
#
#         self.driver.quit()  # Quit the WebDriver once URLs are scraped
#
#         # Save unique URLs to a CSV file
#         with open('urls.csv', 'w', newline='') as csvfile:
#             url_writer = csv.writer(csvfile)
#             url_writer.writerow(['URL'])
#             for url in url_set:
#                 url_writer.writerow([url])
#
#         return list(url_set)  # Convert set back to list for consistent return type
#
# # Example usage:
# scraper = OTCProductScraper(None)
# urls = scraper.scrape_urls()
# print(f"Scraped {len(urls)} unique URLs. Saved to urls.csv.")


import traceback

from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options


class OTCProductScraper:

    def __init__(self, obj):
        self.selenium_helper = obj
        self.CHROME_DRIVER_PATH = "./drivers/chromedriver"
        self.options = Options()
        self.options.add_argument(
            '--disable-blink-features=AutomationControlled')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('ignore-ssl-errors')
        service = Service(executable_path=self.CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=self.options)
        self.driver = driver

    def scrape_data(self):
        url_list = []

        page_numbers = 43
        for i in range(1, page_numbers):
            url = f"https://powertool.lk/shop/page/{i}/"
            self.driver.get(url)
            time.sleep(5)
            WebDriverWait(self.driver, 5)

            status, a_elements = self.selenium_helper.find_xpath_elements(
                self.driver,
                "//ul[@class='products products list-unstyled row g-0 row-cols-2 row-cols-md-3 row-cols-lg-3 row-cols-xl-3 row-cols-xxl-5']//a[@class='woocommerce-LoopProduct-link woocommerce-loop-product__link']")
            a_elements = list(set(a_elements))

            for a_element in a_elements:
                href = a_element.get_attribute('href')
                if href:  # If href is not None
                    url_list.append(href)

        # Create a DataFrame from the list of URLs
        df = pd.DataFrame(url_list, columns=['URL'])

        # Save the DataFrame to a CSV file
        df.to_csv('urls.csv', index=False)

        return df

    def remove_duplicates(self):
        df = pd.read_csv('urls.csv')
        df = df.drop_duplicates()
        df.to_csv('urls.csv', index=False)

    def scrape_products(self):
        df = pd.read_csv('urls.csv')
        df = df['URL'].tolist()
        data = []
        for url in df:
            self.driver.get(url)
            time.sleep(5)
            WebDriverWait(self.driver, 5)

            status, product_name = self.selenium_helper.find_xpath_element(
                self.driver,
                "//div[@class='summary entry-summary']//h1")

            status, product_description = self.selenium_helper.find_xpath_elements(
                self.driver,
                "//div[@class='woocommerce-Tabs-panel woocommerce-Tabs-panel--description panel entry-content wc-tab']//p")

            descriptions = []

            # Iterate over the list of WebElement objects and extract the text content
            for element in product_description:
                descriptions.append(element.text.strip())

            status, product_price = self.selenium_helper.find_xpath_elements(
                self.driver,
                                "//div[@class ='summary entry-summary']//span[@class ='woocommerce-Price-amount amount']")

            # prices = []
            # for price_element in product_price:
            #     prices.append(price_element.text)

            # Assuming product_prices contains the list of price elements

            # Initialize variables to store prices
            cost_price = None
            market_price = None

            # Iterate over the list of price elements
            for price_element in product_price:
                # Extract the text of the price element
                price_text = price_element.text.strip()

                # Check if the price text starts with "Rs" for currency symbol
                if price_text.startswith("Rs"):
                    # If the price text starts with "Rs", it's considered as a cost price
                    if cost_price is None:
                        cost_price = price_text
                    else:
                        # If cost_price already exists, the current price is considered as the market price
                        market_price = price_text
                else:
                    # If the price text doesn't start with "Rs", it's considered as a market price
                    market_price = price_text

            # Print the prices
            # print("Cost Price:", cost_price)
            # print("Market Price:", market_price)

            # status, product_total_price = self.selenium_helper.find_xpath_element(
            #     self.driver,
            #     "//div[@class='summary entry-summary']//div[@id='tec_price']//b")

            status, description_div = self.selenium_helper.find_xpath_elements(self.driver,
                "//div[@class='woocommerce-product-details__short-description']/p")

            description_items = description_div

            # Extract text from each li element and concatenate them with commas
            description_text = ", ".join(
                item.text for item in description_items)

            status, product_images = self.selenium_helper.find_xpath_elements(
                self.driver,
                "//div[@data-thumb]")
            # image_urls_products = product_images.get_attribute("data-thumb")

            image_urls_products = []
            modified_image_urls = []

            # Iterate through each image element and extract the data-thumb attribute
            for image_element in product_images:
                image_url = image_element.get_attribute("data-thumb")
                # Remove the "-100x100" part from the URL
                modified_url = image_url.replace("-100x100.jpg", ".jpg")
                modified_image_urls.append(modified_url)

            # Now you can use the modified_image_urls list for further processing

            # image_urls_products = [figure.get_attribute("data-thumb") for figure in
            #                        product_images]

            status, image_urls = self.selenium_helper.find_xpath_elements(
                self.driver,
                "//ol[@class='flex-control-nav flex-control-thumbs']//img")

            if image_urls:  # Check if `image_urls` is not empty and contains WebElement objects
                # Extracting the src attribute from each WebElement object
                image_urls_extracted = [element.get_attribute("src").replace("-100x100.jpg", ".jpg") for element in
                                        image_urls]
            else:
                # Handle the case where no image URLs were found
                image_urls_extracted = []

            # image_urls = [figure.get_attribute("data-thumb") for figure in
            #               product_images]



            # image_urls = [figure.get_attribute("data-thumb") for figure in
            #               product_images]
            #
            # status, product_category = self.selenium_helper.find_xpath_element(
            #     self.driver,
            #     "//div[@class='summary entry-summary']//span[@class='loop-product-categories']")

            data.append({
                'Product Name': product_name.text,
                'Cost Price' : cost_price,
                'Market Price' :market_price,
                'Product Description_text' : descriptions,
                # 'Product Price': prices,
                # 'Product Total Price': product_total_price.text,
                'Product Description': description_text,
                'Product Image':image_urls_extracted,
                'Image URLs' : modified_image_urls
                # 'Product Category': product_category.text
            })

        df = pd.DataFrame(data)
        df.to_csv('products.csv', index=False)
        self.driver.quit()
        return df