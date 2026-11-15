
"""
Hawaii Department of Taxation (DOTAX) Integration

Retrieves publicly available tax reports and Excel datasets
from the official Hawaii Department of Taxation website.
"""

import requests
from io import BytesIO
from html.parser import HTMLParser
from urllib.parse import urljoin
from openpyxl import load_workbook


# DOTAX configuration

BASE_URL = "https://tax.hawaii.gov/"

REPORT_URL = BASE_URL + "stats/a5_3txcolrpt/"

DASHBOARD_URL = BASE_URL + "data-dashboard/"

SOURCE_NAME = "Hawaii Department of Taxation"

TIMEOUT = 30


class ReportLinkParser(HTMLParser):
    """Extracts report download links from DOTAX pages."""

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


def get_report_links():
    """
    Retrieves available Excel report links from DOTAX.
    """

    response = requests.get(
        REPORT_URL,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    parser = ReportLinkParser()
    parser.feed(response.text)

    reports = []

    for link in parser.links:

        url = link["url"]
        title = link["text"].strip()

        if url.lower().split("?")[0].endswith(".xlsx"):

            reports.append({
                "title": title or "DOTAX Excel Report",
                "url": urljoin(REPORT_URL, url)
            })

    return reports


def download_excel_report(url):
    """
    Downloads and reads a DOTAX Excel report.

    Returns worksheet data organized by sheet name.
    """

    response = requests.get(
        url,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    workbook = load_workbook(
        BytesIO(response.content),
        data_only=True,
        read_only=True
    )

    data = {}

    for sheet in workbook.worksheets:

        rows = list(sheet.iter_rows(values_only=True))

        data[sheet.title] = [
            list(row) for row in rows
        ]

    workbook.close()

    return data


def get_dotax_data(keywords=None):
    """
    Retrieves DOTAX reports.

    Optional keywords filter reports by their titles.

    Example:
        get_dotax_data(["General Excise"])
    """

    reports = get_report_links()

    if keywords:

        keywords = [
            keyword.lower()
            for keyword in keywords
        ]

        reports = [
            report for report in reports
            if any(
                keyword in report["title"].lower()
                for keyword in keywords
            )
        ]

    results = []

    for report in reports:

        try:

            report_data = download_excel_report(
                report["url"]
            )

            results.append({
                "report_name": report["title"],
                "report_url": report["url"],
                "data": report_data,
                "status": "success"
            })

        except (
            requests.RequestException,
            ValueError,
            OSError
        ) as error:

            results.append({
                "report_name": report["title"],
                "report_url": report["url"],
                "data": None,
                "status": "failed",
                "error": str(error)
            })

    return {
        "data_source": SOURCE_NAME,
        "dataset": "Hawaii Tax Statistics",
        "geographic_coverage": "Hawaii",
        "reports_found": len(reports),
        "reports": results
    }


if __name__ == "__main__":

    try:

        result = get_dotax_data()

        print("DOTAX data retrieval completed!")

        print("Source:", result["data_source"])

        print(
            "Reports found:",
            result["reports_found"]
        )

        for report in result["reports"]:

            print(
                report["status"].upper(),
                "-",
                report["report_name"]
            )

    except Exception as error:

        print("DOTAX retrieval failed:")
        print(error)
