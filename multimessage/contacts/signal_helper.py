from typing import Optional
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from signalbot import SignalBot
import asyncio
import os
import json
import requests
from functools import wraps
from contacts.models import Contact, Group

signal_bot: Optional[SignalBot] = None


def reset(request):
    # TODO: unlink every number
    global signal_bot
    signal_bot = None
    return redirect(request.get_full_path())


def register(phone_number):
    global signal_bot

    create_asyncio_eventloop_if_not_exist()
    signal_bot = SignalBot(
        {
            "signal_service": os.environ.get("SIGNAL_SERVICE"),
            "phone_number": phone_number,
        }
    )


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


def is_signal_bot_setup():
    return signal_bot is not None


def setup_signal_bot_if_device_linked():
    if signal_bot is None and is_signal_linked():
        phone_number = get_first_linked_phone_number()
        register(phone_number)


def create_asyncio_eventloop_if_not_exist():
    if asyncio.get_event_loop() is None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def send_message_to(recipiant: Contact, sender: str, message: str):
    print(f"SEND_MESSAGE: sending message to {recipiant}: '{message}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    signal_bot = SignalBot({
        'signal_service': os.environ.get('SIGNAL_SERVICE'),
        'phone_number': sender,
    })
    asyncio.run(signal_bot.send(recipiant.phone_number.as_international, message))
