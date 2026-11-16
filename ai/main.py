
import json

from data.census_api import get_district_data
from ai.recommendations import (
  identify_district_needs,
  recommend_programs
)
from ai.ollama_prompt import ask_ai


def get_government_context(chamber, district):
  """
  Collects district statistics, identified needs,
  and potential government assistance programs.
  """

  district_data = get_district_data(chamber, district)

  identified_needs = identify_district_needs(
    district_data
  )

  program_recommendations = recommend_programs(
    district_data
  )

  government_context = {
    "district": {
      "chamber": chamber,
      "district_number": district
    },
    "district_statistics": district_data,
    "identified_needs": identified_needs,
    "potential_program_matches": program_recommendations
  }

  return government_context


def answer_question(legislator, question):
  chamber = legislator["chamber"]
  district = legislator["district"]

  government_context = get_government_context(
    chamber,
    district
  )

  government_context["legislator_profile"] = {
    "name": legislator["name"],
    "position": legislator["position"],
    "policy_interests": legislator["policy_interests"]
  }

  government_data = json.dumps(
    government_context,
    indent=2,
    default=str
  )

  response = ask_ai(
    question,
    government_data
  )

  return {
    "response": response,
    "government_data": government_context
  }
