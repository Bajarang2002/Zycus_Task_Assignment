import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY,GEMINI_MODEL
from data_loader import get_account,get_last_90_days_tickets,get_data_window
from risk_detector import detect_risks
from prompt import build_prompt

client=genai.Client(api_key=GEMINI_API_KEY)

def generate_health_brief(account_id):
    account=get_account(account_id)
    if account is None:
        raise ValueError(f"Account '{account_id}' was not found in accounts.json.")

    tickets=get_last_90_days_tickets(account_id)
    risks=detect_risks(tickets)
    start_date,end_date=get_data_window(tickets)

    prompt=build_prompt(
        account=account,
        tickets=tickets,
        risks=risks
    )

    response=client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json"
        )
    )

    try:
        generated=json.loads(response.text)
    except json.JSONDecodeError:
        raise ValueError("Gemini returned invalid JSON.")

    result={
        "account_id":account.get("account_id",account_id),
        "company":account.get("company",""),
        "executive_summary":generated.get("executive_summary",""),
        "open_risks_and_flagged_issues":risks,
        "tam_talking_points":generated.get("tam_talking_points",[]),
        "data_window_start":start_date,
        "data_window_end":end_date,
        "ticket_count_90d":len(tickets)
    }

    return result