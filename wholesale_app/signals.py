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



