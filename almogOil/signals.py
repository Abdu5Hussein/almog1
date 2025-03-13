# notifications/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import SellInvoiceItemsTable  # Adjust the import if your model is elsewhere

@receiver(post_save, sender=SellInvoiceItemsTable)
def notify_invoice_status_change(sender, instance, created, **kwargs):
    # You might choose not to send a notification on creation,
    # or you could add extra logic here if needed.
    if created:
        return

    # If you want to notify only when a particular field changes,
    # you could compare the previous value to the new value.
    # For now, we notify every time the record is updated.
    channel_layer = get_channel_layer()
    message = f"Invoice item {instance.pk} has been updated."
    
    # Send the notification to the group 'notifications'
    async_to_sync(channel_layer.group_send)(
        "notifications",  # This should match the group name in your consumer
        {
            "type": "send_notification",  # This maps to a method in your consumer
            "message": message,
        }
    )
