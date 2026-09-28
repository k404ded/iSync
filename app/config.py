"""
iSync Configuration Module
Defines runtime configurations, thresholds, and environment settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
SAMPLE_COURSES_DIR = SAMPLE_DATA_DIR / "course_files"
OUTPUT_DIR = BASE_DIR / "outputs"
SCRATCH_DIR = BASE_DIR / "scratch"

# Ensure runtime directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_COURSES_DIR.mkdir(parents=True, exist_ok=True)

# Environment and Provider
ISYNC_ENV = os.getenv("ISYNC_ENV", "development")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Scoring and Precision Settings
# Precision over quantity: Only flag genuine, verified impacts
LEXICAL_WEIGHT = 0.35
SEMANTIC_WEIGHT = 0.45
CONTEXT_WEIGHT = 0.20

# Thresholds for candidate filtering
CANDIDATE_MATCH_THRESHOLD = 0.25
HIGH_CONFIDENCE_THRESHOLD = 0.70
MEDIUM_CONFIDENCE_THRESHOLD = 0.45

# Demo Defaults
DEFAULT_SOFTWARE = "SOLIDWORKS"
DEFAULT_OLD_VERSION = "2024"
DEFAULT_NEW_VERSION = "2025"
