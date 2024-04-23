# Import statements
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from random import uniform
from time import sleep
import os

# Global Variables
FILEPATH = '/Users/noah/Desktop/Blanks.xlsx'
CSV_FILEPATH = '/Users/noah/Desktop/progress.csv'
SEARCH_ADDRESS = 'https://publicrecords.copyright.gov/advanced-search'
RETRY_LIMIT = 2
SLEEP_MIN = 5.0
SLEEP_MAX = 10.0
START_INDEX = 0
processed_rows_count = 0
SAVE_CONSTANT = 50

# Read in Excel File
df = pd.read_excel(FILEPATH, dtype={'ISBN': str})

# Setting up Chrome WebDriver and launching instance
# ChromeDriverManager().install()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
driver.get(SEARCH_ADDRESS)

# WebDriverWait setup
wait = WebDriverWait(driver, 10)

# Changing Initial ISBN settings
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="input-field-heading"]'))).click()
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cprs-advanced-search"]/div[2]/cprs-advanced-search-row/form/div/div[1]/cprs-mega-mini-menu/form/div[2]/div/div[3]/ul[1]/li[2]/cd-button'))).click()
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="input-search-type"]/option[3]'))).click()

try:
    # Use WebDriverWait to wait for the search bar to be clickable
    search_bar = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="input-"]')))
    search_bar.clear()
    search_bar.send_keys('9781496445834')
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cprs-advanced-search"]/div[2]/cprs-advanced-search-row/form/div/div[4]/cd-button-group/cd-button[1]/button'))).click()

    text = driver.find_element(
        by=By.XPATH,
        value='//*[@id="cprs-search-results-on-advanced-search"]/cprs-module-search-results/div/app-loading-overlay/div/div[2]/div[1]/div[2]/div/div[1]'
    ).text
    print(text)
    if text == "No search results were found":
        # No entries found, add a row with empty copyright info
        new_row = {
            'workID': row['workID'],
            'ISBN': row['ISBN'],
            'Copyright_Title': "",
            'Registration_Number': "",
            'Date': "",
            'Type': "",
            'Claimant': ""
        }

except Exception as e:
    print(e)
