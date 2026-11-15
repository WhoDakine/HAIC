
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)

API_KEY = os.getenv("BEA_API_KEY")

print("Project folder:", PROJECT_ROOT)
print(".env file exists:", ENV_FILE.exists())
print("BEA key loaded:", bool(API_KEY))

API_URL = "https://apps.bea.gov/api/data/"
API_KEY = os.getenv("BEA_API_KEY")

STATE_CODE = "15000"  # Hawaii
START_YEAR = "2020"
END_YEAR = "2025"


def retrieve_bea_data(table_name, description):
    if not API_KEY:
        raise ValueError("BEA_API_KEY was not found in your .env file.")

    params = {
        "UserID": API_KEY,
        "method": "GetData",
        "datasetname": "Regional",
        "TableName": table_name,
        "LineCode": "1",
        "GeoFips": STATE_CODE,
        "Year": f"{START_YEAR},{END_YEAR}",
        "ResultFormat": "JSON"
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    result = response.json()["BEAAPI"]["Results"]

    if "Error" in result:
        error = result["Error"]
        raise RuntimeError(
            f"BEA error code: {error.get('APIErrorCode')}\n"
            f"Description: {error.get('APIErrorDescription')}"
        )   

    observations = result.get("Data", [])

    return {
        "description": description,
        "observations": observations
    }


def main():
    print("Retrieving BEA economic data...\n")

    indicators = {
        "gross_domestic_product": {
            "table": "SAGDP1",
            "description": "Hawaii annual gross domestic product"
        },
        "personal_income": {
            "table": "SAINC1",
            "description": "Hawaii annual personal income"
        }
    }

    for name, details in indicators.items():
        try:
            data = retrieve_bea_data(
                details["table"],
                details["description"]
            )

            observations = data["observations"]

            print(f"\n{name}")
            print(f"Description: {data['description']}")
            print(f"Observations retrieved: {len(observations)}")

            for item in observations:
                print(
                    f"Year: {item.get('TimePeriod')} | "
                    f"Value: {item.get('DataValue')} | "
                    f"Unit: {item.get('UNIT_MULT')}"
                )

        except Exception as error:
            print(f"\n{name} retrieval failed:")
            print(error)

    print("\nBEA retrieval process completed!")
    print("Source: U.S. Bureau of Economic Analysis")
    print("Geography: Hawaii")


if __name__ == "__main__":
    main()
