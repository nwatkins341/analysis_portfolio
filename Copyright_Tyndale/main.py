# Import statements
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from random import uniform
import os

# Global Variables
FILEPATH = '/Users/noah/Desktop/Blanks.xlsx'
CSV_FILEPATH = '/Users/noah/Desktop/progress.csv'
SEARCH_ADDRESS = 'https://publicrecords.copyright.gov/advanced-search'
RETRY_LIMIT = 2
SLEEP_MIN = 3.0
SLEEP_MAX = 6.0
LOAD_DELAY = 3
START_INDEX = 0
processed_rows_count = 0
SAVE_CONSTANT = 50

# Read in Excel File
df = pd.read_excel(FILEPATH, dtype={'ISBN': str})

# Setting up Chrome WebDriver and launching instance
#ChromeDriverManager().install()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
driver.get(SEARCH_ADDRESS)
sleep(LOAD_DELAY)

# Changing Initial ISBN settings
driver.find_element(  # Open menu
    by=By.XPATH,
    value='//*[@id="input-field-heading"]'
).click()
driver.find_element(  # Select ISBN
    by=By.XPATH,
    value='//*[@id="cprs-advanced-search"]/div[2]/cprs-advanced-search-row/form/div/div[1]/cprs-mega-mini-menu/form/div[2]/div/div[3]/ul[1]/li[2]/cd-button'
).click()
driver.find_element(  # Select exact match
    by=By.XPATH,
    value='//*[@id="input-search-type"]/option[3]'
).click()

# Iterating through rows
new_rows = []
for index, row in df.iloc[START_INDEX:].iterrows():
    print(f'{index}: {row.ISBN}')
    retries = 0
    while retries < RETRY_LIMIT:  # The retries counter checks how many times the operation has been retried. After 2, it prints an error.
        try:
            search_bar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="input-"]'))
            )
            search_bar.send_keys(f'{row.ISBN}')
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="cprs-advanced-search"]/div[2]/cprs-advanced-search-row/form/div/div[4]/cd-button-group/cd-button[1]/button'))
            )
            search_button.click()
            sleep(LOAD_DELAY)  # Delay to let the page load

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
                new_rows.append(new_row)
                processed_rows_count += 1
                sleep(round(uniform(SLEEP_MIN, SLEEP_MAX), 1))  # Random time delay to prevent being recognized as a DOD attack
                retries = RETRY_LIMIT
            else:
                divs = driver.find_elements(   # Locate all entries
                by=By.CLASS_NAME,
                value='table.cd.table.table-bordered.table-hover.table-striped.m-0 tbody > div'
                )
                # Loop through entries and pull information as text
                for div in divs:
                    list_items = div.find_elements(
                        by=By.CSS_SELECTOR,
                        value='li'
                    )
                    items = []
                    for list_item in list_items:  # Cleaning up the scraped text
                        list_item = list_item.text
                        cleaned_item = list_item.split(':')[1].strip().rstrip('.').rstrip(',')
                        items.append(cleaned_item)
                    new_row = {
                        'workID': row['workID'],
                        'ISBN': row['ISBN'],
                        'Copyright_Title': items[0],
                        'Registration_Number': items[1],
                        'Date': items[2],
                        'Type': items[3],
                        'Claimant': items[4]
                    }
                    new_rows.append(new_row)
                    processed_rows_count += 1
                    sleep(round(uniform(SLEEP_MIN, SLEEP_MAX), 1))  # Random time delay to prevent being recognized as a DOD attack
                retries = RETRY_LIMIT
            search_bar.clear()
        except:
            driver.find_element(  # Exit popup
                by=By.XPATH,
                value='//*[@id="main-content"]/app-popup-survey/cd-modal/div/div/div/div[4]/div/cd-button[1]/button'
            ).click()
            retries += 1
            if retries == RETRY_LIMIT:  # Preferable to logging in this case because of stakeholder use case
                new_row = {
                    'workID': row['workID'],
                    'ISBN': row['ISBN'],
                    'Copyright_Title': "ERROR",
                    'Registration_Number': "ERROR",
                    'Date': "ERROR",
                    'Type': "ERROR",
                    'Claimant': "ERROR"
                }
                new_rows.append(new_row)
                processed_rows_count += 1
    if processed_rows_count % SAVE_CONSTANT == 0:
        # Save the progress to a CSV file
        file_exists = os.path.isfile(CSV_FILEPATH)
        temp_df = pd.DataFrame(new_rows)
        temp_df.to_csv(CSV_FILEPATH, mode='a', header=not file_exists, index=False)
        print(f"Progress saved at row {processed_rows_count}")

# Saving new dataframe over previous Excel file
new_df = pd.DataFrame(new_rows)
new_df = new_df.sort_values(by=['workID', 'ISBN'])
new_df.to_excel(FILEPATH, index=False)

# Closing the driver to free memory
driver.quit()
