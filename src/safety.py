"""Safety rules for a medication-information collection prototype."""

URGENT_PHRASES = {
    "can't breathe",
    "cannot breathe",
    "trouble breathing",
    "chest pain",
    "passed out",
    "severe allergic",
    "swelling of my face",
    "suicidal",
    "overdose",
}


def has_urgent_language(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in URGENT_PHRASES)


def urgent_response() -> str:
    return (
        "This may need immediate medical attention. MedVoice is not an emergency service. "
        "Please call 911 or seek emergency care now."
    )


def medication_boundary_response() -> str:
    return (
        "I cannot recommend starting, stopping, tapering, or changing a medication. "
        "I will record your question so your physician or pharmacist can review it with you."
    )
