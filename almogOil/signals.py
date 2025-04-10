# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SellinvoiceTable,AllClientsTable
from .notifications import send_order_tracking_notification , send_order_assigned_notification# Import the new function
from .models import SellinvoiceTable, EmployeeQueue,EmployeesTable
from .Tasks import assign_orders

@receiver(post_save, sender=SellinvoiceTable)
def handle_order_creation(sender, instance, created, **kwargs):
    print("✅ Signal for invoice creation triggered")
    
    if created:
        print(f"New invoice created with ID: {instance.pk}. Automatically assigning orders...")
        # Example: Automatically assign orders when a new one is created
        assign_orders()

@receiver(post_save, sender=SellinvoiceTable)
def order_tracking_invoice_status_change_notification(sender, instance, **kwargs):
    """
    Sends a notification to the client whenever the invoice status is changed.
    """
    print(f"✅ Signal for invoice status change triggered for invoice: {instance.pk}")

    if instance.invoice_status and instance.pk:
        print(f"Invoice status has changed. Current status: {instance.invoice_status}")

        title = "Invoice Status Updated"
        body = f"Your invoice number {instance.invoice_no} status is now {instance.invoice_status}"

        # If client is a ForeignKey, access the clientid using 'instance.client.clientid'
        if instance.client_obj:
            client_id = instance.client_obj.clientid  # Accessing clientid from the ForeignKey object
            print(f"Client ID: {client_id}")

            # Now filter AllClientsTable based on client_id
            user = AllClientsTable.objects.filter(clientid=client_id).first()

            if user:
                print(f"Client found: {user.clientid}. Checking FCM token...")
                if user.fcm_token:
                    print(f"Client has valid FCM token. Sending notification...")
                    try:
                        # Call the function to send the notification
                        send_order_tracking_notification(user.fcm_token, title, body)
                        print(f"Notification sent to client with ID: {client_id}")
                    except ValueError as e:
                        print(f"Error sending notification: {str(e)}")
                else:
                    print(f"Client with ID '{client_id}' does not have a valid FCM token.")
            else:
                print(f"Client with ID '{client_id}' not found in AllClientsTable.")

@receiver(post_save, sender=EmployeeQueue)
def order_assigned_notification(sender, instance, created, **kwargs):
    """
    Sends a notification to the employee whenever an order is assigned to them.
    """
    print(f"✅ Signal for order assignment triggered for employee queue entry: {instance.pk}")

    if instance.is_assigned:  # Check if the order is assigned
        print(f"Order assigned status is True. Sending notification to employee.")

        title = "Order Assigned"
        body = f"An order has been assigned to you. Go directly to the warehouse."

        # Fetch the employee using the ForeignKey relationship
        if instance.employee:
            employee = instance.employee  # Accessing the employee object
            print(f"Employee found: {employee.employee_id}. Checking FCM token...")

            # Now directly access the employee's fcm_token
            if employee.fcm_token:
                print(f"Employee has valid FCM token. Sending notification...")
                try:
                    # Send notification to the employee
                    send_order_assigned_notification(employee.fcm_token, title, body)
                    print(f"Notification sent to employee with ID: {employee.employee_id}")
                except ValueError as e:
                    print(f"Error sending notification: {str(e)}")
            else:
                print(f"Employee with ID '{employee.employee_id}' does not have a valid FCM token.")
        else:
            print(f"No employee found for EmployeeQueue entry with ID: {instance.pk}")