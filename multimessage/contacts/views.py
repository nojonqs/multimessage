import threading
from itertools import chain
from typing import Any, Dict, List

import phonenumbers
from contacts.forms import ContactCreateForm, ContactListCreateForm
from contacts.models import Contact, Group
from contacts.signal_helper import (convert_uri_to_qrcode, get_link_qrcode,
                                    get_contact_with_uuid, is_signal_linked,
                                    signal_cli_finishLink,
                                    signal_cli_listContacts,
                                    signal_cli_listGroups, signal_cli_send,
                                    signal_cli_startLink)
from contacts.types import SignalGroup
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse_lazy
from django.views import generic


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

        single_recipients: List[Contact] = f.cleaned_data["single_recipients"] or []
        group_recipients: List[Group] = f.cleaned_data["group_recipients"] or []

        # for recipiant in f.cleaned_data["single_recipiants"]:
        #     print(f"SEND_MESSAGE: sending message to {recipiant}: '{message}'")
        #     send_message_to(recipiant, sender, message)
        signal_cli_send(single_recipients, sender, message)

        # for group in f.cleaned_data["group_recipiants"]:
        #     group: Group
        #     for recipiant in group.contacts.all():
        #         send_message_to(recipiant, sender, message)
        # flatten list of contacts 
        numbers_in_groups = list(chain.from_iterable(map(lambda group: list(group.contacts.all()), group_recipients)))
        print(type(numbers_in_groups))
        signal_cli_send(numbers_in_groups, sender, message)

        return render(request, "contacts/send_message.html", {"form": f})

    if request.method == "GET":
        from contacts.forms import SendMessageForm

        f = SendMessageForm()
        return render(request, "contacts/send_message.html", {"form": f})


def link_device(request):
    uri = request.GET.get("qr_code_uri")
    data = convert_uri_to_qrcode(uri)
    return HttpResponse(data, headers={
        "Content-Type": "image/png"
    })


class HttpResponseWithFuncAfter(HttpResponse):
    # We use this HttpResponse subclass to do communicate the finishLink
    # method to the signal socket after the http response was sent to
    # the client
    def __init__(self, *args, func, ctx, **kwargs):
        self.func = func
        self.ctx = ctx
        super().__init__(*args, **kwargs)

    def close(self):
        super().close()
        self.func(**self.ctx)


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

    # template = loader.get_template("contacts/signal_setup.html")
    # return HttpResponseWithFuncAfter(template.render(context, request), func=on_startlink_qrcode_send, ctx={"uri": qr_code_uri, "device_name": device_name})
    thread = threading.Thread(target=signal_cli_finishLink, kwargs={"uri": qr_code_uri, "device_name": device_name})
    thread.daemon = True
    thread.start()
    return render(request, "contacts/signal_setup.html", context)


def fetch_group_view(request, phone_number):
    if request.method == "GET":
        groups_json = signal_cli_listGroups(phone_number)
        ctx = {"groups_json": groups_json, "account": phone_number}
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


# TEST VIEWS

def list_contacts(request):
    return HttpResponse(signal_cli_listContacts(["**Phone_number**", "**Phone_number**"], "**Phone_number**"))


def get_uuid_for_number(request, phone_number: str):
    res: List[SignalContact] = signal_cli_listContacts([phone_number])
    assert len(res) == 1
    contact: SignalContact = res[0]

    return HttpResponse(contact["uuid"])
