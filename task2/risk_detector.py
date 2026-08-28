import re

CHURN_PATTERNS=[
    (r"\bcompeting vendor\b","The ticket mentions a competing vendor."),
    (r"\bcompetitor\b","The ticket mentions a competitor."),
    (r"\bcompetitive evaluation\b","The ticket mentions a competitive evaluation."),
    (r"\bvendor evaluation\b","The ticket mentions a vendor evaluation."),
    (r"\bevaluating (?:another|a different|competing)\b","The customer appears to be evaluating an alternative."),
    (r"\bconsidering (?:another|a different|competing)\b","The customer appears to be considering an alternative."),
    (r"\bswitch(?:ing)? (?:vendor|provider|platform)\b","The ticket suggests a possible switch."),
    (r"\breplace (?:the )?(?:vendor|provider|platform)\b","The ticket suggests replacement of the current solution."),
    (r"\bcancel(?:lation)?\b","The ticket contains cancellation language."),
    (r"\bterminate(?:d|s|ation)?\b","The ticket contains termination language."),
    (r"\bchurn\b","The ticket explicitly mentions churn."),
    (r"\bleave the platform\b","The ticket suggests leaving the platform."),
    (r"\bmove away from\b","The ticket suggests moving away from the solution.")
]

ESCALATION_PATTERNS=[
    (r"\bcritical\b","The ticket describes the issue as critical."),
    (r"\burgent(?:ly)?\b","The ticket contains urgent language."),
    (r"\bescalat(?:e|ed|ion|ing)\b","The ticket contains escalation language."),
    (r"\bimmediately\b","The ticket requests immediate action."),
    (r"\bproduction outage\b","The ticket reports a production outage."),
    (r"\boutage\b","The ticket reports an outage."),
    (r"\bblocking\b","The ticket describes a blocking issue."),
    (r"\bblocked\b","The ticket describes blocked users or operations."),
    (r"\bbusiness continuity\b","The ticket mentions business continuity."),
    (r"\bdata loss\b","The ticket mentions data loss."),
    (r"\bfailing\b","The ticket describes a failure."),
    (r"\bfailed\b","The ticket describes a failure."),
    (r"\btimeout\b","The ticket reports timeout behavior."),
    (r"\btiming out\b","The ticket reports timeout behavior.")
]

def split_sentences(text):
    if not text:
        return []
    return re.split(r"(?<=[.!?])\s+",text.strip())

def find_evidence_sentence(text,pattern):
    sentences=split_sentences(text)
    for sentence in sentences:
        if re.search(pattern,sentence,re.IGNORECASE):
            return sentence.strip()

    match=re.search(pattern,text,re.IGNORECASE)

    if match:
        start=max(0,text.rfind(".",0,match.start())+1)
        end=text.find(".",match.end())

        if end==-1:
            end=len(text)

        return text[start:end].strip()

    return ""

def calculate_severity(ticket,signal_type):
    urgency=str(ticket.get("urgency","")).upper()

    if urgency=="P1":
        return "high"

    if signal_type=="churn_risk":
        return "high"

    return "medium"

def detect_churn(ticket):
    subject=str(ticket.get("subject",""))
    body=str(ticket.get("body",""))
    text=subject+". "+body

    for pattern,reason in CHURN_PATTERNS:
        if re.search(pattern,text,re.IGNORECASE):
            quote=find_evidence_sentence(text,pattern)

            return {
                "ticket_id":ticket.get("ticket_id",""),
                "signal_type":"churn_risk",
                "severity":calculate_severity(ticket,"churn_risk"),
                "evidence_quote":quote,
                "reason":reason
            }

    return None

def detect_escalation(ticket):
    subject=str(ticket.get("subject",""))
    body=str(ticket.get("body",""))
    text=subject+". "+body

    for pattern,reason in ESCALATION_PATTERNS:
        if re.search(pattern,text,re.IGNORECASE):
            quote=find_evidence_sentence(text,pattern)

            return {
                "ticket_id":ticket.get("ticket_id",""),
                "signal_type":"escalation_risk",
                "severity":calculate_severity(ticket,"escalation_risk"),
                "evidence_quote":quote,
                "reason":reason
            }

    return None

def detect_risks(tickets):
    risks=[]

    for ticket in tickets:
        churn=detect_churn(ticket)

        if churn:
            risks.append(churn)

        escalation=detect_escalation(ticket)

        if escalation:
            risks.append(escalation)

    return risks