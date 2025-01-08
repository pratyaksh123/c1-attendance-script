import asyncio
import json
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

async def collect_data_for_month(driver, month_value, start_date, end_date):
    sanitized_data = []

    # Wait for the month selection dropdown to be visible
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "SelectedMonth"))
    )
    select_input_element = driver.find_element(By.ID, "SelectedMonth")
    select = Select(select_input_element)

    # Select the month value and wait for the page to update
    select.select_by_value(month_value)
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, "SelectedMonth").get_attribute("value") == month_value
    )

    # Submit the form
    submit_button = driver.find_element(By.XPATH, submitButtonXPath)
    submit_button.click()

    # Wait for the detailed report button and click it
    link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, detailedUsageReportButtonXPath))
    )
    link.click()

    # Switch to the new window
    all_windows = driver.window_handles
    driver.switch_to.window(all_windows[-1])

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Fetch rows
    rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'table-row')]")
    print(f"Rows found: {len(rows)}")

    # Extract and print data from rows
    for row in rows:
        columns = row.find_elements(By.CSS_SELECTOR, "div")
        row_data = [col.text.strip() for col in columns if col.text.strip()]
        if len(row_data) >= 8:  # Ensure sufficient columns exist
            visit_date = datetime.strptime(row_data[2], '%m/%d/%Y %I:%M:%S %p')
            if start_date <= visit_date <= end_date and row_data[4] == "Exit" and row_data[7] == "McLean":
                sanitized_data.append({
                    "visit_date": visit_date.isoformat(),
                    "details": row_data
                })

    # Close the detailed report window and switch back
    driver.close()
    driver.switch_to.window(all_windows[0])

    return sanitized_data

def setup_driver():
    """Sets up the WebDriver with headless mode."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run browser in headless mode
    options.add_argument('--disable-gpu')  # Disable GPU acceleration (optional)
    options.add_argument('--window-size=1920,1080')  # Set browser window size (optional)
    options.add_argument('--no-sandbox')  # Bypass OS security model (optional for Linux)
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    return webdriver.Chrome(options=options)

async def main():
    username = os.getenv('username')
    password = os.getenv('password')
    card_index = os.getenv('card_index')
    global submitButtonXPath, detailedUsageReportButtonXPath
    submitButtonXPath = "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/div/div[2]/form/div[9]/div[1]/button"
    detailedUsageReportButtonXPath = "//*[@id=\"async-view\"]/div[2]/div/a"

    # File to store data
    data_file = Path("usage_data.json")
    if data_file.exists():
        try:
            with open(data_file, "r") as f:
                all_data = json.load(f)
        except (json.JSONDecodeError, ValueError):  # Handle invalid or empty JSON
            print("Invalid or empty JSON file. Starting fresh.")
            all_data = {}
    else:
        all_data = {}

    # Set up WebDriver
    driver = setup_driver()
    try:
        driver.get('https://smartrip.wmata.com/Account/AccountLogin.aspx')

        # Log in
        driver.find_element(By.ID, 'UserName').send_keys(username)
        driver.find_element(By.ID, 'Password').send_keys(password)
        driver.find_element(By.XPATH, "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/form/div[3]/div/button").click()

        # Choose the card to get data for
        card_list = driver.find_elements(By.CLASS_NAME, "cardInfo")
        card_list[card_index].click()

        # Go to usage history
        use_history = driver.find_element(By.XPATH, "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/div/div[1]/div/div/div/div[2]/p[3]/a")
        use_history.click()

        # Define date range
        start_date = datetime.strptime("2024-10-18", "%Y-%m-%d")
        end_date = datetime.strptime("2024-12-15", "%Y-%m-%d")
        
        # Get all relevant months
        months = get_months_in_range(start_date, end_date)[::-1]
        print("Months in range", months)
        
        total_valid_visits = 0

        # Collect data for each month sequentially
        for month_value in months:
            if month_value in all_data:
                print(f"Skipping {month_value}, already in local data.")
                continue

            print(f"Processing month: {month_value}")
            month_data = await collect_data_for_month(driver, month_value, start_date, end_date)
            all_data[month_value] = month_data
            total_valid_visits += len(month_data)

            # Navigate back
            back_button = driver.find_element(By.XPATH, "//*[@id=\"form\"]/div[2]/div[2]/button")
            back_button.click()

        # Save updated data to the file
        with open(data_file, "w") as f:
            json.dump(all_data, f, indent=4)

        print(f"Collected data for {len(all_data)} months. Total valid visits {total_valid_visits}")

    finally:
        driver.quit()


# Helper function to get all months in range
def get_months_in_range(start_date, end_date):
    months = []
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        months.append(current_date.strftime("%Y%m"))
        current_date += timedelta(days=32)  # Advance by roughly 1 month
        current_date = current_date.replace(day=1)  # Reset to the 1st of the month
    return months


# Run the async program
asyncio.run(main())
