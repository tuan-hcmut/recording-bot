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

        s3.upload_file(local_file_path, s3_bucket_name, object_name, ExtraArgs={'ACL': 'public-read'})
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
                "origin": "https://google.com",
                "permissions": [
                    "geolocation",
                    "audioCapture",
                    "displayCapture",
                    "videoCapture",
                    "videoCapturePanTiltZoom",
                ],
            },
        )


    driver.get(f'https://google.com')
    sleep(5)
    driver.save_screenshot("screenshots/initial1.png")
    upload_to_s3('screenshots/initial1.png', 'qlay-recording', f"{datetime.utcnow()}.png")

    duration = os.getenv("DURATION_IN_MINUTES", 1)
    duration = int(duration) * 60

    print("Start recording")
    record_command = f"ffmpeg -y -video_size 1920x1080 -framerate 30 -f x11grab -i :99 -f pulse -i default -t {duration} -c:v libx264 -pix_fmt yuv420p -c:a aac -strict experimental recordings/output.mp4"

    await asyncio.gather(
        run_command_async(record_command),
    )

    print("Done recording")
    upload_to_s3('recordings/output.mp4', 'qlay-recording', f"{datetime.utcnow()}.mp4")


if __name__ == "__main__":
    asyncio.run(join_meet())
