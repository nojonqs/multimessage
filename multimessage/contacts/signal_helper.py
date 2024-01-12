import base64
import io
import json
import os
import socket
from typing import List, Optional

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
        # print(f"SIGNAL_SOCKET_RECV: {res}")

        assert res.get("id") == data["id"] or res.get("method") == "receive"

        if res.get("method") == "receive":
            return None
        
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
        "id": f"send_{account}"
    }
    res = send_data_to_socket(data)
    return res


def signal_cli_listContacts(recipients: [str] = None, account: str = None, include_all_recipients = True) -> List[SignalContact]:
    # https://github.com/AsamK/signal-cli/blob/master/man/signal-cli.1.adoc#listcontacts

    # assumes the phone_numbers are valid signal phone numbers

    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "listContacts",
        "params": {
        },
        "id": f"listContacts_{account}"
    }
    if account is not None:
        data["params"]["account"] = account

    if recipients is not None:
        data["params"]["recipients"] = recipients

    if include_all_recipients:
        data["params"]["allRecipients"] = True
    
    res: List[SignalContact] = send_data_to_socket(data)
    return res



def signal_cli_listGroups(account: str, group_id: str = None) -> List[SignalGroup]:
    # https://github.com/AsamK/signal-cli/blob/master/man/signal-cli.1.adoc#listgroups
    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "listGroups",
        "params": {
            "account": account,
            "detailed": True,
        },
        "id": f"listGroups_{account}",
    }
    if group_id is not None:
        data["params"]["groupId"] = group_id
    
    res: List[SignalGroup] = send_data_to_socket(data)
    return res


def list_groups_cleaned(*args, **kwargs) -> List[SignalGroup]:
    res = signal_cli_listGroups(*args, **kwargs)

    groups = list(filter(lambda g: g["name"] is not None, res))
    for g in groups:
        if g["name"] == "":
            g["name"] = "Note to self"
    
    groups = sorted(groups, key=lambda d: d["name"])
    return groups


def signal_cli_listIdentities(account: str, recipient: str = None):
    # https://github.com/AsamK/signal-cli/blob/master/man/signal-cli.1.adoc#listidentities
    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "listIdentities",
        "params": {
            "account": account,
        },
        "id": f"listIdentities_{account}",
    }
    if recipient is not None:
        data["params"]["number"] = recipient
    
    res = send_data_to_socket(data)
    print(res)



def signal_cli_sendSyncRequest(account: str):
    # https://github.com/AsamK/signal-cli/blob/master/man/signal-cli.1.adoc#sendsyncrequest
    data: SignalCliJsonRpcRequest = {
        "jsonrpc": "2.0",
        "method": "sendSyncRequest",
        "params": {
            "account": account
        },
        "id": f"syncRequest_{account}"
    }
    send_data_to_socket(data)


def get_contact_with_uuid(uuid: str, account: str) -> SignalContact:
    contacts = signal_cli_listContacts([uuid], account)
    assert len(contacts) == 1
    contact = contacts[0]
    return contact


def get_contact_with_phonenumber(phone_number: str, account: str) -> SignalContact:
    contacts = signal_cli_listContacts([phone_number], account)
    assert len(contacts) == 1
    contact = contacts[0]
    return contact


def get_uuid_for_number(phone_number: str) -> str:
    return get_contact_with_phonenumber(phone_number, account=None)["uuid"]


def get_contact_name(contact: SignalContact) -> Optional[str]:
    if contact["name"]:
        return contact["name"]
    elif contact["profile"] and contact["profile"].get("givenName"):
        return contact["profile"]["givenName"] + (contact["profile"]["familyName"] or "")
    elif contact["username"]:
        return contact["username"]
    else:
        return None
