from django import template

from contacts.types import SignalContact
from contacts.signal_helper import get_contact_name as name

register = template.Library()

@register.simple_tag
def get_contact_name(contact: SignalContact):
    return name(contact)