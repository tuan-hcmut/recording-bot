import asyncio
import os
import subprocess
import requests
import json
import boto3
from datetime import datetime

from time import sleep

import undetected_chromedriver as uc

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def upload_to_s3(local_file_path, s3_bucket_name, object_name=None):
    s3 = boto3.client('s3', aws_access_key_id="AKIA3Z4NVYHGH6MYOUPV", aws_secret_access_key="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",
                       region_name="us-east-1")
    try:

        s3.upload_file(local_file_path, s3_bucket_name, object_name)
        print(f"File uploaded to {object_name} in {s3_bucket_name}")
        return True
    except Exception as e:
        print(e)
        return False
    
async def run_command_async(command):
    process = await asyncio.create_subprocess_shell(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Wait for the process to complete
    stdout, stderr = await process.communicate()

    return stdout, stderr

async def join_meet():
    time = datetime.utcnow()
    print("starting virtual audio drivers")
    # find audio source for specified browser
    subprocess.check_output(
        "sudo rm -rf /var/run/pulse /var/lib/pulse /root/.config/pulse", shell=True
    )
    subprocess.check_output(
        "sudo pulseaudio -D --verbose --exit-idle-time=-1 --system --disallow-exit  >> /dev/null 2>&1",
        shell=True,
    )
    subprocess.check_output(
        'sudo pactl load-module module-null-sink sink_name=DummyOutput sink_properties=device.description="Virtual_Dummy_Output"',
        shell=True,
    )

    subprocess.check_output(
        'sudo pactl load-module module-null-sink sink_name=MicOutput sink_properties=device.description="Virtual_Microphone_Output"',
        shell=True,
    )
    subprocess.check_output(
        "sudo pactl set-default-source MicOutput.monitor", shell=True
    )
    subprocess.check_output("sudo pactl set-default-sink MicOutput", shell=True)
    subprocess.check_output(
        "sudo pactl load-module module-virtual-source source_name=VirtualMic",
        shell=True,
    )

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
                "origin": "https://zoom.us/wc/join/89624247909",
                "permissions": [
                    "geolocation",
                    "audioCapture",
                    "displayCapture",
                    "videoCapture",
                    "videoCapturePanTiltZoom",
                ],
            },
        )


    duration = os.getenv("DURATION_IN_MINUTES", 1)
    duration = 30

# Join Zoom Meeting
# https://us06web.zoom.us/j/89624247909?pwd=c2J5VzZ6dzZUbUg1emUwWGlCcE1JZz09

# Meeting ID:  896 2424 7909
# Passcode: 617108
    
    driver.get(f'https://zoom.us/wc/join/89624247909')
    driver.implicitly_wait(5) #Wait untils tabs loaded
    driver.save_screenshot("screenshots/main-page.png")
    upload_to_s3('screenshots/main-page.png', 'qlay-recording', f"{time}.png")
    driver.find_element(By.ID, 'input-for-pwd').send_keys("617108")
    driver.find_element(By.ID, 'input-for-name').send_keys("Qlay-bot")
    driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/button').click()
    driver.implicitly_wait(10)
    driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[2]/div/div[1]/div[1]/footer/div[1]/div[1]/div[1]/button').click()
    driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[2]/div/div[1]/div[1]/div[8]/div[2]/div/div[2]/div/button').click()
    driver.save_screenshot("screenshots/c.png")
    upload_to_s3('screenshots/joined.png', 'qlay-recording', f"{time}.png")

    print("Start recording")
    record_command = f"ffmpeg -y -video_size 1920x1080 -framerate 30 -f x11grab -i :99 -f pulse -i default -t {duration} -c:v libx264 -pix_fmt yuv420p -c:a aac -strict experimental recordings/zoom-{time}.mp4"
    
    await asyncio.gather(
        run_command_async(record_command),
    )
    print("Done recording")
    upload_to_s3(f'recordings/zoom-{time}.mp4', 'qlay-recording', f"{time}.mp4")
    driver.quit()


if __name__ == "__main__":
    asyncio.run(join_meet())
