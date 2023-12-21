from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from .models import Contact, ContactList
from .forms import ContactCreateForm, ContactListCreateForm


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