PROGRAMS = [
    {
        "id": "P01",
        "name": "الحمية السلوكية",
        "bmi_range": (22, 40),
        "advantages": [
            "يركز على تغيير العادات وليس النزول السريع فقط",
            "بدون حرمان قاسٍ",
            "نتائج مستدامة على المدى الطويل",
        ],
        "best_for": [
            "من يريد نتائج طويلة المدى",
            "من جرّب أنظمة سابقة ولم يستمر",
        ],
        "link": "https://rasheqa.shop/products/al-hemya-al-solokiya",
    },
    {
        "id": "P02",
        "name": "تكميم بلا تكميم",
        "bmi_range": (30, 50),
        "advantages": [
            "يساعد على تقليل الشهية بشكل طبيعي",
            "لا يحتاج إلى جراحة",
            "آمن وفعّال",
        ],
        "best_for": [
            "من لديه مؤشر كتلة جسم مرتفع",
            "من يعاني من شهية مفتوحة يصعب التحكم فيها",
        ],
        "link": "https://rasheqa.shop/products/takmeem-bila-takmeem",
    },
    {
        "id": "P03",
        "name": "الحمية المائية",
        "bmi_range": (23, 35),
        "advantages": [
            "يساعد على تقليل الانتفاخ والاحتباس المائي",
            "سهل التطبيق",
            "نتائج سريعة وملحوظة",
        ],
        "best_for": [
            "من يعاني من احتباس السوائل",
            "من يريد نظاماً سهل التطبيق",
        ],
        "link": "https://rasheqa.shop/products/al-hemya-al-maiya",
    },
    {
        "id": "P04",
        "name": "حمية الطوارئ",
        "bmi_range": (23, 35),
        "advantages": [
            "نتائج ملحوظة خلال فترة قصيرة",
            "تعزز الدافع للاستمرار",
        ],
        "best_for": [
            "من لديه مناسبة قريبة",
            "من يحتاج دفعة تحفيزية سريعة",
        ],
        "link": "https://rasheqa.shop/products/hemyet-al-taware",
    },
    {
        "id": "P05",
        "name": "كتيب القرنفل للتنحيف",
        "bmi_range": (22, 35),
        "advantages": [
            "يعتمد على مكونات طبيعية 100%",
            "يدعم صحة الجهاز الهضمي",
        ],
        "best_for": [
            "من يفضّل الحلول الطبيعية والآمنة",
        ],
        "link": "https://rasheqa.shop/products/kutayeb-al-qurunful",
    },
]


def get_programs_context() -> str:
    """Build a concise programs reference block for the system prompt."""
    lines = ["\n## Available Rasheqa Programs\n"]
    for p in PROGRAMS:
        lines.append(f"### {p['id']} — {p['name']}")
        lines.append(f"  BMI range: {p['bmi_range'][0]}–{p['bmi_range'][1]}")
        lines.append(f"  Advantages: {' / '.join(p['advantages'])}")
        lines.append(f"  Best for: {' / '.join(p['best_for'])}")
        lines.append(f"  Link: {p['link']}")
        lines.append("")
    return "\n".join(lines)


def recommend_programs(bmi: float) -> list[dict]:
    """Return programs whose BMI range covers the given value."""
    return [p for p in PROGRAMS if p["bmi_range"][0] <= bmi <= p["bmi_range"][1]]
