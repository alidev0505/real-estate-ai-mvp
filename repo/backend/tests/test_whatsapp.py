"""Simulated-webhook test. Meta's API and the LLM are stubbed here ONLY; real WhatsApp delivery
must be confirmed with your own Meta account."""
import hashlib, hmac, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime, timedelta
from config import Config
Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
Config.WHATSAPP_ASYNC = False
Config.WHATSAPP_ACCESS_TOKEN, Config.WHATSAPP_PHONE_NUMBER_ID = "tok", "123"
Config.WHATSAPP_VERIFY_TOKEN, Config.WHATSAPP_APP_SECRET = "verify-me", "appsecret"
Config.AI_API_KEY, Config.AI_MODEL = "k", "m"
from app import create_app
from models import db, Lead, Viewing, Conversation
from models.whatsapp import WhatsAppContact, WhatsAppMessage
from services import ai_service, whatsapp_service as wa

sent, n = [], {"i": 0}
def _id(): n["i"] += 1; return f"wamid.out{n['i']}"
wa.send_text = lambda to, body: (sent.append(("text", to, body)), _id())[1]
wa.send_list = lambda to, body, btn, rows: (sent.append(("list", to, rows)), _id())[1]
wa.send_template = lambda to, name, lang, params: (sent.append(("template", to, name, params)), _id())[1]

AI = [({"property_type": "Apartment", "bedrooms": 2, "area": "Dubai Marina", "purpose": "Investment"}, "Great. What budget?", "en"),
      ({"budget": 1500000}, "And when do you plan to buy?", "en"),
      ({"timeline": "2 months"}, "Thanks, I have what I need. Matching demo properties are below.", "en")]
ai_i = {"i": 0}
def fake(system, messages):
    ex, reply, lang = AI[ai_i["i"]]; ai_i["i"] += 1
    return json.dumps({"reply": reply, "extracted_data": ex, "language": lang})
ai_service.call_llm = fake

app = create_app(); c = app.test_client()
def post(payload, sign=True):
    raw = json.dumps(payload).encode()
    h = {"Content-Type": "application/json"}
    if sign: h["X-Hub-Signature-256"] = "sha256=" + hmac.new(b"appsecret", raw, hashlib.sha256).hexdigest()
    return c.post("/api/whatsapp/webhook", data=raw, headers=h)
def inbound(mid, text=None, rid=None, frm="971501112233", name="Khalid"):
    m = {"id": mid, "from": frm, "type": "text", "text": {"body": text}} if rid is None else \
        {"id": mid, "from": frm, "type": "interactive", "interactive": {"type": "list_reply", "list_reply": {"id": rid, "title": "x"}}}
    return {"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {"contacts": [{"wa_id": frm, "profile": {"name": name}}], "messages": [m]}}]}]}

# webhook verification + signature
assert c.get("/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=verify-me&hub.challenge=777").data == b"777"
assert c.get("/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=nope&hub.challenge=777").status_code == 403
assert post(inbound("w1", "hi"), sign=False).status_code == 401 and not sent
assert c.post("/api/whatsapp/webhook", data="{}", headers={"X-Hub-Signature-256": "sha256=bad"}).status_code == 401

# turn 1: lead is created from the phone number; reply + tap list for next missing field (budget)
assert post(inbound("w1", "I need a 2 bed apartment in Marina for investment")).status_code == 200
with app.app_context():
    lead = Lead.query.filter_by(is_demo=False).one(); assert lead.phone == "+971501112233" and lead.name == "Khalid" and lead.area == "Dubai Marina"
assert sent[0][:2] == ("text", "971501112233") and sent[1][0] == "list"
assert all(len(t) <= 24 for _, t in sent[1][2]) and len(sent[1][2]) <= 10
# dedupe: Meta retry of the same message id does nothing
before = len(sent); post(inbound("w1", "I need a 2 bed apartment in Marina for investment")); assert len(sent) == before and ai_i["i"] == 1
# every option title in both languages obeys WhatsApp limits
for f in wa.Q:
    for lang in ("en", "ar"):
        rows = wa._rows(f, lang); assert len(rows) <= 10 and all(len(t) <= 24 for _, t in rows), (f, lang)

# turn 2 via list reply id, turn 3 qualifies -> matches text
post(inbound("w2", rid="My budget is around AED 1.5 million")); post(inbound("w3", "within two months"))
assert "Marina Residence" in sent[-1][2] and "VIEW 1" in sent[-1][2], sent[-1]
# viewing flow: VIEW 1 -> date -> slot
post(inbound("w4", "VIEW 1")); assert "Which day" in sent[-1][2]
post(inbound("w5", "2")); assert "What time" in sent[-1][2]
post(inbound("w6", "1")); assert "Viewing request submitted" in sent[-1][2]
with app.app_context():
    v = Viewing.query.order_by(Viewing.id.desc()).first(); assert v.time == "11:00 AM" and Lead.query.filter_by(is_demo=False).one().status == "qualified"
    assert any(m.message == "VIEW 1" for m in Conversation.query.all())
post(inbound("w7", "VIEW 9")); assert "couldn't find" in sent[-1][2]
# human agent keyword is actually recorded
post(inbound("w8", "agent")); assert "flagged" in sent[-1][2]
with app.app_context(): assert Lead.query.filter_by(is_demo=False).one().human_requested is True
# opt-out: STOP confirms once, then silence; START resumes
post(inbound("w9", "STOP")); k = len(sent); post(inbound("w10", "hello again")); assert len(sent) == k
post(inbound("w11", "START")); assert "Welcome back" in sent[-1][2]
# non-text message
post({"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {"messages": [{"id": "w12", "from": "971501112233", "type": "image"}]}}]}]})
assert "only read text" in sent[-1][2]
# AI failure -> friendly message, no crash
ai_i["i"] = 99; post(inbound("w13", "anything")); assert "trouble" in sent[-1][2]
# delivery status webhook
with app.app_context(): wid = WhatsAppMessage.query.filter_by(direction="out").first().wa_message_id
post({"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {"statuses": [{"id": wid, "status": "delivered"}]}}]}]})
with app.app_context(): assert WhatsAppMessage.query.filter_by(wa_message_id=wid).one().status == "delivered"

# agent send endpoint (needs login, 24h window, demo-lead protection)
with app.app_context(): lid = Lead.query.filter_by(is_demo=False).one().id
assert c.post(f"/api/leads/{lid}/whatsapp/send", json={"body": "hi"}).status_code == 401
H = {"Authorization": "Bearer " + c.post("/api/auth/login", json={"username": Config.AGENT_USERNAME, "password": Config.AGENT_PASSWORD}).get_json()["token"]}
info = c.get(f"/api/leads/{lid}/whatsapp", headers=H).get_json(); assert info["connected"] and info["within_window"]
r = c.post(f"/api/leads/{lid}/whatsapp/send", json={"body": "Hello from the team"}, headers=H); assert r.status_code == 200 and r.get_json()["via"] == "text"
with app.app_context():
    WhatsAppContact.query.one().last_inbound_at = datetime.utcnow() - timedelta(hours=30); db.session.commit()
r = c.post(f"/api/leads/{lid}/whatsapp/send", json={"body": "late"}, headers=H); assert r.status_code == 409 and "24-hour" in r.get_json()["error"]
Config.WHATSAPP_FOLLOWUP_TEMPLATE = "followup_v1"
r = c.post(f"/api/leads/{lid}/whatsapp/send", json={"body": "late"}, headers=H); assert r.get_json()["via"] == "template" and sent[-1][2] == "followup_v1"
with app.app_context(): demo_id = Lead.query.filter_by(is_demo=True).first().id
assert c.post(f"/api/leads/{demo_id}/whatsapp/send", json={"body": "x"}, headers=H).status_code == 400
print("WHATSAPP TESTS PASSED", len(sent), "messages")
