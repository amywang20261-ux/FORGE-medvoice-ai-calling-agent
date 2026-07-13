from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent import MedVoiceAgent


def main():
    patient_file = Path(__file__).parent / "data" / "patient.json"
    agent = MedVoiceAgent(patient_file)

    print("\nMedVoice:", agent.opening())
    print("\nType 'bye' when you are finished.\n")

    while True:
        patient_input = input("Patient: ").strip()

        if not patient_input:
            print("MedVoice: I did not hear a response. Please try again.\n")
            continue

        if patient_input.lower() in {
            "bye",
            "goodbye",
            "quit",
            "exit",
            "done"
        }:
            print("\nMedVoice: Thank you. Your responses have been recorded.")
            break

        response = agent.respond(patient_input)
        print("MedVoice:", response)
        print()

        if "call 911" in response.lower():
            break

    print("\n--- CARE TEAM SUMMARY ---")
    print(json.dumps(agent.summary(), indent=2))


if __name__ == "__main__":
    main()