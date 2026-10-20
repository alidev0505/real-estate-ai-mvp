"""Simple, transparent property matching: filter on budget, score on fit."""
from models import Property


def match_properties(lead, limit=3):
    if not (lead.budget and lead.area):
        return {"matches": [], "quality": "none"}
    scored = []
    for p in Property.query.filter_by(available=True).all():
        if p.price > lead.budget * 1.10:  # allow 10% negotiation headroom
            continue
        score, reasons = 0, []
        if p.area.lower() == lead.area.lower():
            score += 3; reasons.append("area")
        if lead.property_type and p.property_type.lower() == lead.property_type.lower():
            score += 2; reasons.append("type")
        if lead.bedrooms is not None and p.bedrooms == lead.bedrooms:
            score += 2; reasons.append("bedrooms")
        if lead.purpose and lead.purpose.lower() in p.purpose.lower():
            score += 1; reasons.append("purpose")
        if p.price >= lead.budget * 0.6:
            score += 1; reasons.append("budget")
        scored.append((score, -abs(p.price - lead.budget), p, reasons))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    top = [t for t in scored if t[0] >= 5][:limit]
    quality = "exact" if top and top[0][0] >= 8 else "close"
    if not top:  # nothing close: show nearest options so the flow never dead-ends
        top, quality = scored[:limit], "nearest"
    out = []
    for score, _, p, reasons in top:
        d = p.to_dict(); d["match_score"] = score; d["match_reasons"] = reasons
        out.append(d)
    return {"matches": out, "quality": quality if out else "none"}
