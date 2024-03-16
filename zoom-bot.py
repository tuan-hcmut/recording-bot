import asyncio
import os
import subprocess
import datetime
import requests
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from time import sleep

import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def zoom_bot():
    options = uc.ChromeOptions()

    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    log_path = "chromedriver.log"

    driver = uc.Chrome(service_log_path=log_path, use_subprocess=False, options=options)

    driver.set_window_size(1920, 1080)


    # delete the folder screenshots if it exists even if not empty
    print("Cleaning screenshots")
    if os.path.exists("screenshots"):
        # for each file in the folder delete it
        for f in os.listdir("screenshots"):
            os.remove(f"screenshots/{f}")
    else:
        os.mkdir("screenshots")
    driver.execute_cdp_cmd(
            "Browser.grantPermissions",
            {
                "origin": "https://zoom.us/wc/join/81279067723",
                "permissions": [
                    "geolocation",
                    "audioCapture",
                    "displayCapture",
                    "videoCapture",
                    "videoCapturePanTiltZoom",
                ],
            },
        )
# Join Zoom Meeting
# https://us05web.zoom.us/j/82065192143?pwd=2TcHb8SF83x5jNZcEnpnHavw9RLPdw.1

# Meeting ID:  820 6519 2143
# Passcode: 6XnUSa




    driver.get(f'https://zoom.us/wc/join/82065192143')
    driver.save_screenshot("screenshots/initial1.png")
    driver.implicitly_wait(10) #Wait untils tabs loaded
    driver.find_element(By.ID, 'input-for-pwd').send_keys("6XnUSa")
    driver.find_element(By.ID, 'input-for-name').send_keys("test1")
    driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/button').click()
    driver.implicitly_wait(15)
    driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[2]/div/div[1]/div[1]/footer/div[1]/div[1]/div[1]/button').click()
    driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[2]/div/div[1]/div[1]/div[8]/div[2]/div/div[2]/div/button').click()
    driver.save_screenshot("screenshots/initial2.png")
    sleep(3242341)

    driver.quit()

# Call the zoom_bot function
if __name__ == "__main__":
    asyncio.run(zoom_bot())
