import os
import json
import requests
from datetime import datetime, timedelta

AUTOMATION_EMAIL = os.environ["AUTOMATION_EMAIL"]
AUTOMATION_PASSWORD = os.environ["AUTOMATION_PASSWORD"]
AUTOMATION_PHONENUMBER = os.environ["AUTOMATION_PHONENUMBER"]
TEXTBEE_API_KEY = os.environ["TEXTBEE_API_KEY"]
TEXTBEE_DEVICE_ID = os.environ["TEXTBEE_DEVICE_ID"]

def send_sms(to: str, body: str) -> dict:
    response = requests.post(
        f"https://api.textbee.dev/api/v1/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms",
        json={"recipients": [to], "message": body},
        headers={"x-api-key": TEXTBEE_API_KEY},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
    

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
        if registration_msg and registration_msg.startswith("Registrations open at"):
            date_str = registration_msg.replace("Registrations open at", "").strip()
            registration_msg_check = datetime.strptime(date_str, "%I:%M%p %A, %B %d, %Y")
        else:
            registration_msg_check = None

    else:
        registration_msg_check =  None

    if registration_msg_check and registration_msg_check.date() <= now.date() + timedelta(days=2):
        restricted_list.append(record)
    elif two_week_check.date() == now.date() and registration_msg_check is None:
        sign_up_list.append(record)

#print(json.dumps(sign_up_list, indent=4))
#print("---")
#print(json.dumps(restricted_list, indent=4))

max_msg_length = 2000

if len(sign_up_list) != 0:
    for each_subscriber in subscribers:
        msg_string = "Library Activity Two Week Alert: \n"
        for record in sign_up_list:
            for each_cat in record["categories_arr"]:
                for each_category in each_subscriber["categories"]:
                    if each_cat.get("cat_id") == each_category:
                        if len(msg_string) > max_msg_length:
                            api_response = send_sms(each_subscriber.get("phone"), msg_string)
                            print(api_response)
                            msg_string = "Library Activity Two Week Alert: \n"
                        msg_string += f"{record.get('fromTime')} - {record['title']}\n"
                        msg_string += f"{record.get('url')}\n\n"

        if msg_string != "Library Activity Two Week Alert: \n":
            api_response = send_sms(each_subscriber.get("phone"), msg_string)
            print(api_response)
        

if len(restricted_list) != 0:
    for each_subscriber in subscribers:
        msg_string = "Library Activity Registration Opening Alert: \n"
        for record in restricted_list:
            for each_cat in record["categories_arr"]:
                for each_category in each_subscriber["categories"]:
                    if each_cat.get("cat_id") == each_category:
                        if len(msg_string) > max_msg_length:
                            api_response = send_sms(each_subscriber.get("phone"), msg_string)
                            print(api_response)
                            msg_string = "Library Activity Registration Opening Alert: \n"
                        msg_string += f"{record.get('fromTime')} - {record['title']}\n"
                        msg_string += f"{record.get('registration_msg', {}).get('msg')}\n"
                        msg_string += f"{record.get('url')}\n\n"

        if msg_string != "Library Activity Registration Opening Alert: \n":
            api_response = send_sms(each_subscriber.get("phone"), msg_string)
            print(api_response)