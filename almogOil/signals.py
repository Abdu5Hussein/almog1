from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import SellinvoiceTable, AllClientsTable, EmployeeQueue
from .notifications import send_order_tracking_notification, send_order_assigned_notification
from django.db import transaction
# Temporary cache for invoice status before saving
_previous_invoice_status = {}

@receiver(pre_save, sender=SellinvoiceTable)
def cache_previous_status(sender, instance, **kwargs):
    try:
        original = SellinvoiceTable.objects.get(pk=instance.pk)
        _previous_invoice_status[instance.pk] = original.invoice_status
    except SellinvoiceTable.DoesNotExist:
        _previous_invoice_status[instance.pk] = None


@receiver(post_save, sender=SellinvoiceTable)
def order_tracking_invoice_status_change_notification(sender, instance, created, **kwargs):
    """
    Sends a notification to the client whenever the invoice status is changed.
    """
    print(f"✅ Signal for invoice status change triggered for invoice: {instance.pk}")

    if not created:
        previous_status = _previous_invoice_status.get(instance.pk)
        if previous_status != instance.invoice_status:
            print(f"Invoice status has changed: {previous_status} → {instance.invoice_status}")

            title = "تم تحديث حالة الفاتورة"
            body = f"فاتورتك رقم {instance.invoice_no} تم تحديث حالتها إلى: {instance.invoice_status}"

            if instance.client_obj:
                client = instance.client_obj
                print(f"Client ID: {client.clientid}")

                if client.fcm_token:
                    print(f"Sending notification to client FCM token...")
                    try:
                        send_order_tracking_notification(client.fcm_token, title, body)
                        print(f"✅ Notification sent to client {client.clientid}")
                    except ValueError as e:
                        print(f"❌ Error sending notification: {str(e)}")
                else:
                    print(f"❌ Client {client.clientid} has no FCM token.")
            else:
                print("❌ No client linked to this invoice.")
        else:
            print("ℹ️ Invoice status has not changed — no notification sent.")


@receiver(post_save, sender=EmployeeQueue)
def order_assigned_notification(sender, instance, created, **kwargs):
    """
    Sends a notification to the employee whenever an order is assigned to them.
    """
    print(f"✅ Signal for order assignment triggered for employee queue entry: {instance.pk}")

    if instance.is_assigned and instance.employee:
        employee = instance.employee
        print(f"Employee ID: {employee.employee_id}")

        if employee.fcm_token:
            title = "تم تعيين الطلب"
            body = "تم تعيين طلب جديد لك. الرجاء التوجه مباشرة إلى المخزن."
            try:
                send_order_assigned_notification(employee.fcm_token, title, body)
                print(f"✅ Notification sent to employee {employee.employee_id}")
            except ValueError as e:
                print(f"❌ Error sending notification: {str(e)}")
        else:
            print(f"❌ Employee {employee.employee_id} has no FCM token.")


from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()