import os
import json
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

AUTOMATION_EMAIL = os.environ["AUTOMATION_EMAIL"]
AUTOMATION_PASSWORD = os.environ["AUTOMATION_PASSWORD"]
AUTOMATION_PHONENUMBER = os.environ["AUTOMATION_PHONENUMBER"]

'''uncomment to load secrets from .env
with open(".env", "r") as file:
    config = json.load(file)
'''

config = json.loads(os.environ["CONFIG_JSON"])

libraries = config["libraries"]
subscribers = config["subscribers"]

data_list = []
for library_name, library in libraries.items():

    params = {
        "c": -1,
        "date": "0000-00-00",
        "perpage": 500,
        "page": 1,
        "audience": "",
        "cats": library["cats"],
        "camps": "undefined",
        "inc": 0,
    }

    response = requests.get(
        library["url"],
        params=params
    )

    response.raise_for_status()

    data = response.json()
    data_list.extend(data["results"])



now = datetime.now()
sign_up_list = []
restricted_list = []
for record in data_list:
    seats = record.get("seatsleft")
    date_check = datetime.strptime(record.get("startdt"), "%Y-%m-%d %H:%M:%S")
    two_week_check = (date_check - timedelta(days=14))
    if not record.get("registration_enabled"):
        registration_msg = record.get("registration_msg", {}).get("msg")
        if registration_msg:
            date_str = registration_msg.replace("Registrations open at ", "").strip()
            registration_msg_check = datetime.strptime(date_str, "%I:%M%p %A, %B %d, %Y")
        else:
            registration_msg_check = datetime(1999, 1, 1)

    else:
        registration_msg_check = datetime(1999, 1, 1)

    if registration_msg_check.date() == now.date():
        restricted_list.append(record)
    elif two_week_check.date() == now.date():
        sign_up_list.append(record)

msg_string = "Library Activity Alert: \n"
if len(sign_up_list) != 0:
    for each_subscriber in subscribers:
        for record in sign_up_list:
            for each_cat in record["categories_arr"]:
                for each_category in each_subscriber["categories"]:
                    if each_cat.get("cat_id") == each_category:
                        msg_string += f"{record.get('fromTime')} - {record['title']}\n"
                        msg_string += f"{record.get('url')}\n\n"

if len(restricted_list) != 0:
    for each_subscriber in subscribers:
        msg_string = "Library Activity Alert: \n"
        for record in restricted_list:
            for each_cat in record["categories_arr"]:
                for each_category in each_subscriber["categories"]:
                    if each_cat.get("cat_id") == each_category:
                        msg_string += f"{record.get('fromTime')} - {record['title']}\n"
                        msg_string += f"{record.get('registration_msg', {}).get('msg')}\n"
                        msg_string += f"{record.get('url')}\n\n"

        msg = EmailMessage()

        msg["From"] = AUTOMATION_EMAIL
        msg["To"] = each_subscriber.get("phone")
        msg["Subject"] = ""

        msg.set_content(msg_string)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(AUTOMATION_EMAIL, AUTOMATION_PASSWORD)
            smtp.send_message(msg)