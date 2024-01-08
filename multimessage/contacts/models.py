from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Contact(models.Model):
    display_name = models.CharField(max_length=64, null=False, blank=True)
    phone_number = PhoneNumberField(null=False, blank=False)
    uuid = models.CharField(max_length=64, null=False, blank=True, unique=True)

    @property
    def international_number(self):
        return self.phone_number.as_international

    def save(self, *args, **kwargs):
        if not self.uuid:
            from contacts.signal_helper import get_uuid_for_number
            self.uuid = get_uuid_for_number(self.international_number)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.display_name}, {self.international_number} ({self.uuid})"


class Group(models.Model):
    display_name = models.CharField(max_length=64, null=False, blank=True)
    contacts = models.ManyToManyField(Contact)

    def __str__(self):
        return f"{self.display_name}"
