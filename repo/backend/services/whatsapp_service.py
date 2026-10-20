"""WhatsApp Cloud API gateway: webhook parsing/verification, sending, and the conversation handler.
Provider-specific code (Meta Graph API) lives only in verify_signature/_post/send_*/parse_payload."""
import hashlib
import hmac
import logging
import re
import threading
from collections import defaultdict
from datetime import date, datetime, timedelta

import requests
from sqlalchemy.exc import IntegrityError

from config import Config
from models import db, Lead, Conversation, Property
from models.whatsapp import WhatsAppContact, WhatsAppMessage
from services import ai_service, chat_service, lead_service as ls, property_service

log = logging.getLogger(__name__)
TIMEOUT = 15
_locks = defaultdict(threading.Lock)  # serialise messages per phone number


class WhatsAppError(Exception):
    pass


def is_configured():
    return bool(Config.WHATSAPP_ACCESS_TOKEN and Config.WHATSAPP_PHONE_NUMBER_ID)


# ------------------------------------------------------------------ Meta transport
def verify_signature(raw_body, header):
    if not Config.WHATSAPP_APP_SECRET:
        return Config.WHATSAPP_ALLOW_UNSIGNED  # refuse unsigned payloads unless explicitly allowed for local testing
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(Config.WHATSAPP_APP_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header[7:])


def _post(payload):
    if not is_configured():
        raise WhatsAppError("WhatsApp is not configured (WHATSAPP_ACCESS_TOKEN / WHATSAPP_PHONE_NUMBER_ID).")
    url = f"https://graph.facebook.com/{Config.WHATSAPP_API_VERSION}/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    try:
        r = requests.post(url, json={"messaging_product": "whatsapp", **payload}, timeout=TIMEOUT,
                          headers={"Authorization": f"Bearer {Config.WHATSAPP_ACCESS_TOKEN}"})
    except requests.RequestException as e:
        raise WhatsAppError(f"Network error: {type(e).__name__}") from e
    if not r.ok:
        try:
            msg = r.json().get("error", {}).get("message", r.text[:200])
        except ValueError:
            msg = r.text[:200]
        raise WhatsAppError(f"Meta API {r.status_code}: {msg}")
    try:
        return r.json()["messages"][0]["id"]
    except (KeyError, IndexError, ValueError):
        return None


def send_text(to, body):
    return _post({"to": to, "type": "text", "text": {"body": body[:4000], "preview_url": False}})


def send_list(to, body, button, rows):
    """Interactive list (max 10 rows). rows: [(id, title<=24 chars)]."""
    return _post({"to": to, "type": "interactive", "interactive": {
        "type": "list", "body": {"text": body[:1000]},
        "action": {"button": button[:20], "sections": [{"title": "Options", "rows": [{"id": i[:200], "title": t[:24]} for i, t in rows]}]}}})


def send_template(to, name, lang, params):
    return _post({"to": to, "type": "template", "template": {
        "name": name, "language": {"code": lang},
        "components": [{"type": "body", "parameters": [{"type": "text", "text": p} for p in params]}] if params else []}})


def parse_payload(payload):
    """-> (messages, statuses). messages: [{id, from, name, text}] where text may be None for unsupported types."""
    msgs, statuses = [], []
    for entry in payload.get("entry", []) or []:
        for ch in entry.get("changes", []) or []:
            v = ch.get("value", {}) or {}
            names = {c.get("wa_id"): (c.get("profile") or {}).get("name") for c in v.get("contacts", []) or []}
            for m in v.get("messages", []) or []:
                text = None
                if m.get("type") == "text":
                    text = (m.get("text") or {}).get("body")
                elif m.get("type") == "interactive":
                    i = m.get("interactive") or {}
                    text = (i.get("list_reply") or i.get("button_reply") or {}).get("id")
                msgs.append({"id": m.get("id"), "from": m.get("from"), "name": names.get(m.get("from")), "text": text})
            statuses.extend(v.get("statuses", []) or [])
    return msgs, statuses


# ------------------------------------------------------------------ copy + quick options
MSG = {
    "en": {"need_text": "Sorry, I can only read text messages. Please type your answer.",
           "error": "I'm having trouble processing that right now. Please try again in a moment.",
           "optout": "You've been unsubscribed and won't receive further messages. Reply START to resume.",
           "optin": "Welcome back! How can I help with your property search?",
           "cancelled": "No problem, booking cancelled.", "agent": "Noted. I've flagged your request for a human agent in our system.",
           "no_option": "I couldn't find that option. Reply VIEW 1, VIEW 2 or VIEW 3 after you see your matches.",
           "pick_date": "Which day would you like to view {title}?\n{opts}\nReply with a number, or CANCEL.",
           "pick_slot": "What time works?\n{opts}\nReply with a number, or CANCEL.", "bad_choice": "Please reply with one of the numbers listed, or CANCEL.",
           "booked": "Viewing request submitted for {title} on {when}. Our team will confirm the appointment.",
           "head": "{n} demo {word} match your requirements (availability not verified):", "word1": "property", "wordn": "properties",
           "foot": "To request a viewing, reply {cmds}.", "btn": "Choose option", "body": "Choose an option or type your own answer."},
    "ar": {"need_text": "عذرًا، يمكنني قراءة الرسائل النصية فقط. يرجى كتابة إجابتك.",
           "error": "أواجه مشكلة في معالجة طلبك حاليًا. يرجى المحاولة بعد قليل.",
           "optout": "تم إلغاء اشتراكك ولن تصلك رسائل أخرى. أرسل START للاستئناف.",
           "optin": "أهلًا بعودتك! كيف أساعدك في البحث عن عقار؟",
           "cancelled": "لا مشكلة، تم إلغاء الحجز.", "agent": "تم تسجيل طلبك للتحدث مع وكيل بشري في نظامنا.",
           "no_option": "لم أجد هذا الخيار. أرسل VIEW 1 أو VIEW 2 أو VIEW 3 بعد ظهور العقارات.",
           "pick_date": "ما اليوم المناسب لمعاينة {title}؟\n{opts}\nأرسل رقمًا، أو CANCEL للإلغاء.",
           "pick_slot": "ما الوقت المناسب؟\n{opts}\nأرسل رقمًا، أو CANCEL للإلغاء.", "bad_choice": "يرجى إرسال أحد الأرقام المعروضة، أو CANCEL.",
           "booked": "تم إرسال طلب معاينة {title} بتاريخ {when}. سيؤكد فريقنا الموعد.",
           "head": "وجدنا {n} {word} تجريبية تناسب متطلباتك (التوفر غير مؤكد):", "word1": "عقارًا", "wordn": "عقارات",
           "foot": "لطلب معاينة أرسل {cmds}.", "btn": "اختر", "body": "اختر خيارًا أو اكتب إجابتك."},
}
# field -> [(title en, title ar, sent text en, sent text ar)]  (titles must be <= 24 chars: WhatsApp list limit)
Q = {
    "property_type": [("Apartment", "شقة"), ("Villa", "فيلا"), ("Townhouse", "تاون هاوس"), ("Penthouse", "بنتهاوس")],
    "bedrooms": [("Studio", "استوديو", "A studio"), ("1 bedroom", "غرفة نوم واحدة"), ("2 bedrooms", "غرفتا نوم"), ("3 bedrooms", "3 غرف نوم"),
                 ("4 bedrooms", "4 غرف نوم"), ("5+ bedrooms", "5 غرف أو أكثر", "5 or more bedrooms", "5 غرف نوم أو أكثر")],
    "area": [("Dubai Marina", "دبي مارينا"), ("Downtown Dubai", "وسط مدينة دبي"), ("Business Bay", "الخليج التجاري"), ("Jumeirah", "جميرا"),
             ("Palm Jumeirah", "نخلة جميرا"), ("Arabian Ranches", "أرابيان رانشز"), ("Dubai Hills", "دبي هيلز"), ("JVC", "قرية جميرا الدائرية")],
    "purpose": [("Investment", "استثمار", "It is for investment, mainly rental income", "للاستثمار، بشكل رئيسي للدخل الإيجاري"),
                ("Personal use", "سكن شخصي", "It is for personal use, to live in", "للسكن الشخصي")],
    "budget": [(f"About AED {l}", f"حوالي {a}", f"My budget is around AED {w}", f"ميزانيتي حوالي {a} درهم")
               for l, a, w in [("1M", "مليون", "1 million"), ("1.5M", "1.5 مليون", "1.5 million"), ("2.5M", "2.5 مليون", "2.5 million"),
                               ("4M", "4 ملايين", "4 million"), ("8M", "8 ملايين", "8 million")]],
    "timeline": [("Within 1 month", "خلال شهر"), ("Within 3 months", "خلال 3 أشهر"), ("Within 6 months", "خلال 6 أشهر"), ("6+ months", "أكثر من 6 أشهر")],
}
STOP, START = {"stop", "unsubscribe", "إيقاف"}, {"start", "ابدأ"}
CANCEL, AGENT = {"cancel", "إلغاء"}, {"agent", "human", "وكيل", "موظف"}


def _rows(field, lang):
    ar = lang == "ar"
    return [((o[3] if ar and len(o) > 3 else o[1]) if ar else (o[2] if len(o) > 2 else o[0]), o[1] if ar else o[0]) for o in Q[field]]


def digits(s):
    return re.sub(r"\D", "", (s or "").translate(ls.AR_DIGITS))


# ------------------------------------------------------------------ outbound helpers (log + never raise)
def _log_out(lead_id, wa_id, status, error=None):
    db.session.add(WhatsAppMessage(wa_message_id=wa_id, lead_id=lead_id, direction="out", status=status, error=(error or "")[:300] or None))
    db.session.commit()


def _send(lead, fn, *args):
    try:
        _log_out(lead.id, fn(*args), "sent")
        return True
    except WhatsAppError as e:
        log.warning("WhatsApp send failed: %s", e)
        _log_out(lead.id, None, "failed", str(e))
        return False


def _say(lead, phone, text, store=False):
    if store:
        db.session.add(Conversation(lead_id=lead.id, role="assistant", message=text)); db.session.commit()
    _send(lead, send_text, phone, text)


# ------------------------------------------------------------------ inbound handling
def process_payload(payload):
    msgs, statuses = parse_payload(payload)
    for s in statuses:
        _record_status(s)
    for m in msgs:
        if m["from"] and m["id"]:
            with _locks[m["from"]]:
                try:
                    _handle_message(m)
                except Exception:  # never let one bad message break the webhook worker
                    db.session.rollback(); log.exception("WhatsApp message handling failed")


def dispatch(app, payload):
    """Called by the webhook route. Returns immediately when WHATSAPP_ASYNC is on."""
    def run():
        with app.app_context():
            process_payload(payload)
    if Config.WHATSAPP_ASYNC:
        threading.Thread(target=run, daemon=True).start()
    else:
        run()


def _record_status(s):
    row = WhatsAppMessage.query.filter_by(wa_message_id=s.get("id")).first() if s.get("id") else None
    if row:
        row.status = s.get("status") or row.status
        errs = s.get("errors") or []
        if errs:
            row.error = (errs[0].get("title") or errs[0].get("message") or "error")[:300]
        db.session.commit()


def _get_contact(m):
    c = WhatsAppContact.query.filter_by(phone=m["from"]).first()
    if c:
        return c, db.session.get(Lead, c.lead_id)
    lead = Lead(name=(m["name"] or None), phone="+" + m["from"], status="new")
    db.session.add(lead); db.session.flush()
    c = WhatsAppContact(phone=m["from"], lead_id=lead.id, profile_name=m["name"])
    db.session.add(c); db.session.commit()
    return c, lead


def _handle_message(m):
    try:  # dedupe: Meta retries deliveries
        db.session.add(WhatsAppMessage(wa_message_id=m["id"], direction="in", status="received")); db.session.commit()
    except IntegrityError:
        db.session.rollback(); return
    contact, lead = _get_contact(m)
    phone, text = contact.phone, (m["text"] or "").strip()
    lang = contact.lang or "en"
    if text and chat_service.ARABIC.search(text):
        lang = "ar"
    contact.last_inbound_at = datetime.utcnow()
    if m["name"] and not lead.name:
        lead.name = m["name"]
    db.session.commit()
    low = text.lower()
    t = MSG[lang]

    if contact.opted_out:
        if low in START:
            contact.opted_out = False; db.session.commit(); _say(lead, phone, t["optin"])
        return  # opted-out contacts get no replies
    if low in STOP:
        contact.opted_out, contact.state = True, None; db.session.commit(); _say(lead, phone, t["optout"]); return
    if not text:
        _say(lead, phone, t["need_text"]); return
    if _is_command(low, contact):  # keep booking commands visible in the agent's conversation view
        db.session.add(Conversation(lead_id=lead.id, role="user", message=text))
    if _handle_command(contact, lead, text, low, lang):
        return
    contact.state = None; db.session.commit()
    _ai_turn(contact, lead, text, lang)


def _is_command(low, contact):
    return bool(re.match(r"^(view|معاينة)\s*[\d٠-٩]+$", low)) or low in CANCEL or low in AGENT or (contact.state and digits(low) == low and low != "")


def _handle_command(contact, lead, text, low, lang):
    t, phone = MSG[lang], contact.phone
    if low in CANCEL:
        contact.state = None; db.session.commit(); _say(lead, phone, t["cancelled"], True); return True
    if low in AGENT:
        lead.human_requested = True; db.session.commit(); _say(lead, phone, t["agent"], True); return True
    mt = re.match(r"^(?:view|معاينة)\s*([\d٠-٩]+)$", low)
    if mt:
        matches = property_service.match_properties(lead)["matches"] if lead.status == "qualified" else []
        n = int(digits(mt.group(1)) or 0)
        if not 1 <= n <= len(matches):
            _say(lead, phone, t["no_option"], True); return True
        contact.state, contact.pending_property_id = "pick_date", matches[n - 1]["id"]; db.session.commit()
        days = [date.today() + timedelta(days=i) for i in range(1, 6)]
        opts = "\n".join(f"{i}. {d.strftime('%a %d %b')}" for i, d in enumerate(days, 1))
        _say(lead, phone, t["pick_date"].format(title=matches[n - 1]["title"], opts=opts), True); return True
    if contact.state in ("pick_date", "pick_slot") and digits(low) == low and low:
        n = int(low.translate(ls.AR_DIGITS))
        if contact.state == "pick_date":
            if not 1 <= n <= 5:
                _say(lead, phone, t["bad_choice"], True); return True
            contact.pending_date, contact.state = (date.today() + timedelta(days=n)).isoformat(), "pick_slot"; db.session.commit()
            _say(lead, phone, t["pick_slot"].format(opts="\n".join(f"{i}. {s}" for i, s in enumerate(chat_service.SLOTS, 1))), True); return True
        if not 1 <= n <= len(chat_service.SLOTS):
            _say(lead, phone, t["bad_choice"], True); return True
        prop = db.session.get(Property, contact.pending_property_id)
        day = datetime.strptime(contact.pending_date, "%Y-%m-%d").date()
        chat_service.create_viewing(lead, prop, day, chat_service.SLOTS[n - 1])
        contact.state = None; db.session.commit()
        _say(lead, phone, t["booked"].format(title=prop.title, when=f"{day.strftime('%d %b %Y')} {chat_service.SLOTS[n - 1]}")); return True
    return False


def _ai_turn(contact, lead, text, lang):
    phone = contact.phone
    try:
        r = chat_service.run_turn(lead, text[:2000])
    except ai_service.AIError as e:
        log.warning("AI failure on WhatsApp turn: %s", e)
        _say(lead, phone, MSG[lang]["error"]); return
    contact.lang = lang = r["language"]; db.session.commit()
    _say(lead, phone, r["reply"])
    t = MSG[lang]
    if r["status"] == "qualified" and r["matches"]:
        n = len(r["matches"])
        lines = [t["head"].format(n=n, word=t["word1"] if n == 1 else t["wordn"])]
        lines += [f"{i}. {p['title']}, {p['area']}: AED {p['price']:,}" for i, p in enumerate(r["matches"], 1)]
        lines.append(t["foot"].format(cmds=", ".join(f"VIEW {i}" for i in range(1, n + 1))))
        _say(lead, phone, "\n".join(lines), True)
    elif r["missing_fields"] and r["missing_fields"][0] in Q:
        _send(lead, send_list, phone, t["body"], t["btn"], _rows(r["missing_fields"][0], lang))
