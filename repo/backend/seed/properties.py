"""Fictional demo data. Not real listings and not verified availability."""
from datetime import datetime, timedelta
from models import db, Property, Lead, Conversation, Viewing

AP, VI, TH, PH = "Apartment", "Villa", "Townhouse", "Penthouse"
# title, type, beds, baths, area, price, description
PROPERTIES = [
    ("Marina Residence", AP, 2, 2, "Dubai Marina", 1450000, "Bright corner unit with marina views, close to the tram and promenade."),
    ("Marina Heights", AP, 2, 3, "Dubai Marina", 1620000, "High-floor apartment with balcony and full amenities access."),
    ("Marina Promenade One", AP, 1, 1, "Dubai Marina", 980000, "Compact one-bedroom steps from the waterfront cafes."),
    ("Marina Gate Family Suite", AP, 3, 4, "Dubai Marina", 2800000, "Spacious three-bedroom with maid's room and sea views."),
    ("Downtown Vista", AP, 1, 2, "Downtown Dubai", 1250000, "One-bedroom with skyline outlook near the Boulevard."),
    ("Boulevard Loft", AP, 2, 2, "Downtown Dubai", 2350000, "Designer two-bedroom in a landmark tower."),
    ("Canal View Residence", AP, 2, 2, "Business Bay", 1380000, "Two-bedroom overlooking the Dubai Canal with high rental demand."),
    ("Bay Square Studio", AP, 0, 1, "Business Bay", 720000, "Efficient studio ideal for a rental-focused portfolio."),
    ("Bay Tower One-Bed", AP, 1, 1, "Business Bay", 1050000, "Modern one-bedroom with gym and pool."),
    ("Jumeirah Beach Villa", VI, 4, 5, "Jumeirah", 8500000, "Four-bedroom villa with private garden, minutes from the beach."),
    ("Jumeirah Garden Townhouse", TH, 3, 4, "Jumeirah", 4200000, "Three-bedroom townhouse in a quiet low-rise enclave."),
    ("Palm Shoreline Apartment", AP, 2, 3, "Palm Jumeirah", 3100000, "Sea-facing two-bedroom with beach access."),
    ("Palm Frond Villa", VI, 5, 6, "Palm Jumeirah", 14000000, "Signature frond villa with pool and private beach."),
    ("Ranches Family Villa", VI, 4, 5, "Arabian Ranches", 4900000, "Four-bedroom villa on a landscaped plot near the golf course."),
    ("Ranches Townhouse", TH, 3, 3, "Arabian Ranches", 3600000, "Three-bedroom townhouse in a gated, family-friendly community."),
    ("Hills Park Apartment", AP, 2, 2, "Dubai Hills", 1750000, "Two-bedroom facing the park with a large terrace."),
    ("Hills Estate Villa", VI, 4, 5, "Dubai Hills", 5500000, "Contemporary villa near the mall and golf club."),
    ("JVC Circle Apartment", AP, 1, 1, "JVC", 780000, "Affordable one-bedroom with strong yield potential."),
    ("JVC Garden Two-Bed", AP, 2, 2, "JVC", 1100000, "Two-bedroom in a newer building with a rooftop pool."),
]

DEMO_LEADS = [
    dict(name="Ahmed Khan", email="demo@example.com", phone="+971 50 000 0001", status="qualified",
         property_type="Apartment", bedrooms=2, area="Dubai Marina", purpose="Investment", budget=1500000,
         timeline="2 months", viewing=True, chat=[
             ("assistant", "Hi! Welcome. I can help you find a property in Dubai. What type of property are you looking for?"),
             ("user", "I need a 2 bedroom apartment."), ("assistant", "Great. Which area of Dubai are you interested in?"),
             ("user", "Dubai Marina."), ("assistant", "Is this for personal use or an investment?"),
             ("user", "Investment."), ("assistant", "What approximate budget are you considering?"),
             ("user", "Around 1.5 million AED."), ("assistant", "When are you planning to purchase?"),
             ("user", "Within two months.")]),
    dict(name="Sarah Ali", email="sarah@example.com", phone="+971 50 000 0002", status="info_needed",
         property_type="Villa", bedrooms=None, area="Jumeirah", purpose=None, budget=3000000, timeline=None,
         chat=[("assistant", "Hi! Welcome. I can help you find a property in Dubai. What type of property are you looking for?"),
               ("user", "I'm looking for a villa in Jumeirah, budget around 3 million."),
               ("assistant", "Lovely choice. How many bedrooms do you need, and is it for personal use or investment?")]),
    dict(name="Omar Hassan", email="omar@example.com", phone="+971 50 000 0003", status="new",
         property_type="Apartment", bedrooms=1, area="Downtown Dubai", purpose=None, budget=900000, timeline=None,
         chat=[("assistant", "Hi! Welcome. I can help you find a property in Dubai. What type of property are you looking for?"),
               ("user", "1 bedroom downtown, 900k")]),
    dict(name="Layla Nasser", email="layla@example.com", phone="+971 50 000 0004", status="qualified",
         property_type="Townhouse", bedrooms=3, area="Arabian Ranches", purpose="Personal Use", budget=3700000,
         timeline="3 months", chat=[("assistant", "Hi! Welcome. What type of property are you looking for?"),
                                    ("user", "A 3 bedroom townhouse in Arabian Ranches for my family, up to 3.7M, within 3 months.")]),
]


def seed_properties():
    if Property.query.count() == 0:
        for t, ty, b, ba, a, pr, d in PROPERTIES:
            db.session.add(Property(title=t, property_type=ty, bedrooms=b, bathrooms=ba, area=a, price=pr, description=d))
        db.session.commit()


def seed_demo_leads():
    if Lead.query.filter_by(is_demo=True).count() > 0:
        return
    for i, spec in enumerate(DEMO_LEADS):
        spec = dict(spec); chat = spec.pop("chat"); has_view = spec.pop("viewing", False)
        lead = Lead(is_demo=True, created_at=datetime.utcnow() - timedelta(days=i), **spec)
        db.session.add(lead); db.session.flush()
        for role, msg in chat:
            db.session.add(Conversation(lead_id=lead.id, role=role, message=msg))
        if has_view:
            p = Property.query.filter_by(title="Marina Residence").first()
            db.session.add(Viewing(lead_id=lead.id, property_id=p.id, date=(datetime.utcnow() + timedelta(days=5)).date(), time="11:00 AM"))
    db.session.commit()
