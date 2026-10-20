"""Follow-up message drafts (EN/AR). Drafts only: nothing is ever sent by the app."""

T = {
    "en": {
        "hi": "Hi {name},", "sign": "Best regards,\nYour Dubai Property Team",
        "qualified_subject": "Your property shortlist in {area}",
        "qualified": "Thank you for sharing your requirements ({summary}). Based on them, these demo options may suit you:\n{props}\n\nWould you like to arrange a viewing? Reply with a day and time that works for you.",
        "needinfo_subject": "Finding the right property for you",
        "needinfo": "Thanks for getting in touch about a property in Dubai. To find the best options, could you confirm: {missing}?",
        "viewing_subject": "Your viewing request",
        "viewing": "Thank you for requesting a viewing of {prop} on {when}. Our team will confirm the appointment shortly.",
        "fields": {"property_type": "property type", "bedrooms": "number of bedrooms", "area": "preferred area",
                   "purpose": "whether it is for investment or personal use", "budget": "your budget", "timeline": "your purchase timeline"},
        "there": "there", "any": "Dubai", "demo": "(demo listing)",
    },
    "ar": {
        "hi": "مرحبًا {name}،", "sign": "مع أطيب التحيات،\nفريق العقارات في دبي",
        "qualified_subject": "قائمة العقارات المقترحة لك في {area}",
        "qualified": "شكرًا لمشاركتنا متطلباتك ({summary}). بناءً عليها، قد تناسبك هذه الخيارات التجريبية:\n{props}\n\nهل تود ترتيب موعد معاينة؟ يرجى إخبارنا بالتاريخ والوقت المناسبين لك.",
        "needinfo_subject": "لنجد لك العقار المناسب",
        "needinfo": "شكرًا لتواصلك معنا بخصوص عقار في دبي. لنقترح أفضل الخيارات، هل يمكنك تأكيد: {missing}؟",
        "viewing_subject": "طلب المعاينة",
        "viewing": "شكرًا لطلبك معاينة {prop} بتاريخ {when}. سيؤكد فريقنا الموعد قريبًا.",
        "fields": {"property_type": "نوع العقار", "bedrooms": "عدد غرف النوم", "area": "المنطقة المفضلة",
                   "purpose": "هل هو للاستثمار أم للسكن الشخصي", "budget": "ميزانيتك", "timeline": "الإطار الزمني للشراء"},
        "there": "عميلنا الكريم", "any": "دبي", "demo": "(عقار تجريبي)",
    },
}


def build_drafts(lead, matches, viewing, missing, lang="en"):
    lang = "ar" if lang == "ar" else "en"
    t = T[lang]
    name = (lead.name or "").split(" ")[0] or t["there"]
    summary = ", ".join(str(x) for x in [
        (f"{lead.bedrooms} BR" if lead.bedrooms else ("Studio" if lead.bedrooms == 0 else None)), lead.property_type, lead.area,
        lead.purpose, f"AED {lead.budget:,}" if lead.budget else None, lead.timeline] if x)
    if viewing:
        state = "viewing"
        when = f"{viewing.date.strftime('%d %B %Y')} {viewing.time}"
        body, subject = t["viewing"].format(prop=viewing.property.title, when=when), t["viewing_subject"]
    elif lead.status == "qualified":
        state = "qualified"
        props = "\n".join(f"- {m['title']}, {m['area']}: AED {m['price']:,} {t['demo']}" for m in matches) or "-"
        body = t["qualified"].format(summary=summary, props=props)
        subject = t["qualified_subject"].format(area=lead.area or t["any"])
    else:
        state = "needs_info"
        body = t["needinfo"].format(missing="، ".join(t["fields"][m] for m in missing) if lang == "ar" else ", ".join(t["fields"][m] for m in missing))
        subject = t["needinfo_subject"]
    greeting = t["hi"].format(name=name)
    return {"state": state, "lang": lang, "email": {"subject": subject, "body": f"{greeting}\n\n{body}\n\n{t['sign']}"},
            "whatsapp": {"body": f"{greeting}\n{body}"}, "sent": False,
            "note": "Draft only. Review and send it yourself; the app never sends messages."}
