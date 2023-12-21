from django.urls import path

from . import views

app_name = "contact"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:contact_id>/", views.detail, name='detail'),
    path("create/", views.ContactCreateView.as_view(), name='contact_create'),
    path("create_list/", views.ContactListCreateView.as_view(), name='list_create')
]