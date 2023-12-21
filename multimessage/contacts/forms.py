from django import forms
from .models import Contact, ContactList

class ContactCreateForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["display_name", "phone_number"]

class ContactListCreateForm(forms.ModelForm):
    class Meta:
        model = ContactList
        fields = ["display_name", "contacts"]