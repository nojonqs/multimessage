import base64
import io
import json
import os
import socket
from typing import List

import qrcode
from contacts.models import Contact
from contacts.types import (NoPhoneNumberLinked, SignalCliJsonRpcRequest,
                            SignalCliSocketError, SignalContact, SignalGroup)
from django.apps import apps


def recvall(sock):
    MAX_MSG_SIZE = 4096
    fragments = []
    while True:
        chunk = sock.recv(MAX_MSG_SIZE)
        fragments.append(chunk)
        if chunk[-1:] == b"\n":
            break
    return b''.join(fragments)


def send_data_to_socket(data: SignalCliJsonRpcRequest):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(os.environ.get("SIGNAL_CLI_SOCKET"))

        # Add newline so the socket knows when we are finished sending
        # NO!! this did not cost me 2 hours to figure out!!!
        # I'm not crying, you're crying!
        d = (json.dumps(data) + "\n")
        print(f"SIGNAL_SOCKET_SEND: {data}")
        s.sendall(d.encode())
        res = json.loads(recvall(s))
        print(f"SIGNAL_SOCKET_RECV: {res}")

        assert res["id"] == data["id"]

        if "error" in res:
            print("[ERROR]", res["error"]["code"], res["error"]["message"])
            raise SignalCliSocketError()

    return res["result"]


def signal_cli_startLink(device_name: str = None) -> str:
    # https://github.com/AsamK/signal-cli/blob/master/man/signal-cli-jsonrpc.5.adoc#startlink
    
    if device_name is None:
        device_name = "multi_message"

    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "startLink",
        "id": f"startLink_{device_name}"
    }
    res = send_data_to_socket(data)

    return res["deviceLinkUri"]


def signal_cli_finishLink(uri, device_name):
    # https://github.com/AsamK/signal-cli/blob/master/man/signal-cli-jsonrpc.5.adoc#finishlink

    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "finishLink",
        "params": {
            "deviceName": device_name,
            "deviceLinkUri": uri,
        },
        "id": f"finishLink_{uri}"
    }
    send_data_to_socket(data)


def convert_uri_to_qrcode(uri: str) -> bytes:
    qr_code = qrcode.make(uri, version=10)
    buffer = io.BytesIO()
    qr_code.save(buffer)
    return base64.b64encode(buffer.getvalue())


def get_link_qrcode(device_name: str = None) -> bytes:
    if device_name is None:
        device_name = "multi_message"
    
    uri = signal_cli_startLink(device_name)
    return convert_uri_to_qrcode(uri)


def get_first_linked_phone_number():
    numbers = signal_cli_listAccounts()
    if len(numbers) == 0:
        raise NoPhoneNumberLinked()

    return numbers[0]


def signal_cli_listAccounts():
    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "listAccounts",
        "id": "listAccounts",
    }

    # result is a list of mappings {"number": "+XXXXXXXXXXXXX"}
    res = send_data_to_socket(data)

    # extract phone numbers only
    numbers_list = list(map(lambda mapping: mapping["number"], res))
    print(numbers_list)

    return numbers_list


def is_signal_linked():
    res = signal_cli_listAccounts()
    return len(res) > 0


def signal_cli_send(recipients: [Contact], account: str, message: str):
    # https://github.com/AsamK/signal-cli/blob/master/man/signal-cli.1.adoc#send

    uuids: List[str] = list(map(lambda recipiant: recipiant.uuid, recipients))

    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "send",
        "params": {
            "account": account,
            "recipient": uuids,
            "message": message,
        },
        "id": f"send_{account}_{uuids}"
    }
    res = send_data_to_socket(data)
    # signal.sendMessage(message=message, attachments=[], recipient=recipiant.phone_number.as_international)


def signal_cli_listContacts(recipients: [str], account: str = None):
    # https://github.com/AsamK/signal-cli/blob/master/man/signal-cli.1.adoc#listcontacts

    # assumes the phone_numbers are valid signal phone numbers

    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "listContacts",
        "params": {
            "recipient": recipients,
        },
        "id": f"listContacts_{account}_{recipients}"
    }
    if account is not None:
        data["params"]["account"] = account
    
    res: List[SignalContact] = send_data_to_socket(data)
    return res



def signal_cli_listGroups(account: str) -> List[SignalGroup]:
    # https://github.com/AsamK/signal-cli/blob/master/man/signal-cli.1.adoc#listgroups
    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "listGroups",
        "params": {
            "account": account,
        },
        "id": f"listGroups_{account}",
    }
    res: List[SignalGroup] = send_data_to_socket(data)
    return res
