from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render
from .models import Contact, ContactList
from .forms import ContactCreateForm, ContactListCreateForm
from .signal_helper import is_signal_linked, is_signal_bot_setup, send_message_to


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def detail(request, contact_id):
    return HttpResponse("Contact detail for contact with id " + str(contact_id))


class ContactCreateView(generic.CreateView):
    template_name = 'contacts/contact_create_form.html'
    form_class = ContactCreateForm
    model = Contact

    success_url = reverse_lazy('contact:index')


class ContactListCreateView(generic.CreateView):
    template_name = 'contacts/contact_list_create_form.html'
    form_class = ContactListCreateForm
    model = ContactList

    success_url = reverse_lazy('contact:index')


def prepare_message(request):
    if request.method == 'POST':
        from contacts.forms import SendMessageForm
        f = SendMessageForm(request.POST)

        if not f.is_valid():
            raise ValueError(
                "SEND_MESSAGE: post request does not fit the SendMessageForm")

        message = f.cleaned_data['message']

        for recipiant in f.cleaned_data['single_recipiants']:
            print(f"SEND_MESSAGE: sending message to {recipiant}: '{message}'")
            send_message_to(recipiant, message)

        for group in f.cleaned_data['group_recipiants']:
            group: ContactList
            for recipiant in group.contacts.all():
                send_message_to(recipiant, message)

        return render(request, 'contacts/send_message.html', {'form': f})

    if request.method == 'GET':
        from contacts.forms import SendMessageForm
        f = SendMessageForm()
        return render(request, 'contacts/send_message.html', {'form': f})


def setup(request):
    global signal_bot
    context = {
        'is_signal_linked': is_signal_linked(),
        'is_bot_setup': is_signal_bot_setup(),
    }
    return render(request, 'contacts/signal_setup.html', context)
