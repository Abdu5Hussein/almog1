# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SellinvoiceTable,AllClientsTable
from .notifications import send_order_tracking_notification , send_order_assigned_notification# Import the new function
from .models import SellinvoiceTable, EmployeeQueue,EmployeesTable
from .Tasks import assign_orders

@receiver(post_save, sender=SellinvoiceTable)
def handle_order_creation(sender, instance, created, **kwargs):
    if created:
        # Example: Automatically assign orders when a new one is created
        assign_orders() 
        
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


@receiver(post_save, sender=EmployeeQueue)
def order_assigned_notification(sender, instance, created, **kwargs):
    """
    Sends a notification to the employee whenever an order is assigned to them.
    """
    if instance.is_assigned:  # Check if the order is assigned
        title = "Order Assigned"
        body = f"An order has been assigned to you. Go directly to the warehouse."

        # Fetch the employee using the ForeignKey relationship
        if instance.employee:
            employee = instance.employee  # Accessing the employee object

            # Now directly access the employee's fcm_token
            if employee.fcm_token:
                try:
                    # Send notification to the employee
                    send_order_assigned_notification(employee.fcm_token, title, body)
                except ValueError as e:
                    print(f"Error sending notification: {str(e)}")
            else:
                print(f"Employee with ID '{employee.employee_id}' does not have an FCM token.")

