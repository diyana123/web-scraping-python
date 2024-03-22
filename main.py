import traceback

from helpers.helper import SeleniumHelper
from sources.Scrapper import OTCProductScraper
import pandas as pd
import time
import urllib


def main():
    obj1 = SeleniumHelper()
    obj1.check_connection()
    driver = obj1.init_chrome_driver()

    obj2 = OTCProductScraper(obj=obj1)
    # df = obj2.scrape_data()
    # obj2.remove_duplicates()
    # obj2.scrape_products()

main()