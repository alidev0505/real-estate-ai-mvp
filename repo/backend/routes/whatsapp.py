"""WhatsApp routes. The two /whatsapp/webhook endpoints are public (Meta calls them) and protected by
the verify token + HMAC signature. Everything else here requires the agent login."""
import hmac
import logging
import re
from datetime import datetime, timedelta
from flask import Blueprint, current_app, jsonify, request
from config import Config
from models import db, Lead, Conversation
from models.whatsapp import WhatsAppContact, WhatsAppMessage
from services import auth_service, whatsapp_service as wa

wa_bp = Blueprint("whatsapp", __name__, url_prefix="/api")
wa_bp.before_request(auth_service.guard)
log = logging.getLogger(__name__)


def err(msg, code=400):
    return jsonify({"error": msg}), code


@wa_bp.get("/whatsapp/webhook")
def verify():
    a = request.args
    tok = Config.WHATSAPP_VERIFY_TOKEN
    if a.get("hub.mode") == "subscribe" and tok and hmac.compare_digest(a.get("hub.verify_token", ""), tok):
        return a.get("hub.challenge", ""), 200, {"Content-Type": "text/plain"}
    return "Forbidden", 403


@wa_bp.post("/whatsapp/webhook")
def receive():
    if not wa.verify_signature(request.get_data(), request.headers.get("X-Hub-Signature-256", "")):
        log.warning("Rejected WhatsApp webhook with bad/missing signature")
        return "Invalid signature", 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return "Bad request", 400
    if payload.get("object") == "whatsapp_business_account":
        wa.dispatch(current_app._get_current_object(), payload)
    return "", 200  # always 200 quickly so Meta does not retry


# ---- agent-facing ----
def _window(contact):
    return bool(contact and contact.last_inbound_at and datetime.utcnow() - contact.last_inbound_at < timedelta(hours=24))


@wa_bp.get("/leads/<int:lead_id>/whatsapp")
def lead_info(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead: return err("Lead not found", 404)
    c = WhatsAppContact.query.filter_by(lead_id=lead_id).first()
    last = WhatsAppMessage.query.filter_by(lead_id=lead_id, direction="out").order_by(WhatsAppMessage.id.desc()).first()
    return jsonify({"configured": wa.is_configured(), "demo": bool(lead.is_demo), "has_phone": len(wa.digits(c.phone if c else lead.phone)) >= 8,
                    "connected": bool(c), "within_window": _window(c), "opted_out": bool(c and c.opted_out),
                    "template_configured": bool(Config.WHATSAPP_FOLLOWUP_TEMPLATE),
                    "last_outbound_status": last.status if last else None, "last_outbound_error": last.error if last else None})


@wa_bp.post("/leads/<int:lead_id>/whatsapp/send")
def send(lead_id):
    d = request.get_json(silent=True) or {}
    body = str(d.get("body") or "").strip()[:4000]
    lang = "ar" if d.get("lang") == "ar" else "en"
    lead = db.session.get(Lead, lead_id)
    if not lead: return err("Lead not found", 404)
    if lead.is_demo: return err("This is a demo lead with a fictional number. Sending is disabled.", 400)
    if not wa.is_configured(): return err("WhatsApp is not configured. Set the WHATSAPP_* values in backend/.env.", 503)
    c = WhatsAppContact.query.filter_by(lead_id=lead_id).first()
    phone = c.phone if c else wa.digits(lead.phone)
    if not 8 <= len(phone) <= 15: return err("This lead has no valid phone number.", 400)
    if not c:
        c = WhatsAppContact.query.filter_by(phone=phone).first() or WhatsAppContact(phone=phone, lead_id=lead_id, lang=lang)
        db.session.add(c); db.session.flush()
    if c.opted_out: return err("This contact opted out of WhatsApp messages.", 409)
    try:
        if _window(c):
            if not body: return err("Message cannot be empty.")
            wid, via = wa.send_text(phone, body), "text"
            stored = body
        elif Config.WHATSAPP_FOLLOWUP_TEMPLATE:
            first = (lead.name or "").split(" ")[0] or ("عميلنا" if lang == "ar" else "there")
            wid, via = wa.send_template(phone, Config.WHATSAPP_FOLLOWUP_TEMPLATE, lang, [first]), "template"
            stored = f"[Template message '{Config.WHATSAPP_FOLLOWUP_TEMPLATE}' sent]"
        else:
            db.session.rollback()
            return err("Outside WhatsApp's 24-hour reply window. Free-text messages are only allowed within 24 hours of the "
                       "customer's last message. Create an approved template and set WHATSAPP_FOLLOWUP_TEMPLATE.", 409)
    except wa.WhatsAppError as e:
        db.session.rollback(); wa._log_out(lead_id, None, "failed", str(e))
        return err(f"WhatsApp rejected the message: {e}", 502)
    db.session.add(Conversation(lead_id=lead_id, role="assistant", message=f"[Agent follow-up via WhatsApp] {stored}"))
    db.session.commit()
    wa._log_out(lead_id, wid, "sent")
    return jsonify({"sent": True, "via": via, "wa_message_id": wid})
