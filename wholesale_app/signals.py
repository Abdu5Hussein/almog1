from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from almogOil.models import OrderBuyinvoicetable,PreOrderItemsTable, PreOrderTable,SellInvoiceItemsTable, Mainitem,SellinvoiceTable
from .whatsapp_service import send_whatsapp_message_via_green_api
from .HozmaApi_views import Buyhandle_confirm_action
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from almogOil import models as almogOil_models
import logging
from decimal import Decimal
from almogOil.api_views import create_transactions_history_record

@receiver(post_save, sender=PreOrderItemsTable)
def check_and_confirm_preorder(sender, instance, **kwargs):
    print("Signal triggered for:", instance.autoid)
    preorder = instance.invoice_instance

    # Get all related items
    related_items = PreOrderItemsTable.objects.filter(invoice_instance=preorder)

    # If all items are processed, continue
    if all(item.quantity_proccessed for item in related_items):
        if preorder.shop_confrim:
            return  # Already confirmed

        client = preorder.client
        sell_invoice = almogOil_models.SellinvoiceTable.objects.create(
            invoice_no=preorder.invoice_no,
            client_obj=client,
            client_id=client.clientid,
            client_name=client.name,
            client_rate=client.category,
            client_category=client.subtype,
            client_limit=client.loan_limit,
            client_balance=preorder.client_balance,
            invoice_date=timezone.now(),
            invoice_status="لم تحضر",
            payment_status="اجل",
            for_who="حزمة",
            date_time=timezone.now(),
            price_status="",
            amount=preorder.amount,
            net_amount=preorder.net_amount,  # will be updated later
        )

        total_amount = 0

        for item in related_items:
            if item.confirm_quantity is None:
                item.confirm_quantity = item.quantity
                item.save()

            almogOil_models.SellInvoiceItemsTable.objects.create(
                invoice_instance=sell_invoice,
                invoice_no=preorder.invoice_no,
                item_no=item.item_no,
                pno=item.pno,
                main_cat=item.main_cat,
                sub_cat=item.sub_cat,
                name=item.name,
                company=item.company,
                company_no=item.company_no,
                quantity=item.confirm_quantity,
                date=timezone.now(),
                place=item.place,
                dinar_unit_price=item.dinar_unit_price,
                dinar_total_price=item.dinar_total_price,
                prev_quantity=item.prev_quantity,
                current_quantity=item.current_quantity,
            )

            total_amount += Decimal(item.dinar_total_price or 0)

# Safely handle discount and delivery_price
            discount = Decimal(preorder.client.discount or 0)
            delivery_price = Decimal(preorder.client.delivery_price or 0)

# Calculate net total
            net_Total = total_amount - (total_amount * discount) + delivery_price 

            try:
                mainitem = almogOil_models.Mainitem.objects.get(pno=item.pno)
                mainitem.itemvalue = max(mainitem.itemvalue - item.confirm_quantity, 0)
                mainitem.save()
            except almogOil_models.Mainitem.DoesNotExist:
                pass

        preorder.shop_confrim = True
        preorder.invoice_status = "تم شراءهن المورد"
        preorder.amount = total_amount
        preorder.net_amount = net_Total
        sell_invoice.net_amount = net_Total
        sell_invoice.amount = total_amount
        preorder.save()
        sell_invoice.save()
        transaction = f" {sell_invoice.invoice_no}فاتورة  بيع- رقم" ,
        details = f"تأكيد فاتورة بيع من اجل حزمة رقم {sell_invoice.invoice_no} من العميل {client.name}، بتاريخ {timezone.now().date()}، الكمية الإجمالية المؤكدة: {item.confirm_quantity }"
        create_transactions_history_record("client", client, "debit", sell_invoice.amount, transaction, details)

@receiver(post_save, sender=SellinvoiceTable)
def update_preorder_status_on_delivery(sender, instance, **kwargs):
    if instance.invoice_status == "سلمت":
        PreOrderTable.objects.filter(invoice_no=instance.invoice_no).update(invoice_status="جاري التوصيل")