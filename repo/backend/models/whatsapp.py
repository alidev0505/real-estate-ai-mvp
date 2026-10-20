"""WhatsApp tables. Separate file + new tables only, so existing databases need no migration."""
from datetime import datetime
from models import db


class WhatsAppContact(db.Model):
    __tablename__ = "whatsapp_contact"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)  # digits only, e.g. 971501234567
    lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"), nullable=False, index=True)
    profile_name = db.Column(db.String(120))
    lang = db.Column(db.String(2), default="en")
    last_inbound_at = db.Column(db.DateTime)           # drives the 24-hour reply window
    opted_out = db.Column(db.Boolean, default=False)
    state = db.Column(db.String(20))                   # None | pick_date | pick_slot (viewing booking flow)
    pending_property_id = db.Column(db.Integer)
    pending_date = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WhatsAppMessage(db.Model):
    """Dedupes inbound webhooks (Meta retries) and tracks outbound delivery status."""
    __tablename__ = "whatsapp_message"
    id = db.Column(db.Integer, primary_key=True)
    wa_message_id = db.Column(db.String(120), unique=True, index=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"), index=True)
    direction = db.Column(db.String(3), nullable=False)  # in | out
    status = db.Column(db.String(20))                    # received | sent | delivered | read | failed
    error = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
