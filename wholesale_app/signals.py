from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from almogOil.models import OrderBuyinvoicetable
from .whatsapp_service import send_whatsapp_message_via_green_api


@receiver(post_save, sender=OrderBuyinvoicetable)
def send_whatsapp_after_save(sender, instance, created, **kwargs):
    if not instance.send and instance.source_obj and instance.source_obj.phone_number:
        phone_number = instance.source_obj.phone_number
        message = f"فاتورتك رقم {instance.invoice_no} من {instance.source} جاهزة. المبلغ الإجمالي: {instance.net_amount}."

        print(f"[Signal] Sending WhatsApp to {phone_number}: {message}")
        response = send_whatsapp_message_via_green_api(phone_number, message)

        if response:
            instance.send = True
            instance.send_date = timezone.now()
            instance.save(update_fields=["send", "send_date"])
            print(f"[Signal] ✅ WhatsApp sent and invoice updated: {instance.invoice_no}")
        else:
            print(f"[Signal] ❌ Failed to send WhatsApp for invoice: {instance.invoice_no}")
