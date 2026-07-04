import os
import sqlite3
import time
import requests
from playwright.sync_api import sync_playwright


url = "https://eastmeadow.libcal.com/ajax/calendar/list"

params = {
    "c": 20871,
    "date": "0000-00-00",
    "perpage": 2000,
    "page": 1,
    "audience": "",
    "cats": "",
    "camps": "undefined",
    "inc": 0,
}

response = requests.get(url, params=params, timeout=10)

# Raise an exception if the request failed (404, 500, etc.)
response.raise_for_status()

# Parse the JSON into Python objects
data = response.json()

print(data["results"][0].keys())

#print(type(data))

for record in data["results"]:
    print(f"{record['date']} - Time: {record['start']} Title: {record['title']}")