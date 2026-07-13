import os

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

required = [
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_PHONE_NUMBER",
    "PATIENT_PHONE_NUMBER",
    "BASE_URL",
]
missing = [name for name in required if not os.getenv(name)]
if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
call = client.calls.create(
    to=os.environ["PATIENT_PHONE_NUMBER"],
    from_=os.environ["TWILIO_PHONE_NUMBER"],
    url=f"{os.environ['BASE_URL'].rstrip('/')}/handle-call",
    status_callback=f"{os.environ['BASE_URL'].rstrip('/')}/call-status",
)
print(f"Started call: {call.sid}")
