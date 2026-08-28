# Zycus AI Support Triage

An AI-powered customer support automation system built using **Python, FastAPI, Google Gemini, ChromaDB, RAG, and Streamlit**.

The project provides two major capabilities:

- **Task 1:** AI-powered support ticket triage using RAG.
- **Task 2:** Account health and customer-risk analysis.

---

## 📁 Project Structure

```text
.
├── task1/
│   ├── Chroma_db/
│   ├── Data/
│   ├── config.py
│   ├── main.py
│   ├── prompt.py
│   ├── rag.py
│   ├── schemas.py
│   ├── streamlit_app.py
│   ├── triage.py
│   └── requirements.txt
│
├── task2/
│   ├── Data/
│   │   ├── accounts.json
│   │   └── tickets.json
│   ├── config.py
│   ├── data_loader.py
│   ├── health_summarizer.py
│   ├── main.py
│   ├── prompt.py
│   ├── risk_detector.py
│   ├── schemas.py
│   ├── streamlit_app.py
│   └── requirements.txt
│
├── task3/
│   └── evaluation/
│       ├── evaluate.py
│       ├── task1_test.json
│       ├── task2_test.json
│       └── evaluation_report.json
│
└── task4/
    └── Design_Note.pdf


🚀 Task 1 — AI Support Ticket Triage

Task 1 automatically analyzes and classifies customer support tickets using Gemini + RAG + ChromaDB.

The system retrieves relevant Markdown knowledge-base documents and provides the retrieved context to Gemini for structured classification.

Key Features
Ticket classification
Product-area detection
Issue-category detection
P1/P2/P3 urgency
Known-issue detection
Knowledge-base retrieval
Recommended support team
Customer-facing first response
Workflow
Customer Ticket
      │
      ▼
   FastAPI
      │
      ▼
 ChromaDB + RAG
      │
      ▼
Knowledge Base
      │
      ▼
 Gemini LLM
      │
      ▼
Structured Triage
Input
{
  "subject": "Unable to login",
  "body": "Users are receiving SESSION_INVALID during login.",
  "product": "CloudSync",
  "product_area": "Authentication",
  "plan_tier": "Business"
}
Output
{
  "product_area": "Authentication",
  "issue_category": "Login/Access",
  "urgency": "P2",
  "reasoning": "The reported SESSION_INVALID error matches a documented knowledge-base issue.",
  "known_issue": true,
  "knowledge_base_references": [
    {
      "source": "troubleshooting/authentication-sso.md",
      "relevance": 0.85
    }
  ],
  "recommended_team": "Identity",
  "first_response": "Customer-facing response..."
}
🔍 Task 2 — Account Risk Analysis

Task 2 analyzes customer account health and identifies potential risks for Customer Success/TAM teams.

The system accepts an Account ID, retrieves account and ticket data, and analyzes signals such as:

Usage
Seat utilization
Support incidents
P1 incidents
Inactivity
NPS
Open tickets
Competitive vendor evaluation
Renewal risk
Workflow
Account ID
    │
    ▼
 FastAPI
    │
    ├── accounts.json
    └── tickets.json
            │
            ▼
     Risk Analysis
            │
            ▼
       Gemini LLM
            │
            ▼
    Account Health
Input
{
  "account_id": "ACC-3336"
}
Output
{
  "account_id": "ACC-3336",
  "company": "Omni Consumer Products",
  "executive_summary": "Omni Consumer Products is currently classified as At Risk.",
  "open_risks_and_flagged_issues": [
    {
      "ticket_id": "TKT-10293",
      "signal_type": "escalation_risk",
      "severity": "medium",
      "reason": "The ticket reports timeout behavior."
    }
  ],
  "tam_talking_points": [
    "Investigate recent P1 incidents.",
    "Review seat utilization and inactive usage.",
    "Develop a remediation plan for open tickets."
  ],
  "ticket_count_90d": 1
}
Unknown Account Handling

If the Account ID does not exist, the system returns a controlled error:

{
  "detail": "Account 'ACC-2765' was not found in accounts.json."
}

This prevents unsupported AI-generated account analysis.

🧪 Task 3 — Evaluation

The project includes an automated evaluation framework.

task3/evaluation/
├── evaluate.py
├── task1_test.json
├── task2_test.json
└── evaluation_report.json
Results
Metric	Result
Total Tests	12
Passed	11
Failed	1
Pass Rate	92%
Quality Score	0.93
Task 1	5/6
Task 2	6/6

Task 2 achieved 6/6 tests passed.

🏗️ Architecture
                 ┌─────────────────┐
                 │  Streamlit UI   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   FastAPI API   │
                 └────────┬────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
       ┌──────────────┐       ┌──────────────┐
       │    Task 1    │       │    Task 2    │
       │ Ticket Triage│       │ Account Risk │
       └──────┬───────┘       └──────┬───────┘
              │                      │
              ▼                      ▼
       ┌──────────────┐       ┌──────────────┐
       │ ChromaDB/RAG │       │ JSON Data    │
       └──────┬───────┘       └──────┬───────┘
              │                      │
              └──────────┬───────────┘
                         ▼
                 ┌──────────────┐
                 │ Gemini LLM   │
                 └──────┬───────┘
                        ▼
                 Structured JSON
🛠️ Tech Stack
Technology	Purpose
Python	Core development
FastAPI	REST API
Google Gemini	LLM reasoning
ChromaDB	Vector database
RAG	Knowledge retrieval
Streamlit	User interface
Pydantic	Data validation
JSON	Account/ticket data
Markdown	Knowledge base
📦 Installation
Task 1
cd task1
pip install -r requirements.txt
python -m uvicorn main:app --reload

In another terminal:

cd task1
streamlit run streamlit_app.py
Task 2
cd task2
pip install -r requirements.txt
python -m uvicorn main:app --reload

In another terminal:

cd task2
streamlit run streamlit_app.py
🔑 Environment Variables

Create a .env file locally:

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.1-flash-lite
EMBEDDING_MODEL=gemini-embedding-001

Never commit API keys or .env files to GitHub.

Recommended .gitignore:

.env
.env.*
__pycache__/
*.pyc
Chroma_db/
*.db
*.sqlite
.venv/
venv/
🧪 Run Evaluation
cd task3/evaluation
python evaluate.py

The evaluation report is generated as:

evaluation_report.json
🎯 Design Considerations
Accuracy

RAG retrieval, relevance thresholds, structured prompts, and output validation improve classification quality.

Explainability

The system provides reasoning, evidence, knowledge-base references, and risk explanations.

Security

API keys are stored using environment variables. Production deployments should add PII redaction, encryption, authentication, authorization, and audit logging.

Scalability

Potential improvements include:

Async processing
Caching
Batching
Multiple FastAPI workers
Rate limiting
Persistent vector storage
Background workers
🔮 Future Improvements
Production-grade vector database
Redis caching
Authentication and RBAC
PII detection/redaction
Monitoring and observability
Human-in-the-loop escalation
CRM integration
Support-platform integration
Docker deployment
Horizontal scaling
🏆 Project Summary

Zycus AI Support Triage demonstrates an end-to-end AI automation workflow combining:

LLM + RAG + Semantic Search + Support Ticket Triage + Account Risk Analysis + FastAPI + Streamlit

The project focuses on:

Accuracy → Explainability → Security → Scalability

👨‍💻 Author

Bajarang Khemana Dhamanekar

AI / ML Engineer

Skills Demonstrated
Python
FastAPI
Generative AI
Google Gemini
RAG
ChromaDB
LLM Applications
Streamlit
Pydantic
Semantic Search
Prompt Engineering
API Development
AI Automation
