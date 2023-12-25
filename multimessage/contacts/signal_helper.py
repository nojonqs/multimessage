from typing import Optional
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from signalbot import SignalBot
import asyncio
import os
import json
import requests

signal_bot: Optional[SignalBot] = None

def reset(request):
   # TODO: unlink every number
   global signal_bot
   signal_bot = None
   return redirect(request.get_full_path())

def get_first_linked_account():
   if not is_signal_linked():
      print("ERROR get_linked_account")
   res = requests.get(f"http://{os.environ.get('SIGNAL_SERVICE')}/v1/accounts")
   accounts = json.loads(res.content)
   print(accounts[0])
   return accounts[0]
   

def is_signal_linked():
    print('SIGNAL: IS_LINKED')
    res = requests.get(f"http://{os.environ.get('SIGNAL_SERVICE')}/v1/accounts")
    accounts = json.loads(res.content)
    return len(accounts) == 1


def setup_signal_bot_if_device_linked():
    print('SIGNAL: SETUP_IF_LINKED')
    if signal_bot is None and is_signal_linked():
        phone_number = get_first_linked_account()
        register(phone_number)


def send_message(request):
    if not is_signal_linked():
        print("ERROR: Signal not linked yet")
        return redirect(reverse_lazy('contact:signal_setup'))
    
    setup_signal_bot_if_device_linked()
    # TODO: add phone number support
    asyncio.run(signal_bot.send('PHONE_NUMBER_HERE', "du knödel"))
    return redirect(reverse_lazy('contact:index'))


def register(phone_number):
    global signal_bot

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    signal_bot = SignalBot({
        'signal_service': os.environ.get("SIGNAL_SERVICE"),
        'phone_number': phone_number,
    })

    
def setup(request):
   global signal_bot
   print(f"is_signal_setup: {is_signal_linked()}, is bot setup: {signal_bot is not None}")
   context = {
      'is_signal_linked': is_signal_linked(),
      'is_bot_setup': signal_bot is None,
   }
   return render(request, 'contacts/signal_setup.html', context)