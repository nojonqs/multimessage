from django.urls import path
from .signal_helper import send_message, register

from django.views.generic import RedirectView

from . import views

app_name = "contact"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:contact_id>/", views.detail, name='detail'),
    path("create/", views.ContactCreateView.as_view(), name='contact_create'),
    path("create_list/", views.ContactListCreateView.as_view(), name='list_create'),

    # TODO: Fix address and port hardcoding
    # TODO: Make device name user chosen
    path("signal_link_device", RedirectView.as_view(url="http://127.0.0.1:8080/v1/qrcodelink/?device_name=multi_message"), name="signal_link_device"),
    path("signal_send_message", send_message, name="signal_send_message"),
    path("signal_setup_bot", register, name="signal_setup_bot"),
]