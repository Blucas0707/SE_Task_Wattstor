import os

from dotenv import load_dotenv

load_dotenv()

if os.getenv("ENV") == "testing":
    DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
else:
    DATABASE_URL = os.getenv("DATABASE_URL")

AUTH_ALGORITHM = os.getenv('AUTH_ALGORITHM')
AUTH_SECRET_KEY = os.getenv('AUTH_SECRET_KEY')
