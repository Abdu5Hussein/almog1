# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SellinvoiceTable,AllClientsTable
from .notifications import send_order_tracking_notification  # Import the new function

@receiver(post_save, sender=SellinvoiceTable)
def order_tracking_invoice_status_change_notification(sender, instance, **kwargs):
    """
    Sends a notification to the client whenever the invoice status is changed.
    """
    if instance.invoice_status and instance.pk:
        title = "Invoice Status Updated"
        body = f"Your invoice number {instance.invoice_no} status is now {instance.invoice_status}"

        # If client is a ForeignKey, access the clientid using 'instance.client.clientid'
        if instance.client_obj:
            client_id = instance.client_obj.clientid  # Accessing clientid from the ForeignKey object

            # Now filter AllClientsTable based on client_id
            user = AllClientsTable.objects.filter(clientid=client_id).first()

            if user and user.fcm_token:
                try:
                    # Call the function to send the notification
                    send_order_tracking_notification(user.fcm_token, title, body)
                except ValueError as e:
                    print(f"Error sending notification: {str(e)}")
            else:
                print(f"Client with ID '{client_id}' not found.")