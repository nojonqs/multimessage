from django.apps import AppConfig
from .signal_helper import setup_signal_bot_if_device_linked

class ContactsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contacts'

    def ready(self) -> None:
        setup_signal_bot_if_device_linked()
        
        return super().ready()
