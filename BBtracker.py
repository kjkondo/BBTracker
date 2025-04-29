import time
import atexit
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

"""
This script uses the Best Buy API to track the availability of Nvidia RTX 3080 GPUs
and sends an alert via email (SMS gateway) when available.

Ensure you have an API key from Best Buy (as of 04/28/2025, available with a custom domain).
"""

# Configuration
API_KEY = '[INSERT API KEY]'
ICLOUD_LOGIN_EMAIL = '[INSERT iCLOUD EMAIL]'
APP_PASSWORD = '[INSERT APP PASSWORD]'
SENDER_EMAIL = '[INSERT EMAIL]'
RECEIVER_EMAIL = '[INSERT EMAIL]'
BASE_URL = 'https://api.bestbuy.com/v1/products'
CATEGORY_ID = 'abcat0507002'  # GPU category
SHOW_FIELDS = (
    'name,onlineAvailability,inStoreAvailability,orderable,url'
)
SORT_ORDER = 'name.dsc'

# Best Buy GPU typical peak update times
PEAK_TIMES = [
    (3.0, 5.5),   # 04:00 - 05:29
]


# Check if current time falls within peak times (supports half-hours)
def is_now_peak():
    now = datetime.now()
    current_time = now.hour + now.minute / 60  # e.g., 19 + 30/60 = 19.5
    return any(start <= current_time < end for start, end in PEAK_TIMES)


# Send email (SMS) notification
def send_email(item=None):
    subject = "SCRIPT EXITING"
    body = "\n!!! SCRIPT IS EXITING !!!"

    if item:
        subject = "ALERT"
        body = f"\n{item['name']}\n{item['url']}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.mail.me.com', 465) as server:
            server.login(ICLOUD_LOGIN_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print(f"Email sent successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Call Best Buy API and check for RTX 5090 availability
def request_data():
    print(f"Tracking executed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    api_url = (
        f"{BASE_URL}(categoryPath.id={CATEGORY_ID})"
        f"?apiKey={API_KEY}&sort={SORT_ORDER}&show={SHOW_FIELDS}&pageSize=100&format=json"
    )

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        products = response.json().get("products", [])
    except Exception as e:
        print(f"API request failed: {e}")
        return

    found = False

    for product in products:
        if "RTX 3080" in product.get('name', '') and product.get('onlineAvailability', False):
            found = True
            print("FOUND!!! ☺☺☺")
            send_email(product)

    if found and is_now_peak():
        print("Tracking pause...")
        time.sleep(5 * 60)  # Sleep 5 min after finding during peak

    print("Tracking restarting...")


# Final goodbye message and notification
def goodbye():
    print("Goodbye! Script is exiting...")
    send_email()


# Main script
if __name__ == "__main__":
    atexit.register(goodbye)
    print("Tracking started...")

    while True:
        request_data()
        if is_now_peak():
            time.sleep(5)  # Check every 5 seconds during peak
        else:
            time.sleep(5 * 60)  # Check every 5 minutes outside peak
