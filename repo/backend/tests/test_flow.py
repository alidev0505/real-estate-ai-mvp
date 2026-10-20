"""Pipeline test. The LLM call is stubbed here ONLY to verify merge/qualify/match/viewing logic offline.
The real LLM path (services/ai_service.py) needs your API key and is not exercised by this test."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import date, timedelta
from config import Config
Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
from app import create_app
from services import ai_service

SCRIPT = [
    ({"property_type": "Apartment", "bedrooms": 2, "area": None, "purpose": None, "budget": None, "timeline": None}, "Which area?"),
    ({"area": "Dubai Marina", "bedrooms": None, "purpose": None}, "Investment or personal use?"),
    ({"purpose": "investment", "budget": None}, "Budget?"),
    ({"budget": "AED 1.5M junk", "timeline": None}, "Timeline?"),   # invalid budget string -> parsed to 1.5 (rejected)
    ({"budget": 1500000, "timeline": "2 months", "area": None, "purpose": None}, "Thanks! Matching demo properties are below."),
]
step = {"i": 0}
def fake(system, messages):
    ex, reply = SCRIPT[step["i"]]; step["i"] += 1
    return json.dumps({"reply": reply, "extracted_data": ex})
ai_service.call_llm = fake
Config.AI_API_KEY, Config.AI_MODEL = "k", "m"

app = create_app(); c = app.test_client()
assert c.get("/api/leads").status_code == 401 and c.get("/api/dashboard/stats").status_code == 401
assert c.post("/api/auth/login", json={"username": "agent", "password": "wrong"}).status_code == 401
tok = c.post("/api/auth/login", json={"username": Config.AGENT_USERNAME, "password": Config.AGENT_PASSWORD}).get_json()["token"]
H = {"Authorization": "Bearer " + tok}
assert c.get("/api/leads", headers={"Authorization": "Bearer junk"}).status_code == 401
assert c.post("/api/chat", json={"message": "  "}).status_code == 400
lid, last = None, None
for msg in ["2 bed apartment", "Marina", "investment", "1.5m", "2 months"]:
    last = c.post("/api/chat", json={"message": msg, "lead_id": lid}).get_json(); lid = last["lead_id"]
    print(last["status"], last["profile"])
assert last["status"] == "qualified" and last["profile"]["area"] == "Dubai Marina"
assert last["profile"]["purpose"] == "Investment" and last["profile"]["budget"] == 1500000
assert 1 <= len(last["matches"]) <= 3 and last["matches"][0]["area"] == "Dubai Marina"
print("matches:", [(m["title"], m["price"]) for m in last["matches"]])
assert len(c.get(f"/api/leads/{lid}/conversation", headers=H).get_json()) == 11  # greeting + 5 user + 5 assistant
pid = last["matches"][0]["id"]; d = (date.today() + timedelta(days=3)).isoformat()
assert c.post("/api/viewings", json={"lead_id": lid, "property_id": pid, "date": "2020-01-01", "time": "2:00 PM"}).status_code == 400
assert c.post("/api/viewings", json={"lead_id": lid, "property_id": pid, "date": d, "time": "9:00 AM"}).status_code == 400
assert c.post("/api/viewings", json={"lead_id": lid, "property_id": pid, "date": d, "time": "2:00 PM"}).status_code == 201
assert c.get(f"/api/leads/{lid}", headers=H).get_json()["follow_up"]["status"] == "Viewing Requested"
print(c.get("/api/dashboard/stats", headers=H).get_json(), len(c.get("/api/properties", headers=H).get_json()), "properties")
# --- new features ---
d = c.get(f"/api/leads/{lid}/followup-drafts?lang=ar", headers=H).get_json()
assert d["state"] == "viewing" and d["sent"] is False and "مرحبًا" in d["email"]["body"]
d = c.get(f"/api/leads/{lid}/followup-drafts", headers=H).get_json(); assert "Marina Residence" in d["email"]["body"]
P = {"title": "Test Tower", "property_type": "Apartment", "bedrooms": 2, "bathrooms": 2, "area": "Dubai Marina", "price": 1400000}
assert c.post("/api/properties", json=P).status_code == 401
r = c.post("/api/properties", json=P, headers=H); assert r.status_code == 201; npid = r.get_json()["id"]
assert c.post("/api/properties", json={**P, "price": 5}, headers=H).status_code == 400
assert c.post("/api/properties", json={**P, "image_url": "javascript:x"}, headers=H).status_code == 400
assert c.put(f"/api/properties/{npid}", json={"price": 1300000, "available": False}, headers=H).get_json()["price"] == 1300000
assert c.delete(f"/api/properties/{npid}", headers=H).get_json()["deleted"] is True
assert c.delete(f"/api/properties/{pid}", headers=H).get_json()["archived"] is True  # has a viewing
from models import db, Lead
with app.app_context():
    db.session.add(Lead(name="=HYPERLINK(\"x\")", status="new")); db.session.commit()
csv_text = c.get("/api/leads/export.csv", headers=H).data.decode()
assert "'=HYPERLINK" in csv_text and csv_text.startswith("\ufeffid,name") and c.get("/api/leads/export.csv").status_code == 401
# Arabic: Arabic-Indic digits in budget, language fallback detection
SCRIPT.append(({"budget": "١٫٥٠٠٫٠٠٠", "area": "Business Bay"}, "تم"))
step["i"] = len(SCRIPT) - 1
r = c.post("/api/chat", json={"message": "منطقة الأعمال", "lead_id": lid}).get_json()
assert r["language"] == "ar" and r["profile"]["area"] == "Business Bay", r
SCRIPT.append(({"property_type": "Villa"}, "تمام")); step["i"] = len(SCRIPT) - 1
r = c.post("/api/chat", json={"message": "أبحث عن فيلا", "lang": "ar"}).get_json()
assert r["language"] == "ar" and r["profile"]["property_type"] == "Villa"
assert c.get(f"/api/leads/{r['lead_id']}/conversation", headers=H).get_json()[0]["message"].startswith("مرحبًا")
print("NEW FEATURES OK")
Config.AI_API_KEY = ""
r = c.post("/api/chat", json={"message": "hi"}); assert r.status_code == 502 and "trouble" in r.get_json()["error"]
print("ALL PASSED")
