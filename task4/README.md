# Zycus AI Support Triage and TAM Support

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


# 🎯 Task 1 — AI Support Ticket Triage

Task 1 automatically analyzes and classifies customer support tickets using **Gemini + RAG + ChromaDB**.

The system retrieves relevant Markdown knowledge-base documents and provides the retrieved context to Gemini for structured classification.

## Key Features

- Ticket classification
- Product-area detection
- Issue-category detection
- P1/P2/P3 urgency classification
- Known-issue detection
- Knowledge-base retrieval
- Knowledge-base source references
- Recommended support team
- Customer-facing first response

## Workflow

```text
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
```

## 📥 Input

```json
{
  "subject": "Unable to login",
  "body": "Users are receiving SESSION_INVALID during login.",
  "product": "CloudSync",
  "product_area": "Authentication",
  "plan_tier": "Business"
}
```

## 📤 Output

```json
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
```

---

# 🔍 Task 2 — Account Risk Analysis

Task 2 analyzes customer account health and identifies potential risks for **Customer Success/TAM teams**.

The system accepts an **Account ID**, retrieves account and ticket data, and analyzes customer-health signals such as:

- Usage
- Seat utilization
- Support incidents
- P1 incidents
- Inactivity
- NPS
- Open tickets
- Competitive vendor evaluation
- Renewal risk

## Workflow

```text
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
```

## 📥 Input

```json
{
  "account_id": "ACC-3336"
}
```

## 📤 Output

```json
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
```

## ❌ Unknown Account Handling

If the Account ID does not exist, the system returns a controlled error instead of generating unsupported analysis.

```json
{
  "detail": "Account 'ACC-2765' was not found in accounts.json."
}
```

This prevents unsupported AI-generated account analysis.

---

# 🧪 Task 3 — Evaluation

The project includes an automated evaluation framework.

```text
task3/evaluation/
├── evaluate.py
├── task1_test.json
├── task2_test.json
└── evaluation_report.json
```

## 📊 Evaluation Results

| Metric | Result |
|---|---:|
| Total Tests | 12 |
| Passed | 11 |
| Failed | 1 |
| Pass Rate | 92% |
| Quality Score | 0.93 |
| Task 1 | 5/6 |
| Task 2 | 6/6 |

**Task 2 achieved 6/6 tests passed.**

---

# 🏗️ Architecture

```text
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
```

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core development |
| **FastAPI** | REST API |
| **Google Gemini** | LLM reasoning |
| **ChromaDB** | Vector database |
| **RAG** | Knowledge retrieval |
| **Streamlit** | User interface |
| **Pydantic** | Data validation |
| **JSON** | Account and ticket data |
| **Markdown** | Knowledge base |

---

# 📦 Installation

## Task 1

Navigate to the Task 1 directory:

```bash
cd task1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
python -m uvicorn main:app --reload
```

Open another terminal and run Streamlit:

```bash
cd task1
streamlit run streamlit_app.py
```

---

## Task 2

Navigate to the Task 2 directory:

```bash
cd task2
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
python -m uvicorn main:app --reload
```

Open another terminal and run Streamlit:

```bash
cd task2
streamlit run streamlit_app.py
```

---

# 🔑 Environment Variables

Create a `.env` file locally.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.1-flash-lite
EMBEDDING_MODEL=gemini-embedding-001
```

Replace `your_gemini_api_key` with your actual Gemini API key.

> **Never commit API keys or `.env` files to GitHub.**

---

# 🔐 Security

Recommended `.gitignore`:

```gitignore
.env
.env.*
__pycache__/
*.pyc
Chroma_db/
*.db
*.sqlite
.venv/
venv/
```

The following should not be committed:

- `.env` files
- API keys
- `__pycache__/`
- Generated database files
- Sensitive customer information

If an API key is accidentally exposed:

1. Revoke the exposed key.
2. Generate a new key.
3. Remove the secret from Git history.
4. Update the local `.env` file.
5. Verify GitHub secret scanning.

---

# 🧪 Run Evaluation

Navigate to the evaluation directory:

```bash
cd task3/evaluation
```

Run the evaluation:

```bash
python evaluate.py
```

The evaluation report is generated as:

```text
evaluation_report.json
```

---

# 🎯 Design Considerations

## Accuracy

RAG retrieval, relevance thresholds, structured prompts, and output validation help improve classification quality.

## Explainability

The system provides:

- Reasoning
- Evidence
- Knowledge-base references
- Risk explanations

This makes the AI-generated results easier to understand and validate.

## Security

API keys are stored using environment variables.

For production, additional security measures should include:

- PII redaction
- Encryption
- Authentication
- Authorization
- Role-based access control
- Audit logging
- Secure secret management

## Scalability

Potential improvements include:

- Async processing
- Caching
- Batching
- Multiple FastAPI workers
- API rate limiting
- Persistent vector storage
- Background workers

---

# 🔮 Future Improvements

- Production-grade vector database
- Redis caching
- Authentication and RBAC
- PII detection and redaction
- Monitoring and observability
- Human-in-the-loop escalation
- CRM integration
- Support-platform integration
- Docker deployment
- Horizontal scaling

---

# 💡 Why RAG?

RAG allows Task 1 to use information from the internal knowledge base instead of relying only on the LLM's general knowledge.

```text
Customer Ticket
      │
      ▼
Semantic Search
      │
      ▼
Relevant Knowledge Base
      │
      ▼
Gemini LLM
      │
      ▼
Final Classification
```

This improves the ability to identify known issues and provides knowledge-base references that support the classification.

---

# 💡 Why ChromaDB?

ChromaDB is used as the vector database for storing and retrieving knowledge-base embeddings.

It provides:

- Semantic similarity search
- Vector storage
- Fast retrieval
- Simple local deployment
- Integration with RAG workflows

---

# 💡 Why FastAPI?

FastAPI provides the REST API layer for the application.

Key benefits:

- Request validation
- Pydantic integration
- Automatic API documentation
- Lightweight architecture
- Async support
- Easy deployment

---

# 💡 Why Streamlit?

Streamlit provides an interactive interface for both tasks without requiring a separate frontend application.

### Task 1

Users can enter:

```text
Subject
Body
Product
Product Area
Plan Tier
```

and receive:

```text
Issue Category
Urgency
Known Issue
Recommended Team
First Response
```

### Task 2

Users can enter:

```text
Account ID
```

and receive:

```text
Account Health
Executive Summary
Risks
Flagged Issues
TAM Talking Points
```

---

# 💡 Structured JSON Output

The system produces structured JSON responses so that results can easily be consumed by other applications.

Potential integrations include:

- CRM systems
- Customer support platforms
- Customer-success dashboards
- Internal automation
- Reporting systems
- Alerting systems

Structured outputs also make automated evaluation easier.

---

# 📈 Overall Project Flow

```text
                    ┌─────────────────────┐
                    │     User Input      │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │     Task 1      │         │     Task 2      │
        │ Support Ticket  │         │  Account ID     │
        │     Triage      │         │  Risk Analysis  │
        └────────┬────────┘         └────────┬────────┘
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │    ChromaDB     │         │ accounts.json   │
        │       RAG       │         │ tickets.json   │
        └────────┬────────┘         └────────┬────────┘
                 │                           │
                 └─────────────┬─────────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │  Google Gemini  │
                      │       LLM       │
                      └────────┬────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │ Structured JSON │
                      └────────┬────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │   Streamlit UI  │
                      └─────────────────┘
```

---

# 🧪 Testing Strategy

The evaluation framework contains separate test datasets for each task.

```text
Task 1
  │
  └── task1_test.json
          │
          ▼
     evaluate.py
          │
          ▼
evaluation_report.json


Task 2
  │
  └── task2_test.json
          │
          ▼
     evaluate.py
          │
          ▼
evaluation_report.json
```

Current evaluation:

```text
Total Tests       : 12
Passed            : 11
Failed            : 1
Pass Rate         : 92%
Quality Score     : 0.93

Task 1            : 5/6
Task 2            : 6/6
```

---

# 📌 Security Checklist

Before pushing the repository to GitHub:

- Remove `.env` files
- Add `.env` to `.gitignore`
- Remove API keys
- Remove `__pycache__/`
- Remove generated database files
- Check GitHub secret scanning
- Rotate accidentally exposed API keys
- Avoid committing sensitive customer information
- Verify repository history for secrets

---

# 📝 Example `.gitignore`

```gitignore
# Environment
.env
.env.*

# Python
__pycache__/
*.py[cod]
*.pyo

# Virtual environments
venv/
.venv/
env/

# ChromaDB
Chroma_db/

# Databases
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

# 🏆 Project Summary

**Zycus AI Support Triage** demonstrates an end-to-end AI automation workflow combining:

**LLM + RAG + Semantic Search + Support Ticket Triage + Account Risk Analysis + FastAPI + Streamlit**

The project focuses on:

**Accuracy → Explainability → Security → Scalability**

---

# 👨‍💻 Author

**Bajarang Khemana Dhamanekar**

**AI / ML Engineer**

## Skills Demonstrated

```text
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
```

---

# ⭐ Project

If you find this project useful, consider giving the repository a ⭐ star.
