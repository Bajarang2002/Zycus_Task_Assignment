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
