import asyncio
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

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
                    "visit_date": visit_date,
                    "details": row_data
                })

    print(sanitized_data, len(sanitized_data))

    # Close the detailed report window and switch back
    driver.close()
    driver.switch_to.window(all_windows[0])

    return sanitized_data


async def main():
    username = "pratyaksh5676"
    password = "Pratyaksh5676*"
    global submitButtonXPath, detailedUsageReportButtonXPath
    submitButtonXPath = "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/div/div[2]/form/div[9]/div[1]/button"
    detailedUsageReportButtonXPath = "//*[@id=\"async-view\"]/div[2]/div/a"

    # Set up WebDriver
    driver = webdriver.Chrome()
    try:
        driver.get('https://smartrip.wmata.com/Account/AccountLogin.aspx')

        # Log in
        driver.find_element(By.ID, 'UserName').send_keys(username)
        driver.find_element(By.ID, 'Password').send_keys(password)
        driver.find_element(By.XPATH, "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/form/div[3]/div/button").click()

        # Choose the card to get data for
        card_list = driver.find_elements(By.CLASS_NAME, "cardInfo")
        card_list[1].click()

        # Go to usage history
        use_history = driver.find_element(By.XPATH, "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/div/div[1]/div/div/div/div[2]/p[3]/a")
        use_history.click()

        # Define date range
        start_date = datetime.strptime("2024-10-18", "%Y-%m-%d")
        end_date = datetime.strptime("2024-12-15", "%Y-%m-%d")
        
        # Get all relevant months
        months = get_months_in_range(start_date, end_date)[::-1]
        print("Months in range", months)

        # Collect data for each month sequentially
        all_data = []
        for month_value in months:
            print(f"Processing month: {month_value}")
            month_data = await collect_data_for_month(driver, month_value, start_date, end_date)
            all_data.extend(month_data)

            # Navigate back
            back_button = driver.find_element(By.XPATH, "//*[@id=\"form\"]/div[2]/div[2]/button")
            back_button.click()

        print(f"Collected {len(all_data)} records:")
        for record in all_data:
            print(record, end="\n")

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
