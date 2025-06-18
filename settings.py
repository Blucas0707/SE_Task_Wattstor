import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TEST_DATABASE_URL") if os.getenv("TEST_DATABASE_URL") else os.getenv("DATABASE_URL")
AUTH_ALGORITHM = os.getenv('AUTH_ALGORITHM')
AUTH_SECRET_KEY = os.getenv('AUTH_SECRET_KEY')
