import os
import re

id_pattern = re.compile(r'^.\d+$') 

API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
FORCE_SUB = os.environ.get("FORCE_SUB", "")
DB_NAME = os.environ.get("DB_NAME", "")
DB_URL = os.environ.get("DB_URL", "")
FLOOD = int(os.environ.get("FLOOD", "10"))
START_PIC = os.environ.get("START_PIC", "")
ADMIN = [int(admin) for admin in os.environ.get("ADMIN", "").split()]
PORT = int(os.environ.get("PORT", "8080"))
