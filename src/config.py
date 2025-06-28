# src/config.py
import os
import logging
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"
SHEET_NAME = "stock-sheet-gurjyot"
LOG_FILE = "stock_analysis.log"
WORKSHEET_NAME = "Sheet2" if TEST_MODE else "Sheet1"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
CALLS_PER_MINUTE = 5
PERIOD = 60  # seconds

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize Google Sheets
creds_dict = json.loads(GOOGLE_CREDS_JSON)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gspread_client = gspread.authorize(creds)
sheet = gspread_client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

# Initialize OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

