from django.apps import AppConfig
import asyncio

class ContactsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contacts'

    def ready(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        return super().ready()
