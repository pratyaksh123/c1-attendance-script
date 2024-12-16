import time

from selenium import webdriver
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException      

        
if __name__ == "__main__":
    username = "pratyaksh5676"
    password = "Pratyaksh5676*"
    loginButtonXPath = "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/form/div[3]/div/button"
    useHistoryXPath = "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/div/div[1]/div/div/div/div[2]/p[3]/a"
    submitButtonXPath = "//*[@id=\"mm-0\"]/div/div[1]/div/div[2]/div/div[2]/form/div[9]/div[1]/button"
    detailedUsageReportButtonXPath = "//*[@id=\"async-view\"]/div[2]/div/a"
    try: 
        driver = webdriver.Chrome()
        baseURL = r'https://smartrip.wmata.com/Account/AccountLogin.aspx'
        driver.get(baseURL)
        
        
        
    finally:
        # driver.quit()
        pass
        time.sleep(5000)
        driver.close()