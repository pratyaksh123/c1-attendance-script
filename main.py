import time

from selenium import webdriver
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException      

driver = webdriver.Chrome()

baseURL = r'https://smartrip.wmata.com/Account/AccountLogin.aspx'
driver.get(baseURL)

"""
User Name Xpath: //*[@id="ctl00_ctl00_MainContent_MainContent_txtUsername"]
Password: //*[@id="ctl00_ctl00_MainContent_MainContent_txtPassword"]
Log In BUtton: //*[@id="ctl00_ctl00_MainContent_MainContent_btnSubmit"]
"""

username = "pratyaksh5676"
password = "Pratyaksh5676*"
loginButtonXPath = "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/form/div[3]/div/button"
useHistoryXPath = "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/div/div[1]/div/div/div/div[2]/p[3]/a"
submitButtonXPath = "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/div/div[2]/form/div[9]/div[1]/button"
detailedUsageReportButtonXPath = "//*[@id=\"async-view\"]/div[2]/div/a"

try:
    # Login into Wmata website

    userNameElement = driver.find_element(By.ID, 'UserName')
    userNameElement.send_keys(username)

    passwordElement = driver.find_element(By.ID, 'Password')
    passwordElement.send_keys(password)

    loginButton = driver.find_element(By.XPATH, loginButtonXPath)
    loginButton.click()

    # Choose the card to get data for

    cardIndex = 1

    cardList = driver.find_elements(By.CLASS_NAME, "cardInfo")
    card = cardList[cardIndex]
    card.click()

    # get useHistory

    useHistory = driver.find_element(By.XPATH, useHistoryXPath)
    useHistory.click()

    # Fetch the useHistory by start and end dates

    startDate = '09/15/2024'
    enddate = '12/15/2024'

    submitButton = driver.find_element(By.XPATH, submitButtonXPath)
    submitButton.click()


    link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, detailedUsageReportButtonXPath))
        )
    link.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Fetch rows again
    rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'table-row')]")
    print(f"Rows found: {len(rows)}")

    # Extract and print data from rows
    for row in rows:
        columns = row.find_elements(By.CSS_SELECTOR, "div")
        row_data = [col.text.strip() for col in columns]
        print(row_data)

finally:
    # driver.quit()
    time.sleep(5000)
    driver.close()