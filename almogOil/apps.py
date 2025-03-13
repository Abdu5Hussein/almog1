from django.apps import AppConfig


class AlmogOilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'almogOil'

    def ready(self):
        from almogOil.Tasks import schedule_assign_orders
        schedule_assign_orders()  # Ensure the task is scheduled when Django starts