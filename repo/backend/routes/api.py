import logging
from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from config import Config
from models import db, Lead, Conversation, Property, Viewing
import re
from services import ai_service, auth_service, lead_service as ls, property_service

api = Blueprint("api", __name__, url_prefix="/api")
log = logging.getLogger(__name__)
SLOTS = ["11:00 AM", "2:00 PM", "5:00 PM"]
GREETING = "Hi! Welcome. I can help you find a property in Dubai. What type of property are you looking for?"
GREETING_AR = "مرحبًا بك! يسعدني مساعدتك في العثور على عقار في دبي. ما نوع العقار الذي تبحث عنه؟"
ARABIC = re.compile(r"[\u0600-\u06FF]")
FRIENDLY_ERROR = "I'm having trouble processing that right now. Please try again in a moment."


api.before_request(auth_service.guard)


def err(msg, code=400):
    return jsonify({"error": msg}), code


@api.errorhandler(SQLAlchemyError)
def db_error(e):
    db.session.rollback()
    log.exception("Database error")
    return err("A database error occurred. Please try again.", 500)


@api.get("/health")
def health():
    return jsonify({"ok": True, "ai_configured": Config.ai_configured(), "provider": Config.AI_PROVIDER,
                    "model": Config.AI_MODEL or None, "database": Config.SQLALCHEMY_DATABASE_URI.split(":")[0]})


# ---- Leads ----
@api.post("/leads")
def create_lead():
    d = request.get_json(silent=True) or {}
    lead = Lead(name=(d.get("name") or "")[:120] or None, email=(d.get("email") or "")[:160] or None,
                phone=(d.get("phone") or "")[:40] or None)
    db.session.add(lead); db.session.commit()
    return jsonify(lead.to_dict()), 201


def _lead_row(l):
    d = l.to_dict()
    d["follow_up_status"] = ls.follow_up(l)["status"]
    d["message_count"] = Conversation.query.filter_by(lead_id=l.id).count()
    return d


@api.get("/leads")
def list_leads():
    return jsonify([_lead_row(l) for l in Lead.query.order_by(Lead.updated_at.desc()).all()])


@api.get("/leads/<int:lead_id>")
def get_lead(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        return err("Lead not found", 404)
    d = lead.to_dict()
    d["missing_fields"] = ls.missing_fields(lead)
    d["follow_up"] = ls.follow_up(lead)
    d["viewings"] = [v.to_dict() for v in Viewing.query.filter_by(lead_id=lead_id).all()]
    return jsonify(d)


@api.get("/leads/<int:lead_id>/conversation")
def get_conversation(lead_id):
    if not db.session.get(Lead, lead_id):
        return err("Lead not found", 404)
    msgs = Conversation.query.filter_by(lead_id=lead_id).order_by(Conversation.id).all()
    return jsonify([m.to_dict() for m in msgs])


# ---- Chat ----
@api.post("/chat")
def chat():
    d = request.get_json(silent=True) or {}
    text = (d.get("message") or "").strip()
    lang = "ar" if d.get("lang") == "ar" else "en"  # only used for the greeting
    if not text:
        return err("Message cannot be empty")
    if len(text) > 2000:
        return err("Message is too long (max 2000 characters)")

    lead = db.session.get(Lead, d["lead_id"]) if d.get("lead_id") else None
    if d.get("lead_id") and not lead:
        return err("Lead not found", 404)
    if not lead:  # lead state always lives on the server; the client only holds an id
        lead = Lead()
        db.session.add(lead); db.session.flush()
        db.session.add(Conversation(lead_id=lead.id, role="assistant", message=GREETING_AR if lang == "ar" else GREETING))

    history = [{"role": m.role, "content": m.message}
               for m in Conversation.query.filter_by(lead_id=lead.id).order_by(Conversation.id).all()]
    history.append({"role": "user", "content": text})
    try:
        result = ai_service.chat_turn(history, lead.profile())
    except ai_service.AIError as e:
        log.warning("AI failure: %s", e)
        db.session.commit()  # keep the lead (and greeting) created above
        return jsonify({"error": FRIENDLY_ERROR, "lead_id": lead.id}), 502

    db.session.add(Conversation(lead_id=lead.id, role="user", message=text))
    ls.merge_extracted(lead, result["extracted_data"])
    if result.get("human_requested") is True:
        lead.human_requested = True
    db.session.flush()
    lead.status = ls.compute_status(lead)
    db.session.add(Conversation(lead_id=lead.id, role="assistant", message=result["reply"].strip()))
    db.session.commit()

    language = result.get("language") if result.get("language") in ("ar", "en") else ("ar" if ARABIC.search(text) else "en")
    matches = property_service.match_properties(lead) if lead.status == "qualified" else {"matches": [], "quality": "none"}
    return jsonify({"lead_id": lead.id, "reply": result["reply"].strip(), "profile": lead.profile(),
                    "status": lead.status, "missing_fields": ls.missing_fields(lead),
                    "human_requested": lead.human_requested, "matches": matches["matches"],
                    "match_quality": matches["quality"], "language": language})


# ---- Properties ----
@api.get("/properties")
def list_properties():
    return jsonify([p.to_dict() for p in Property.query.order_by(Property.area, Property.price).all()])


@api.get("/properties/matches/<int:lead_id>")
def matches(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        return err("Lead not found", 404)
    m = property_service.match_properties(lead)
    return jsonify({"matches": m["matches"], "match_quality": m["quality"], "count": len(m["matches"])})


# ---- Viewings ----
@api.post("/viewings")
def create_viewing():
    d = request.get_json(silent=True) or {}
    lead = db.session.get(Lead, d.get("lead_id") or 0)
    prop = db.session.get(Property, d.get("property_id") or 0)
    if not lead or not prop:
        return err("Lead or property not found", 404)
    try:
        day = datetime.strptime(str(d.get("date")), "%Y-%m-%d").date()
    except ValueError:
        return err("Invalid date. Use YYYY-MM-DD.")
    if day < date.today() or day > date.today() + timedelta(days=60):
        return err("Choose a date within the next 60 days.")
    if d.get("time") not in SLOTS:
        return err(f"Invalid time slot. Choose one of: {', '.join(SLOTS)}")
    v = Viewing(lead_id=lead.id, property_id=prop.id, date=day, time=d["time"])
    db.session.add(v)
    db.session.add(Conversation(lead_id=lead.id, role="assistant",
                                message=f"Viewing request submitted for {prop.title} on {day.strftime('%d %B %Y')} at {d['time']}. "
                                        "Our team will confirm the appointment."))
    db.session.commit()
    return jsonify(v.to_dict()), 201


@api.get("/viewings")
def list_viewings():
    return jsonify([v.to_dict() for v in Viewing.query.order_by(Viewing.date, Viewing.id).all()])


# ---- Dashboard ----
@api.get("/dashboard/stats")
def stats():
    q = Lead.query
    return jsonify({"total_leads": q.count(), "new_leads": q.filter_by(status="new").count(),
                    "qualified_leads": q.filter_by(status="qualified").count(),
                    "viewings": Viewing.query.count(),
                    "info_needed": q.filter_by(status="info_needed").count()})
