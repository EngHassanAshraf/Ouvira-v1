from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings


def send_sms(phone: str, message: str, from_number: str) -> bool:

    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
        )

        sms = client.messages.create(body=message, from_=from_number, to=phone)

        return True

    except TwilioRestException as e:
        return False
