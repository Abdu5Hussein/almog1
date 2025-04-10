from django.apps import AppConfig
from .firebase_config import initialize_firebase

class AlmogOilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'almogOil'

    def ready(self):
        initialize_firebase()  # Ensure Firebase is initialized
        import almogOil.signals  # Ensure signals are connected
