from django.apps import AppConfig
import asyncio

class ContactsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contacts'

    def ready(self) -> None:
        return super().ready()
