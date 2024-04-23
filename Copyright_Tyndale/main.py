# Import statements
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from random import uniform
from time import sleep
import os

# Global Variables
FILEPATH = '/Users/noah/Desktop/Missing_Copyright_revised_v1_to_Noah.xlsx'
CSV_FILEPATH = '/Users/noah/Desktop/progress.csv'
SEARCH_ADDRESS = 'https://publicrecords.copyright.gov/advanced-search'
RETRY_LIMIT = 2
SLEEP_MIN = 3.0
SLEEP_MAX = 6.0
START_INDEX = 0  # Allows program to start anywhere in the Excel file if needed
processed_rows_count = 0
SAVE_CONSTANT = 50  # Saves the df every 50 rows in case of failure

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

# Iterating through rows
existing_df = pd.DataFrame()
new_rows = []
for index, row in df.iloc[START_INDEX:].iterrows():
    print(f'{index}: {row.ISBN}')
    retries = 0
    while retries < RETRY_LIMIT:
        try:
            # Use WebDriverWait to wait for the search bar to be clickable
            search_bar = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="input-"]')))
            search_bar.clear()
            search_bar.send_keys(f'{row.ISBN}')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cprs-advanced-search"]/div[2]/cprs-advanced-search-row/form/div/div[4]/cd-button-group/cd-button[1]/button'))).click()
            try:
                sleep(SLEEP_MIN)
                text = driver.find_element(
                    by=By.XPATH,
                    value='//*[@id="cprs-search-results-on-advanced-search"]/cprs-module-search-results/div/app-loading-overlay/div/div[2]/div[1]/div[2]/div/div[1]'
                ).text
                print(text)
                if text == "No search results were found":
                    # No entries found, add a row with empty copyright info
                    blank_row = {
                        'workID': row['workID'],
                        'ISBN': row['ISBN'],
                        'Copyright_Title': "",
                        'Registration_Number': "",
                        'Date': "",
                        'Type': "",
                        'Claimant': ""
                    }
                    processed_rows_count += 1
                    new_rows.append(blank_row)
                    print(blank_row)
                    sleep(round(uniform(SLEEP_MIN, SLEEP_MAX), 1))
                    retries = RETRY_LIMIT
            except NoSuchElementException:
                # Wait for the divs to be present
                divs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table.cd.table.table-bordered.table-hover.table-striped.m-0 tbody > div')))
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
                    print(new_row)
                    processed_rows_count += 1
                    if new_row not in new_rows:
                        new_rows.append(new_row)
                sleep(round(uniform(SLEEP_MIN, SLEEP_MAX), 1))  # Random time delay to prevent being recognized as a DOD attack
                retries = RETRY_LIMIT
        except StaleElementReferenceException:
            # If a StaleElementReferenceException is caught, retry
            print("Encountered a stale element, retrying...")
            retries += 1
        except Exception as e:
            driver.find_element(  # Exit popup
                by=By.XPATH,
                value='//*[@id="main-content"]/app-popup-survey/cd-modal/div/div/div/div[4]/div/cd-button[1]/button'
            ).click()
            retries += 1
    if processed_rows_count % SAVE_CONSTANT == 0: # TODO: OR WHEN END OF SCRIPT
        # Check if the CSV file exists and is not empty
        file_exists = os.path.isfile(CSV_FILEPATH) and os.path.getsize(CSV_FILEPATH) > 0

        # Create a DataFrame from new rows
        temp_df = pd.DataFrame(new_rows)

        # If the file doesn't exist or is empty, write with header
        # Otherwise, append without header
        if not file_exists:
            temp_df.to_csv(CSV_FILEPATH, mode='w', header=True, index=False)
            existing_df = temp_df.copy()
        else:
            temp_df.to_csv(CSV_FILEPATH, mode='a', header=False, index=False)
            # Update existing_df with the newly appended data
            existing_df = pd.concat([existing_df, temp_df])

        print(f"Progress saved at row {processed_rows_count}")

        # Reset new_rows for the next batch
        new_rows = []


# Read the data from the CSV file
final_df = pd.read_csv(CSV_FILEPATH)

# Sort the DataFrame if necessary
final_df = final_df.sort_values(by=['workID', 'ISBN'])

# Write the sorted data to the Excel file, overwriting any existing data
final_df.to_excel(FILEPATH, index=False)

# Inform about the completion
print("Data successfully written to the Excel file.")


# Closing the driver to free memory
driver.quit()
