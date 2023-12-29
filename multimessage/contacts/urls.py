from django.urls import path
from django.urls import reverse_lazy
from contacts.views import link_device, send_message_view, setup_view

from django.views.generic import RedirectView

from . import views

app_name = "contact"
urlpatterns = [
    path(
        "", RedirectView.as_view(pattern_name="contact:contact_overview"), name="index"
    ),
    path("create/", views.ContactCreateView.as_view(), name="contact_create"),
    path("create_group/", views.GroupCreateView.as_view(), name="group_create"),
    path(
        "overview/contacts/", views.ContactOverview.as_view(), name="contact_overview"
    ),
    path("overview/groups/", views.GroupOverview.as_view(), name="group_overview"),
    path(
        "delete/contact/<int:pk>/",
        views.ContactDeleteView.as_view(),
        name="contact_delete",
    ),
    path(
        "delete/group/<int:pk>/", views.GroupDeleteView.as_view(), name="group_delete"
    ),
    path("send_message/", send_message_view, name="signal_send_message"),
    path("setup/", setup_view, name="signal_setup"),
    path("link_device_qrcode/", link_device, name="signal_link_device_qrcode"),
]
