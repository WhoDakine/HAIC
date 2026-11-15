
"""
DBEDT / READ Data Integration
Hawaii Department of Business, Economic Development & Tourism

Retrieves published Monthly Economic Indicators (MEI)
Excel data tables from the official DBEDT website.
"""

import requests
from io import BytesIO
from html.parser import HTMLParser
from urllib.parse import urljoin
from openpyxl import load_workbook


# DBEDT configuration

BASE_URL = "https://dbedt.hawaii.gov/economic/"

MEI_URL = BASE_URL + "mei/"

SOURCE_NAME = "DBEDT / READ"

DATASET_NAME = "Monthly Economic Indicators"

TIMEOUT = 30


class ExcelLinkParser(HTMLParser):
    """Finds the latest Excel data-table download link."""

    def __init__(self):
        super().__init__()
        self.links = []
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            attrs = dict(attrs)
            href = attrs.get("href")

            if href:
                self.current_link = {
                    "url": href,
                    "text": ""
                }

    def handle_data(self, data):
        if self.current_link:
            self.current_link["text"] += data

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.current_link:
            self.links.append(self.current_link)
            self.current_link = None


def get_latest_excel_url():
    """
    Finds the current Monthly Economic Indicators
    Excel download on the official DBEDT website.
    """

    response = requests.get(
        MEI_URL,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    parser = ExcelLinkParser()
    parser.feed(response.text)

    for link in parser.links:

        title = link["text"].strip().lower()
        url = link["url"].lower()

        if (
            "data tables" in title
            and "excel" in title
            and url.endswith((".xlsx", ".xls"))
        ):
            return urljoin(MEI_URL, link["url"])

    raise ValueError(
        "Could not find the latest DBEDT Excel data tables."
    )


def fetch_dbedt_workbook():
    """
    Downloads and opens the latest DBEDT
    Monthly Economic Indicators workbook.
    """

    excel_url = get_latest_excel_url()

    response = requests.get(
        excel_url,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    workbook = load_workbook(
        BytesIO(response.content),
        data_only=True,
        read_only=True
    )

    return workbook


def get_dbedt_data():
    """
    Retrieves all worksheets from the latest
    DBEDT Monthly Economic Indicators workbook.

    Returns a dictionary organized by worksheet.
    """

    workbook = fetch_dbedt_workbook()

    data = {}

    for sheet in workbook.worksheets:

        rows = list(sheet.iter_rows(values_only=True))

        data[sheet.title] = [
            list(row) for row in rows
        ]

    workbook.close()

    return {
        "data_source": SOURCE_NAME,
        "dataset": DATASET_NAME,
        "geographic_coverage": [
            "Hawaii",
            "Honolulu County",
            "Hawaii County",
            "Maui County",
            "Kauai County"
        ],
        "data": data
    }


if __name__ == "__main__":

    try:
        result = get_dbedt_data()

        print("DBEDT data retrieved successfully!")

        print("Source:", result["data_source"])
        print("Dataset:", result["dataset"])

        print("\nAvailable worksheets:")

        for sheet_name in result["data"]:
            print("-", sheet_name)

    except Exception as error:

        print("DBEDT retrieval failed:")
        print(error)
