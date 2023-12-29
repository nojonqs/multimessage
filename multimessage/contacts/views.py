from typing import Any, Dict
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
import phonenumbers
from .models import Contact, Group
from .forms import ContactCreateForm, ContactListCreateForm
from .signal_helper import is_signal_linked, is_signal_bot_setup, send_message_to


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def link_device(request):
    name = request.GET.get("device_name") or "multi_message"
    return redirect(f"http://127.0.0.1:8080/v1/qrcodelink/?device_name={name}")


def detail(request, contact_id):
    return HttpResponse("Contact detail for contact with id " + str(contact_id))


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

        for recipiant in f.cleaned_data["single_recipiants"]:
            print(f"SEND_MESSAGE: sending message to {recipiant}: '{message}'")
            send_message_to(recipiant, sender, message)

        for group in f.cleaned_data["group_recipiants"]:
            group: Group
            for recipiant in group.contacts.all():
                send_message_to(recipiant, sender, message)

        return render(request, "contacts/send_message.html", {"form": f})

    if request.method == "GET":
        from contacts.forms import SendMessageForm

        f = SendMessageForm()
        return render(request, "contacts/send_message.html", {"form": f})


def setup_view(request):
    global signal_bot
    context = {
        "is_signal_linked": is_signal_linked(),
        "is_bot_setup": is_signal_bot_setup(),
    }
    return render(request, "contacts/signal_setup.html", context)
