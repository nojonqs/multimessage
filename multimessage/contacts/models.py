from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Contact(models.Model):
    display_name = models.CharField(max_length=64, null=False, blank=True)
    phone_number = PhoneNumberField(null=False, blank=False, unique=True)

    def __str__(self):
       return f"{self.display_name} ({self.phone_number})"


class Group(models.Model):
  display_name = models.CharField(max_length=64, null=False, blank=True)
  contacts = models.ManyToManyField(Contact)

  def __str__(self):
     return f"{self.display_name}"