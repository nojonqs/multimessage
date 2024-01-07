from typing import Any, Dict

from contacts.models import Contact, Group
from contacts.signal_helper import signal_cli_listAccounts
from django import forms
from phonenumber_field.formfields import PhoneNumberField


class ContactCreateForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["display_name", "phone_number"]


class ContactListCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["display_name", "contacts"]


def get_linked_phone_numbers_as_dict():
    d = {n: n for n in signal_cli_listAccounts()}
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
    message = forms.CharField(max_length=4096, widget=forms.Textarea)
    single_recipients = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    group_recipients = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )


class ContactInfoForm(forms.Form):
    phone_number = PhoneNumberField(max_length=32, required=False)
    uuid = forms.CharField(max_length=64, required=False)
    account = forms.ChoiceField(choices=get_linked_phone_numbers_as_dict, required=False)

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()

        if not any(cleaned_data.get(x, "") for x in ("phone_number", "uuid")):
            msg = "You must either enter a phone number or uuid."
            self._errors["phone_number"] = self.error_class([(msg)])
            self._errors["uuid"] = self.error_class([(msg)])

        return cleaned_data


