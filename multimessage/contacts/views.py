from typing import Any, Dict
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
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


class ContactCreateView(generic.CreateView):
    template_name = "contacts/contact_create_form.html"
    form_class = ContactCreateForm
    model = Contact

    success_url = reverse_lazy("contact:contact_overview")


class ContactListCreateView(generic.CreateView):
    template_name = "contacts/contact_list_create_form.html"
    form_class = ContactListCreateForm
    model = Group

    success_url = reverse_lazy("contact:group_overview")


class ContactDeleteView(generic.DeleteView):
    model = Contact
    success_url = reverse_lazy("contact:contact_overview")


class ContactOverview(generic.ListView):
    model = Contact
    template_name = "contacts/contact_overview.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        contacts = Contact.objects.all()
        context.update({"contacts_list": contacts})
        return context


class GroupOverview(generic.ListView):
    model = Group
    template_name = "contacts/group_overview.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        groups = Group.objects.all()
        context.update({"groups_list": groups})


def send_message_view(request):
    if request.method == "POST":
        from contacts.forms import SendMessageForm

        f = SendMessageForm(request.POST)

        if not f.is_valid():
            raise ValueError(
                "SEND_MESSAGE: post request does not fit the SendMessageForm"
            )

        message = f.cleaned_data["message"]

        for recipiant in f.cleaned_data["single_recipiants"]:
            print(f"SEND_MESSAGE: sending message to {recipiant}: '{message}'")
            send_message_to(recipiant, message)

        for group in f.cleaned_data["group_recipiants"]:
            group: Group
            for recipiant in group.contacts.all():
                send_message_to(recipiant, message)

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
