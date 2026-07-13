# MedVoice AI Calling Agent — Sample Prototype

This sample adapts an outbound AI-calling architecture to a medication-conversation use case.
It is designed for **pre-visit information collection**, not medical decision-making.

## Demonstrated scenarios

1. **Medication-name uncertainty**
   - The patient does not remember a blood-pressure medication.
   - The agent checks the patient's stored list.
   - The agent matches generic and brand names, including `Lasix` → `furosemide`.

2. **Side effect and medication request**
   - The patient says gabapentin helps with sleep but causes nausea.
   - The patient asks about Zofran.
   - The agent records the request and preference but does not prescribe, recommend tapering,
     or recommend switching medication.

## Project structure

```text
medvoice_calling_agent_sample/
├── data/patient.json
├── src/
│   ├── agent.py
│   ├── app.py
│   ├── medication_aliases.py
│   └── safety.py
├── demo_console.py
├── make_call.py
├── requirements.txt
└── .env.example
```

## Run the safe console demo

```bash
cd medvoice_calling_agent_sample
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python demo_console.py
```

The default `DEMO_MODE=true` runs without OpenAI, Twilio, MongoDB, or a real phone call.

## Run the Flask/Twilio sample

```bash
python src/app.py
```

Expose port 5000 using a secure development tunnel, put its HTTPS URL in `BASE_URL`, then run:

```bash
python make_call.py
```

Twilio sends speech transcripts to `/conversation`; the application returns TwiML speech responses.
Visit `/summary` to see the structured notes created during the conversation.

## Optional OpenAI mode

Set:

```text
DEMO_MODE=false
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
```

The agent uses the OpenAI Responses API while retaining explicit safety instructions. A production
system still needs deterministic validation, clinical review, audit logging, consent management,
security controls, and extensive testing.

## Important production limitations

- The alias table is only a tiny demo and is not a validated drug knowledge base.
- Do not place real protected health information in this prototype.
- Do not record calls without appropriate notice and legally valid consent.
- Use authenticated webhooks and validate Twilio request signatures.
- Add role-based access, encryption, retention controls, monitoring, and human escalation.
- Emergency language must end the normal workflow and direct the patient to immediate help.
- Medication reconciliation and all treatment decisions must be performed by licensed clinicians.
