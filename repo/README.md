# AI Real Estate Lead Automation MVP (Dubai)

Lead chat -> requirement extraction -> rule-based qualification -> property matching -> viewing request -> agent dashboard.
All properties and seeded leads are **fictional demo data**. Customers can chat on the web or over **WhatsApp** (Meta Cloud API).

**Tech stack:** Python, Flask, SQLAlchemy (SQLite / PostgreSQL), React 18, Vite, Tailwind CSS, LLM APIs (Anthropic, OpenAI, Gemini), Meta WhatsApp Cloud API.

## Run
```bash
# Backend (Python 3.10+)
cd backend && python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then set AI_PROVIDER, AI_API_KEY, AI_MODEL
python app.py               # http://localhost:5000 (creates and seeds the DB on first run)

# Frontend
cd frontend && npm install && npm run dev    # http://localhost:5173 (proxies /api to :5000)
```
`AI_PROVIDER` = `anthropic` | `openai` | `gemini`. Use PostgreSQL by setting `DATABASE_URL=postgresql://...`.

## New in this version
- **Arabic + English chat**: language is auto-detected from the customer's message (or toggle in the chat header). Replies, tap options, profile panel and the viewing flow switch language and direction (RTL).
- **Tap-to-select answers**: tick-box options for the next missing field (type, bedrooms, area, purpose, budget, timeline). Typing still works any time.
- **Follow-up drafts** (lead page): WhatsApp/email text in English or Arabic based on lead state. Drafts only; nothing is sent.
- **Agent sign-in**: set `AGENT_USERNAME`, `AGENT_PASSWORD`, `SECRET_KEY` in `backend/.env`. Dashboard APIs require a token; only chat, viewing requests and health are public.
- **Property admin**: add, edit, hide/show, delete (archived if it has viewings). **Export leads to CSV** from the Leads page (formula-injection safe).

## Demo
Open **Try AI Assistant**, click **Load demo conversation** (it sends 5 scripted customer messages through the real AI),
then pick a property and schedule a viewing. The lead, chat and viewing appear under **Dashboard**.

## How it works
- `services/ai_service.py`: calls the LLM with `prompts/real_estate_agent.txt` + current profile; expects JSON `{reply, extracted_data, human_requested}`.
- `services/lead_service.py`: validates and merges extraction (nulls/invalid values never overwrite); **the backend, not the LLM, computes missing fields and qualification**.
- `services/property_service.py`: budget filter (+10% headroom) then simple scoring on area, type, bedrooms, purpose.
- `routes/api.py`: all endpoints from the spec, plus `/api/health`.
- `python backend/tests/test_flow.py`: offline pipeline test (LLM stubbed there only).

## WhatsApp
The same qualification flow runs over WhatsApp: signed-webhook verification (HMAC-SHA256), 24-hour window handling with template fallback, and STOP/START opt-out. Setup steps are in [docs/WHATSAPP_SETUP.md](docs/WHATSAPP_SETUP.md).

## Tests
```bash
cd backend && python tests/test_flow.py && python tests/test_whatsapp.py   # offline, no API keys needed
```

## Extending
Add another lead source (Instagram, web forms) as a route that calls `chat_service.run_turn()` with a `lead_id` per contact.

## Known MVP limits
Single shared agent login (no roles), `POST /api/viewings` is public so any lead id can be booked against, follow-ups are drafts only, property data stays in English even in Arabic chat, property images are generated placeholders (set `image_url` to use real photos).


## Security
Never commit `backend/.env`. It is git-ignored; copy `backend/.env.example` and fill in your own keys.
