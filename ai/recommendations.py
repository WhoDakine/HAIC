
from data.database import (
    initialize_database,
    get_all_programs,
    get_program_tags,
    get_program_requirements,
    get_program_sources
)


# Each indicator connects a district statistic to a program tag.
# All six indicators are percentages where a higher value represents a potentially greater community need.
# These are not eligibility requirements or fixed thresholds.

NEED_INDICATORS = {
    "poverty": {
        "label": "Poverty",
        "data_key": "pct_poverty",
        "tag": "poverty",
        "unit": "percent"
    },
    "uninsured": {
        "label": "Uninsured population",
        "data_key": "pct_uninsured",
        "tag": "healthcare",
        "unit": "percent"
    },
    "unemployment": {
        "label": "Unemployment",
        "data_key": "unemployment_rate",
        "tag": "employment",
        "unit": "percent"
    },
    "housing": {
        "label": "Rent burden",
        "data_key": "pct_rent_burden_35plus",
        "tag": "housing",
        "unit": "percent"
    },
    "disability": {
        "label": "Disability",
        "data_key": "pct_disability",
        "tag": "disability",
        "unit": "percent"
    },
    "senior_services": {
        "label": "Population age 65+",
        "data_key": "pct_age_65_plus",
        "tag": "senior_services",
        "unit": "percent"
    }
}


def to_number(value):
    """
    Converts a value to a number.

    Returns None when the value is missing or invalid.
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


def identify_district_needs(district_data):
    """
    Compares district indicators with Hawaii statewide estimates.

    Expected district_data structure:

    {
        "pct_poverty": 18.0,

        "state_benchmarks": {
            "pct_poverty": 11.0
        },

        "district_margins_of_error": {
            "pct_poverty": 2.0
        },

        "state_margins_of_error": {
            "pct_poverty": 0.5
        }
    }

    The function does not use fixed percentage thresholds.

    It identifies indicators above the statewide estimate
    and ranks them by relative difference.

    ACS margins of error are retained for interpretation.
    This function does not perform a formal statistical
    significance test.
    """

    state_benchmarks = district_data.get(
        "state_benchmarks", {}
    )

    district_moes = district_data.get(
        "district_margins_of_error", {}
    )

    state_moes = district_data.get(
        "state_margins_of_error", {}
    )

    results = []

    for need_name, indicator in NEED_INDICATORS.items():

        data_key = indicator["data_key"]

        district_value = to_number(
            district_data.get(data_key)
        )

        state_value = to_number(
            state_benchmarks.get(data_key)
        )

        district_moe = to_number(
            district_moes.get(data_key)
        )

        state_moe = to_number(
            state_moes.get(data_key)
        )

        # Won't make a comparison if either value is missing

        if district_value is None or state_value is None:
            results.append({
                "need": need_name,
                "label": indicator["label"],
                "district_value": district_value,
                "state_value": state_value,
                "difference_percentage_points": None,
                "relative_difference_percent": None,
                "district_moe": district_moe,
                "state_moe": state_moe,
                "status": "comparison_unavailable",
                "tag": indicator["tag"]
            })

            continue

        difference = district_value - state_value

        # Relative difference expresses how far the district is above/below the statewide estimate
        if state_value != 0:
            relative_difference = (
                difference / state_value
            ) * 100
        else:
            relative_difference = None

        if difference > 0:
            status = "above_state_estimate"

        elif difference < 0:
            status = "below_state_estimate"

        else:
            status = "equal_to_state_estimate"

        results.append({
            "need": need_name,
            "label": indicator["label"],
            "district_value": district_value,
            "state_value": state_value,
            "difference_percentage_points": round(
                difference, 2
            ),
            "relative_difference_percent": (
                round(relative_difference, 2)
                if relative_difference is not None
                else None
            ),
            "district_moe": district_moe,
            "state_moe": state_moe,
            "status": status,
            "tag": indicator["tag"]
        })

    # Rank indicators by relative difference
    # Indicators above the state estimate appear first
    # Note that this is a descriptive ranking

    results.sort(
        key=lambda item: (
            item["relative_difference_percent"]
            if item["relative_difference_percent"] is not None
            else float("-inf")
        ),
        reverse=True
    )

    for index, result in enumerate(results, start=1):
        result["rank"] = index

    return results


def get_program_catalog():
    """
    Retrieves programs and their associated information
    from the SQLite database.
    """

    initialize_database()

    programs = get_all_programs()

    catalog = []

    for program in programs:

        program_id = program["program_id"]

        catalog.append({
            "program_id": program_id,
            "program_name": program["program_name"],
            "agency": program["agency"],
            "description": program["description"],
            "eligible_entities": program["eligible_entities"],
            "eligible_locations": program["eligible_locations"],
            "funding_amount": program["funding_amount"],
            "application_deadline": program["application_deadline"],
            "official_url": program["official_url"],
            "eligibility_status": program["eligibility_status"],
            "last_verified": program["last_verified"],
            "tags": get_program_tags(program_id),
            "requirements": get_program_requirements(program_id),
            "sources": get_program_sources(program_id)
        })

    return catalog


def calculate_match_score(matched_needs, total_needs):
    """
    Calculates the percentage of identified above-state
    indicators addressed by a program.

    This score measures need coverage only.

    It does not represent eligibility, funding probability,
    or likelihood of receiving an award.
    """

    if total_needs == 0:
        return 0

    return round(
        (len(matched_needs) / total_needs) * 100,
        2
    )


def recommend_programs(district_data, limit=10):
    """
    Recommends programs based on district indicators
    that are above Hawaii statewide estimates.

    Program tags are compared with the needs identified
    through statewide benchmarking.

    Only programs with at least one matching tag
    are returned.
    """

    all_needs = identify_district_needs(district_data)

    # Only indicators above the statewide estimate are used for program matching

    elevated_needs = [
        need for need in all_needs
        if need["status"] == "above_state_estimate"
    ]

    catalog = get_program_catalog()

    recommendations = []

    for program in catalog:

        program_tags = program["tags"]

        # Convert database tags to lowercase strings
        normalized_tags = {
            str(tag).strip().lower()
            for tag in program_tags
        }

        matched_needs = []

        for need in elevated_needs:

            if need["tag"].lower() in normalized_tags:
                matched_needs.append(need)

        if not matched_needs:
            continue

        match_score = calculate_match_score(
            matched_needs,
            len(elevated_needs)
        )

        recommendations.append({
            "program_id": program["program_id"],
            "program_name": program["program_name"],
            "agency": program["agency"],
            "description": program["description"],
            "official_url": program["official_url"],
            "funding_amount": program["funding_amount"],
            "application_deadline": program["application_deadline"],
            "eligibility_status": program["eligibility_status"],
            "eligible_entities": program["eligible_entities"],
            "eligible_locations": program["eligible_locations"],
            "last_verified": program["last_verified"],
            "matched_needs": matched_needs,
            "match_score": match_score,
            "requirements": program["requirements"],
            "sources": program["sources"]
        })

    recommendations.sort(
        key=lambda program: (
            program["match_score"],
            len(program["matched_needs"])
        ),
        reverse=True
    )

    return {
        "identified_needs": all_needs,
        "elevated_needs": elevated_needs,
        "recommendations": recommendations[:limit],
        "total_elevated_needs": len(elevated_needs),
        "benchmark_available": any(
            need["status"] != "comparison_unavailable"
            for need in all_needs
        )
    }
