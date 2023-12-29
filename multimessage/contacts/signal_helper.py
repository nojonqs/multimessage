import asyncio
import json
import os

import requests
from contacts.models import Contact
from signalbot import SignalBot


class NoPhoneNumberLinked(Exception):
    pass


def get_first_linked_phone_number():
    numbers = get_linked_phone_numbers()
    if len(numbers) == 0:
        raise NoPhoneNumberLinked()

    return numbers[0]


def get_linked_phone_numbers():
    if not is_signal_linked():
        raise NoPhoneNumberLinked()
    res = requests.get(f"http://{os.environ.get('SIGNAL_SERVICE')}/v1/accounts")
    accounts = json.loads(res.content)
    return accounts


def is_signal_linked():
    res = requests.get(f"http://{os.environ.get('SIGNAL_SERVICE')}/v1/accounts")
    accounts = json.loads(res.content)
    return len(accounts) >= 1


def send_message_to(recipiant: Contact, sender: str, message: str):
    print(f"SEND_MESSAGE: sending message to {recipiant}: '{message}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    signal_bot = SignalBot({
        'signal_service': os.environ.get('SIGNAL_SERVICE'),
        'phone_number': sender,
    })
    asyncio.run(signal_bot.send(recipiant.phone_number.as_international, message))


def fetch_groups_of_number(phone_number: str):
    res = requests.get(
        f"http://{os.environ.get('SIGNAL_SERVICE')}/v1/groups/{phone_number}"
    )
    print(res)
    print(res.content)
