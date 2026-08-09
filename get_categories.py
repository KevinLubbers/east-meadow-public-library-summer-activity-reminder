
import json
import requests
import re
from urllib.parse import urlparse
from urllib.parse import urljoin

class LibCal:
    def __init__(self, url):
        self.url = url
        self.html = None
        self.categories = {}

    def is_valid_url(self):
        parsed = urlparse(self.url)

        if parsed.scheme != "https":
            return False

        hostname = parsed.hostname or ""

        return (
            hostname == "libcal.com"
            or hostname.endswith(".libcal.com")
        )

    def fetch(self):
        if not self.is_valid_url():
            raise ValueError("URL does not appear to be a LibCal URL")

        response = requests.get(
            urljoin(self.url, "/calendars"),
            timeout=10)
        response.raise_for_status()

        self.html = response.text
        return self.html

    def get_categories(self):
        if self.html is None:
            self.fetch()

        matches = re.findall(
            r'categoryNameMap\[(\d+)\]\s*=\s*"((?:\\.|[^"\\])*)"',
            self.html
        )

        self.categories = {
            int(category_id): json.loads(f'"{category_name}"')
            for category_id, category_name in matches
        }

        return self.categories


"""
urls = ["https://eastmeadow.libcal.com/calendars", "https://hicksvillelibrary.libcal.com/calendars", "https://freeportlibrary.libcal.com/calendars"]
for url in urls:
    response = requests.get(url)

    response.raise_for_status()
    #updated regexer, still testing to see if new one is necessary
    matches = re.findall(
        r'categoryNameMap\[(\d+)\]\s*=\s*"([^"]*)"',
        response.text
    )
    cleaner_matches = re.findall(
        r'categoryNameMap\[(\d+)\]\s*=\s*"((?:\\.|[^"\\])*)"',
        response.text
    )
    categories = {}
    for category_id, category_name in cleaner_matches:
        category_name = json.loads(f'"{category_name}"')
        categories[int(category_id)] = category_name

    print(url)
    print(categories)
"""