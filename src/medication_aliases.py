"""Small demo alias table. Replace with a validated medication terminology source in production."""

ALIASES = {
    "lisinopril": {"lisinopril", "prinivil", "zestril"},
    "furosemide": {"furosemide", "lasix"},
    "gabapentin": {"gabapentin", "neurontin"},
    "ondansetron": {"ondansetron", "zofran"},
}


def normalize_medication_name(text: str) -> str | None:
    cleaned = text.lower().strip()
    for generic_name, names in ALIASES.items():
        if any(name in cleaned for name in names):
            return generic_name
    return None


def display_name(generic_name: str) -> str:
    brands = sorted(ALIASES.get(generic_name, set()) - {generic_name})
    if brands:
        return f"{generic_name.title()} ({'/'.join(name.title() for name in brands)})"
    return generic_name.title()
