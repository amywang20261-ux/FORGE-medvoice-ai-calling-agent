from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, Response, request
from twilio.twiml.voice_response import Gather, VoiceResponse

from agent import MedVoiceAgent

load_dotenv()
app = Flask(__name__)

PATIENT_FILE = Path(__file__).resolve().parents[1] / "data" / "patient.json"
agent = MedVoiceAgent(PATIENT_FILE)


@app.get("/")
def health():
    return {"status": "ok", "service": "MedVoice sample"}


@app.route("/handle-call", methods=["GET", "POST"])
def handle_call():
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/conversation",
        method="POST",
        speech_timeout="auto",
    )
    gather.say(agent.opening())
    response.append(gather)
    response.redirect("/handle-call")
    return Response(str(response), mimetype="text/xml")


@app.post("/conversation")
def conversation():
    speech = request.form.get("SpeechResult", "").strip()
    answer = agent.respond(speech)

    response = VoiceResponse()
    if "call 911" in answer.lower():
        response.say(answer)
        response.hangup()
        return Response(str(response), mimetype="text/xml")

    gather = Gather(
        input="speech",
        action="/conversation",
        method="POST",
        speech_timeout="auto",
    )
    gather.say(answer)
    response.append(gather)
    response.say("I did not hear a response. We can continue at another time. Goodbye.")
    response.hangup()
    return Response(str(response), mimetype="text/xml")


@app.get("/summary")
def summary():
    return app.response_class(
        json.dumps(agent.summary(), indent=2),
        mimetype="application/json",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
