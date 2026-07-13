from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from medication_aliases import normalize_medication_name, display_name
from safety import has_urgent_language, urgent_response, medication_boundary_response

try:
    from openai import OpenAI
except ImportError:  # Allows deterministic demo without the package.
    OpenAI = None


SYSTEM_INSTRUCTIONS = """
You are MedVoice, an automated medication-conversation assistant.
Your job is to collect patient experiences and questions before a clinical visit.

Rules:
1. Clearly identify yourself as an automated assistant.
2. Do not diagnose, prescribe, recommend a new drug, recommend tapering, or advise dose changes.
3. Do not tell a patient to start or stop a medication.
4. When a patient asks for medication advice, acknowledge the concern and say it will be documented
   for a physician or pharmacist.
5. Confirm uncertain medication names using the patient's listed medications and generic/brand aliases.
6. Ask one short question at a time using plain language.
7. Preserve patient preferences, including a desire to stay on a current medication.
8. For potentially urgent symptoms, direct the patient to emergency care.
"""


class MedVoiceAgent:
    def __init__(self, patient_path: str | Path):
        self.patient = json.loads(Path(patient_path).read_text())
        self.history: list[dict[str, str]] = []
        self.notes: dict[str, Any] = {
            "patient_id": self.patient["patient_id"],
            "medications_discussed": {},
            "questions_for_care_team": [],
            "preferences": [],
            "possible_side_effects": [],
            "medication_list_corrections": [],
        }
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        self.client = None
        if not self.demo_mode and OpenAI and os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def opening(self) -> str:
        return (
            f"Hello {self.patient['first_name']}. I am MedVoice, an automated assistant helping "
            "you prepare for your medication visit. I cannot change medications or provide emergency care. "
            "Please have your medication bottles, list, or a trusted helper nearby if possible. "
            "Are you ready to begin?"
        )

    def listed_medication(self, generic_name: str) -> dict[str, Any] | None:
        for med in self.patient["medications"]:
            if med["generic_name"] == generic_name:
                return med
        return None

    def respond(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})

        if has_urgent_language(user_text):
            answer = urgent_response()
        elif self.client:
            answer = self._llm_response(user_text)
        else:
            answer = self._deterministic_response(user_text)

        self.history.append({"role": "assistant", "content": answer})
        return answer

    def _deterministic_response(self, text: str) -> str:
        lowered = text.lower()
        med_name = normalize_medication_name(text)

        if "don't remember" in lowered or "do not remember" in lowered or "not sure what" in lowered:
            bp_meds = [
                med for med in self.patient["medications"]
                if med["generic_name"] in {"lisinopril", "furosemide"}
            ]
            names = " and ".join(display_name(med["generic_name"]) for med in bp_meds)
            return (
                f"That is okay. Your current list shows {names}. "
                "Do either of those names match the medicine you take for blood pressure?"
            )

        if med_name:
            med = self.listed_medication(med_name)
            if med:
                self.notes["medications_discussed"].setdefault(med_name, {
                    "listed_dose": med["dose"],
                    "listed_frequency": med["frequency"],
                    "patient_statements": []
                })
                self.notes["medications_discussed"][med_name]["patient_statements"].append(text)

            if med_name == "furosemide" and "lasix" in lowered:
                return (
                    "Yes. Lasix is a brand name for furosemide, and it appears on your medication list. "
                    "How do you take it each day?"
                )

            if med_name == "gabapentin":
                if "nause" in lowered:
                    self.notes["possible_side_effects"].append({
                        "medication": "gabapentin",
                        "reported_effect": "nausea after each dose"
                    })
                if "zofran" in lowered or "ondansetron" in lowered or "could i get" in lowered:
                    self.notes["questions_for_care_team"].append(
                        "Patient asks whether treatment is appropriate for nausea associated with gabapentin."
                    )
                    return (
                        "I am sorry the nausea is happening after every dose. "
                        + medication_boundary_response()
                        + " You also said gabapentin helps you sleep. Is keeping that benefit important to you?"
                    )

        if "works the best" in lowered or "want to stay" in lowered or "keep taking" in lowered:
            self.notes["preferences"].append(
                "Patient prefers to remain on the current gabapentin regimen because prior alternatives "
                "or dose changes were less helpful."
            )
            return (
                "I understand. I will record that you prefer the current gabapentin routine because it works "
                "better for you than previous options, while the nausea remains a concern. "
                "What would you most like your clinician to discuss with you?"
            )

        if any(term in lowered for term in ["stop", "taper", "increase", "decrease", "switch medication"]):
            self.notes["questions_for_care_team"].append(text)
            return medication_boundary_response()

        if lowered in {"yes", "yes.", "ready", "i am ready"}:
            return (
                "Thank you. Are you taking any medications for your high blood pressure? "
                "You may use the name on the bottle, a brand name, or say that you do not remember."
            )

        return (
            "Thank you. I have recorded that. Please tell me the medication name, what you take it for, "
            "how often you take it, and any side effects or questions you want your care team to review."
        )

    def _llm_response(self, user_text: str) -> str:
        medication_context = json.dumps(self.patient["medications"], indent=2)
        transcript = "\n".join(
            f"{item['role']}: {item['content']}" for item in self.history[-10:]
        )
        response = self.client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=SYSTEM_INSTRUCTIONS,
            input=(
                f"Patient medication list:\n{medication_context}\n\n"
                f"Conversation:\n{transcript}\n\n"
                "Give one safe, concise spoken response. Do not provide a medication recommendation."
            ),
        )
        return response.output_text.strip()

    def summary(self) -> dict[str, Any]:
        return self.notes
