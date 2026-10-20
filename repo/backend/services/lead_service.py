"""Lead profile merging, rule-based qualification and follow-up status."""
import re
from models import Conversation, Viewing

REQUIRED = ["property_type", "bedrooms", "area", "purpose", "budget", "timeline"]
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")
PURPOSES = {"investment": "Investment", "invest": "Investment", "rental": "Investment",
            "personal": "Personal Use", "personal use": "Personal Use", "end user": "Personal Use"}


def missing_fields(lead):
    return [f for f in REQUIRED if getattr(lead, f) in (None, "")]


def _s(v, n=80):
    return v.strip()[:n] if isinstance(v, str) and v.strip() else None


def merge_extracted(lead, ex):
    """Merge LLM extraction into the lead. Nulls/invalid values never overwrite stored data."""
    if _s(ex.get("property_type"), 40):
        lead.property_type = ex["property_type"].strip().title()
    try:
        b = int(ex["bedrooms"]) if ex.get("bedrooms") is not None else None
        if b is not None and 0 <= b <= 12:
            lead.bedrooms = b
    except (TypeError, ValueError):
        pass
    if _s(ex.get("area")):
        lead.area = ex["area"].strip()
    p = _s(ex.get("purpose"), 40)
    if p and p.lower() in PURPOSES:
        lead.purpose = PURPOSES[p.lower()]
    try:
        bud = ex.get("budget")
        if isinstance(bud, str):
            bud = float(re.sub(r"[^\d.]", "", bud.translate(AR_DIGITS)) or 0)
        if bud is not None and 100_000 <= float(bud) <= 500_000_000:  # invalid budgets are ignored
            lead.budget = int(bud)
    except (TypeError, ValueError):
        pass
    if _s(ex.get("timeline"), 60):
        lead.timeline = ex["timeline"].strip()
    if _s(ex.get("name"), 120) and not lead.name:
        lead.name = ex["name"].strip()
    em = _s(ex.get("email"), 160)
    if em and re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+$", em) and not lead.email:
        lead.email = em
    if _s(ex.get("phone"), 40) and not lead.phone:
        lead.phone = ex["phone"].strip()


def compute_status(lead):
    miss = missing_fields(lead)
    if not miss:
        return "qualified"
    has_user_msgs = Conversation.query.filter_by(lead_id=lead.id, role="user").count() > 0
    return "info_needed" if has_user_msgs and len(miss) < len(REQUIRED) else "new"


def follow_up(lead):
    viewing = Viewing.query.filter_by(lead_id=lead.id).first()
    if viewing:
        status = "Viewing Requested"
    elif lead.status == "qualified":
        status = "Qualified"
    else:
        status = "Waiting for Lead"
    return {"status": status,
            "steps": [{"label": "Initial response", "done": True},
                      {"label": "Follow-up #1", "done": bool(viewing)},
                      {"label": "Follow-up #2", "done": False}],
            "human_requested": bool(lead.human_requested),
            "note": "Simulated for the MVP. No WhatsApp or email messages are sent."}
