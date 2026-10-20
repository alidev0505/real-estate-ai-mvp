"""Simple single-agent sign-in with signed, expiring tokens. MVP-grade, not production auth."""
import hmac
from flask import jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from config import Config

PUBLIC = {("GET", "/api/health"), ("POST", "/api/chat"), ("POST", "/api/viewings"), ("POST", "/api/auth/login"),
          ("GET", "/api/whatsapp/webhook"), ("POST", "/api/whatsapp/webhook")}


def _ser():
    return URLSafeTimedSerializer(Config.SECRET_KEY, salt="agent-auth")


def check_credentials(username, password):
    ok_u = hmac.compare_digest(str(username or ""), Config.AGENT_USERNAME)
    ok_p = hmac.compare_digest(str(password or ""), Config.AGENT_PASSWORD)
    return ok_u and ok_p


def make_token(username):
    return _ser().dumps({"u": username})


def current_agent():
    h = request.headers.get("Authorization", "")
    if not h.startswith("Bearer "):
        return None
    try:
        return _ser().loads(h[7:], max_age=Config.TOKEN_MAX_AGE)["u"]
    except (BadSignature, SignatureExpired, KeyError):
        return None


def guard():
    """before_request hook: everything except PUBLIC endpoints needs a valid agent token."""
    if request.method == "OPTIONS" or (request.method, request.path.rstrip("/")) in PUBLIC:
        return None
    if not current_agent():
        return jsonify({"error": "Please sign in to continue."}), 401
    return None
