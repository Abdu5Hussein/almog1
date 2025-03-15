from django.apps import AppConfig


class AlmogOilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'almogOil'

    def ready(self):
        # Schedule the background task when Django starts
        from almogOil.Tasks import schedule_assign_orders
        schedule_assign_orders()

        # Ensure signals are imported so that they register
        import almogOil.signals  # noqa
