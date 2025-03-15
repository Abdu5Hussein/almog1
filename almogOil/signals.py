from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import SellinvoiceTable  # Adjust as needed

@receiver(post_save, sender=SellinvoiceTable)
def notify_invoice_status_change(sender, instance, created, **kwargs):
    if created:
        return  # Optionally skip notification on creation

    # Use the 'client' field from the model as the identifier.
    client_id = instance.client
    if not client_id:
        return  # If there's no client identifier, don't send a notification

    # Group name for this client
    room_group_name = f'user_{client_id}'
    message = f"تم تحديث حالة الفاتورة رقم {instance.invoice_no} إلى {instance.invoice_status}."

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": "send_notification",
            "message": message,
        }
    )