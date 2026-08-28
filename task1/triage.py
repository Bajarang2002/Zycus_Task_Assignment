import json

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL
from rag import search_knowledge_base
from prompt import build_triage_prompt

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def triage_ticket(
    subject,
    body,
    product=None,
    product_area=None,
    plan_tier=None
):
    query = f"""
Subject:
{subject}

Customer Problem:
{body}

Product:
{product or ""}

Product Area:
{product_area or ""}

Plan Tier:
{plan_tier or ""}
"""

    knowledge = search_knowledge_base(
        query,
        top_k=5
    )

    prompt = build_triage_prompt(
        subject=subject,
        body=body,
        product=product,
        product_area=product_area,
        plan_tier=plan_tier,
        knowledge=knowledge
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )

    result = json.loads(response.text)

    if knowledge:
        result["known_issue"] = True

        result["knowledge_base_references"] = [
            {
                "source": item["source"],
                "relevance": item["relevance"]
            }
            for item in knowledge
        ]
    else:
        result["known_issue"] = False
        result["knowledge_base_references"] = []

    return result