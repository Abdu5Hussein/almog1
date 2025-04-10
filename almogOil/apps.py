from django.apps import AppConfig
from .firebase_config import initialize_firebase

class AlmogOilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'almogOil'

    def ready(self):
        # ✅ Initialize Firebase
        initialize_firebase()

        # ✅ Schedule background task
        from almogOil.Tasks import schedule_assign_orders
        schedule_assign_orders()

        # ✅ Register signals
        import almogOil.signals  # noqa
