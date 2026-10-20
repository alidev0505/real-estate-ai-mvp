import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///realestate.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").lower()
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "")
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]

    @classmethod
    def ai_configured(cls):
        key_ok = cls.AI_API_KEY and not cls.AI_API_KEY.startswith("your_")
        model_ok = cls.AI_MODEL and not cls.AI_MODEL.startswith("your_")
        return bool(key_ok and model_ok)


import secrets as _secrets
Config.SECRET_KEY = os.getenv("SECRET_KEY") or _secrets.token_hex(32)  # set in .env so logins survive restarts
Config.AGENT_USERNAME = os.getenv("AGENT_USERNAME", "agent")
Config.AGENT_PASSWORD = os.getenv("AGENT_PASSWORD", "change-me")
Config.TOKEN_MAX_AGE = 12 * 3600


# ---- WhatsApp Cloud API (Meta) ----
Config.WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
Config.WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
Config.WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
Config.WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
Config.WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v21.0")  # use the version shown in your Meta dashboard
Config.WHATSAPP_FOLLOWUP_TEMPLATE = os.getenv("WHATSAPP_FOLLOWUP_TEMPLATE", "")  # approved template for messages outside the 24h window
Config.WHATSAPP_ALLOW_UNSIGNED = os.getenv("WHATSAPP_ALLOW_UNSIGNED", "false").lower() == "true"  # local testing only
Config.WHATSAPP_ASYNC = True  # process webhooks in a background thread so Meta always gets a fast 200
