
import os
import requests


YEAR = "2024"
STATE_FIPS = "15"

# Optional Census API key.
# Set the CENSUS_API_KEY environment variable rather than putting a key directly into this file.
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

BASE_URL = (
    f"https://api.census.gov/data/{YEAR}/acs/acs5"
)

SUBJECT_URL = BASE_URL + "/subject"
PROFILE_URL = BASE_URL + "/profile"


# Detailed ACS variables
DETAILED_VARIABLES = [
    "NAME",
    "B01003_001E",  # Total population
    "B19013_001E",  # Median household income
    "B17001_002E",  # Population below poverty level
    "B25064_001E",  # Median gross rent
    "B25001_001E"   # Total housing units
]


# Subject table estimates and margins of error.
SUBJECT_VARIABLES = [
    "NAME",

    "S1701_C03_001E",  # Poverty percentage
    "S1701_C03_001M",

    "S2701_C05_001E",  # Uninsured percentage
    "S2701_C05_001M",

    "S2301_C04_001E",  # Unemployment rate
    "S2301_C04_001M",

    "S1810_C03_001E",  # Disability percentage
    "S1810_C03_001M",

    "S0101_C02_030E",  # Age 65 and over percentage
    "S0101_C02_030M"
]


# Data Profile estimates and margins of error.
PROFILE_VARIABLES = [
    "NAME",
    "DP04_0142PE",
    "DP04_0142PM"
]


# Maps the recommendation system's indicator names to their Census API variable names.
BENCHMARK_VARIABLES = {
    "pct_poverty": {
        "estimate": "S1701_C03_001E",
        "moe": "S1701_C03_001M"
    },

    "pct_uninsured": {
        "estimate": "S2701_C05_001E",
        "moe": "S2701_C05_001M"
    },

    "unemployment_rate": {
        "estimate": "S2301_C04_001E",
        "moe": "S2301_C04_001M"
    },

    "pct_disability": {
        "estimate": "S1810_C03_001E",
        "moe": "S1810_C03_001M"
    },

    "pct_age_65_plus": {
        "estimate": "S0101_C02_030E",
        "moe": "S0101_C02_030M"
    },

    "pct_rent_burden_35plus": {
        "estimate": "DP04_0142PE",
        "moe": "DP04_0142PM"
    }
}


def get_geography(chamber):
    """
    Returns the Census geography for the selected chamber.

    Senate = Upper chamber
    House = Lower chamber
    """

    chamber = chamber.lower()

    if chamber == "senate":
        return (
            "state legislative district "
            "(upper chamber)"
        )

    elif chamber == "house":
        return (
            "state legislative district "
            "(lower chamber)"
        )

    else:
        raise ValueError(
            "Chamber must be House or Senate."
        )


def fetch_census_data(
    url,
    variables,
    geography,
    district=None
):
    """
    Retrieves Census API data.

    If district is provided, retrieves the selected
    legislative district.

    If district is None, retrieves Hawaii statewide data.
    """

    params = {
        "get": ",".join(variables)
    }

    if district is None:

        # Hawaii statewide data
        params["for"] = f"state:{STATE_FIPS}"

    else:

        # Legislative district data
        params["for"] = (
            f"{geography}:{district:03d}"
        )

        params["in"] = f"state:{STATE_FIPS}"

    # Include API key if one has been configured.
    if CENSUS_API_KEY:
        params["key"] = CENSUS_API_KEY

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list) or len(data) < 2:
        raise ValueError(
            "No Census data returned."
        )

    return dict(zip(data[0], data[1]))


def to_number(value):
    """
    Converts a Census API value to a number.

    Returns None when the value is missing,
    invalid, or a negative Census special value.
    """

    if value is None:
        return None

    try:
        number = float(value)

        if number < 0:
            return None

        return number

    except (ValueError, TypeError):
        return None


def extract_benchmarks(subject, profile):
    """
    Extracts statewide or district estimates for
    the six recommendation indicators.
    """

    benchmarks = {}

    for indicator, variables in BENCHMARK_VARIABLES.items():

        variable = variables["estimate"]

        if variable.startswith("DP04"):
            value = profile.get(variable)
        else:
            value = subject.get(variable)

        benchmarks[indicator] = to_number(value)

    return benchmarks


def extract_margins_of_error(subject, profile):
    """
    Extracts ACS margins of error for the six indicators.

    Subject table MOEs use M.
    Data Profile percentage MOEs use PM.
    """

    margins = {}

    for indicator, variables in BENCHMARK_VARIABLES.items():

        variable = variables["moe"]

        if variable.startswith("DP04"):
            value = profile.get(variable)
        else:
            value = subject.get(variable)

        margins[indicator] = to_number(value)

    return margins


def get_district_data(chamber, district):
    """
    Retrieves district statistics, statewide benchmarks,
    and margins of error for a Hawaii legislative district.

    Uses the 2020-2024 ACS 5-Year Estimates.
    """

    district = int(district)

    if district < 1:
        raise ValueError(
            "Invalid district number."
        )

    geography = get_geography(chamber)


    # Retrieve district detailed table data
    detailed = fetch_census_data(
        BASE_URL,
        DETAILED_VARIABLES,
        geography,
        district
    )


    # Retrieve district subject table data
    subject = fetch_census_data(
        SUBJECT_URL,
        SUBJECT_VARIABLES,
        geography,
        district
    )


    # Retrieve Hawaii statewide subject data
    state_subject = fetch_census_data(
        SUBJECT_URL,
        SUBJECT_VARIABLES,
        "state"
    )


    #  Retrieve district and statewide profile data
    profile = {}
    state_profile = {}

    profile_warnings = []

    try:
        profile = fetch_census_data(
            PROFILE_URL,
            PROFILE_VARIABLES,
            geography,
            district
        )

    except (requests.RequestException, ValueError) as error:
        profile_warnings.append(
            f"District profile data unavailable: {error}"
        )

    try:
        state_profile = fetch_census_data(
            PROFILE_URL,
            PROFILE_VARIABLES,
            "state"
        )

    except (requests.RequestException, ValueError) as error:
        profile_warnings.append(
            f"Statewide profile data unavailable: {error}"
        )


    # Calculate district benchmarks
    district_benchmarks = extract_benchmarks(
        subject,
        profile
    )


    # Calculate statewide benchmarks
    state_benchmarks = extract_benchmarks(
        state_subject,
        state_profile
    )


    # Retrieve district margins of error
    district_margins_of_error = extract_margins_of_error(
        subject,
        profile
    )


    # Retrieve statewide margins of error
    state_margins_of_error = extract_margins_of_error(
        state_subject,
        state_profile
    )

   # Build final district data dictionary
    district_data = {

        "district_name": detailed.get("NAME"),

        "chamber": chamber.title(),

        "district_number": district,

        # General district statistics

        "population": to_number(
            detailed.get("B01003_001E")
        ),

        "median_household_income": to_number(
            detailed.get("B19013_001E")
        ),

        "population_below_poverty": to_number(
            detailed.get("B17001_002E")
        ),

        "median_gross_rent": to_number(
            detailed.get("B25064_001E")
        ),

        "housing_units": to_number(
            detailed.get("B25001_001E")
        ),

        # District indicators

        "pct_poverty": district_benchmarks[
            "pct_poverty"
        ],

        "pct_uninsured": district_benchmarks[
            "pct_uninsured"
        ],

        "unemployment_rate": district_benchmarks[
            "unemployment_rate"
        ],

        "pct_disability": district_benchmarks[
            "pct_disability"
        ],

        "pct_age_65_plus": district_benchmarks[
            "pct_age_65_plus"
        ],

        "pct_rent_burden_35plus": district_benchmarks[
            "pct_rent_burden_35plus"
        ],

        # Hawaii statewide estimates

        "state_benchmarks": state_benchmarks,

        # District margins of error

        "district_margins_of_error": (
            district_margins_of_error
        ),

        # Statewide margins of error

        "state_margins_of_error": (
            state_margins_of_error
        ),

        # Data source information

        "data_source": "U.S. Census Bureau",

        "dataset": "ACS 5-Year Estimates",

        "data_period": "2020-2024",

        "release_year": 2026,

        "profile_data_warning": (
            "; ".join(profile_warnings)
            if profile_warnings
            else None
        )
    }

    return district_data
