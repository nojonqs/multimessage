import json
import threading
from itertools import chain, zip_longest
from typing import Any, Dict, List, Optional

import phonenumbers
from contacts.forms import (ContactCreateForm, ContactInfoForm,
                            ContactListCreateForm, SendMessageForm)
from contacts.models import Contact, Group
from contacts.signal_helper import (convert_uri_to_qrcode, get_contact_name,
                                    get_contact_with_phonenumber,
                                    get_contact_with_uuid, get_link_qrcode,
                                    is_signal_linked, list_groups_cleaned,
                                    signal_cli_finishLink,
                                    signal_cli_listAccounts,
                                    signal_cli_listContacts,
                                    signal_cli_listGroups,
                                    signal_cli_listIdentities, signal_cli_send,
                                    signal_cli_sendSyncRequest,
                                    signal_cli_startLink)
from contacts.types import (SignalAccount, SignalContact, SignalGroup,
                            SignalGroupWithContacts)
from django.core.cache import caches
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse_lazy
from django.views import generic
from phonenumber_field.phonenumber import PhoneNumber


class ContactOverview(generic.ListView):
    model = Contact
    template_name = "contacts/contact_overview.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        contacts = Contact.objects.all()
        context.update({"contacts_list": contacts})
        return context


class ContactCreateView(generic.CreateView):
    model = Contact
    form_class = ContactCreateForm
    template_name = "contacts/contact_create.html"
    success_url = reverse_lazy("contact:contact_overview")


class ContactDeleteView(generic.DeleteView):
    model = Contact
    success_url = reverse_lazy("contact:contact_overview")


class GroupOverview(generic.ListView):
    model = Group
    template_name = "contacts/group_overview.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        groups = Group.objects.all()
        context.update({"groups_list": groups})
        return context


class GroupCreateView(generic.CreateView):
    model = Group
    form_class = ContactListCreateForm
    template_name = "contacts/group_create.html"
    success_url = reverse_lazy("contact:group_overview")


class GroupDeleteView(generic.DeleteView):
    model = Group
    success_url = reverse_lazy("contact:group_overview")


def send_message_view(request):
    if request.method == "POST":
        from contacts.forms import SendMessageForm

        f = SendMessageForm(request.POST)

        if not f.is_valid():
            raise ValueError(
                "SEND_MESSAGE: post request does not fit the SendMessageForm"
            )

        message = f.cleaned_data["message"]
        sender = f.cleaned_data["sender"]
        assert phonenumbers.is_valid_number(phonenumbers.parse(sender))

        single_recipients: List[Contact] = f.cleaned_data["single_recipients"]
        group_recipients: List[Group] = f.cleaned_data["group_recipients"]

        # for recipiant in f.cleaned_data["single_recipiants"]:
        #     print(f"SEND_MESSAGE: sending message to {recipiant}: '{message}'")
        #     send_message_to(recipiant, sender, message)
        results_contacts = {}
        if len(single_recipients):
            results_contacts = signal_cli_send(single_recipients, sender, message)

        # for group in f.cleaned_data["group_recipiants"]:
        #     group: Group
        #     for recipiant in group.contacts.all():
        #         send_message_to(recipiant, sender, message)
        # flatten list of contacts 
        results_groups = {}
        numbers_in_groups = list(chain.from_iterable(map(lambda group: list(group.contacts.all()), group_recipients)))
        if len(numbers_in_groups):
            results_groups = signal_cli_send(numbers_in_groups, sender, message)

        return render(request, "contacts/send_message.html", {"form": f})

    if request.method == "GET":
        from contacts.forms import SendMessageForm

        f = SendMessageForm()

        account: SignalAccount = signal_cli_listAccounts()[0]

        signal_groups: List[SignalGroup] = list_groups_cleaned(account=account)

        signal_contacts: List[SignalContact] = signal_cli_listContacts(recipients=None, account=account, include_all_recipients=False)
        signal_contacts = filter(lambda c: get_contact_name(c) is not None, signal_contacts)
        signal_contacts = sorted(signal_contacts, key=lambda c: get_contact_name(c).lower())

        return render(request, "contacts/send_message.html", {"form": f, "groups_json": signal_groups, "contacts_json": signal_contacts, "account": account})


def link_device(request):
    uri = request.GET.get("qr_code_uri")
    data = convert_uri_to_qrcode(uri)
    return HttpResponse(data, headers={
        "Content-Type": "image/png"
    })


def setup_view(request):
    device_name = request.GET.get("device_name") or "multi_message"
    qr_code_uri = signal_cli_startLink(device_name)
    qr_code_bytes = convert_uri_to_qrcode(qr_code_uri).decode()
    # print(qr_code_image)

    context = {
        "is_signal_linked": is_signal_linked(),
        "device_name": device_name,
        "qr_code_uri": qr_code_uri,
        "qr_code_bytes": qr_code_bytes,
    }

    thread = threading.Thread(target=signal_cli_finishLink, kwargs={"uri": qr_code_uri, "device_name": device_name})
    thread.daemon = True
    thread.start()
    return render(request, "contacts/signal_setup.html", context)


def fetch_group_view(request, account):
    if request.method == "GET":
        groups_json: List[SignalGroup] = list_groups_cleaned(account)

        ctx = {"groups_json": groups_json, "account": account}
        return render(request, "contacts/view_groups.html", context=ctx)


def import_group_from_signalcli(request, account: str, signal_group_id: str):
    groups: List[SignalGroup] = signal_cli_listGroups(account, signal_group_id)
    if len(groups) == 0:
        return HttpResponseBadRequest()
    
    assert len(groups) == 1
    group = groups[0]

    contact_models = []
    for member in group["members"]:
        assert member["uuid"]
        m = get_contact_with_uuid(member["uuid"], account)
        number = m["number"]
        uuid = m["uuid"]
        name = m["profile"]["givenName"]
        
        if Contact.objects.filter(uuid=uuid).exists():
            c = Contact.objects.get(uuid=uuid)
        else:
            c = Contact.objects.create(display_name=name, phone_number=number, uuid=uuid)

        contact_models.append(c)
    
    display_name = group["name"]
    group_model = Group.objects.create(display_name=display_name)
    group_model.contacts.add(*contact_models)

    print(f"Created group model {group_model} from group json {group}")


def get_group_members(request, account: str, group_id: str):
    if request.method == "GET":
        print(f"Got get request with {account = } and {group_id = }")
        groups: SignalGroup = signal_cli_listGroups(account, group_id)
        if len(groups) == 0:
            return HttpResponseBadRequest(f"Could not fetch group with id {group_id}")

        assert len(groups) == 1
        group = groups[0]

        members: List[SignalAccount] = group["members"]
        members_uuids = list(map(lambda m: m["uuid"], members))

        members: List[SignalContact] = signal_cli_listContacts(members_uuids, account)
        if members is None:
            return HttpResponseBadRequest("Please try again...")
        
        def sort_by_any_name(m):
            if m["profile"] and m["profile"].get("givenName"):
                return m["profile"]["givenName"].lower()
            elif m["username"]:
                return m["username"].lower()
            elif m["name"]:
                return m["name"].lower()
            else:
                return "?"

        members = sorted(members, key=sort_by_any_name)
        print(f"Returning {len(members)} members for group {group_id}")
        return HttpResponse(json.dumps(members))
        
    return None


def sync_contacts_groups_from_primarydevice(request, account: str):
    signal_cli_sendSyncRequest(account)

def list_identities_view(request, account: str):
    signal_cli_listIdentities(account)


# TEST VIEWS

def info_about_contact(request):
    if request.method == "GET":
        form = ContactInfoForm()
        request.session["searched_contacts"] = []
        contacts = request.session.get("searched_contacts") or []
        return render(request, "contacts/info_about_contact.html", {"form": form, "contacts": contacts})

    if request.method == "POST":
        form = ContactInfoForm(request.POST)
        if not form.is_valid():
            contacts = request.session.get("searched_contacts") or []
            return render(request, "contacts/info_about_contact.html", {"form": form, "contacts": contacts})

        phone_number: Optional[PhoneNumber] = form.cleaned_data["phone_number"] or None
        uuid: str = form.cleaned_data["uuid"] or None
        account: str = form.cleaned_data["account"] or None
        print(f"INFO: Account is {account}")
        
        # we assert this since the form should take care of that
        assert phone_number or uuid

        if uuid:
            contact: SignalContact = get_contact_with_uuid(uuid, account)
        if phone_number:
            contact: SignalContact = get_contact_with_phonenumber(phone_number.as_international, account)
        
        contacts: List[SignalContact] = request.session.get("searched_contacts") or []
        
        contacts = [c for c in contacts if c["uuid"] != contact["uuid"]]
        
        contacts.insert(0, contact)
        request.session["searched_contacts"] = contacts

        return render(request, "contacts/info_about_contact.html", {"form": form, "contacts": contacts})


def list_contacts(request):
    return HttpResponse(signal_cli_listContacts(include_all_recipients=False))


def get_uuid_for_number(request, phone_number: str):
    res: List[SignalContact] = signal_cli_listContacts([phone_number])
    assert len(res) == 1
    contact: SignalContact = res[0]

    return HttpResponse(contact["uuid"])
