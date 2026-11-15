
"""
BLS Data Integration
U.S. Bureau of Labor Statistics

Retrieves Hawaii employment, unemployment,
and wage statistics through the official BLS API.
"""

import requests


# BLS configuration

BASE_URL = (
    "https://api.bls.gov/publicAPI/v1/timeseries/data/"
)

SOURCE_NAME = "U.S. Bureau of Labor Statistics"

STATE = "Hawaii"

STATE_FIPS = "15"

START_YEAR = "2021"
END_YEAR = "2025"

TIMEOUT = 30


# Hawaii BLS time series

BLS_SERIES = {

    "unemployment_rate": {
        "series_id": "LASST150000000000003",
        "description": "Hawaii unemployment rate",
        "unit": "Percent"
    },

    "total_nonfarm_employment": {
        "series_id": "SMS15000000000000001",
        "description": "Total nonfarm employment",
        "unit": "Thousands of employees"
    },

    "average_hourly_earnings": {
        "series_id": "SMU15000000500000003",
        "description": "Average hourly earnings, private sector",
        "unit": "Dollars"
    }

}


def fetch_bls_data(
    series_ids,
    start_year=START_YEAR,
    end_year=END_YEAR
):
    """
    Retrieves one or more BLS time series.

    Uses the public BLS API without registration.
    """

    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year)
    }

    response = requests.post(
        BASE_URL,
        json=payload,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    result = response.json()

    if result.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError(
            "BLS API request failed: "
            + str(result.get("message"))
        )

    return result.get("Results", {}).get("series", [])


def format_series_data(series):
    """
    Organizes BLS observations into a readable format.
    """

    observations = []

    for item in series.get("data", []):

        # Ignore annual averages for this monthly dataset.
        period = item.get("period", "")

        if not period.startswith("M"):
            continue

        observations.append({

            "year": int(item["year"]),

            "period": period,

            "period_name": item.get("periodName"),

            "value": float(item["value"]) if item["value"] != "-" else None,

            "footnotes": [
                note.get("text")
                for note in item.get("footnotes", [])
                if note.get("text")
            ]

        })

    return observations


def get_bls_data():
    """
    Retrieves Hawaii employment, unemployment,
    and wage statistics.

    Returns a standardized data dictionary.
    """

    series_ids = [
        item["series_id"]
        for item in BLS_SERIES.values()
    ]

    raw_results = fetch_bls_data(series_ids)

    results_by_id = {
        series["seriesID"]: series
        for series in raw_results
    }

    indicators = {}

    for indicator, metadata in BLS_SERIES.items():

        series_id = metadata["series_id"]

        series = results_by_id.get(series_id)

        if series is None:

            indicators[indicator] = {
                "description": metadata["description"],
                "unit": metadata["unit"],
                "observations": [],
                "warning": "No data returned for this series."
            }

            continue

        indicators[indicator] = {

            "series_id": series_id,

            "description": metadata["description"],

            "unit": metadata["unit"],

            "observations": format_series_data(series)

        }

    return {

        "data_source": SOURCE_NAME,

        "dataset": "Labor Market Statistics",

        "geographic_coverage": STATE,

        "state_fips": STATE_FIPS,

        "data_period": (
            f"{START_YEAR}-{END_YEAR}"
        ),

        "indicators": indicators

    }


if __name__ == "__main__":

    try:

        result = get_bls_data()

        print("BLS data retrieved successfully!")

        print("Source:", result["data_source"])

        print("Geography:", result["geographic_coverage"])

        print("Period:", result["data_period"])

        print("\nAvailable indicators:")

        for name, indicator in result["indicators"].items():

            print("\n", name)

            print("Description:", indicator["description"])

            print("Unit:", indicator["unit"])

            observations = indicator["observations"]

            print(
                "Observations retrieved:",
                len(observations)
            )

            if observations:

                print(
                    "Latest observation:",
                    observations[0]
                )

    except Exception as error:

        print("BLS retrieval failed:")
        print(error)
