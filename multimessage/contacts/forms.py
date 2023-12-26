from django import forms
from contacts.models import Contact, ContactList
from contacts.signal_helper import get_linked_phone_numbers

class ContactCreateForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["display_name", "phone_number"]

class ContactListCreateForm(forms.ModelForm):
    class Meta:
        model = ContactList
        fields = ["display_name", "contacts"]

def get_linked_phone_numbers_as_dict():
    d = {n: n for n in get_linked_phone_numbers()}
    return d

class SendMessageForm(forms.Form):
    sender = forms.ChoiceField(choices=get_linked_phone_numbers_as_dict)
    message = forms.CharField(max_length=2048, widget=forms.Textarea)
    single_recipiants = forms.ModelMultipleChoiceField(queryset=Contact.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    group_recipiants = forms.ModelMultipleChoiceField(queryset=ContactList.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)