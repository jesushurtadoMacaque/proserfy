import os
from dotenv import load_dotenv


load_dotenv()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_AUTH_ENDPOINT = os.environ.get("GOOGLE_AUTH_ENDPOINT", None)
GOOGLE_REDIRECT_URL = os.environ.get("GOOGLE_REDIRECT_URL", None)
GOOGLE_RESPONSE_TYPE = os.environ.get("GOOGLE_RESPONSE_TYPE", None)
GOOGLE_SCOPE = os.environ.get("GOOGLE_SCOPE", None)
GOOGLE_TOKEN_URL = os.environ.get("GOOGLE_TOKEN_URL", None)
