"""
Disability Service – Classifies disability type from extracted text
and returns relevant benefits.
"""
import re

# Static benefits database (can be extended or fetched from a database)
BENEFITS_DB = {
    "visual_impairment": [
        "Scholarships for visually impaired students",
        "Free/discounted public transport (state-specific)",
        "Priority in reservation for certain government jobs",
        "Screen reader and digital accessibility support programs"
    ],
    "hearing_impairment": [
        "Interpreter support in government offices",
        "Scholarships for hearing-impaired students",
        "Assistive device schemes (hearing aids, cochlear implants)",
        "Special recruitment drives"
    ],
    "locomotor_disability": [
        "Wheelchair and mobility aid grants",
        "Job reservations under PwD quota",
        "Rehabilitation and physiotherapy support",
        "Accessible infrastructure in schools and offices"
    ],
    "intellectual_disability": [
        "Special education and vocational training centers",
        "Government caregiver allowance",
        "Inclusive employment and therapy programs"
    ],
    "multiple_disability": [
        "Combined benefits from relevant disability categories",
        "Additional caregiver support schemes",
        "Priority in housing and welfare programs"
    ],
    "unknown": [
        "Certificate not recognized. Please verify manually.",
        "Upload a clearer certificate or check document type."
    ]
}

def classify_disability(text):
    """
    Rule-based classification of disability type using regex patterns.
    Returns one of: locomotor_disability, visual_impairment, hearing_impairment,
    intellectual_disability, unknown.
    """
    if not text or len(text) < 10:
        return "unknown"

    text_low = text.lower()

    patterns = {
        "locomotor_disability": [
            r"locomotor disability", r"he is a case of locomotor",
            r"physical disability", r"orthopedic disability",
            r"paraparesis", r"lumber disc", r"spinal", r"back injury",
            r"wheelchair", r"mobility impairment"
        ],
        "visual_impairment": [
            r"visual impairment", r"blind", r"low vision",
            r"eye disability", r"sight loss"
        ],
        "hearing_impairment": [
            r"hearing impairment", r"deaf", r"hard of hearing",
            r"hearing loss"
        ],
        "intellectual_disability": [
            r"intellectual disability", r"mental disability",
            r"autism", r"down syndrome"
        ]
    }

    scores = {}
    for dtype, pattern_list in patterns.items():
        score = 0
        for pat in pattern_list:
            if re.search(pat, text_low, re.IGNORECASE):
                score += 1
        scores[dtype] = score

    # Find the category with highest score
    best_type = max(scores, key=scores.get)
    return best_type if scores[best_type] > 0 else "unknown"

def extract_disability_details(text):
    """
    Extract additional details: disability percentage, certificate number,
    and diagnosis snippet.
    """
    details = {
        "type": "unknown",
        "percentage": None,
        "diagnosis": "",
        "certificate_number": ""
    }
    if not text:
        return details

    text_low = text.lower()

    # Extract percentage (e.g., "45%")
    perc_match = re.search(r'(\d{1,3})\s*%', text_low)
    if not perc_match:
        perc_match = re.search(r'(\d{1,3})\s*percent', text_low)
    if perc_match:
        details["percentage"] = int(perc_match.group(1))

    # Extract certificate number
    cert_match = re.search(r'certificate\s*no[.:]*\s*([A-Z0-9/]+)', text_low, re.IGNORECASE)
    if cert_match:
        details["certificate_number"] = cert_match.group(1)

    # Extract diagnosis (simple: text after "diagnosis")
    if "diagnosis" in text_low:
        idx = text_low.find("diagnosis")
        if idx != -1:
            details["diagnosis"] = text_low[idx:idx+200].strip()

    return details

def get_benefits(disability_type):
    """Return list of benefits for a given disability type."""
    return BENEFITS_DB.get(disability_type, BENEFITS_DB["unknown"])