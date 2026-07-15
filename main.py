import os
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

AUTOMATION_EMAIL = os.environ["AUTOMATION_EMAIL"]
AUTOMATION_PASSWORD = os.environ["AUTOMATION_PASSWORD"]
AUTOMATION_PHONENUMBER = os.environ["AUTOMATION_PHONENUMBER"]

url = "https://eastmeadow.libcal.com/ajax/calendar/list"

params = {
    "c": 20871,
    "date": "0000-00-00",
    "perpage": 500,
    "page": 1,
    "audience": "",
    "cats": "76973, 76959, 76952",
    "camps": "undefined",
    "inc": 0,
}

response = requests.get(url, params=params, timeout=10)

# Raise an exception if the request failed (404, 500, etc.)
response.raise_for_status()

# Parse the JSON into Python objects
data = response.json()

#print(data["results"][0].keys())

#print(type(data))

now = datetime.now()
msg_string = "Library Activity Alert: \n"
for record in data["results"]:
    seats = record.get("seatsleft")
    date_check = datetime.strptime(record.get("startdt"), "%Y-%m-%d %H:%M:%S")
    reg_open = (date_check - timedelta(days=14))


    if reg_open.date() == now.date():
        msg_string += f"{record.get('startdt')} - {record['title']} - Registration Open: {record.get('registration_enabled')} - Seats Available: {record.get('seatsleft_text')}\n"
        msg_string += f"{record.get('url')}"
        #print(f"{record.get('startdt')} - {record['title']} - Registration Open: {record.get('registration_enabled')} - Seats Available: {record.get('seatsleft_text')}")
        #print(f"{record.get('url')}")
        #print()


msg = EmailMessage()

msg["From"] = AUTOMATION_EMAIL
msg["To"] = AUTOMATION_PHONENUMBER
msg["Subject"] = ""

msg.set_content(msg_string)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(AUTOMATION_EMAIL, AUTOMATION_PASSWORD)
    #print(repr(msg))
    smtp.send_message(msg)