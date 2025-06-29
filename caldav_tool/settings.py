import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

CALDAV_URL = os.getenv("CALDAV_URL", "http://localhost:5232/")
CALDAV_USERNAME = os.getenv("CALDAV_USERNAME", "user")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD", "password") 