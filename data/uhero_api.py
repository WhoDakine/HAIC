
"""
UHERO Data Integration
University of Hawaii Economic Research Organization

Retrieves published UHERO research, economic forecasts,
and publication information through its WordPress REST API.
"""

import requests
import re
from html import unescape


# UHERO configuration

BASE_URL = "https://uhero.hawaii.edu/"

API_URL = BASE_URL + "wp-json/wp/v2/posts"

DATA_PORTAL_URL = "https://data.uhero.hawaii.edu/"

SOURCE_NAME = "University of Hawaii Economic Research Organization"

TIMEOUT = 30


# Economic research categories

DEFAULT_KEYWORDS = [
    "economic forecast",
    "employment",
    "income",
    "housing",
    "tourism",
    "economic activity"
]


def clean_html(value):
    """Removes HTML tags from published text."""

    if not value:
        return ""

    value = re.sub(r"<[^>]+>", "", value)

    return unescape(value).strip()


def fetch_uhero_publications(
    keyword,
    per_page=20
):
    """
    Retrieves UHERO publications matching a keyword.

    Uses the official UHERO WordPress REST API.
    """

    params = {
        "search": keyword,
        "per_page": per_page,
        "_fields": "date,link,title,excerpt"
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    publications = response.json()

    if not isinstance(publications, list):
        raise ValueError(
            "Unexpected UHERO API response."
        )

    results = []

    for publication in publications:

        results.append({

            "title": clean_html(
                publication.get("title", {}).get("rendered")
            ),

            "date": publication.get("date"),

            "url": publication.get("link"),

            "summary": clean_html(
                publication.get("excerpt", {}).get("rendered")
            ),

            "keyword": keyword

        })

    return results


def get_uhero_data(keywords=None):
    """
    Retrieves UHERO research and economic forecasts.

    Optional keywords allow targeted searches.

    Example:
        get_uhero_data(["employment", "tourism"])
    """

    if keywords is None:
        keywords = DEFAULT_KEYWORDS

    publications = []
    seen_urls = set()

    warnings = []

    for keyword in keywords:

        try:

            results = fetch_uhero_publications(
                keyword
            )

            for publication in results:

                url = publication["url"]

                if url and url not in seen_urls:

                    publications.append(publication)

                    seen_urls.add(url)

        except (
            requests.RequestException,
            ValueError
        ) as error:

            warnings.append(
                f"{keyword}: {error}"
            )

    return {

        "data_source": SOURCE_NAME,

        "dataset": "UHERO Economic Research and Forecasts",

        "data_portal": DATA_PORTAL_URL,

        "geographic_coverage": [
            "Hawaii",
            "Honolulu County",
            "Hawaii County",
            "Maui County",
            "Kauai County"
        ],

        "categories_searched": keywords,

        "publications_found": len(publications),

        "publications": publications,

        "warnings": warnings or None

    }


if __name__ == "__main__":

    try:

        result = get_uhero_data()

        print("UHERO retrieval completed!")

        print("Source:", result["data_source"])

        print(
            "Publications found:",
            result["publications_found"]
        )

        print("\nAvailable publications:")

        for publication in result["publications"]:

            print(
                "-",
                publication["title"]
            )

            print(
                "  Date:",
                publication["date"]
            )

        if result["warnings"]:

            print("\nWarnings:")

            for warning in result["warnings"]:
                print("-", warning)

        print(
            "\nUHERO Data Portal:",
            result["data_portal"]
        )

    except Exception as error:

        print("UHERO retrieval failed:")
        print(error)
