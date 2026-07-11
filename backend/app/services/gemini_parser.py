import json

from google import genai

from app.config import settings
from app.matching.intent_parser import MatchingIntent

_client = genai.Client(api_key=settings.gemini_api_key)


PROMPT = """
You extract structured job search intent.

Return ONLY valid JSON.

Schema:

{
  "skills": [],
  "role_types": [],
  "domains": [],
  "locations": [],
  "experience_levels": []
}

Rules:

- Return arrays only.
- Use lowercase.
- Never explain.
- Never wrap in markdown.
"""


def parse_with_gemini(query: str) -> MatchingIntent:
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{PROMPT}\n\nUser query:\n{query}",
    )

    text = response.text.strip()

    data = json.loads(text)

    return MatchingIntent(
        skills=data.get("skills", []),
        role_types=data.get("role_types", []),
        domains=data.get("domains", []),
        locations=data.get("locations", []),
        experience_levels=data.get("experience_levels", []),
    )