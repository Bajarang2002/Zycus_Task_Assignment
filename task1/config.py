import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = next(
    (
        path
        for path in (BASE_DIR / "data", BASE_DIR / "Data")
        if path.exists()
    ),
    BASE_DIR / "data"
)

KB_PATH = next(
    (
        path
        for path in (
            DATA_DIR / "knowledge_base",
            DATA_DIR / "knowledge-base"
        )
        if path.exists() and any(path.rglob("*.md"))
    ),
    DATA_DIR / "knowledge_base"
)

TICKETS_PATH = DATA_DIR / "tickets.json"
CHROMA_PATH = BASE_DIR / "chroma_db"

ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "gemini-embedding-001"
)

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing in .env")

DATA_DIR.mkdir(parents=True, exist_ok=True)
KB_PATH.mkdir(parents=True, exist_ok=True)
CHROMA_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("ZYCUS TRIAGE CONFIGURATION")
print("=" * 70)
print("BASE_DIR:", BASE_DIR)
print("KB_PATH:", KB_PATH)
print("KB_EXISTS:", KB_PATH.exists())
print("CHROMA_PATH:", CHROMA_PATH)
print("=" * 70)