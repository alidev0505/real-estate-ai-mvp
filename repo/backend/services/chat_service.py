"""Channel-independent chat turn + viewing creation. Used by the WhatsApp gateway.
(The web chat route keeps its own inline copy of this logic so existing code stays untouched.)"""
import re
from models import db, Conversation, Viewing
from services import ai_service, lead_service as ls, property_service

ARABIC = re.compile(r"[\u0600-\u06FF]")
SLOTS = ["11:00 AM", "2:00 PM", "5:00 PM"]


def run_turn(lead, text):
    """One AI turn for an existing lead. Raises ai_service.AIError on AI failure (nothing is saved then)."""
    history = [{"role": m.role, "content": m.message}
               for m in Conversation.query.filter_by(lead_id=lead.id).order_by(Conversation.id).all()]
    history.append({"role": "user", "content": text})
    result = ai_service.chat_turn(history, lead.profile())
    db.session.add(Conversation(lead_id=lead.id, role="user", message=text))
    ls.merge_extracted(lead, result["extracted_data"])
    if result.get("human_requested") is True:
        lead.human_requested = True
    db.session.flush()
    lead.status = ls.compute_status(lead)
    reply = result["reply"].strip()
    db.session.add(Conversation(lead_id=lead.id, role="assistant", message=reply))
    db.session.commit()
    lang = result.get("language") if result.get("language") in ("ar", "en") else ("ar" if ARABIC.search(text) else "en")
    m = property_service.match_properties(lead) if lead.status == "qualified" else {"matches": [], "quality": "none"}
    return {"reply": reply, "status": lead.status, "missing_fields": ls.missing_fields(lead), "language": lang,
            "matches": m["matches"], "match_quality": m["quality"]}


def create_viewing(lead, prop, day, slot):
    v = Viewing(lead_id=lead.id, property_id=prop.id, date=day, time=slot)
    db.session.add(v)
    db.session.add(Conversation(lead_id=lead.id, role="assistant",
                                message=f"Viewing request submitted for {prop.title} on {day.strftime('%d %B %Y')} at {slot}. "
                                        "Our team will confirm the appointment."))
    db.session.commit()
    return v
