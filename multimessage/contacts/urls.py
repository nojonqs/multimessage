from django.urls import path
from contacts.views import send_message_view, setup_view

from django.views.generic import RedirectView

from . import views

app_name = "contact"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:contact_id>/", views.detail, name='detail'),
    path("create/", views.ContactCreateView.as_view(), name='contact_create'),
    path("create_list/", views.ContactListCreateView.as_view(), name='list_create'),
    path("overview/contacts/", views.ContactOverview.as_view(), name="contact_overview"),
    path("overview/groups/", views.GroupOverview.as_view(), name="group_overview"),

    path("send_message/", send_message_view, name="signal_send_message"),
    path("setup/", setup_view, name="signal_setup"),
    path("link_device_qrcode/", RedirectView.as_view(url="http://127.0.0.1:8080/v1/qrcodelink/?device_name=multi_message"), name="signal_link_device_qrcode"),
]