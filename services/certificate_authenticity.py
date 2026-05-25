import math
import re

OFFICIAL_TERMS = [
    "disability certificate",
    "medical board",
    "competent authority",
    "chairperson",
    "member",
    "issued on",
    "valid till",
    "registration no",
    "official seal",
    "signature",
    "government of india",
    "rights of persons with disabilities act",
    "rpwd",
    "udid",
    "unique disability id",
    "disability percentage",
    "certificate no",
    "document no"
]

SUSPICIOUS_TERMS = [
    "sample",
    "draft",
    "for reference",
    "copy",
    "unauthorized",
    "not valid",
    "fake",
    "photocopy",
    "scanned document",
    "amateur",
    "edited",
    "handwritten"
]

MIN_WORDS_FOR_VALID = 30


def sigmoid(x):
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def extract_authenticity_features(text):
    text_low = text.lower()
    official_count = sum(1 for term in OFFICIAL_TERMS if term in text_low)
    suspicious_count = sum(1 for term in SUSPICIOUS_TERMS if term in text_low)
    word_count = len(re.findall(r"\w+", text_low))
    line_count = len(text_low.splitlines())
    has_signature = bool(re.search(r"signature|signed by|authorized signatory|signatory", text_low))
    has_seal = bool(re.search(r"seal|stamp|official seal|round seal", text_low))
    has_certificate_no = bool(re.search(r"certificate\s*(no|number|#)", text_low))

    return {
        "official_count": official_count,
        "suspicious_count": suspicious_count,
        "word_count": word_count,
        "line_count": line_count,
        "has_signature": has_signature,
        "has_seal": has_seal,
        "has_certificate_no": has_certificate_no
    }


def predict_certificate_authenticity(text, filename=None):
    """
    Lightweight authenticity predictor for disability certificates.
    Uses simple feature scoring with a logistic-style model.
    """
    if not text or len(text.strip()) < MIN_WORDS_FOR_VALID:
        return {
            "label": "Fake",
            "confidence": 0.18,
            "reason": "Document text is too short or unclear for a valid certificate."
        }

    features = extract_authenticity_features(text)

    # Simple weighted model to emulate lightweight ML scoring.
    score = -1.4
    score += 0.35 * min(features["official_count"], 5)
    score += 0.18 * features["has_signature"]
    score += 0.18 * features["has_seal"]
    score += 0.25 * features["has_certificate_no"]
    score -= 0.30 * min(features["suspicious_count"], 3)
    score += 0.08 * min(features["word_count"] / 50, 4)
    score += 0.05 * min(features["line_count"] / 10, 3)

    probability = sigmoid(score)
    label = "Legitimate" if probability >= 0.55 else "Fake"

    reasons = []
    if features["official_count"]:
        reasons.append(f"{features['official_count']} official phrase(s) detected")
    if features["has_signature"]:
        reasons.append("signature or signatory marker found")
    if features["has_seal"]:
        reasons.append("official seal/stamp language detected")
    if features["has_certificate_no"]:
        reasons.append("certificate number pattern recognized")
    if features["suspicious_count"]:
        reasons.append(f"{features['suspicious_count']} suspicious term(s) found")
    if features["word_count"] < MIN_WORDS_FOR_VALID:
        reasons.append("document text appears too short")

    if not reasons:
        reasons.append("No strong authenticity signals found; verify manually.")

    return {
        "label": label,
        "confidence": round(probability * 100, 1),
        "reason": "; ".join(reasons)
    }
