import traceback
import requests
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from wasabi import msg
from selenium.webdriver.support import expected_conditions as EC

import time


from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class SeleniumHelper:
    def __init__(self):
        self.CHROME_DRIVER_PATH = "./drivers/chromedriver"
        self.options = Options()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('ignore-ssl-errors')

    def init_chrome_driver(self):
        service = Service(executable_path=self.CHROME_DRIVER_PATH)
        driver = Chrome(service=service, options=self.options)
        return driver

    def check_connection(self):
        connection = False
        try_count = 1
        while not connection:
            try:
                var = requests.get('https://www.google.com/',
                                   timeout=30).status_code
                connection = True
                print("Internet connected...")
            except:
                connection = False
                print("No internet connection... Check count: ", try_count)
                time.sleep(5)
                try_count += 1

    def find_xpath_element(self, driver, xpath, is_get_text=False):
        try:
            if is_get_text:
                return True, driver.find_element(by=By.XPATH, value=xpath).text
            else:
                return True, driver.find_element(by=By.XPATH, value=xpath)
        except:
            return False, None

    def find_xpath_elements(self, driver, xpath, is_get_text=False):
        try:
            if is_get_text:
                return True, driver.find_elements(by=By.XPATH, value=xpath).text
            else:
                return True, driver.find_elements(by=By.XPATH, value=xpath)
        except:
            return False, None

    def driver_execute(self, driver, program):
        try:
            driver.execute_script(program)
        except:
            traceback.print_exc()

    def sleep_time(self, val):
        time.sleep(val)

    def click_xpath(self, driver, xpath):
        try:
            driver.find_element(by=By.XPATH, value=xpath).click()
            msg.good('click_xpath pass')
            return True
        except:
            msg.fail('click_xpath fail')
            return False

    def find_elements_by_xpath(self, driver, xpath):
        try:
            elements = driver.find_elements_by_xpath(xpath)
            return elements
        except Exception as e:
            print(f"An error occurred while finding elements by XPath: {e}")
            return None

    def driver_scroll_down(self, web_driver, scroll_count=int, y_down=int,
                           waiting_time=float):
        try:
            msg.info('driver_scroll_down start')
            for i in tqdm(range(scroll_count)):
                from_no = 0
                web_driver.execute_script(
                    "window.scrollTo(" + str(from_no) + ", " + str(
                        i * y_down) + ")")
                time.sleep(float(waiting_time))
                from_no += y_down
            msg.info('driver_scroll_down finish')
            return True
        except:
            msg.fail('driver_scroll_down fail')
            return False
