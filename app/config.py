import os
from pathlib import Path
from dotenv import load_dotenv

# =================================== PATHS ===================================
# --- Base Paths ---
# config.py is in app/, so parent is app, parent.parent is project root
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Configurable Paths ---
COMPANY_DATASET_DIR = BASE_DIR / "company_dataset"
WEB_DATA_DIR = BASE_DIR / "web_data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "template"
ENV_DIR = BASE_DIR / "placify_env"

COMPANIES_FILE = COMPANY_DATASET_DIR / "companies.json"
RESUME_DIR = WEB_DATA_DIR / "resume"
PDF_DIR = WEB_DATA_DIR / "pdf"
ANALYSIS_DIR = WEB_DATA_DIR / "analysis"

# Ensure directories exist
os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)

# =================================== API Keys Setup ====================================
ENV_FILE = ENV_DIR / ".env"

# Load the environment variables from the specific .env file
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    print(f"Warning: .env file not found at {ENV_FILE}")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables.")
