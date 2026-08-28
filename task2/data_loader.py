import json
from datetime import datetime,timedelta
from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent
DATA_DIR=BASE_DIR/"data"
ACCOUNTS_FILE=DATA_DIR/"accounts.json"
TICKETS_FILE=DATA_DIR/"tickets.json"

def load_json(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path,"r",encoding="utf-8") as file:
        return json.load(file)

def normalize_records(data,possible_keys):
    if isinstance(data,list):
        return data
    if isinstance(data,dict):
        for key in possible_keys:
            value=data.get(key)
            if isinstance(value,list):
                return value
        for value in data.values():
            if isinstance(value,list):
                return value
    raise ValueError("Unable to identify records inside JSON file.")

def load_accounts():
    data=load_json(ACCOUNTS_FILE)
    return normalize_records(data,["accounts","account","data"])

def load_tickets():
    data=load_json(TICKETS_FILE)
    return normalize_records(data,["tickets","ticket","data"])

def get_account(account_id):
    accounts=load_accounts()
    requested_id=str(account_id).strip().upper()
    for account in accounts:
        current_id=str(account.get("account_id","")).strip().upper()
        if current_id==requested_id:
            return account
    return None

def get_account_tickets(account_id):
    tickets=load_tickets()
    requested_id=str(account_id).strip().upper()
    result=[]
    for ticket in tickets:
        current_id=str(ticket.get("account_id","")).strip().upper()
        if current_id==requested_id:
            result.append(ticket)
    return result

def parse_date(value):
    if not value:
        return None
    if isinstance(value,datetime):
        return value
    value=str(value).strip()
    formats=[
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f+00:00",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value,fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError:
        return None

def get_last_90_days_tickets(account_id):
    tickets=get_account_tickets(account_id)
    if not tickets:
        return []
    parsed=[]
    for ticket in tickets:
        created_at=parse_date(ticket.get("created_at"))
        if created_at:
            parsed.append((created_at,ticket))
    if not parsed:
        return []
    latest_date=max(date for date,ticket in parsed)
    start_date=latest_date-timedelta(days=90)
    result=[]
    for created_at,ticket in parsed:
        if start_date<=created_at<=latest_date:
            result.append(ticket)
    result.sort(
        key=lambda ticket:parse_date(ticket.get("created_at")) or datetime.min,
        reverse=True
    )
    return result

def get_data_window(tickets):
    dates=[]
    for ticket in tickets:
        date=parse_date(ticket.get("created_at"))
        if date:
            dates.append(date)
    if not dates:
        return "",""
    start=min(dates)
    end=max(dates)
    return start.isoformat(),end.isoformat()