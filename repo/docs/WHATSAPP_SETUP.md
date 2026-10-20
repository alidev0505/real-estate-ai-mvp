# WhatsApp gateway: merge guide

Uses the **Meta WhatsApp Cloud API**. Customers message your WhatsApp number; the same AI qualification flow runs, replies go back on WhatsApp, matches are sent as text, and viewings are booked with `VIEW 1` + number replies. Agents can send follow-ups from the lead page.

## A. Copy new files (nothing existing is overwritten except FollowUpDrafts.jsx)
| From add-on | To your project |
|---|---|
| backend/models/whatsapp.py | backend/models/whatsapp.py |
| backend/services/chat_service.py | backend/services/chat_service.py |
| backend/services/whatsapp_service.py | backend/services/whatsapp_service.py |
| backend/routes/whatsapp.py | backend/routes/whatsapp.py |
| backend/tests/test_whatsapp.py | backend/tests/test_whatsapp.py |
| frontend/src/components/FollowUpDrafts.jsx | same path (**replaces** the v2 file; if you edited yours, diff first) |

## B. Edit 4 existing files
1. `backend/config.py` : paste at the very end the block from `config_additions.py`.
2. `backend/.env` : paste the lines from `env_additions.txt`.
3. `backend/services/auth_service.py` : add the two webhook paths to `PUBLIC`:
   `("GET", "/api/whatsapp/webhook"), ("POST", "/api/whatsapp/webhook")`
   (Meta cannot log in, so these two are public. They are protected by the verify token and HMAC signature instead.)
4. `backend/app.py` : add these imports with the others, and register the blueprint next to the others:
   ```python
   from routes.whatsapp import wa_bp
   import models.whatsapp  # noqa: F401   (must be imported before db.create_all())
   ...
   app.register_blueprint(wa_bp)
   ```
5. `frontend/src/services/api.js` : add inside the `api` object:
   ```js
   whatsappInfo: (id) => req(`/leads/${id}/whatsapp`),
   sendWhatsApp: (id, body, lang) => post(`/leads/${id}/whatsapp/send`, { body, lang }),
   ```
No new Python packages are needed. Existing databases need no migration: the gateway only adds two new tables.

## C. Test offline (no Meta account needed)
```bash
cd backend && python tests/test_whatsapp.py    # expect: WHATSAPP TESTS PASSED
python tests/test_flow.py                       # your existing tests still pass
```

## D. Connect to Meta
1. developers.facebook.com -> Create app -> type **Business** -> add the **WhatsApp** product.
2. WhatsApp -> API Setup: copy the **Phone number ID** -> `WHATSAPP_PHONE_NUMBER_ID`. Add your own phone as a test recipient.
3. Access token: the temporary token expires in ~24h. For anything longer, create a **System User** in Business Settings, give it the app, generate a permanent token with `whatsapp_business_messaging` -> `WHATSAPP_ACCESS_TOKEN`.
4. App settings -> Basic -> **App secret** -> `WHATSAPP_APP_SECRET` (required: unsigned webhooks are rejected).
5. Pick any long random string for `WHATSAPP_VERIFY_TOKEN`.
6. Set `WHATSAPP_API_VERSION` to the Graph version your dashboard shows.
7. Expose your local backend over HTTPS: `ngrok http 5000` (or cloudflared). Restart the backend.
8. WhatsApp -> Configuration -> Webhook: Callback URL `https://<your-tunnel>/api/whatsapp/webhook`, Verify token = your string -> **Verify and save**. Then **subscribe to the `messages` field**.
9. Send a WhatsApp message to the test number. A lead appears in the dashboard and the AI replies.

## E. Rules you must know
- **24-hour window:** free-text replies are allowed only within 24h of the customer's last message. Outside it, Meta requires an approved **template**. Create one in WhatsApp Manager (e.g. body: `Hi {{1}}, thanks for your property enquiry. Reply to continue.`), then set `WHATSAPP_FOLLOWUP_TEMPLATE=<template name>`. The template language must match what you approved.
- **Opt-out:** customers can reply STOP. They get no further replies until START. Do not bypass this.
- **Demo leads** can never be messaged (their numbers are fictional).
- **Production:** run the backend with gunicorn (not `python app.py`), use PostgreSQL, a permanent token, and a stable HTTPS URL.

## F. If your project already has its own WhatsApp gateway
Do not copy blindly. Compare first: both would register `/api/whatsapp/webhook`. Keep one webhook per Meta app. You can reuse `chat_service.run_turn()` from your gateway instead of using mine.
