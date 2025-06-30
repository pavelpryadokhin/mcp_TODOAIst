import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


CALDAV_URL = os.getenv("CALDAV_URL")
CALDAV_USERNAME = os.getenv("CALDAV_USERNAME")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD")

if not all([CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD]):
    raise ValueError("Missing required environment variables: CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD") 