from django.apps import AppConfig
from .firebase_config import initialize_firebase

class AlmogOilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'almogOil'

    def ready(self):
        # ✅ Initialize Firebase
        initialize_firebase()

        # ✅ Schedule order assignments (your existing task)
        from almogOil.Tasks import schedule_assign_orders
        schedule_assign_orders()

        # ✅ Start WhatsApp message scheduler
        from wholesale_app.scheduler import start_scheduler  # <-- Make sure this matches your filename
        start_scheduler()

        # ✅ Register Django signals
        import almogOil.signals  # noqa
