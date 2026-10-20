// Client-facing chat strings and tap-to-select options (English / Arabic).
export const T = {
  en: { title: 'AI Real Estate Assistant', sub: 'Dubai Property Concierge', online: 'Online', newChat: 'New chat', demoBanner: 'Demo mode.', demoNote: 'Fictional properties; availability is not verified.',
    loadDemo: 'Load demo conversation', placeholder: "Describe the property you're looking for…", send: 'Send', pick: 'Tap an option or type your own answer',
    profile: 'Lead profile', notProvided: 'Not provided', of: 'of', demoListing: 'Demo listing', details: 'Details', schedule: 'Schedule viewing', beds: 'Beds', baths: 'Baths', studio: 'Studio',
    matchN: (n) => `${n} ${n === 1 ? 'property matches' : 'properties match'} your requirements.`, nearest: (n) => `No exact match. Here are the ${n} closest demo properties.`,
    great: 'Great choice. Would you like to schedule a viewing?', viewingDone: 'Viewing request submitted.', confirm: 'Our team will confirm.',
    scheduleTitle: 'Schedule a viewing', date: 'Date', time: 'Time', request: 'Request viewing', submitting: 'Submitting…', demoNotVerified: 'Demo data. Availability is not verified.',
    status: { qualified: '🔥 Qualified lead', info_needed: '🟡 Information needed', new: '🔵 New lead' },
    fields: { property_type: 'Property type', bedrooms: 'Bedrooms', area: 'Preferred area', purpose: 'Purpose', budget: 'Budget', timeline: 'Purchase timeline' } },
  ar: { title: 'مساعد العقارات الذكي', sub: 'مستشار العقارات في دبي', online: 'متصل', newChat: 'محادثة جديدة', demoBanner: 'وضع تجريبي.', demoNote: 'عقارات وهمية؛ التوفر غير مؤكد.',
    loadDemo: 'تشغيل محادثة تجريبية', placeholder: 'صف العقار الذي تبحث عنه…', send: 'إرسال', pick: 'اختر خيارًا أو اكتب إجابتك',
    profile: 'ملف العميل', notProvided: 'غير محدد', of: 'من', demoListing: 'عقار تجريبي', details: 'التفاصيل', schedule: 'حجز معاينة', beds: 'غرف', baths: 'حمامات', studio: 'استوديو',
    matchN: (n) => `وجدنا ${n} ${n === 1 ? 'عقارًا' : 'عقارات'} تناسب متطلباتك.`, nearest: (n) => `لا يوجد تطابق تام. إليك أقرب ${n} عقارات تجريبية.`,
    great: 'اختيار ممتاز. هل تود حجز موعد معاينة؟', viewingDone: 'تم إرسال طلب المعاينة.', confirm: 'سيؤكد فريقنا الموعد.',
    scheduleTitle: 'حجز معاينة', date: 'التاريخ', time: 'الوقت', request: 'اطلب المعاينة', submitting: 'جارٍ الإرسال…', demoNotVerified: 'بيانات تجريبية. التوفر غير مؤكد.',
    status: { qualified: '🔥 عميل مؤهل', info_needed: '🟡 مطلوب معلومات', new: '🔵 عميل جديد' },
    fields: { property_type: 'نوع العقار', bedrooms: 'غرف النوم', area: 'المنطقة', purpose: 'الغرض', budget: 'الميزانية', timeline: 'موعد الشراء' } },
}
export const GREETING = { en: 'Hi! Welcome. I can help you find a property in Dubai. What type of property are you looking for?', ar: 'مرحبًا بك! يسعدني مساعدتك في العثور على عقار في دبي. ما نوع العقار الذي تبحث عنه؟' }
export const DEMO_SCRIPT = {
  en: ["I'm looking for a 2 bedroom apartment.", 'Dubai Marina.', 'Investment.', 'AED 1.5 million.', 'Within two months.'],
  ar: ['أبحث عن شقة بغرفتي نوم.', 'دبي مارينا.', 'للاستثمار.', 'ميزانيتي ١٫٥ مليون درهم.', 'خلال شهرين.'],
}
// [label en, label ar, text sent en (optional), text sent ar (optional)]
export const OPTIONS = {
  property_type: [['Apartment', 'شقة'], ['Villa', 'فيلا'], ['Townhouse', 'تاون هاوس'], ['Penthouse', 'بنتهاوس']],
  bedrooms: [['Studio', 'استوديو', 'A studio'], ['1 bedroom', 'غرفة نوم واحدة'], ['2 bedrooms', 'غرفتا نوم'], ['3 bedrooms', '3 غرف نوم'], ['4 bedrooms', '4 غرف نوم'], ['5+ bedrooms', '5 غرف نوم أو أكثر']],
  area: [['Dubai Marina', 'دبي مارينا'], ['Downtown Dubai', 'وسط مدينة دبي'], ['Business Bay', 'الخليج التجاري'], ['Jumeirah', 'جميرا'], ['Palm Jumeirah', 'نخلة جميرا'], ['Arabian Ranches', 'أرابيان رانشز'], ['Dubai Hills', 'دبي هيلز'], ['JVC', 'قرية جميرا الدائرية']],
  purpose: [['Investment (rental income)', 'استثمار (دخل إيجاري)', 'It is for investment, mainly rental income', 'للاستثمار، بشكل رئيسي للدخل الإيجاري'], ['Personal use (to live in)', 'سكن شخصي', 'It is for personal use, to live in', 'للسكن الشخصي']],
  budget: [['About AED 1M', 'حوالي مليون درهم', 'My budget is around AED 1 million', 'ميزانيتي حوالي مليون درهم'], ['About AED 1.5M', 'حوالي 1.5 مليون', 'My budget is around AED 1.5 million', 'ميزانيتي حوالي 1.5 مليون درهم'],
    ['About AED 2.5M', 'حوالي 2.5 مليون', 'My budget is around AED 2.5 million', 'ميزانيتي حوالي 2.5 مليون درهم'], ['About AED 4M', 'حوالي 4 ملايين', 'My budget is around AED 4 million', 'ميزانيتي حوالي 4 ملايين درهم'],
    ['About AED 8M', 'حوالي 8 ملايين', 'My budget is around AED 8 million', 'ميزانيتي حوالي 8 ملايين درهم']],
  timeline: [['Within 1 month', 'خلال شهر'], ['Within 3 months', 'خلال 3 أشهر'], ['Within 6 months', 'خلال 6 أشهر'], ['More than 6 months', 'أكثر من 6 أشهر']],
}
export const FIELD_ORDER = ['property_type', 'bedrooms', 'area', 'purpose', 'budget', 'timeline']
export const hasArabic = (s) => /[\u0600-\u06FF]/.test(s)
