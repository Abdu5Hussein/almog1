from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from almogOil.models import OrderBuyinvoicetable,PreOrderItemsTable, PreOrderTable,SellInvoiceItemsTable, Mainitem,SellinvoiceTable
from .whatsapp_service import send_whatsapp_message_via_green_api
from .HozmaApi_views import Buyhandle_confirm_action


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



@receiver(post_save, sender=PreOrderItemsTable)
def auto_distribute_and_confirm(sender, instance, **kwargs):
    pno = instance.pno

    try:
        main_item = Mainitem.objects.get(pno=pno)
        available_quantity = main_item.itemvalue

        # Get ALL relevant preorder items for this product, ordered by oldest invoice
        preorder_items = PreOrderItemsTable.objects.filter(
            pno=pno,
            confirm_quantity_=True,  # Only unconfirmed
            invoice_instance__shop_confrim=False
        ).select_related('invoice_instance').order_by('invoice_instance__autoid')

        # Allocate quantity
        for item in preorder_items:
            preorder = item.invoice_instance
            needed_qty = item.quantity

            if available_quantity <= 0:
                break

            alloc_qty = min(available_quantity, needed_qty)

            item.confirm_quantity = alloc_qty
            item.dinar_total_price = item.dinar_unit_price * alloc_qty
            item.save()

            available_quantity -= alloc_qty

        # Update Mainitem stock
        main_item.itemvalue = available_quantity
        main_item.save()

        # ✅ Try to fulfill preorders whose all items are now confirmed (even partially)
        preorder_ids = set(i.invoice_instance.autoid for i in preorder_items)

        for preorder_id in preorder_ids:
            preorder = PreOrderTable.objects.get(autoid=preorder_id)
            related_items = PreOrderItemsTable.objects.filter(invoice_instance=preorder)

            # Only fulfill if every item has confirm_quantity set
            if all(i.confirm_quantity is not None for i in related_items):
                client = preorder.client

                sell_invoice = SellinvoiceTable.objects.create(
                    invoice_no=preorder.invoice_no,
                    client_obj=client,
                    client_id=client.clientid,
                    client_name=client.name,
                    client_rate=client.category,
                    client_category=client.subtype,
                    client_limit=client.loan_limit,
                    client_balance=preorder.client_balance,
                    invoice_date=timezone.now(),
                    invoice_status="تم التوصيل",
                    payment_status="اجل",
                    for_who="حزمة",
                    date_time=timezone.now(),
                    price_status="",
                    amount=preorder.amount,
                )

                for i in related_items:
                    SellInvoiceItemsTable.objects.create(
                        invoice_instance=sell_invoice,
                        invoice_no=preorder.invoice_no,
                        item_no=i.item_no,
                        pno=i.pno,
                        main_cat=i.main_cat,
                        sub_cat=i.sub_cat,
                        name=i.name,
                        company=i.company,
                        company_no=i.company_no,
                        quantity=i.confirm_quantity,
                        date=timezone.now(),
                        place=i.place,
                        dinar_unit_price=i.dinar_unit_price,
                        dinar_total_price=i.dinar_total_price,
                        prev_quantity=i.prev_quantity,
                        current_quantity=i.current_quantity,
                    )

                preorder.shop_confrim = True
              
                preorder.save()

    except Mainitem.DoesNotExist:
        pass
