from typing import Optional
from django.shortcuts import redirect
from signalbot import SignalBot
import asyncio
import os

signal_bot: Optional[SignalBot] = None

def send_message(request):
    if signal_bot is not None:
      asyncio.run(signal_bot.send('PHONE_NUMBER_HERE', "du knödel"))
    else:
       print("signal_bot not initialized")
    return redirect("contact:index")

def register(request):
    global signal_bot

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    signal_bot = SignalBot({
        'signal_service': os.environ.get("SIGNAL_SERVICE"),
        'phone_number': 'PHONE_NUMBER_HERE'
    })
    return redirect("contact:index")
    