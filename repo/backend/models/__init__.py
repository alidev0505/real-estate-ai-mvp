from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(160))
    phone = db.Column(db.String(40))
    status = db.Column(db.String(20), default="new")  # new | info_needed | qualified
    property_type = db.Column(db.String(40))
    bedrooms = db.Column(db.Integer)
    area = db.Column(db.String(80))
    purpose = db.Column(db.String(40))
    budget = db.Column(db.Integer)
    timeline = db.Column(db.String(60))
    human_requested = db.Column(db.Boolean, default=False)
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def profile(self):
        return {k: getattr(self, k) for k in
                ("property_type", "bedrooms", "area", "purpose", "budget", "timeline")}

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        return d


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"), nullable=False, index=True)
    role = db.Column(db.String(12), nullable=False)  # user | assistant
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "lead_id": self.lead_id, "role": self.role,
                "message": self.message, "created_at": self.created_at.isoformat()}


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    property_type = db.Column(db.String(40), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    area = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(60), default="Investment / Personal Use")
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d["is_demo"] = True  # all seeded properties are fictional demo data
        return d


class Viewing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"), nullable=False, index=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(12), nullable=False)
    status = db.Column(db.String(20), default="requested")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lead = db.relationship("Lead")
    property = db.relationship("Property")

    def to_dict(self):
        return {"id": self.id, "lead_id": self.lead_id, "property_id": self.property_id,
                "date": self.date.isoformat(), "time": self.time, "status": self.status,
                "created_at": self.created_at.isoformat(),
                "lead_name": self.lead.name or f"Lead #{self.lead_id}",
                "property_title": self.property.title, "property_area": self.property.area}
