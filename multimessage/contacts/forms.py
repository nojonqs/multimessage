from contacts.models import Contact, Group
from contacts.signal_helper import get_linked_phone_numbers
from django import forms


class ContactCreateForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["display_name", "phone_number"]


class ContactListCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["display_name", "contacts"]


def get_linked_phone_numbers_as_dict():
    d = {n: n for n in get_linked_phone_numbers()}
    return d


class SendMessageForm(forms.Form):
    # TODO: make sender be a ModelChoiceField. This gives us a bit more
    # confidence in its existence and we do not have the overhead of
    # fetching all the connected phone numbers.
    # To do this, we need a model for connected phone numbers, create
    # them during signal setup and check for if they are still correct.
    # The last part is a big headache I think, so we work with strings
    # for now
    sender = forms.ChoiceField(choices=get_linked_phone_numbers_as_dict)
    message = forms.CharField(max_length=2048, widget=forms.Textarea)
    single_recipiants = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    group_recipiants = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
