from contacts.views import (get_uuid_for_number, import_group_from_signalcli,
                            info_about_contact, link_device, list_contacts,
                            list_identities_view, send_message_view,
                            setup_view,
                            sync_contacts_groups_from_primarydevice)
from django.urls import path
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
    path("link_device_qrcode/<str:qrcode_uri>/", link_device, name="signal_link_device_qrcode"),
    path(
        "signal/fetch_groups/<str:account>/",
        views.fetch_group_view,
        name="signal_fetch_groups",
    ),
    path("list_contacts/", list_contacts, name="listContacts"),
    path("uuid/<str:phone_number>/", get_uuid_for_number),
    path("import_group_from_signalcli/<str:account>/<path:signal_group_id>/", import_group_from_signalcli, name="import_group_from_signalcli"),
    path("info_about_contact/", info_about_contact, name="info_about_contact"),
    path("sync/<str:account>/", sync_contacts_groups_from_primarydevice, name="sync_with_primary"),
    path("list_identities/<str:account>/", list_identities_view, name="list_identities"),
]
