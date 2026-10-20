"""Agent-only routes: sign-in, property admin, CSV export, follow-up drafts."""
import csv
import io
import logging
from flask import Blueprint, Response, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from config import Config
from models import db, Lead, Property, Viewing
from services import auth_service, followup_service, lead_service as ls, property_service

admin = Blueprint("admin", __name__, url_prefix="/api")
admin.before_request(auth_service.guard)
log = logging.getLogger(__name__)
TYPES = {"Apartment", "Villa", "Townhouse", "Penthouse"}


def err(msg, code=400):
    return jsonify({"error": msg}), code


@admin.errorhandler(SQLAlchemyError)
def db_error(e):
    db.session.rollback(); log.exception("Database error")
    return err("A database error occurred. Please try again.", 500)


@admin.post("/auth/login")
def login():
    d = request.get_json(silent=True) or {}
    if not auth_service.check_credentials(d.get("username"), d.get("password")):
        return err("Incorrect username or password.", 401)
    return jsonify({"token": auth_service.make_token(d["username"]), "username": d["username"], "expires_in": Config.TOKEN_MAX_AGE})


@admin.get("/auth/me")
def me():
    return jsonify({"username": auth_service.current_agent()})


# ---- Property admin ----
def _validate_property(d, partial=False):
    out = {}
    def need(k): return not partial or k in d
    try:
        if need("title"):
            t = str(d.get("title") or "").strip()
            if not 1 <= len(t) <= 120: raise ValueError("Title is required (max 120 characters).")
            out["title"] = t
        if need("property_type"):
            if d.get("property_type") not in TYPES: raise ValueError(f"Type must be one of: {', '.join(sorted(TYPES))}.")
            out["property_type"] = d["property_type"]
        for k, lo, hi, label in (("bedrooms", 0, 12, "Bedrooms"), ("bathrooms", 0, 12, "Bathrooms"), ("price", 50_000, 1_000_000_000, "Price (AED)")):
            if need(k):
                v = int(d.get(k)); 
                if not lo <= v <= hi: raise ValueError(f"{label} must be between {lo:,} and {hi:,}.")
                out[k] = v
        if need("area"):
            a = str(d.get("area") or "").strip()
            if not 1 <= len(a) <= 80: raise ValueError("Area is required.")
            out["area"] = a
        if "purpose" in d: out["purpose"] = str(d["purpose"] or "Investment / Personal Use")[:60]
        if "description" in d: out["description"] = str(d["description"] or "")[:1000]
        if "image_url" in d:
            u = str(d["image_url"] or "").strip()
            if u and not u.startswith(("http://", "https://")): raise ValueError("Image URL must start with http:// or https://")
            out["image_url"] = u[:300] or None
        if "available" in d: out["available"] = bool(d["available"])
    except (TypeError, ValueError) as e:
        raise ValueError(str(e) if "must" in str(e) or "required" in str(e) or "Image" in str(e) else "Check the numeric fields.")
    return out


@admin.post("/properties")
def add_property():
    try: data = _validate_property(request.get_json(silent=True) or {})
    except ValueError as e: return err(str(e))
    p = Property(**data); db.session.add(p); db.session.commit()
    return jsonify(p.to_dict()), 201


@admin.put("/properties/<int:pid>")
def edit_property(pid):
    p = db.session.get(Property, pid)
    if not p: return err("Property not found", 404)
    try: data = _validate_property(request.get_json(silent=True) or {}, partial=True)
    except ValueError as e: return err(str(e))
    for k, v in data.items(): setattr(p, k, v)
    db.session.commit()
    return jsonify(p.to_dict())


@admin.delete("/properties/<int:pid>")
def delete_property(pid):
    p = db.session.get(Property, pid)
    if not p: return err("Property not found", 404)
    if Viewing.query.filter_by(property_id=pid).count():  # keep history intact
        p.available = False; db.session.commit()
        return jsonify({"deleted": False, "archived": True})
    db.session.delete(p); db.session.commit()
    return jsonify({"deleted": True, "archived": False})


# ---- CSV export ----
def _safe(v):
    s = "" if v is None else str(v)
    return "'" + s if s[:1] in ("=", "+", "-", "@", "\t", "\r") else s  # block spreadsheet formula injection


@admin.get("/leads/export.csv")
def export_leads():
    buf = io.StringIO(); w = csv.writer(buf)
    cols = ["id", "name", "email", "phone", "status", "property_type", "bedrooms", "area", "purpose", "budget", "timeline", "human_requested", "is_demo", "created_at"]
    w.writerow(cols + ["follow_up_status"])
    for l in Lead.query.order_by(Lead.id).all():
        d = l.to_dict(); w.writerow([_safe(d[c]) for c in cols] + [ls.follow_up(l)["status"]])
    return Response("\ufeff" + buf.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=leads.csv"})


# ---- Follow-up drafts ----
@admin.get("/leads/<int:lead_id>/followup-drafts")
def drafts(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead: return err("Lead not found", 404)
    matches = property_service.match_properties(lead)["matches"] if lead.status == "qualified" else []
    viewing = Viewing.query.filter_by(lead_id=lead_id).order_by(Viewing.id.desc()).first()
    lang = "ar" if request.args.get("lang") == "ar" else "en"
    return jsonify(followup_service.build_drafts(lead, matches, viewing, ls.missing_fields(lead), lang))
