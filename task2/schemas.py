from typing import List
from pydantic import BaseModel

class RiskFlag(BaseModel):
    ticket_id:str
    signal_type:str
    severity:str
    evidence_quote:str
    reason:str

class AccountHealthResponse(BaseModel):
    account_id:str
    company:str
    executive_summary:str
    open_risks_and_flagged_issues:List[RiskFlag]
    tam_talking_points:List[str]
    data_window_start:str
    data_window_end:str
    ticket_count_90d:int