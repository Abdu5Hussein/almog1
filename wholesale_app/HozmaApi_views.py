from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import json
import random
import re
import difflib
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Count, Sum, Avg, F, Q, Exists, Case,DecimalField, When, OuterRef,Value,FloatField,  ExpressionWrapper, DurationField,CharField ,Min,Max,StdDev
from django.db.models.functions import TruncMonth, TruncDay
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import F, Q, Sum, IntegerField
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.dispatch import receiver
from rest_framework.decorators import action
from django.db import transaction
from .pagination import StandardResultsSetPagination
from django_q.tasks import async_task
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.exceptions import ValidationError
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework import generics, mixins,viewsets
from rest_framework import viewsets, status
from rest_framework.response import Response
from decimal import Decimal
from io import BytesIO
from almogOil import models as almogOil_models
from wholesale_app import models as hozma_models
from almogOil import serializers as almogOil_serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from almogOil.authentication import CookieAuthentication
from drf_spectacular.utils import extend_schema_view,extend_schema,OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes, OpenApiSchemaBase
from .whatsapp_service import send_whatsapp_message_via_green_api ,send_excel_file_greenapi_upload
from wholesale_app import serializers as wholesale_serializers
import xlsxwriter
from num2words import num2words
from products import serializers as products_serializers
import hashlib
from django.core.cache import cache
from django.core.paginator import Paginator
from dateutil.relativedelta import relativedelta
from almogOil.api_views import create_transactions_history_record, filter_fields, post_to_print_server

CACHE_TTL = 60 * 5   # 5 دقائق

def get_last_PreOrderTable_no():
    last_preorder = almogOil_models.PreOrderTable.objects.order_by("-invoice_no").first()
    last_sell = almogOil_models.SellinvoiceTable.objects.order_by("-invoice_no").first()

    last_preorder_no = last_preorder.invoice_no if last_preorder else 0
    last_sell_no = last_sell.invoice_no if last_sell else 0

    # Get the maximum of the two and add 1 to ensure uniqueness
    next_unique_invoice_no = max(last_preorder_no, last_sell_no) + 1

    return next_unique_invoice_no

def get_next_buy_invoice_no():
    last_buy = almogOil_models.Buyinvoicetable.objects.order_by("-invoice_no").first()
    last_order_buy = almogOil_models.OrderBuyinvoicetable.objects.order_by("-invoice_no").first()

    last_buy_no = last_buy.invoice_no if last_buy else 0
    last_order_buy_no = last_order_buy.invoice_no if last_order_buy else 0

    return max(last_buy_no, last_order_buy_no) + 1


@extend_schema(
    description="""create a new pre-order item""",
    tags=["PreOrder", "PreOrder Items"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def create_pre_order(request):
    if request.method != "POST":
        return Response({"error": "Invalid HTTP method. Only POST is allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        data = request.data
        client_identifier = data.get("client")
        if not client_identifier:
            return Response({"success": False, "error": "Client is null"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch client
        try:
            if str(client_identifier).isdigit():
                client_obj = almogOil_models.AllClientsTable.objects.get(clientid=int(client_identifier))
            else:
                client_obj = almogOil_models.AllClientsTable.objects.get(name=client_identifier)

            balance_data = almogOil_models.TransactionsHistoryTable.objects.filter(client_object_id=client_obj.clientid).aggregate(
                total_debt=Sum('debt') or Decimal("0.0000"),
                total_credit=Sum('credit') or Decimal("0.0000")
            )
        except almogOil_models.AllClientsTable.DoesNotExist:
            return Response({"success": False, "error": "Client not found"}, status=status.HTTP_400_BAD_REQUEST)

        total_debt = balance_data.get('total_debt') or Decimal('0.0000')
        total_credit = balance_data.get('total_credit') or Decimal('0.0000')
        client_balance = total_credit - total_debt

        # Preferably refactor this function
        last_receipt_no = get_last_PreOrderTable_no() + 1

        for_who = "application" if data.get("for_who") == "application" else None

        invoice_data = {
            'invoice_no': last_receipt_no,
            'client': client_obj.clientid,
            'client_id': client_obj.clientid,
            'client_name': client_obj.name,
            'client_rate': client_obj.category,
            'client_category': client_obj.subtype,
            'client_limit': client_obj.loan_limit,
            'client_balance': client_balance,
            'invoice_date': timezone.now(),
            'invoice_status': "لم تشتري",
            'payment_status': data.get("payment_status"),
            'for_who': for_who,
            'date_time': timezone.now(),
            'price_status': "",
            'mobile': data.get("mobile") if data.get("mobile") else False,
        }

        serializer = almogOil_serializers.PreOrderSerializer(data=invoice_data)
        if serializer.is_valid():
            serializer.save()
            async_task('almogOil.Tasks.assign_orders')

            return Response({
                "success": True,
                "message": "Sell invoice created and order assignment triggered!",
                "invoice_no": serializer.instance.invoice_no,
                "client_balance": serializer.instance.client_balance
            }, status=status.HTTP_201_CREATED)

        return Response({"success": False, "error": serializer.errors,"last_receipt_no":last_receipt_no}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@extend_schema(
description="""get last pre order invoice number""",
tags=["PreOrder", "PreOrder last invoice number"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_sellinvoice_no(request):
    try:
        # Get the last autoid by ordering the table by invoice_no in descending order
        last_invoice = almogOil_models.PreOrderTable.objects.order_by('-invoice_no').first()
        if last_invoice:
            return Response({'autoid': last_invoice.invoice_no}, status=status.HTTP_200_OK)
        else:
            # Handle the case where the table is empty
            return Response({'autoid': 0, 'message': 'No invoices found'}, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
"""

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def Sell_invoice_create_item(request):
    if request.method == "POST":
        try:
            data = request.data

            # Validate required fields
            required_fields = ["pno", "fileid", "invoice_id", "itemvalue", "sellprice"]
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Get the related product
            try:
                product = almogOil_models.Mainitem.objects.get(pno=data.get("pno"), fileid=data.get("fileid"))
            except almogOil_models.Mainitem.DoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get the related source information (ForeignKey relationship)
            source_phone = product.source.mobile if product.source and product.source.mobile else "218942434823"

            # Get the related invoice and update its amount
            try:
                invoice = almogOil_models.PreOrderTable.objects.get(invoice_no=data.get("invoice_id"))
                invoice.amount += (Decimal(product.buyprice or 0) * Decimal(data.get("itemvalue") or 0))
                invoice.save()
            except almogOil_models.PreOrderTable.DoesNotExist:
                return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if sufficient quantity exists
            item_value = int(data.get("itemvalue") or 0)

            # Prepare the data for creating a new SellInvoiceItemsTable instance
            item_data = {
                'invoice_instance': invoice.autoid,
                'invoice_no': data.get("invoice_id"),
                'item_no': product.oem_numbers,
                'pno': data.get("pno"),
                'main_cat': product.itemmain,
                'sub_cat': product.itemsubmain,
                'name': product.itemname,
                'company': product.companyproduct,
                'company_no': product.replaceno,
                'quantity': item_value,
                'date': timezone.now(),
                'place': product.itemplace,
                'dinar_unit_price': Decimal(product.buyprice or 0),
                'dinar_total_price': Decimal(product.buyprice or 0) * item_value,
                'prev_quantity': product.itemvalue,
                'current_quantity': product.itemvalue - item_value,
            }

            # Use serializer to create the SellInvoiceItemsTable record
            serializer = almogOil_serializers.PreOrderItemsSerializer(data=item_data)
            if serializer.is_valid():
                serializer.save()

                # Send WhatsApp message to the source after successfully adding the item
                message_body = f"New item {product.itemname} has been added to invoice {data.get('invoice_id')}. Quantity: {item_value}."
                response = send_whatsapp_message_via_green_api(source_phone, message_body)

                if response and "idMessage" in response:
                    # Successfully sent message
                    return Response({
                        "message": "Item created successfully and message sent",
                        "item_id": serializer.instance.autoid,
                        "confirm_status": "confirmed",
                        "phone_number": source_phone  # Include the phone number that the message was sent to
                    }, status=status.HTTP_201_CREATED)
                else:
                    # If message sending failed
                    return Response({
                        "message": "Item created successfully, but failed to send WhatsApp message.",
                        "phone_number": source_phone  # Include the phone number in the response even if the message fails
                    }, status=status.HTTP_201_CREATED)

            # If serializer is not valid, return the errors
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Invalid HTTP method. Only POST is allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
"""

@extend_schema(
    description="""Confirm PreOrder items into SellInvoice and move to SellInvoiceMainItem,
                   or update quantity of PreOrder items if specified.
                   Also provides the ability to confirm without any changes to quantity.""",
    tags=["PreOrder", "Confirm PreOrder Items"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def confirm_or_update_preorder_items(request):
    if not request.user.has_perm('almogOil.hozma_BuyInvoices'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        data = request.data
        invoice_no = data.get('invoice_no')

        if not invoice_no:
            return Response({"error": "Missing invoice_no"}, status=status.HTTP_400_BAD_REQUEST)

        # Get PreOrder for the given invoice
        preorder = almogOil_models.PreOrderTable.objects.filter(invoice_no=invoice_no).first()

        if not preorder:
            return Response({"error": "No PreOrder found for this invoice"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the PreOrder is already confirmed
        if preorder.shop_confrim:
            return Response({"error": "This PreOrder has already been confirmed and cannot be modified."}, status=status.HTTP_400_BAD_REQUEST)

        # Option to update quantity or confirm the order (optional fields)
        item_quantities = data.get("item_quantities", [])
        action_type = data.get("action_type", "confirm")  # Default to 'confirm', other option is 'update'

        # Process the 'update' action first
        if action_type == "update":
            return buyhandle_update_action(preorder, item_quantities)

        # Process the 'confirm' action
        elif action_type == "confirm":
            return handle_confirm_action(preorder)

        else:
            return Response({"error": "Invalid action_type. Use 'confirm' or 'update'."}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def buyhandle_update_action(preorder, item_quantities):
    # Update the quantity for specified items
    preorder_items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance=preorder.autoid)

    for item in item_quantities:
        item_no = item.get("item_no")  # Ensure we are using item_no from the request JSON
        new_quantity = item.get("new_quantity")

        if not item_no or new_quantity is None:
            continue  # Skip if item_no or new_quantity is not provided

        # Check if the item exists in the PreOrderItemsTable using pno
        preorder_item = preorder_items.filter(pno=item_no).first()  # Now using item_no from the request JSON

        if not preorder_item:
            return Response({"error": f"Item with pno {item_no} is not part of this PreOrder."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the quantity in PreOrderItemsTable
        preorder_item.confirm_quantity = new_quantity
        preorder_item.dinar_total_price = preorder_item.dinar_unit_price * new_quantity  # Recalculate the total price
        preorder_item.save()

    # After updating the quantities for all items, recalculate the total amount for the PreOrder
    total_amount = sum([item.dinar_total_price for item in preorder_items])  # Sum the dinar_total_price of all items

    # Update the total amount in PreOrderTable
    preorder.amount = total_amount
    preorder.save()

    return Response({"success": True, "message": "PreOrder items updated with new quantities."}, status=status.HTTP_200_OK)


def handle_confirm_action(preorder):

    # Confirm the PreOrder and move items to SellInvoiceMainItem
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
        invoice_status="تم التوصيل",
        payment_status="اجل",  # or use the actual status from the PreOrder
        for_who="حزمة",  # You can change based on your logic
        date_time=timezone.now(),
        price_status="",

        amount=preorder.amount,
    )

    # Process the preorder items and move them to SellInvoiceItemsTable
    preorder_items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance=preorder.autoid)
    for item in preorder_items:
        # Check if confirm_quantity is None (not set), then set it to the original quantity
        if item.confirm_quantity is None:
            item.confirm_quantity = item.quantity  # Set confirm_quantity to the original quantity
            item.save()  # Save the updated PreOrderItemsTable

        # Now send the confirmed quantity to SellInvoiceItemsTable
        almogOil_models.SellInvoiceItemsTable.objects.create(
            invoice_instance=sell_invoice,
            invoice_no=preorder.invoice_no,
            item_no=item.oem_numbers,
            pno=item.pno,
            main_cat=item.main_cat,
            sub_cat=item.sub_cat,
            name=item.name,
            company=item.company,
            company_no=item.company_no,
            quantity=item.confirm_quantity,  # Use confirm_quantity here
            date=timezone.now(),
            place=item.place,
            dinar_unit_price=item.dinar_unit_price,
            dinar_total_price=item.dinar_total_price,
            prev_quantity=item.prev_quantity,
            current_quantity=item.current_quantity,
        )

        # Update Mainitem quantity after confirming the order
        try:
            mainitem = almogOil_models.Mainitem.objects.get(pno=item.pno)
            mainitem.itemvalue = max(mainitem.itemvalue - item.confirm_quantity, 0)  # Use confirm_quantity here
            mainitem.save()
        except almogOil_models.Mainitem.DoesNotExist:
            pass

    # Mark the PreOrder as confirmed
    preorder.shop_confrim = True
    preorder.save()

    return Response({"success": True, "message": "PreOrder items confirmed and moved to SellInvoice."}, status=status.HTTP_200_OK)
"""
@api_view(["POST"])
@permission_classes([IsAuthenticated])  # Allow access for any user
@authentication_classes([CookieAuthentication])  # No authentication required for this view
def send_test_whatsapp_message(request):

    try:
        # Extract 'to' and 'body' from the request data
        to = request.data.get('to')
        body = request.data.get('body')

        # Validate input
        if not to or not body:
            return Response(
                {'error': 'Both "to" and "body" are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Call the Green API to send the message
        result = send_whatsapp_message_via_green_api(to, body)

        # Check if the API call was successful
        if result:
            return Response(
                {'success': True, 'response': result},
                status=status.HTTP_200_OK
            )
        else:
            # Return an error if the message could not be sent
            return Response(
                {'success': False, 'message': 'Failed to send message.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        # Catch any unexpected exceptions and return an internal server error
        return Response(
            {'success': False, 'message': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
"""
 # Assuming you have this function

from django.db import transaction

from django.db import transaction
"""
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def full_Sell_invoice_create_item(request):
    if request.method != "POST":
        return Response({"error": "Invalid HTTP method. Only POST is allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = request.data
    required_fields = ["pno", "fileid", "invoice_id", "itemvalue", "sellprice"]
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

    invoice_id = data.get("invoice_id")

    try:
        with transaction.atomic():
            # Lock product row
            try:
                product = almogOil_models.Mainitem.objects.select_for_update().get(
                    pno=data.get("pno"),
                    fileid=data.get("fileid")
                )
            except almogOil_models.Mainitem.DoesNotExist:
                raise ValueError("Product not found")

            item_value = int(data.get("itemvalue") or 0)
            if item_value > product.showed:
                raise ValueError("Insufficient quantity available")

            try:
                invoice = almogOil_models.PreOrderTable.objects.select_for_update().get(invoice_no=invoice_id)
            except almogOil_models.PreOrderTable.DoesNotExist:
                raise ValueError("Invoice not found")

            # Update invoice
            buy_price = Decimal(product.buyprice or 0)
            line_total = buy_price * item_value
            invoice.amount += line_total
            discount = Decimal(invoice.client.discount or 0)
            delivery_price = Decimal(invoice.client.delivery_price or 0)
            invoice.net_amount = invoice.amount - (discount * invoice.amount) + delivery_price
            invoice.save()

            # Update product quantity
            product.showed -= item_value
            product.save()

            dinar_total_price = buy_price * item_value
            item_data = {
                'invoice_instance': invoice.autoid,
                'invoice_no': invoice_id,
                'item_no': product.oem_numbers,
                'pno': data.get("pno"),
                'main_cat': product.itemmain,
                'sub_cat': product.itemsubmain,
                'name': product.itemname,
                'company': product.companyproduct,
                'company_no': product.replaceno,
                'quantity': item_value,
                'date': timezone.now(),
                'place': product.itemplace,
                'dinar_unit_price': product.buyprice,
                'dinar_total_price': dinar_total_price,
                'prev_quantity': product.showed + item_value,
                "remaining": 0,
                "returned": 0,
                'current_quantity': product.showed,
            }

            serializer = almogOil_serializers.PreOrderItemsSerializer(data=item_data)
            if not serializer.is_valid():
                # Ensure rollback
                transaction.set_rollback(True)
                raise ValueError(serializer.errors)

            serializer.save()

            # === Buy Invoice ===
            source_name = product.source.name if product.source else "Unknown"
            source_obj = product.source
            buyitem_value = item_value
            cost_price = Decimal(product.costprice or 0)
            buy_dinar_total_price = cost_price * buyitem_value

            buy_invoice = almogOil_models.OrderBuyinvoicetable.objects.filter(
                source=source_name,
                send=False,
                confirmed=False
            ).first()

            if not buy_invoice:
                buy_invoice = almogOil_models.OrderBuyinvoicetable.objects.create(
                    source=source_name,
                    invoice_date=timezone.now(),
                    amount=0,
                    net_amount=0,
                    invoice_no=int(timezone.now().timestamp()),
                    source_obj=product.source
                )

            buy_invoice.related_preorders.add(invoice)

            existing_buy_item = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(
                invoice_no=buy_invoice,
                pno=product.pno
            ).first()

            if existing_buy_item:
                new_total_quantity = existing_buy_item.Asked_quantity + item_value
                existing_buy_item.Asked_quantity = new_total_quantity
                existing_buy_item.dinar_total_price = new_total_quantity * buy_price
                existing_buy_item.cost_total_price = new_total_quantity * cost_price
                existing_buy_item.invoice_no2 = buy_invoice.invoice_no
                existing_buy_item.date = timezone.now().date()
                existing_buy_item.prev_quantity = product.itemvalue
                existing_buy_item.main_cat = product.itemmain
                existing_buy_item.sub_cat = product.itemsubmain
                existing_buy_item.source = source_obj
                existing_buy_item.save()
            else:
                almogOil_models.OrderBuyInvoiceItemsTable.objects.create(
                    item_no=product.oem_numbers,
                    pno=product.pno,
                    oem=product.oem_numbers,
                    sourrce_pno=product.source_pno,
                    name=product.itemname,
                    company=product.companyproduct,
                    company_no=product.replaceno,
                    Asked_quantity=buyitem_value,
                    date=timezone.now().date(),
                    quantity_unit="",
                    dinar_unit_price=product.costprice,
                    dinar_total_price=buyitem_value * cost_price,
                    cost_unit_price=cost_price,
                    cost_total_price=buyitem_value * cost_price,
                    prev_quantity=product.itemvalue,
                    current_buy_price=product.buyprice,
                    invoice_no2=buy_invoice.invoice_no,
                    invoice_no=buy_invoice,
                    main_cat=product.itemmain,
                    sub_cat=product.itemsubmain,
                    source=source_obj
                )

            buy_invoice.amount += buy_dinar_total_price
            buy_invoice.net_amount = buy_invoice.amount
            buy_invoice.save()

            # Optional WhatsApp
            client_phone = invoice.client.mobile
            message_body = (
                f"👋 مرحبًا، تمت إضافة المنتج ({product.itemname}) إلى فاتورتك رقم {invoice_id}.\n"
                f"الكمية: {item_value}\n"
                f"السعر للوحدة: {product.buyprice}\n"
                f"الإجمالي: {dinar_total_price}\n"
                f"📦 شكراً لتعاملك معنا!"
            )
            send_whatsapp_message_via_green_api(client_phone, message_body)

            return Response({
                "message": "Item created successfully.",
                "item_id": serializer.instance.autoid,
                "phone_number": client_phone,
                "buy_invoice_send": buy_invoice.send,
                "confirmation": buy_invoice.confirmed,
                "buy_invoice_id": buy_invoice.invoice_no,
                "source_name": source_name,
                "left item": product.showed
            }, status=status.HTTP_201_CREATED)

    except ValueError as ve:
        return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Optional: delete invoice if you know it's a temporary/test invoice
        almogOil_models.PreOrderTable.objects.filter(invoice_no=invoice_id).delete()
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def show_all_preordersBuy(request):
    # Filter PreOrderTable for invoices where shop_confirm is False
    preorders = almogOil_models.OrderBuyinvoicetable.objects.filter(confirmed=False)

    # Filter PreOrderItemsTable based on the related PreOrderTable invoice_no
    preorder_items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_instance__shop_confrim=False)

    # Serialize the data
    preorder_serializer = wholesale_serializers.OrderBuyinvoiceSerializer(preorders, many=True)
    preorder_items_serializer = wholesale_serializers.OrderBuyInvoiceItemsSerializer(preorder_items, many=True)

    # Return the response
    return Response({
        'preorders': preorder_serializer.data,
        'preorder_items': preorder_items_serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def show_preordersBuy(request):
    invoice_no = request.query_params.get('invoice_no')  # Get the invoice_no from query params

    if invoice_no:
        try:
            # Filter by specific invoice_no
            preorders = almogOil_models.OrderBuyinvoicetable.objects.filter(invoice_no=invoice_no)
            preorder_items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no__invoice_no=invoice_no)
        except almogOil_models.OrderBuyinvoicetable.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=404)
    else:
        # If no invoice_no is provided, fetch all preorders where confirmed=False
        preorders = almogOil_models.OrderBuyinvoicetable.objects.filter(confirmed=False)
        preorder_items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no__confirmed=False)

    preorder_serializer = wholesale_serializers.OrderBuyinvoiceSerializer(preorders, many=True)
    preorder_items_serializer = wholesale_serializers.OrderBuyInvoiceItemsSerializer(preorder_items, many=True)

    return Response({
        'preorders_buy': preorder_serializer.data,
        'preorder_items_buy': preorder_items_serializer.data
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def show_preorders_buy_v2(request):
    
    """
    - GET  with ?invoice_no=…    → single invoice + items (unchanged, used by the modal).
    - POST {page, status_filter, sent_filter, search_term, …} → list view.
    """
    # ----------------------------------------------------------------
    # 1️⃣  STILL allow the old GET-by-invoice for the modal
    # ----------------------------------------------------------------
    if request.method == "GET" and request.query_params.get('invoice_no'):
        inv_no = request.query_params['invoice_no']
        orders = almogOil_models.OrderBuyinvoicetable.objects.filter(invoice_no=inv_no)
        items  = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no__invoice_no=inv_no)
        return Response({
            "preorders_buy":       wholesale_serializers.OrderBuyinvoiceSerializer(orders, many=True).data,
            "preorder_items_buy":  wholesale_serializers.OrderBuyInvoiceItemsSerializer(items, many=True).data
        })

    # ----------------------------------------------------------------
    # 2️⃣  List endpoint – POST
    # ----------------------------------------------------------------
    data          = request.data
    page          = int(data.get('page', 1))
    page_size     = int(data.get('page_size', 10))
    status_flt    = data.get('status_filter', 'all')      # pending | confirmed | all
    sent_flt      = data.get('sent_filter', 'all')        # sent | not_sent | all
    date_flt      = data.get('date_filter', 'all')        # today | week | month | all
    search_term   = (data.get('search_term') or '').strip()
    sort_by       = data.get('sort_by', 'date_desc')      # date_desc | date_asc | amount_desc | amount_asc …

    # ---------------- base queryset ---------------
    qs = almogOil_models.OrderBuyinvoicetable.objects.all()

    # ---------------- status filter ---------------
    if status_flt == 'pending':
        qs = qs.filter(confirmed=False)
    elif status_flt == 'confirmed':
        qs = qs.filter(confirmed=True)

    # ---------------- sent filter -----------------
    if sent_flt == 'sent':
        qs = qs.filter(send=True)
    elif sent_flt == 'not_sent':
        qs = qs.filter(send=False)

    # ---------------- date filter -----------------
    if date_flt != 'all':
        today = now().replace(hour=0, minute=0, second=0, microsecond=0)
        if date_flt == 'today':
            qs = qs.filter(invoice_date__gte=today)
        elif date_flt == 'week':
            week_start = today - timedelta(days=today.weekday())
            qs = qs.filter(invoice_date__gte=week_start)
        elif date_flt == 'month':
            month_start = today.replace(day=1)
            qs = qs.filter(invoice_date__gte=month_start)

    # ---------------- search ----------------------
    if search_term:
        qs = qs.filter(
            Q(invoice_no__icontains=search_term) |
            Q(source__icontains=search_term)
        )

    # ---------------- sorting ---------------------
    sort_map = {
        'date_desc':     '-invoice_date',
        'date_asc':      'invoice_date',
        'amount_desc':   '-net_amount',
        'amount_asc':    'net_amount',
        'confirm_first': '-confirmed',
        'pending_first': 'confirmed',
        'sent_first':    '-send',
        'not_sent_first':'send',
    }
    qs = qs.order_by(sort_map.get(sort_by, '-invoice_date'))

    # ---------------- summary (before paging) -----
    total_orders     = qs.count()
    confirmed_orders = qs.filter(confirmed=True).count()
    pending_orders   = total_orders - confirmed_orders
    sent_orders      = qs.filter(send=True).count()
    not_sent_orders  = total_orders - sent_orders

    # ---------------- pagination ------------------
    paginator  = Paginator(qs, page_size)
    page_obj   = paginator.get_page(page)

    return Response({
        "preorders_buy": wholesale_serializers.OrderBuyinvoiceSerializer(page_obj, many=True).data,
        "summary": {
            "total_orders":     total_orders,
            "confirmed_orders": confirmed_orders,
            "pending_orders":   pending_orders,
            "sent_orders":      sent_orders,
            "not_sent_orders":  not_sent_orders,
        },
        "pagination": {
            "current_page": page_obj.number,
            "total_pages":  paginator.num_pages,
            "has_next":     page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }
    })
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def confirm_or_update_preorderBuy_items(request):
    if not request.user.has_perm('almogOil.hozma_BuyInvoices'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        data = request.data
        invoice_no = data.get('invoice_no')

        if not invoice_no:
            return Response({"error": "Missing invoice_no"}, status=status.HTTP_400_BAD_REQUEST)

        # Get PreOrder for the given invoice
        preorder = almogOil_models.OrderBuyinvoicetable.objects.filter(invoice_no=invoice_no).first()

        if not preorder:
            return Response({"error": "No PreOrder found for this invoice"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the PreOrder is already confirmed
        if preorder.confirmed:
            return Response({"error": "This PreOrder has already been confirmed and cannot be modified."}, status=status.HTTP_400_BAD_REQUEST)

        # Option to update quantity or confirm the order (optional fields)
        item_quantities = data.get("item_quantities", [])
        action_type = data.get("action_type", "confirm")  # Default to 'confirm', other option is 'update'

        # Process the 'update' action first
        if action_type == "update":
            return Buyhandle_update_action(preorder, item_quantities)

        # Process the 'confirm' action
        elif action_type == "confirm":
            return Buyhandle_confirm_action(preorder)

        else:
            return Response({"error": "Invalid action_type. Use 'confirm' or 'update'."}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def Buyhandle_update_action(preorder, item_quantities):
    # Update the quantity for specified items
    preorder_items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no=preorder.autoid)

    for item in item_quantities:
        item_no = item.get("item_no")  # Ensure we are using item_no from the request JSON
        new_quantity = item.get("new_quantity")

        if not item_no or new_quantity is None:
            continue  # Skip if item_no or new_quantity is not provided

        # Check if the item exists in the PreOrderItemsTable using pno
        preorder_item = preorder_items.filter(pno=item_no).first()  # Now using item_no from the request JSON

        if not preorder_item:
            return Response({"error": f"Item with pno {item_no} is not part of this PreOrder."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the quantity in PreOrderItemsTable
        preorder_item.Confirmed_quantity = new_quantity
        preorder_item.dinar_total_price = preorder_item.dinar_unit_price * new_quantity  # Recalculate the total price
        preorder_item.cost_total_price = preorder_item.cost_unit_price * new_quantity  # Recalculate the cost total price
        preorder_item.save()

    # After updating the quantities for all items, recalculate the total amount for the PreOrder
    total_amount = sum([item.cost_total_price for item in preorder_items])  # Sum the dinar_total_price of all items

    # Update the total amount in PreOrderTable
    preorder.amount = total_amount
    preorder.net_amount= total_amount
    preorder.save()

    return Response({"success": True, "message": "PreOrder items updated with new quantities."}, status=status.HTTP_200_OK)

def Buyhandle_confirm_action(preorder):
    # Prevent confirmation unless preorder.send is True
    if not preorder.send:
        return Response({"success": False, "message": "Cannot confirm preorder. 'send' must be True."}, status=status.HTTP_400_BAD_REQUEST)

    # Get all related preorders (not just the first)
    related_preorders = preorder.related_preorders.all().order_by('autoid')
    if not related_preorders.exists():
        return Response({"success": False, "message": "No related preorder found."}, status=status.HTTP_400_BAD_REQUEST)

    # Confirm the PreOrder and move items to BuyInvoiceMainItem
    source = preorder.source_obj

    # Create Buy Invoice
    Buy_invoice = almogOil_models.Buyinvoicetable.objects.create(
        invoice_no=preorder.invoice_no,
        source=preorder.source,
        source_obj=source,
        confirmation_date=timezone.now(),
        invoice_date=preorder.invoice_date,
        send_date=preorder.send_date,
        net_amount=preorder.net_amount,
        amount=preorder.amount,
    )
     
    # Process PreOrder items and move them to BuyInvoiceItemsTable
    preorder_items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no=preorder.autoid)
    confirmed_quantity = sum(item.Confirmed_quantity or 0 for item in preorder_items)

    for item in preorder_items:
        if item.Confirmed_quantity is None:
            item.Confirmed_quantity = item.Asked_quantity
            item.save()

        # Save to BuyInvoiceItemsTable
        almogOil_models.BuyInvoiceItemsTable.objects.create(
            invoice_no2=preorder.invoice_no,
            invoice_no=Buy_invoice,
            item_no=item.item_no or "",
            pno=item.pno or "",
            main_cat=item.main_cat or "",
            sub_cat=item.sub_cat or "",
            name=item.name or "",
            company=item.company or "",
            company_no=item.company_no or "",
            quantity=item.Confirmed_quantity or 0,
            quantity_unit="",
            currency="",
            dinar_unit_price=item.dinar_unit_price or 0,
            dinar_total_price=item.dinar_total_price or 0,
            current_buy_price =item.current_buy_price or 0,
            cost_unit_price=item.cost_unit_price or 0,
            cost_total_price=item.cost_total_price or 0,
            exchange_rate=Decimal('1.0000'),
            buysource=preorder.source_obj,
            prev_quantity=item.prev_quantity or 0,
            current_quantity=item.current_quantity or 0,
            source=item.source if hasattr(item, "source") else None
        )

        # Distribute confirmed quantity to ALL related preorder items (FIFO)
        related_preorder_items = almogOil_models.PreOrderItemsTable.objects.filter(
            invoice_instance__in=related_preorders,
            pno=item.pno
        ).order_by('invoice_instance', 'autoid')  # Order to ensure fair distribution

        remaining_quantity = item.Confirmed_quantity or 0
        for pre_item in related_preorder_items:
            if remaining_quantity < 0:
                break

            requested_quantity = pre_item.quantity or 0
            assign_quantity = min(remaining_quantity, requested_quantity)

            pre_item.confirm_quantity = assign_quantity
            pre_item.quantity_proccessed = True
            pre_item.dinar_total_price = pre_item.dinar_unit_price * assign_quantity
            
            pre_item.current_quantity = pre_item.prev_quantity - assign_quantity
            pre_item.save()

            remaining_quantity -= assign_quantity

        # Update stock in Mainitem
        try:
            mainitem = almogOil_models.Mainitem.objects.get(pno=item.pno)
            mainitem.itemvalue = max(mainitem.itemvalue + item.Confirmed_quantity, 0)
            mainitem.buylastdate= timezone.now()
            mainitem.buysource=mainitem.source.name
            mainitem.save()
        except almogOil_models.Mainitem.DoesNotExist:
            pass

    preorder.confirmed = True
    preorder.save()
    transaction = f" {Buy_invoice.invoice_no}فاتورة  شراء- رقم" ,
    details = f"تأكيد طلب شراء رقم {Buy_invoice.invoice_no} من المصدر {source.name}، بتاريخ {timezone.now().date()}، عدد الأصناف: {preorder_items.count()}، الكمية الإجمالية المؤكدة: {confirmed_quantity}"
    create_transactions_history_record("source", source, "debit", Buy_invoice.amount, transaction, details)

    return Response({"success": True, "message": "PreOrder items confirmed and moved to buyinvoice."}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])  # Allow access for any user
@authentication_classes([CookieAuthentication])  # No authentication for this view
def send_unsent_invoices(request):
    if not request.user.has_perm('almogOil.hozma_BuyInvoices'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    # Extract the invoice number from the request body
    invoice_no = request.data.get('invoice_no')

    if not invoice_no:
        return Response({'error': 'invoice_no is required'}, status=400)

    try:
        # Fetch the invoice record from the database
        record = almogOil_models.OrderBuyinvoicetable.objects.get(invoice_no=invoice_no, send=False, source_obj__isnull=False)
    except almogOil_models.OrderBuyinvoicetable.DoesNotExist:
        return Response({'error': 'Invoice not found or already sent'}, status=404)

    try:
        # Extract phone number and validate
        phone = getattr(record.source_obj, 'phone', '')
        if not phone:
            return Response({'error': 'Phone number missing for invoice'}, status=400)

        # Get the invoice items
        items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no=record)
        if not items.exists():
            return Response({'error': 'No items found for this invoice'}, status=404)

        # Prepare the invoice data
        invoice_data = prepare_invoice_data(record, items)

        # Create an Excel file with Arabic formatting
        excel_buffer = create_excel_invoice(invoice_data)

        # Send the invoice via the Green API (you can customize this function)
        file_name = f"invoice_{invoice_data['invoice_no']}.xlsx"
        success = send_excel_file_greenapi_upload(phone, file_name, excel_buffer)

        if success:
            # Update the invoice record as sent
            record.send = True
            record.send_date = timezone.now()
            record.save()

            return Response({'message': f'Invoice {invoice_data["invoice_no"]} sent successfully to {phone}'}, status=200)
        else:
            return Response({'error': 'Failed to send invoice'}, status=500)

    except Exception as e:
        return Response({'error': f'Error processing invoice: {str(e)}'}, status=500)



def prepare_invoice_data(record, items):
    # Extract relevant fields and prepare data for invoice creation
    invoice_date = record.send_date or timezone.now().date()

    total_amount = float(record.amount) if hasattr(record, 'amount') else 0
    total = float(record.buy_net_amount) if hasattr(record, 'buy_net_amount') else 0

    # Convert total amount to words (Libyan Dinar)
    total_in_words = num2words(total_amount, lang='ar') + ' دينار ليبي فقط لا غير'

    invoice_data = {
        'company_name': 'منصة حُزمة',
        'invoice_no': record.invoice_no,
        'date': invoice_date,
        'payment_type':  'آجلة',
        'customer_name': record.source_obj.name if record.source_obj else '',
        'customer_info': record.source_obj.address if record.source_obj else '',
        'commission': record.source_obj.commission if record.source_obj else 0,
        'items': [],
        'total': total_amount,
        'hoz_total': total,
        'total_in_words': total_in_words,
        'notes': [
            '💻 زر موقعنا الإلكتروني الآن واستمتع بالعروض الحصرية: www.hozma.net',
    '📞 لمزيد من التفاصيل، يمكنك الاتصال بنا على الرقم: 123-7890.'
        ]
    }

    for item in items:
        invoice_data['items'].append({
            'pno': item.sourrce_pno,
            'name': item.name,
            'company': item.company,
            'Asked_quantity': item.Asked_quantity,
            
            'dinar_unit_price': item.current_buy_price,
           
        })


    return invoice_data




def create_excel_invoice(invoice_data):
    excel_buffer = BytesIO()
    workbook = xlsxwriter.Workbook(excel_buffer)
    worksheet = workbook.add_worksheet('فاتورة')

    # Page setup for A4
    worksheet.set_paper(9)  # A4 paper
    worksheet.set_portrait()
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    worksheet.set_print_scale(90)
    worksheet.hide_gridlines(2)
    worksheet.fit_to_pages(1, 1)

    rtl_format = {'reading_order': 2}

    # Company Name - Larger, bold, and center-aligned with bottom border
    company_format = workbook.add_format({
        **rtl_format,
        'bold': True,
        'font_size': 18,
        'align': 'center',
        'valign': 'vcenter',
        'font_name': 'Arial',
        'bottom': 3,
        'font_color': '#003366'
    })

    # Invoice header info format - bold, medium size, right-aligned
    header_label_format = workbook.add_format({
        **rtl_format,
        'bold': True,
        'font_size': 12,
        'align': 'right',
        'font_name': 'Arial',
        'valign': 'vcenter'
    })

    header_value_format = workbook.add_format({
        **rtl_format,
        'font_size': 12,
        'align': 'right',
        'font_name': 'Arial',
        'valign': 'vcenter'
    })

    # Address and customer info format
    customer_info_format = workbook.add_format({
        **rtl_format,
        'font_size': 11,
        'align': 'right',
        'font_name': 'Arial',
        'text_wrap': True,
        'valign': 'top'
    })

    # Table header format - bold with background and border
    table_header_format = workbook.add_format({
        **rtl_format,
        'bold': True,
        'font_size': 12,
        'bg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_name': 'Arial',
        'text_wrap': True
    })

    # Item cell format (Right aligned)
    item_cell_right = workbook.add_format({
        **rtl_format,
        'font_size': 11,
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'font_name': 'Arial',
        'text_wrap': True
    })

    # Item name format - larger, bold, right aligned
    item_name_format = workbook.add_format({
        **rtl_format,
        'bold': True,
        'font_size': 13,
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'font_name': 'Arial',
        'text_wrap': True,
        'font_color': '#2F5496'
    })

    # Currency format (Right aligned)
    currency_format = workbook.add_format({
        **rtl_format,
        'font_size': 11,
        'border': 1,
        'align': 'right',
        'num_format': '#,##0.00 "د.ل"',
        'font_name': 'Arial'
    })

    # Total row format - bold, larger font, right aligned with border
    total_format = workbook.add_format({
        **rtl_format,
        'bold': True,
        'font_size': 13,
        'border': 1,
        'align': 'right',
        'font_name': 'Arial',
        'font_color': '#000000'
    })

    # Total amount value format - bold, larger font, center aligned
    total_value_format = workbook.add_format({
        **rtl_format,
        'bold': True,
        'font_size': 13,
        'border': 1,
        'align': 'center',
        'font_name': 'Arial',
        'num_format': '#,##0.00 "د.ل"',
        'font_color': '#000000'
    })

    # Amount in words format - italic, right aligned
    amount_words_format = workbook.add_format({
        **rtl_format,
        'italic': True,
        'font_size': 11,
        'align': 'right',
        'font_name': 'Arial',
        'text_wrap': True,
        'font_color': '#666666'
    })

    # Notes format
    notes_format = workbook.add_format({
        **rtl_format,
        'font_size': 11,
        'align': 'right',
        'font_name': 'Arial',
        'text_wrap': True,
        'valign': 'top'
    })

    # Signature format
    signature_format = workbook.add_format({
        **rtl_format,
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'font_name': 'Arial',
        'bottom': 1
    })

    # Write Company Name (Merged across B-G to center it better)
    worksheet.merge_range('B1:G1', invoice_data['company_name'], company_format)
    worksheet.set_row(0, 30)

    # Invoice details - shifted one column to the right (B instead of A)
    worksheet.merge_range('B2:C2', f'فاتورة شراء رقم:{invoice_data["invoice_no"]}', header_value_format)
    worksheet.merge_range('E2:F2', f'التاريخ:{invoice_data["date"]}', header_value_format)
    worksheet.merge_range('B3:C3', f'نوع الدفع:{invoice_data["payment_type"]}', header_value_format)
    worksheet.merge_range('E3:F3', f'اسم المورد:{invoice_data["customer_name"]}', header_value_format)
    worksheet.merge_range('E4:G4', f'عنوان المورد:{invoice_data["customer_info"]}', customer_info_format)

    # Spacing rows
    worksheet.set_row(3, 35)
    worksheet.set_row(4, 30)

    # Table headers starting at row 5 (index 5) - shifted one column to the right
    headers = ['رقم الصنف', 'بيان الصنف', 'الكمية', 'السعر']
 # Reversed order
    col_widths = [15, 50, 15, 15]

    start_col = 4  # Column E
    for i, (header, width) in enumerate(zip(headers, col_widths)):
        col_idx = start_col - i
        worksheet.write(5, col_idx, header, table_header_format)
        worksheet.set_column(col_idx, col_idx, width)


    # Write items starting at row 6 - shifted one column to the right
    row = 6
    for item in invoice_data['items']:
        worksheet.write(row, 1, item['dinar_unit_price'], currency_format)  # السعر
        worksheet.write(row, 2, item['Asked_quantity'], item_cell_right)    # الكمية
        worksheet.write(row, 3, f"{item['name']} / {item['company'] or ''}", item_name_format)  # بيان الصنف
        worksheet.write(row, 4, item['pno'], item_cell_right)     # column E
        worksheet.set_row(row, 25)
        row += 1

    # Total row - shifted one column to the right
     # Total rows - one under the other, right-aligned
    worksheet.write(row, 2, 'المبلغ الإجمالي:', total_format)
    worksheet.write(row, 1, invoice_data['hoz_total'], total_value_format)
    worksheet.set_row(row, 25)
    row += 1

    worksheet.write(row, 2, 'الخصم:', total_format)
    worksheet.write(row, 1, invoice_data['commission'], total_value_format)
    worksheet.set_row(row, 25)
    row += 1

    worksheet.write(row, 2, 'الصافي:', total_format)
    worksheet.write(row,1, invoice_data['total'], total_value_format)
    worksheet.set_row(row, 25)
    row += 1


    # Empty row for spacing
    worksheet.set_row(row, 10)
    row += 1

    # Total amount in words - shifted one column to the right
    worksheet.merge_range(row, 1, row, 6, f'المبلغ بالحروف: {invoice_data["total_in_words"]}', amount_words_format)
    worksheet.set_row(row, 25)
    row += 2

    # Notes - shifted one column to the right
    for note in invoice_data['notes']:
        worksheet.merge_range(row, 1, row, 6, note, notes_format)
        worksheet.set_row(row, 20)
        row += 1

    # Signature lines - shifted one column to the right
    row += 2
    worksheet.merge_range(row, 1, row, 3, 'توقيع المورد:', signature_format)  # columns B-D
    worksheet.merge_range(row, 4, row, 6, 'توقيع المستلم:', signature_format)  # columns E-G
    worksheet.set_row(row, 35)

    workbook.close()
    excel_buffer.seek(0)
    return excel_buffer
"""
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def create_mainitem(request):
    data = request.data.copy()

    source_id = data.get("source")
    buyprice = data.get("buyprice")

    if not source_id:
        return Response({"error": "معرف المصدر مفقود"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        source = almogOil_models.AllSourcesTable.objects.get(id=source_id)
    except almogOil_models.AllSourcesTable.DoesNotExist:
        return Response({"error": "المصدر غير موجود"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        comstistion = float(source.comstistion or 0)
        buyprice = float(buyprice or 0)
        costprice = comstistion * buyprice
        data["costprice"] = costprice
    except (TypeError, ValueError):
        return Response({"error": "بيانات الشراء أو النسبة غير صالحة"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = products_serializers.MainitemSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
        return Response({
            "message": "تم إنشاء العنصر بنجاح.",
            "data": products_serializers.MainitemSerializer(instance).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
"""
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def update_mainitem(request, pk):
    try:
        instance = almogOil_models.Mainitem.objects.get(pk=pk)
    except almogOil_models.Mainitem.DoesNotExist:
        return Response({"error": "Mainitem not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = products_serializers.MainitemSerializer(instance, data=request.data, partial=(request.method == "PATCH"))
    if serializer.is_valid():
        instance = serializer.save()
        return Response({
            "message": "Mainitem updated successfully.",
            "data":products_serializers.MainitemSerializer(instance).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""

"""
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])  # No authentication required
def register_source_user(request):
    required_fields = ['username', 'password', 'name']

    for field in required_fields:
        if field not in request.data:
            return Response({field: "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

    username = request.data.get('username')
    if almogOil_models.AllSourcesTable.objects.filter(username=username).exists():
        return Response({"username": "This username is already taken."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = almogOil_models.AllSourcesTable.objects.create(
            username=username,
            password=make_password(request.data['password']),
            name=request.data.get('name', ''),
            email=request.data.get('email', ''),
            mobile=request.data.get('mobile', ''),
            type='source'  # Enforce type as "source"
        )
        return Response({"message": "Source user created successfully."}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
"""
@extend_schema(
    summary="عرض كل المصادر",
    description="إرجاع قائمة بجميع المصادر (AllSourcesTable).",
    tags=["Sources"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def show_all_sources(request):
    if not request.user.has_perm('almogOil.hozma_Products'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    sources = almogOil_models.AllSourcesTable.objects.all()
    serializer = almogOil_serializers.SourcesSerializer(sources, many=True)
    return Response(serializer.data)
@extend_schema(
    summary="عرض تفاصيل مصدر معين",
    description="إرجاع تفاصيل مصدر معين باستخدام رقم العميل (clientid).",
    tags=["Sources"],
    parameters=[
        OpenApiParameter(name="source_id", description="رقم العميل", required=True, type=int)
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def show_source_details(request, source_id):
    if not request.user.has_perm('almogOil.hozma_Products'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        source = almogOil_models.AllSourcesTable.objects.get(clientid=source_id)
    except almogOil_models.AllSourcesTable.DoesNotExist:
        return Response({"detail": "Source not found."}, status=404)

    serializer = almogOil_serializers.SourcesSerializer(source)
    return Response(serializer.data)

@extend_schema(
    summary="تعديل معلومات المصدر",
    description="تعديل جزئي أو كامل لمصدر موجود باستخدام `clientid`.",
    tags=["Sources"],
    request=almogOil_serializers.SourcesSerializer,
    responses={
        200: almogOil_serializers.SourcesSerializer,
        400: OpenApiResponse(description="بيانات غير صالحة"),
        404: OpenApiResponse(description="المصدر غير موجود"),
    },
    parameters=[
        OpenApiParameter(name="source_id", description="رقم العميل", required=True, type=int)
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def edit_source_info(request, source_id):
    if not request.user.has_perm('almogOil.hozma_Products'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        source = almogOil_models.AllSourcesTable.objects.get(clientid=source_id)
    except almogOil_models.AllSourcesTable.DoesNotExist:
        return Response({"detail": "Source not found."}, status=404)

    serializer = almogOil_serializers.SourcesSerializer(source, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)



def safe_csv(value):
    # Splits on both ',' and ';'
    return [v.strip() for v in re.split(r'[;,]', value or '') if v.strip()]

def normalize_oem_list(oem_string):
    return set(o.strip() for o in re.split(r'[;,]', str(oem_string)) if o.strip())



# Assuming your model name is CompanyTable (adjust accordingly)
def validate_company_name(name):
    all_companies = almogOil_models.Companytable.objects.values_list('companyname', flat=True)
    normalized_name = name.strip().lower()
    if normalized_name in [c.lower() for c in all_companies]:
        return None  # Name is valid
    else:
        close_matches = difflib.get_close_matches(normalized_name, [c.lower() for c in all_companies], n=1, cutoff=0.6)
        if close_matches:
            # Suggest the closest match
            original_case_match = next((c for c in all_companies if c.lower() == close_matches[0]), close_matches[0])
            return Response(
                {'error': f'اسم الشركة "{name}" غير موجود. هل تقصد "{original_case_match}"؟'},
                status=400
            )
        else:
            return Response({'error': f'اسم الشركة "{name}" غير موجود في قاعدة البيانات'}, status=400)



@extend_schema(
    summary="إنشاء منتج رئيسي من مصدر",
    description="""
يتم إنشاء منتج جديد بناءً على معلومات المورد ورقم OEM وسعر الشراء والكمية المعروضة.  
العملية تشمل:
- التحقق من وجود الشركة
- حساب السعر بعد الخصم
- حساب سعر التكلفة بناءً على العمولة
- التحقق من وجود المنتج أو تحديثه بناءً على `source_pno` أو `pno`
- مطابقة OEM مع الجداول الحالية أو إنشاء سجل جديد

⚠️ يتم أيضًا تحديث المنتج الحالي إذا كان السعر الجديد أقل.
""",
    tags=["Mainitem", "Sources"],
    request=products_serializers.MainitemSerializer,
    responses={
        201: OpenApiResponse(description="تم إنشاء المنتج بنجاح"),
        200: OpenApiResponse(description="تم تحديث المنتج الحالي أو المنتج موجود مسبقًا"),
        400: OpenApiResponse(description="طلب غير صالح أو بيانات ناقصة"),
        500: OpenApiResponse(description="خطأ غير متوقع في الخادم"),
    },
    examples=[
        OpenApiExample(
            "مثال على الإدخال",
            value={
                "oem_number": "123ABC",
                "external_oem": "456DEF",
                "companyproduct": "Toyota",
                "buyprice": "150.0000",
                "showed": 5,
                "discount": "0.1",
                "discount-type": "source",
                "category_type": "Engine",
                "pno": "5678",
                "source_pno": "SRC-7890",
                "replaceno": "TYT-002",
                "source": "client123"
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def create_mainitem_by_source(request):
    
    
    data = request.data.copy()

    # Define required fields and their Arabic labels
    required_fields = {
        'oem_number': 'رقم OEM',
        'companyproduct': 'الشركة المصنعة',
        'buyprice': 'سعر الشراء',
        'showed': 'الكمية المعروضة',
        'source': 'المصدر'
    }

    # Check for missing fields
    missing = [arabic for key, arabic in required_fields.items() if not data.get(key)]
    
    if missing:
        return Response({'error': f'الحقول التالية مفقودة: {", ".join(missing)}'}, status=400)
    try:
        
        company = str(data.get('companyproduct', '')).strip()
        company_validation = validate_company_name(company)
        if company_validation:
           return company_validation
        original_buyprice = Decimal(str(data.get('buyprice', '0'))).quantize(Decimal('0.0000'))
        showed = data.get('showed')
        source = str(data.get('source', '')).strip()
        discount = Decimal(str(data.get('discount') or '0'))
        discount_type = str(data.get('discount-type', 'source')).strip().lower()
        category_type = str(data.get('category_type', '')).strip()
        pno = str(data.get('pno') or '').strip()
        source_pno = str(data.get('source_pno') or pno).strip()
        oem_in = str(data.get('oem_number', ''))
        external_oem = str(data.get('external_oem', ''))
        all_oems = safe_csv(oem_in) + safe_csv(external_oem)
        oem_csv = ",".join(all_oems)


        
        incoming_oems = normalize_oem_list(oem_csv)

        replaceno = str(data.get('replaceno', '')).strip()
        if not almogOil_models.ItemCategory.objects.filter(name__iexact=category_type).exists():
            return Response({'error': f' صنف الفئة "{category_type}" غير موجودة في جدول التصنيفات'}, status=400)
        


        if discount > 0:
            discounted_buyprice = (original_buyprice - (original_buyprice * discount)).quantize(Decimal('0.0000'))
        else:
            discounted_buyprice = original_buyprice

        data['buyprice'] = str(discounted_buyprice)

        try:
            source_obj = almogOil_models.AllSourcesTable.objects.get(clientid__iexact=source)
            commission = Decimal(str(source_obj.commission)).quantize(Decimal('0.0000'))

            if discount_type == 'market':
                # Cost price remains based on original buyprice
                costprice = (original_buyprice - (original_buyprice * commission)).quantize(Decimal('0.0000'))
            else:
                # Default: cost price from discounted buyprice
                costprice = (discounted_buyprice - (discounted_buyprice * commission)).quantize(Decimal('0.0000'))

            data['costprice'] = str(costprice)
        except almogOil_models.AllSourcesTable.DoesNotExist:
            return Response({'error': f'المصدر "{source}" غير موجود في جدول الموردين'}, status=400)
        
        existing_product = almogOil_models.Mainitem.objects.filter(
            source__exact=source,
            source_pno__exact=source_pno
        ).first()

        if existing_product:
            update_data = {
                'showed': showed,
                'costprice': str(costprice),
                'buyprice': str(discounted_buyprice),
                'source_pno': source_pno   # احتفظ به حتى لو كان كما هو
 
            }
            serializer = products_serializers.MainitemSerializer(
                existing_product,
                data=update_data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'تم تحديث الحقول: الكمية المعروضة، سعر التكلفة، وسعر الشراء للمنتج المطابق لنفس المورد ورقم الخص بالمورد.',
                    'data': data
                }, status=200)
            return Response(serializer.errors, status=400)

               # ❷ ــــ إذا لم يُوجد منتج مطابق لـ (source, source_pno) نتابع إنشاء/تحديث المنطق القديم
        #      يمكنك حذف كتلة if-pno القديمة بالكامل أو إبقاؤها كمعيار ثانوي إن أردت.
        #      هنا مثال سريع لجعلها معياراً ثانوياً:

        if pno:
            with transaction.atomic():
             existing_product = almogOil_models.Mainitem.objects.select_for_update().filter(pno=pno).first()
             if existing_product:
                update_data = {
                    'showed': showed,
                    'costprice': str(costprice),
                    'buyprice': str(discounted_buyprice),
                    'source_pno': source_pno
                }
                serializer = products_serializers.MainitemSerializer(
                    existing_product,
                    data=update_data,
                    partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        'message': ' تم تحديث الحقول الكمية المعروضة، وسعر التكلفة، وسعر الشراء للمنتج الموجود مسبقًا',
                        'data': data
                    }, status=200)
                return Response(serializer.errors, status=400)

        with transaction.atomic():
            if not pno:
                last_product = almogOil_models.Mainitem.objects.order_by('-pno').first()
                if last_product:
                    try:
                        last_pno = int(last_product.pno)
                        pno = str(last_pno + 1)
                    except (ValueError, TypeError):
                        pno = '1000'
                else:
                    pno = '1000'
                data['pno'] = pno

            data['source_pno'] = source_pno

            oem_matches = []
            for row in almogOil_models.Oemtable.objects.all():
                existing_oems = normalize_oem_list(row.oemno) 
                if incoming_oems & existing_oems:  # Check if there is any intersection  
                    oem_matches.append(row) 



            if oem_matches:
                company_oem = None
                for match in oem_matches:
                    if match.cname.lower() == company.lower() or match.cno.lower() == replaceno.lower():
                        company_oem = match
                        break

                if company_oem:
                    all_oems = safe_csv(company_oem.oemno)
                    existing_items = almogOil_models.Mainitem.objects.filter(Q(companyproduct__iexact=company)
                                                                              | Q(replaceno__iexact=replaceno))
                    item_to_update = None
                    for item in existing_items:
                        item_oems = safe_csv(item.oem_numbers)
                        if set(item_oems) & set(all_oems):
                            item_to_update = item
                            break

                    if item_to_update:
                        if Decimal(str(item_to_update.buyprice)) > discounted_buyprice:
                            update_payload = data.copy()
                            update_payload['oem_numbers'] = company_oem.oemno
                            update_payload.pop('pno', None)
                            serializer = products_serializers.MainitemSerializer(
                                item_to_update, data=update_payload, partial=True
                            )
                            if serializer.is_valid():
                                instance = serializer.save()
                                instance.oem_numbers = company_oem.oemno
                                instance.save()
                                return Response({
                                    'message': 'تم تحديث المنتج الحالي بسعر أقل',
                                    'data': data
                                }, status=200)
                            return Response(serializer.errors, status=400)
                        return Response({
                            'message': 'المنتج الموجود لديه نفس السعر أو سعر أفضل',
                            'data': data
                        }, status=200)

                    data['oem_numbers'] = company_oem.oemno
                    data['itemno'] = str(data.get('oem_number', '')).strip()  # 👈 ADD HERE
                    serializer = products_serializers.MainitemSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=201)
                    return Response(serializer.errors, status=400)

                else:
                    new_oem_row = almogOil_models.Oemtable.objects.create(
                        cname=company,
                        cno=replaceno,
                        oemno=oem_csv
                    )
                    data['oem_numbers'] = new_oem_row.oemno
                    data['itemno'] = str(data.get('oem_number', '')).strip()  # 👈 ADD HERE

                    serializer = products_serializers.MainitemSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=201)
                    return Response(serializer.errors, status=400)

            else:
                new_oem_row = almogOil_models.Oemtable.objects.create(
                    cname=company,
                    cno=replaceno,
                    oemno=oem_csv
                )
                data['oem_numbers'] = new_oem_row.oemno
                serializer = products_serializers.MainitemSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=201)
                return Response(serializer.errors, status=400)

    except Exception as e:
        return Response({'error': f'حدث خطأ غير متوقع: {str(e)}'}, status=500)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])  # anonymous OK
def create_oem_entry(request):
    """
    POST payload:
      - cname : str  (e.g. "Toyota")
      - cno   : str  (e.g. "58634")
      - oemno : str  (comma-separated OEM codes, e.g. "6589,123456")
    """
    serializer = wholesale_serializers.OemTableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    summary="فلترة المنتجات الرئيسية (Mainitem)",
    description="""
نقطة النهاية هذه تستقبل طلب POST يحتوي على مجموعة من المفاتيح لفلترة بيانات المنتجات، 
بالإضافة إلى مفاتيح خاصة بالتقسيم (pagination).  
تقوم بالآتي:

1. بناء Q-object من الفلاتر.
2. حساب cache_key باستخدام MD5.
3. في حال وجود نتيجة مخزنة، تُرجع مباشرة.
4. وإلا، يتم تنفيذ الفلترة والتقسيم والعمليات الحسابية والتخزين المؤقت ثم ترجع النتائج.
    
✅ بعض الفلاتر المتاحة:
- `pno`, `itemname`, `itemno`, `itemmain`, `itemsubmain`, `itemthird`
- `companyproduct`, `companyno`, `source`, `model`, `country`, `category`
- `discount`, `availability`, `showed`, `resvalue`, `has_image`
- `fromdate`, `todate` (بصيغة YYYY-MM-DD)
""",
    tags=["Mainitem", "Filtering"],
    request=None,
    responses={
        200: OpenApiResponse(description="نجحت عملية الفلترة"),
        400: OpenApiResponse(description="طلب غير صالح أو تنسيق تاريخ خاطئ"),
        405: OpenApiResponse(description="طريقة الطلب غير مسموحة"),
    },
    examples=[
        OpenApiExample(
            name="مثال لطلب فلترة",
            value={
                "pno": "123",
                "companyproduct": "Toyota",
                "category": "Engine",
                "availability": "available",
                "discount": "available",
                "page": 1,
                "size": 20,
                "fromdate": "2024-01-01",
                "todate": "2024-12-31",
                "has_image": "yes"
            },
            request_only=True,
            response_only=False
        )
    ]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def web_filter_items(request):
    """
    POST body is a JSON containing filter keys (pno, itemname, category, fromdate, todate, etc.)
    plus pagination keys: page (int) and size (int).
    We will:
      1. Build a Q‐object from all provided filters.
      2. Compute cache_key = MD5(str(filters_dict)) + page + size
      3. If cached, return immediately.
      4. Otherwise, filter -> paginate -> serialize -> compute totals -> cache -> return.
    """
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        filters = request.data  # a dict
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)

    # Extract page/size (defaults)
    try:
        page_number = int(filters.get("page", 1))
    except (ValueError, TypeError):
        page_number = 1

    try:
        page_size = int(filters.get("size", 20))
    except (ValueError, TypeError):
        page_size = 20

    # Build a reproducible string for all filter fields EXCEPT page/size,
    # so that changing only page/size still hits different cache entries:
    filters_for_key = dict(filters)  # shallow copy
    # Remove pagination keys before hashing
    filters_for_key.pop("page", None)
    filters_for_key.pop("size", None)

    # Compute MD5 of sorted filter‐dict (so ordering doesn’t matter):
    filters_json = json.dumps(filters_for_key, sort_keys=True)
    base_hash   = hashlib.md5(filters_json.encode("utf-8")).hexdigest()
    cache_key   = f"webfilter_{base_hash}_p{page_number}_s{page_size}"

    # 1) Check cache
    cached = cache.get(cache_key)
    if isinstance(cached, dict):
        # Return a shallow copy with a "cached_flag" set
        result = cached.copy()
        result["cached_flag"] = True
        return Response(result, status=status.HTTP_200_OK)

    # 2) Build the Q‐object from all possible filters
    filters_q = Q()

    # Example of your existing filters logic:
    if filters.get("fileid"):
        filters_q &= Q(fileid__icontains=filters["fileid"])
    if filters.get("itemno"):
        filters_q &= Q(itemno__icontains=filters["itemno"])
    if filters.get("itemmain"):
        filters_q &= Q(itemmain__icontains=filters["itemmain"])
    if filters.get("itemsubmain"):
        filters_q &= Q(itemsubmain__icontains=filters["itemsubmain"])
    if filters.get("engine_no"):
        filters_q &= Q(engine_no__icontains=filters["engine_no"])
    if filters.get("itemthird"):
        filters_q &= Q(itemthird__icontains=filters["itemthird"])
    if filters.get("companyproduct"):
        filters_q &= Q(companyproduct__icontains=filters["companyproduct"])
    if filters.get("itemname"):
        filters_q &= Q(itemname__icontains=filters["itemname"])
    if filters.get("eitemname"):
        filters_q &= Q(eitemname__icontains=filters["eitemname"])
    if filters.get("companyno"):
        filters_q &= Q(replaceno__icontains=filters["companyno"])
    if filters.get("pno"):
        filters_q &= Q(pno__icontains=filters["pno"])
    if filters.get("source"):
        filters_q &= Q(ordersource__icontains=filters["source"])
    if filters.get("model"):
        filters_q &= Q(itemthird__icontains=filters["model"])
    if filters.get("country"):
        filters_q &= Q(itemsize__icontains=filters["country"])
    if filters.get("oem"):
        filters_q &= Q(oem_numbers__icontains=filters["oem"])
    if filters.get("category"):
        filters_q &= Q(category__icontains=filters["category"])
    if filters.get("item_type"):
        filters_q &= Q(item_category__name__iexact=filters["item_type"])

    if filters.get("discount") == "available":
        filters_q &= Q(discount__isnull=False) & ~Q(discount=0)

    if filters.get("oem_combined"):
        val = filters["oem_combined"]
        filters_q &= (Q(oem_numbers__icontains=val) | Q(replaceno__icontains=val))

    # "showed" logic (0 or >0)
    if filters.get("showed") == "0":
        filters_q &= Q(showed=0)
    if filters.get("showed") == ">0":
        filters_q &= Q(showed__gt=0)

    # availability logic:
    availability = filters.get("availability")
    if availability == "not_available":
        filters_q &= Q(showed=0)
    elif availability == "limited":
        filters_q &= Q(showed__lte=10, showed__gt=0)
    elif availability == "available":
        filters_q &= Q(showed__gt=10)

    # resvalue logic:
    if filters.get("resvalue") == ">0":
        filters_q &= Q(rshowed__gt=0)

    # showed_itemtemp logic:
    if filters.get("showed_itemtemp") == "lte":
        filters_q &= Q(showed__lte=F("itemtemp"))

    # Date‐range on orderlastdate
    fromdate = filters.get("fromdate", "").strip()
    todate   = filters.get("todate", "").strip()
    if fromdate and todate:
        try:
            from_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
            # include entire end‐day:
            to_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)
            filters_q &= Q(orderlastdate__range=[from_obj, to_obj])
        except ValueError:
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

    # 3) Apply the Q filter and order

     # 3) Handle has_image filter by annotating then applying to the Q
    # First prepare a subquery that checks ImageTable.productid == Mainitem.pno
    images_subquery = almogOil_models.Imagetable.objects.filter(productid=OuterRef("fileid"))

# …everything up to the has_image logic stays the same…
    base_queryset = (
    almogOil_models.Mainitem.objects
    .filter(filters_q)
    .annotate(has_image_exists=Exists(images_subquery))
    )

    if filters.get("has_image") == "yes":
        base_queryset = base_queryset.filter(has_image_exists=True)
    elif filters.get("has_image") == "no":
        base_queryset = base_queryset.filter(has_image_exists=False)

# Use the annotated+filtered queryset directly:
    base_qs = base_queryset.order_by("itemname")
    # 4) Paginate on the server:
    paginator = Paginator(base_qs, page_size)
    page_obj  = paginator.get_page(page_number)  # this handles out‐of‐range gracefully
    serialized_data = wholesale_serializers.MainitemSerializerHozma(page_obj, many=True).data

    # 5) Compute totals over the ENTIRE filtered queryset (not just this page):
    #     (If you want to compute only for the current page, move this inside the loop below.)
    total_itemvalue = total_itemvalueb = total_resvalue = 0
    total_cost = total_order = total_buy = 0.0

    # We want overall sums over all items in filtered base_qs, not just page_obj.
    # To avoid fetching every row into Python, you might do an aggregate. But if you want them serially:
    for rec in base_qs.values(
        "itemvalue", "itemvalueb", "resvalue", "costprice", "orderprice", "buyprice"
    ):
        iv = float(rec.get("itemvalue") or 0)
        ivb = float(rec.get("itemvalueb") or 0)
        rv = float(rec.get("resvalue") or 0)
        cp = float(rec.get("costprice") or 0)
        op = float(rec.get("orderprice") or 0)
        bp = float(rec.get("buyprice") or 0)

        total_itemvalue += iv
        total_itemvalueb += ivb
        total_resvalue += rv
        total_cost += iv * cp
        total_order += iv * op
        total_buy += iv * bp

    # 6) Build the response payload
    response_payload = {
        "data": serialized_data,
        "last_page": paginator.num_pages,
        "total_rows": paginator.count,
        "page_size": page_size,
        "page": page_number,
        "total_itemvalue": total_itemvalue,
        "total_itemvalueb": total_itemvalueb,
        "total_resvalue": total_resvalue,
        "total_cost": total_cost,
        "total_order": total_order,
        "total_buy": total_buy,
        "cached_flag": False,
    }

    # 7) Cache it (for, say, 5 minutes = 300 s)
    cache.set(cache_key, response_payload, timeout=300)

    return Response(response_payload)
"""
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def delete_invoice(request):
    invoice_no = request.data.get('invoice_no')

    if not invoice_no:
        return Response({'error': 'invoice_no is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        invoice = almogOil_models.OrderBuyinvoicetable.objects.get(invoice_no=invoice_no)

        # Delete related items first
        almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no=invoice).delete()

        # Then delete the invoice
        invoice.delete()

        return Response({'message': 'Invoice and related items deleted successfully.'}, status=status.HTTP_200_OK)
    except almogOil_models.OrderBuyinvoicetable.DoesNotExist:
        return Response({'error': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)

"""


"""

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def delete_preorder_and_items(request, invoice_no):
    try:
        preorder = almogOil_models.PreOrderTable.objects.get(invoice_no=invoice_no)
    except almogOil_models.PreOrderTable.DoesNotExist:
        return Response({"detail": "PreOrder with this invoice number not found."}, status=status.HTTP_404_NOT_FOUND)

    # Delete related items
    deleted_items_count, _ = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance=preorder).delete()

    # Delete the preorder itself
    preorder.delete()

    return Response({
        "message": f"Deleted order and {deleted_items_count} items for invoice number {invoice_no}."
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def delete_all_preorders_and_items(request):
    # Delete all preorder items first (to avoid FK issues)
    items_deleted, _ = almogOil_models.PreOrderItemsTable.objects.all().delete()
    orders_deleted, _ = almogOil_models.PreOrderTable.objects.all().delete()

    return Response({
        "message": f"Deleted {orders_deleted} orders and {items_deleted} items."
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def delete_all_preordersBuy_and_items(request):
    # Delete all preorder items first (to avoid FK issues)
    items_deleted, _ = almogOil_models.OrderBuyInvoiceItemsTable.objects.all().delete()
    orders_deleted, _ = almogOil_models.OrderBuyinvoicetable.objects.all().delete()

    return Response({
        "message": f"Deleted {orders_deleted} orders and {items_deleted} items."
    }, status=status.HTTP_200_OK)
"""

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_buy_invoices_for_preorder(request, invoice_no):
    if not request.user.has_perm('almogOil.hozma_SellInvoices'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )    
    try:
        preorder = almogOil_models.PreOrderTable.objects.get(invoice_no=invoice_no)
        buy_invoices = preorder.related_buy_invoices.all()

        data = [
            {
                "buy_invoice_no": invoice.invoice_no,
                "amount": invoice.amount,
                "net_amount": invoice.net_amount,
                "source": invoice.source,
                "confirmed": invoice.confirmed,
                "send": invoice.send,
            }
            for invoice in buy_invoices
        ]
        return Response({"preorder_invoice": invoice_no, "related_buy_invoices": data}, status=200)

    except almogOil_models.PreOrderTable.DoesNotExist:
        return Response({"error": "PreOrder invoice not found"}, status=404)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_preorders_for_buy_invoice(request, buy_invoice_no):
    if not request.user.has_perm('almogOil.hozma_BuyInvoices'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )    
    try:
        buy_invoice = almogOil_models.OrderBuyinvoicetable.objects.get(invoice_no=buy_invoice_no)
        preorders = buy_invoice.related_preorders.all()

        data = [
            {
                "preorder_invoice_no": preorder.invoice_no,
                "client_name": preorder.client.name if preorder.client else "",
                "amount": preorder.amount,
                "date": preorder.date,
            }
            for preorder in preorders
        ]
        return Response({"buy_invoice_no": buy_invoice_no, "related_preorders": data}, status=200)

    except almogOil_models.OrderBuyinvoicetable.DoesNotExist:
        return Response({"error": "Buy invoice not found"}, status=404)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_related_preorders(request, buy_invoice_id):
    if not request.user.has_perm('almogOil.hozma_BuyInvoices'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )    
    try:
        buy_invoice = almogOil_models.OrderBuyinvoicetable.objects.get(invoice_no=buy_invoice_id)
        related_preorders = buy_invoice.related_preorders.all()

        if not related_preorders.exists():
            return Response({"message": "No related preorders found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = wholesale_serializers.PreorderSerializer(related_preorders, many=True)

        return Response({
            "message": "Successfully retrieved related preorders.",
            "related_preorders": serializer.data
        }, status=status.HTTP_200_OK)

    except almogOil_models.OrderBuyinvoicetable.DoesNotExist:
        return Response({"error": "Buy invoice not found."}, status=status.HTTP_404_NOT_FOUND)



import logging

# Set up logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])  # Adjust if any authentication is needed
def api_auto_confirm_preorder(request):
    if not request.user.has_perm('almogOil.hozma_BuyInvoices'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )    
    invoice_no = request.data.get('invoice_no')
    if not invoice_no:
        return Response({'error': 'Missing invoice_no'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Attempt to get preorder based on invoice_no
        preorder = almogOil_models.PreOrderTable.objects.get(invoice_no=invoice_no)
    except almogOil_models.PreOrderTable.DoesNotExist:
        logger.error(f"PreOrder with invoice_no {invoice_no} does not exist.")
        return Response({'error': 'Preorder not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(f"Error occurred while fetching PreOrder with invoice_no {invoice_no}: {e}")
        return Response({'error': 'Internal server error. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        # Fetch related buy invoices
        related_buy_invoices = almogOil_models.OrderBuyinvoicetable.objects.filter(
            related_preorders=preorder
        )

        # Fetch preorder items based on invoice
        preorder_items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance=preorder.autoid)

        available_items = {}
        missing_items = []

        # Check each item availability
        for item in preorder_items:
            try:
                product = almogOil_models.Mainitem.objects.filter(pno=item.pno)
                available_qty = product.itemvalue or 4
                request_qty = item.confirm_quantity or item.quantity
                if available_qty >= request_qty:
                    available_items[item.pno] = request_qty
                else:
                    missing_items.append(item.pno)
            except almogOil_models.Mainitem.DoesNotExist:
                missing_items.append(item.pno)
            except Exception as e:
                logger.exception(f"Error checking availability for item {item.pno}: {e}")
                missing_items.append(item.pno)

        if all(invoice.confirmed for invoice in related_buy_invoices):
    # If all items are available
         if len(available_items) == preorder_items.count():
            handle_confirm_action(preorder)  # Preorder fully confirmed
            return Response({
            'status': 'fully_confirmed',
            'message': 'Preorder fully confirmed.',
            'confirmed_items': available_items,
            'available_qty':available_qty
            }, status=status.HTTP_200_OK)

         return Response({
        'status': 'waiting_for_inventory',
        'message': 'Some items are still not available.',
        'missing_items': missing_items,

        'available_items': available_items  # Include available items with their quantities
     }, status=status.HTTP_200_OK)

        if available_items:
            buyhandle_update_action(preorder, available_items)  # Call action for available items
            handle_confirm_action(preorder)  # Proceed with confirmation
            return Response({
                'status': 'partially_confirmed',
                'message': 'Some items were confirmed. Waiting for the rest.',
                'confirmed_items': available_items,
                'missing_items': missing_items
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 'not_ready',
            'message': 'Waiting for item availability or invoice confirmation.',
            'missing_items': missing_items
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Unexpected error during processing preorder with invoice_no {invoice_no}: {e}")
        return Response({'error': 'Internal server error. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def invoice_summary(request):
    if not request.user.has_perm('almogOil.hozma_Dashboard'):  # change 'almogOil' to your app name
        return Response(
        {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
        status=status.HTTP_403_FORBIDDEN
        )   
    today = now().date()
    this_month = today.replace(day=1)

    # First day of previous month
    last_month = (this_month - timedelta(days=1)).replace(day=1)

    # Total invoices and amount for current month
    current_month_invoices = almogOil_models.SellinvoiceTable.objects.filter(invoice_date__date__gte=this_month)
    current_count = current_month_invoices.count()
    current_amount = current_month_invoices.aggregate(Sum('amount'))['amount__sum'] or 0

    # Total invoices for last month
    last_month_invoices = almogOil_models.SellinvoiceTable.objects.filter(
        invoice_date__date__gte=last_month,
        invoice_date__date__lt=this_month
    )
    last_count = last_month_invoices.count()

    # Calculate rate of change
    if last_count == 0:
        change_rate = 100 if current_count > 0 else 0
    else:
        change_rate = ((current_count - last_count) / last_count) * 100

    return Response({
        "total_invoices": current_count,
        "total_amount": float(current_amount),
        "change_rate": round(change_rate, 2)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def invoice_statistics(request):
    if not request.user.has_perm('almogOil.hozma_Dashboard'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )    
    today = now()

    # Current month range
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + relativedelta(months=1)) - timedelta(seconds=1)

    # Last month range
    start_of_last_month = start_of_month - relativedelta(months=1)
    end_of_last_month = start_of_month - timedelta(seconds=1)

    # Count invoices this month
    current_month_count = almogOil_models.PreOrderTable.objects.filter(
        date_time__range=(start_of_month, end_of_month)
    ).count()

    # Count invoices last month
    last_month_count = almogOil_models.PreOrderTable.objects.filter(
        date_time__range=(start_of_last_month, end_of_last_month)
    ).count()

    # Percentage increase calculation
    if last_month_count > 0:
        percentage_increase = ((current_month_count - last_month_count) / last_month_count) * 100
    else:
        percentage_increase = 100.0 if current_month_count > 0 else 0.0

    # Count confirmed by shop this month
    shop_confirmed_count = almogOil_models.PreOrderTable.objects.filter(
        date_time__range=(start_of_month, end_of_month),
        shop_confrim=True
    ).count()

    # Count new orders today not confirmed by shop
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    new_unconfirmed_today = almogOil_models.PreOrderTable.objects.filter(
        date_time__range=(start_of_today, end_of_today),
        shop_confrim=False
    ).count()

    return Response({
        'current_month_invoice_count': current_month_count,
        'last_month_invoice_count': last_month_count,
        'percentage_increase': round(percentage_increase, 2),
        'shop_confirmed_this_month': shop_confirmed_count,
        'new_unconfirmed_orders_today': new_unconfirmed_today
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def item_analytics(request):
    if not request.user.has_perm('almogOil.hozma_Dashboard'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )    
    # Get time period from query params (default: last 30 days)
    period = request.GET.get('period', '30d')
    
    # Calculate date ranges
    end_date = datetime.now()
    if period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '30d':
        start_date = end_date - timedelta(days=30)
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
    elif period == '1y':
        start_date = end_date - timedelta(days=365)
    else:
        # Custom period in days
        try:
            days = int(period[:-1])
            start_date = end_date - timedelta(days=days)
        except:
            start_date = end_date - timedelta(days=30)

    # 1. Sales Trends Over Time
    sales_trends = (
        almogOil_models.Mainitem.objects
        .filter(buylastdate__range=[start_date, end_date])
        .annotate(day=TruncDay('buylastdate'))
        .values('day')
        .annotate(
            total_sales=Sum('buyprice'),
            count=Count('fileid')
        )
        .order_by('day')
    )

    # 2. Top Selling Items
    top_items = (
       almogOil_models.Mainitem.objects
        .filter(buylastdate__range=[start_date, end_date])
        .values('itemname', 'companyproduct')
        .annotate(
            total_sales=Sum('buyprice'),
            count=Count('fileid'),
            avg_price=Avg('buyprice')
        )
        .order_by('-total_sales')[:10]
    )

    # 3. Inventory Analysis
    inventory_stats = {
        'total_items':  almogOil_models.Mainitem.objects.count(),
        'available_items':  almogOil_models.Mainitem.objects.filter(showed__gt=0).count(),
        'out_of_stock':  almogOil_models.Mainitem.objects.filter(showed=0).count(),
        'low_stock': almogOil_models.Mainitem.objects.filter(showed__range=(1, 10)).count(),
        'avg_price':  almogOil_models.Mainitem.objects.aggregate(avg=Avg('buyprice'))['avg'],
        'total_inventory_value':  almogOil_models.Mainitem.objects.aggregate(total=Sum(F('buyprice') * F('itemvalue')))['total']
    }

    # 4. Category Distribution
    categories = (
         almogOil_models.Mainitem.objects
        .values('itemmain')
        .annotate(
            count=Count('fileid'),
            percentage=100 * Count('fileid') /  almogOil_models.Mainitem.objects.count()
        )
        .order_by('-count')[:5]
    )

    # 5. Price Range Distribution
    price_ranges = (
         almogOil_models.Mainitem.objects
        .annotate(price_range=Case(
            When(buyprice__lt=100, then=Value('0-100')),
            When(buyprice__gte=100, buyprice__lt=500, then=Value('100-500')),
            When(buyprice__gte=500, buyprice__lt=1000, then=Value('500-1000')),
            When(buyprice__gte=1000, buyprice__lt=5000, then=Value('1000-5000')),
            When(buyprice__gte=5000, then=Value('5000+')),
            default=Value('Unknown'),
            output_field=CharField()
        ))
        .values('price_range')
        .annotate(count=Count('fileid'))
        .order_by('price_range')
    )

    # 6. Recent Activity
    recent_orders = (
         almogOil_models.Mainitem.objects
        .filter(buylastdate__isnull=False)
        .order_by('-buylastdate')[:5]
        .values('itemname', 'buyprice', 'buylastdate', 'buysource')
    )

    # 7. Source Analysis
    source_analysis = (
         almogOil_models.Mainitem.objects
        .filter(buylastdate__range=[start_date, end_date])
        .values('buysource')
        .annotate(
            count=Count('fileid'),
            total_sales=Sum('buyprice'),
            avg_price=Avg('buyprice')
        )
        .order_by('-total_sales')[:5]
    )

    return Response({
        'period': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        },
        'sales_trends': list(sales_trends),
        'top_items': list(top_items),
        'inventory_stats': inventory_stats,
        'categories': list(categories),
        'price_ranges': list(price_ranges),
        'recent_orders': list(recent_orders),
        'source_analysis': list(source_analysis),
    })

   
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def item_category_analysis(request):
    if not request.user.has_perm('almogOil.hozma_Dashboard'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )      
    
    analysis = (
        almogOil_models.Mainitem.objects
        .values('itemmain', 'itemsubmain', 'itemname')
        .annotate(
            count=Count('fileid'),
            total_value=Sum(ExpressionWrapper(F('buyprice') * F('showed'), output_field=FloatField())),
            avg_price=Avg('buyprice'),
            min_price=Min('buyprice'),
            max_price=Max('buyprice')
        )
        .order_by('itemmain', 'itemsubmain', 'itemname')
    )

    hierarchical_data = {}
    for item in analysis:
        main = item['itemmain'] or 'Uncategorized'
        sub = item['itemsubmain'] or 'Uncategorized'
        name = item['itemname'] or 'Unnamed'

        if main not in hierarchical_data:
            hierarchical_data[main] = {
                'name': main,
                'count': 0,
                'total_value': 0,
                'children': {}
            }

        if sub not in hierarchical_data[main]['children']:
            hierarchical_data[main]['children'][sub] = {
                'name': sub,
                'count': 0,
                'total_value': 0,
                'children': []
            }

        hierarchical_data[main]['children'][sub]['children'].append({
            'name': name,
            'count': item['count'],
            'total_value': item['total_value'],
            'avg_price': item['avg_price'],
            'min_price': item['min_price'],
            'max_price': item['max_price']
        })

        hierarchical_data[main]['count'] += item['count']
        hierarchical_data[main]['total_value'] += item['total_value']
        hierarchical_data[main]['children'][sub]['count'] += item['count']
        hierarchical_data[main]['children'][sub]['total_value'] += item['total_value']

    result = []
    for main_data in hierarchical_data.values():
        main_entry = {
            'name': main_data['name'],
            'count': main_data['count'],
            'total_value': main_data['total_value'],
            'children': []
        }
        for sub_data in main_data['children'].values():
            main_entry['children'].append(sub_data)
        result.append(main_entry)

    return Response(result)

def calculate_percentile(sorted_data, percentile):
    if not sorted_data:
        return None
    index = (len(sorted_data) - 1) * Decimal(str(percentile))
    lower = int(index)
    upper = lower + 1
    if upper >= len(sorted_data):
        return sorted_data[lower]
    weight = index - lower
    return sorted_data[lower] * (Decimal(1) - weight) + sorted_data[upper] * weight

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def item_price_analysis(request):
    if not request.user.has_perm('almogOil.hozma_Dashboard'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )    
    try:
        prices = list(
            almogOil_models.Mainitem.objects
            .filter(buyprice__isnull=False)
            .values_list('buyprice', flat=True)
        )
        prices.sort()

        price_stats = {
            'avg_price': almogOil_models.Mainitem.objects.aggregate(avg=Avg('buyprice'))['avg'],
            'min_price': almogOil_models.Mainitem.objects.aggregate(min=Min('buyprice'))['min'],
            'max_price': almogOil_models.Mainitem.objects.aggregate(max=Max('buyprice'))['max'],
            'price_stddev': almogOil_models.Mainitem.objects.aggregate(stddev=StdDev('buyprice'))['stddev'],
            'median_price': calculate_percentile(prices, 0.5),
            'q1': calculate_percentile(prices, 0.25),
            'q3': calculate_percentile(prices, 0.75),
        }

        scatter_data = (
            almogOil_models.Mainitem.objects
            .filter(buyprice__isnull=False, itemvalue__isnull=False)
            .values_list('buyprice', 'itemvalue')[:500]
        )

        return Response({
            'price_stats': price_stats,
            'scatter_data': list(scatter_data),
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def item_source_analysis(request):
    if not request.user.has_perm('almogOil.hozma_Dashboard'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )     
    try:
        # Annotate lead time
        items_with_lead_time = (
            almogOil_models.Mainitem.objects
            .exclude(source__isnull=True)
            .annotate(
                lead_time=ExpressionWrapper(
                    F('buylastdate') - F('orderlastdate'),
                    output_field=DurationField()
                )
            )
        )

        # Aggregate source stats
        source_stats = (
            items_with_lead_time
            .values('source__name')
            .annotate(
                count=Count('fileid'),
                total_value=Sum(ExpressionWrapper(F('buyprice') * F('showed'), output_field=None)),
                avg_price=Avg('buyprice'),
                avg_lead_time=Avg('lead_time'),
            )
            .order_by('-count')
        )

        # Raw stats for replacement calculation
        all_sources = almogOil_models.Mainitem.objects.exclude(source__isnull=True).values('source__name')

        replacement_raw = (
            all_sources
            .annotate(
                total_count=Count('fileid'),
                replacement_count=Count('fileid', filter=Q(replaceno__isnull=False))
            )
        )

        # Calculate replacement rate safely in Python
        replacement_stats = []
        for row in replacement_raw:
            total = row['total_count']
            replacements = row['replacement_count']
            rate = (replacements / total * 100) if total > 0 else 0
            replacement_stats.append({
                'source__name': row['source__name'],
                'replacement_count': replacements,
                'total_count': total,
                'replacement_rate': rate,
            })

        return Response({
            'source_stats': list(source_stats),
            'replacement_stats': replacement_stats,
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def SalesAnalysisView(request):
    if not request.user.has_perm('almogOil.hozma_Dashboard'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        ) 
    # 1. Top 10 Clients by Total Purchases
    top_clients = (
        almogOil_models.SellinvoiceTable.objects
        .values('client_name', 'client_id')
        .annotate(
            total_purchase=Sum('amount'),
         
            total_quantity=Sum('quantity')
        )
        .order_by('-total_purchase')[:10]
    )

    # 2. Top 10 Items by Quantity Sold
    top_items = (
        almogOil_models.SellInvoiceItemsTable.objects
        .values('name', 'pno', 'company')
        .annotate(
            total_quantity=Sum('quantity'),
            total_price=Sum('dinar_total_price'),
           
        )
        .order_by('-total_quantity')[:10]
    )

    # 3. Monthly Sales Totals
    monthly_sales = (
        almogOil_models.SellinvoiceTable.objects
        .annotate(month=TruncMonth('date_time'))
        .values('month')
        .annotate(
            total_sales=Sum('amount'),
        
        )
        .order_by('month')
    )

    return Response({
        "top_clients": list(top_clients),
        "top_items": list(top_items),
        "monthly_sales": list(monthly_sales),
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def purchase_analysis(request):
    if not request.user.has_perm('almogOil.hozma_Dashboard'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )     
    # 1. Top 10 Vendors by Total Purchases
    top_vendors = (
        almogOil_models.Buyinvoicetable.objects
        .values('source', 'source_obj__name')  # assuming AllSourcesTable has a 'name' field
        .annotate(
            total_purchase=Sum('net_amount'),
            
            total_paid=Sum('amount')
        )
        .order_by('-total_purchase')[:10]
    )

    # 2. Top 10 Purchased Items by Quantity
    top_items = (
        almogOil_models.BuyInvoiceItemsTable.objects
        .values('name', 'pno', 'company')
        .annotate(
            total_quantity=Sum('quantity'),
            total_price=Sum('dinar_total_price'),
            total_cost=Sum('cost_total_price')
        )
        .order_by('-total_quantity')[:10]
    )

    # 3. Monthly Purchase Totals
    monthly_purchases = (
        almogOil_models.Buyinvoicetable.objects
        .annotate(month=TruncMonth('invoice_date'))
        .values('month')
        .annotate(
            total_purchased=Sum('amount'),
     
          
        )
        .order_by('month')
    )

    return Response({
        "top_vendors": list(top_vendors),
        "top_purchased_items": list(top_items),
        "monthly_purchases": list(monthly_purchases),
    })
       
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])  # Allow anonymous access
def unique_company_products(request):
    company_products = almogOil_models.Mainitem.objects \
        .exclude(companyproduct__isnull=True) \
        .exclude(companyproduct__exact='') \
        .values_list('companyproduct', flat=True) \
        .distinct()

    return Response(list(company_products))    
   
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def item_detail_api(request, pno):
    item = get_object_or_404(almogOil_models.Mainitem, pno=pno)
    return Response(products_serializers.MainitemSerializer(item).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_preorder_with_items_and_client(request, invoice_no):
    client_id = request.query_params.get("client_id")
    if not client_id:
        return Response({"error": "client_id is required"}, status=400)

    try:
        preorder = almogOil_models.PreOrderTable.objects.get(invoice_no=invoice_no, client=client_id)
    except almogOil_models.PreOrderTable.DoesNotExist:
        return Response({"error": "PreOrder not found for this client"}, status=404)

    serializer = wholesale_serializers.PreOrderTableSerializerCart(preorder)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_client_preorders(request):
    client_id = request.query_params.get("client_id")

    if not client_id:
        return Response({"error": "client_id is required"}, status=400)

    preorders = almogOil_models.PreOrderTable.objects.filter(client=client_id)



   
    serializer = wholesale_serializers.SimplePreOrderSerializer(preorders, many=True)
    return Response(serializer.data)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def update_client_info(request, clientid):
    try:
        client = almogOil_models.AllClientsTable.objects.get(clientid=clientid)
    except almogOil_models.AllClientsTable.DoesNotExist:
        return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

    updatable_fields = [
        "name", "address", "email", "website", "phone", "mobile",
        "geo_location",
    ]

    updated = False
    address_changed = False
    geo_changed = False

    for field in updatable_fields:
        if field in request.data:
            new_value = request.data[field]
            old_value = getattr(client, field)
            if new_value != old_value:
                setattr(client, field, new_value)
                updated = True
                if field == "address":
                    address_changed = True
                elif field == "geo_location":
                    geo_changed = True

    if updated:
        client.save()

        # Check if address or geo_location changed
        if address_changed or geo_changed:
            message_body = f"تم تغيير معلومات العميل:\n"
            if address_changed:
                message_body += f"- العنوان الجديد: {client.address}\n"
            if geo_changed:
                message_body += f"- الموقع الجغرافي الجديد: {client.geo_location}\n"
            message_body += f"اسم العميل: {client.name}"

            # Send to client
            if client.mobile:
                send_whatsapp_message_via_green_api(client.mobile, message_body)

            # Send to head of company
            send_whatsapp_message_via_green_api("218942434823", message_body)

        return Response({"detail": "Client info updated successfully."}, status=status.HTTP_200_OK)

    return Response({"detail": "No data provided to update."}, status=status.HTTP_400_BAD_REQUEST)







@extend_schema(
    description="Retrieve all OEM table entries (no filtering, paginating, or caching).",
    responses={
        200: wholesale_serializers.OemTableSerializer(many=True)
    },
    tags=["OEM Table"],
)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])  # No authentication
def get_oem_table_data(request):
    if not request.user.has_perm('almogOil.hozma_Products'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )      
    oem_data = almogOil_models.Oemtable.objects.all()
    serializer = wholesale_serializers.OemTableSerializer(oem_data, many=True)
    return Response(serializer.data)









@extend_schema(
    description=(
        "Filter, paginate, and cache OEM table entries. "
        "Accepts POST payload with optional filter fields (`cname`, `cno`, `oemno`), "
        "plus pagination params (`page`, `page_size`). "
        "Results are cached for 5 minutes per unique filter+page combination."
    ),
    request=wholesale_serializers.OemTableSerializer,  # used only for documentation of filter fields
    responses={
        200: OpenApiResponse(
            response=wholesale_serializers.OemTableSerializer(many=True),
            description="Paginated list of filtered OEM entries (with `results`, `count`, `next`, `previous`)."
        )
    },
    parameters=[
        OpenApiParameter(
            name="page", description="Page number (optional, default=1).",
            type=OpenApiTypes.INT, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="page_size", description="Items per page (optional, default=20).",
            type=OpenApiTypes.INT, location=OpenApiParameter.QUERY
        ),
    ],
    tags=["OEM Table"],
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def cached_oemtable_list(request):
    if not request.user.has_perm('almogOil.hozma_Products'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )    
    """
    يستقبل فلترة عبر الـ POST:
        {
          "cname":  "...",
          "cno":    "...",
          "oemno":  "...",
          "page":        2,          # اختياري: يمكن أيضاً إرساله كـ query-param
          "page_size":  50           # اختياري
        }
    ويُعيد النتائج مقسّمة صفحات ومخزَّنة في الكاش.
    """
    # -------- بناء شروط الفلترة -------------
    filters = {}
    cname   = request.data.get('cname', '').strip()
    cno     = request.data.get('cno', '').strip()
    oemno   = request.data.get('oemno', '').strip()

    if cname:
        filters['cname__icontains'] = cname
    if cno:
        filters['cno__icontains'] = cno
    if oemno:
        filters['oemno__icontains'] = oemno

    # -------- مفاتيح الصفحة والحجم ----------
    page      = str(request.data.get('page') or request.query_params.get('page') or 1)
    page_size = str(request.data.get('page_size') or request.query_params.get('page_size') or 20)

    # -------- مفتاح الكاش  ------------------
    cache_key = f"oemtable:{hashlib.md5(str(filters).encode()).hexdigest()}:{page}:{page_size}"

    if cached := cache.get(cache_key):
        return Response(cached)

    # -------- جلب البيانات من قاعدة البيانات --
    queryset = almogOil_models.Oemtable.objects.filter(**filters).order_by('fileid')

    paginator = StandardResultsSetPagination()
    paginator.page_size = int(page_size)

    result_page = paginator.paginate_queryset(queryset, request)
    serializer  = wholesale_serializers.OemTableSerializer(result_page, many=True)
    response    = paginator.get_paginated_response(serializer.data).data

    # -------- تخزين في الكاش -----------------
    cache.set(cache_key, response, CACHE_TTL)

    return Response(response)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_item_categories_with_counts(request):
    categories = almogOil_models.ItemCategory.objects.all()
    data = []

    for category in categories:
        count = almogOil_models.Mainitem.objects.filter(item_category=category).count()
        data.append({
            'id': category.id,
            'name': category.name,
            'item_count': count,
        })

    return Response({'categories': data})    

@extend_schema(
    description=(
        "Send a WhatsApp message via Green API to a client. "
        "Requires `clientid` and `message` in the POST payload."
    ),
    request=wholesale_serializers.WhatsAppMessageSerializer,

    tags=["Messaging"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])             
@authentication_classes([CookieAuthentication])                 
def send_whatsapp_message(request):
    serializer = wholesale_serializers.WhatsAppMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    clientid = serializer.validated_data["clientid"]
    message  = serializer.validated_data["message"]

    try:
        client = almogOil_models.AllClientsTable.objects.get(clientid=clientid)
    except almogOil_models.AllClientsTable.DoesNotExist:
        return Response(
            {"detail": f"Client with ID {clientid} not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    number = client.mobile or client.phone
    if not number:
        return Response(
            {"detail": "No phone or mobile number found for this client."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        response = send_whatsapp_message_via_green_api(number, message)
    except Exception as e:
        return Response(
            {"detail": f"Failed to send message: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY
        )

    return Response(
        {
            "status": "sent",
            "client": clientid,
            "number": number,
            "green_api_response": response,
        },
        status=status.HTTP_200_OK
    )



@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_employee_image(request, pk):
    try:
        employee = almogOil_models.EmployeesTable.objects.get(employee_id=pk)
        serializer = almogOil_serializers.EmployeeImageUploadSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except almogOil_models.EmployeesTable.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    description=(
        "Create a new Terms and Conditions entry. "
        "If `is_active=True`, automatically deactivate any previously active terms."
    ),
    request=wholesale_serializers.TermsAndConditionsSerializer,
    responses={
        201: wholesale_serializers.TermsAndConditionsSerializer,
        400: OpenApiResponse(description="Validation errors."),
    },
    tags=["Terms & Conditions"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def create_terms_and_conditions(request):
    if not request.user.has_perm('almogOil.hozma_Settings'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )    
    serializer = wholesale_serializers.TermsAndConditionsSerializer(data=request.data)
    if serializer.is_valid():
        # Optional: deactivate previous active terms
        if serializer.validated_data.get("is_active", False):
            almogOil_models.TermsAndConditions.objects.filter(is_active=True).update(is_active=False)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    description=(
        "Update (or create) the active Return Policy. "
        "This view fetches the currently active `ReturnPolicy` instance and applies the provided data."
    ),
    request=wholesale_serializers.ReturnPolicySerializer,
    
    tags=["Return Policy"],
)
@api_view(["POST"])
@authentication_classes([CookieAuthentication])
@permission_classes([IsAuthenticated])
def return_policy_api_view(request):
    if not request.user.has_perm('almogOil.hozma_Settings'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    instance = almogOil_models.ReturnPolicy.objects.filter(is_active=True).first()
    serializer = wholesale_serializers.ReturnPolicySerializer(instance, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"success": True, "message": "تم تحديث سياسة الإرجاع بنجاح"})

    return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
"""
@api_view(['DELETE'])
@authentication_classes([CookieAuthentication])
@permission_classes([IsAuthenticated])
def delete_all_images(request):
    almogOil_models.Imagetable.objects.all().delete()
    return Response({'message': 'All images deleted successfully.'}, status=status.HTTP_200_OK)

"""

@extend_schema(
    summary="تصفية العملاء مع الفرز والتصفح",
    description="""
يقوم هذا الطلب بتصفية العملاء حسب حالة الاتصال (`is_online`) مع دعم للفرز مثل:
- الترتيب حسب عدد الطلبات أو المبلغ الإجمالي أو الاسم أو الأحدث/الأقدم.
""",
    tags=["Clients"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "page": {"type": "integer", "example": 1},
                "page_size": {"type": "integer", "example": 10},
                "is_online": {"type": "boolean", "example": True},
                "sort_by": {
                    "type": "string",
                    "example": "total_amount_desc",
                    "enum": [
                        "total_amount_desc", "total_amount_asc",
                        "orders_desc", "orders_asc",
                        "newest", "oldest",
                        "name_a_to_z", "name_z_to_a"
                    ]
                }
            }
        }
    },
    responses={
        200: OpenApiResponse(description="تم جلب العملاء بنجاح مع نتائج مفلترة.")
    }
)
@api_view(['POST'])
@authentication_classes([CookieAuthentication])
@permission_classes([IsAuthenticated])
def filter_clients(request):
    if not request.user.has_perm('almogOil.hozma_Clients'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        ) 
    data = request.data
    page = int(data.get('page', 1))
    page_size = int(data.get('page_size', 10))
    is_online = data.get('is_online', None)  # ممكن يكون 'true', 'false', أو None نص

    # تحويل is_online من نص إلى boolean إذا موجود
    if is_online is not None:
        if isinstance(is_online, str):
            if is_online.lower() == 'true':
                is_online = True
            elif is_online.lower() == 'false':
                is_online = False
            else:
                is_online = None  # تجاهل الفلتر إذا غير واضح

    sort_by = data.get('sort_by', 'name_asc')

    # إنشاء مفتاح كاش فريد حسب بيانات الطلب
    cache_key = f"filtered_clients_{hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    # جلب كل العملاء
    clients = almogOil_models.AllClientsTable.objects.all()
    online_count = clients.filter(is_online=True).count()

    # فلترة حسب حالة الأونلاين إذا محددة
    if is_online is not None:
        clients = clients.filter(is_online=is_online)

    # تعليق (annotate) العملاء بعدد الطلبات والمجموع الكلي
    clients = clients.annotate(
        total_orders=Count('preordertable'),
        total_amount=Sum('preordertable__amount')
    )

    # منطق الترتيب
    if sort_by == 'total_amount_desc':
        clients = clients.order_by('-total_amount')
    elif sort_by == 'total_amount_asc':
        clients = clients.order_by('total_amount')
    elif sort_by == 'orders_desc':
        clients = clients.order_by('-total_orders')
    elif sort_by == 'orders_asc':
        clients = clients.order_by('total_orders')
    elif sort_by == 'newest':
        clients = clients.order_by('-last_activity')
    elif sort_by == 'oldest':
        clients = clients.order_by('last_activity')
    elif sort_by == 'name_a_to_z':
        clients = clients.order_by('name')
    elif sort_by == 'name_z_to_a':
        clients = clients.order_by('-name')
    else:
        clients = clients.order_by('name')

    # تطبيق التقسيم إلى صفحات
    paginator = Paginator(clients, page_size)
    page_obj = paginator.get_page(page)

    # تهيئة السيرياليزر مع تمرير الطلب في context لتمكين روابط الصور
    serializer = wholesale_serializers.ClientInfoSerializer(page_obj, many=True, context={'request': request})

    response_data = {
        'total_clients': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'page_size': page_size,
        'online_clients_count': online_count,  # عدد العملاء أونلاين
        'results': serializer.data
    }

    # تخزين النتيجة في الكاش لمدة 5 دقائق
    cache.set(cache_key, response_data, timeout=300)

    return Response(response_data)


@extend_schema(
    summary="ملخص حالة فواتير الشراء",
    description="""
يعيد عدد الفواتير غير المؤكدة وعدد الفواتير التي لم يتم إرسالها بعد.
""",
    tags=["Invoices"],
    responses={
        200: OpenApiResponse(description="نجح في إرجاع إحصائيات الفواتير."),
        403: OpenApiResponse(description="غير مصرح لك بالوصول.")
    }
)
@api_view(['GET'])
@authentication_classes([CookieAuthentication])
@permission_classes([IsAuthenticated])
def get_invoice_status_summary(request):
    unconfirmed_count = almogOil_models.OrderBuyinvoicetable.objects.filter(confirmed=False).count()
    unsent_count = almogOil_models.OrderBuyinvoicetable.objects.filter(send=False).count()

    return Response({
        'unconfirmed_invoices': unconfirmed_count,
        'unsent_invoices': unsent_count
    })

@extend_schema(
    summary="عرض صور المنتج",
    description="يسترجع صور المنتج باستخدام رقم `pno`.",
    tags=["Products"],
    parameters=[
        OpenApiParameter(name='id', description="رقم المنتج (pno)", required=True, type=str)
    ],
    responses={
        200: OpenApiResponse(description="صور المنتج بنجاح"),
        404: OpenApiResponse(description="لم يتم العثور على المنتج")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_product_images(request, id):
    try:
        product = almogOil_models.Mainitem.objects.get(pno=id)
    except almogOil_models.Mainitem.DoesNotExist:
        return Response({"error": "Product not found!"}, status=404)

    images = almogOil_models.Imagetable.objects.filter(productid=product.fileid)
    serializer = products_serializers.productImageSerializer(images, many=True)

    return Response(serializer.data)

@extend_schema(
    summary="جلب قائمة الشركات",
    description="يرجع قائمة بجميع الشركات مع اسم الشركة وشعارها (أو صورة افتراضية).",
    tags=["Companies"],
    responses={
        200: OpenApiResponse(description="تم إرجاع قائمة الشركات")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_company_list(request):
    companies = almogOil_models.Companytable.objects.all()

    data = {
        "main_types": [
            {
                "typename": company.companyname or "بدون اسم",
                "logo_obj": company.logo_obj.url if company.logo_obj else "/media/default.png"
            }
            for company in companies
        ]
    }

    return Response(data)


@extend_schema(
description="""Get a specific client from db.""",
tags=["Clients"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_all_clients1(request,id=None):

    if request.method == 'GET':
        clients = almogOil_models.AllClientsTable.objects.all().filter(clientid=id)
        serializer = almogOil_serializers.AllClientsTableSerializer(clients, many=True)
        return Response({'clients': serializer.data})
    
@extend_schema(
    summary="إنشاء فاتورة طلب جديدة مع عنصر واحد على الأقل",
    description="""
ينشئ هذا الطلب فاتورة طلب جديدة (`PreOrder`) ويضيف عناصر إليها فوراً.

- يتم تحديد العميل إما بالرقم (`clientid`) أو بالاسم.
- يجب تمرير قائمة `items` مع كل عنصر يحتوي على `pno`, `fileid`, و `itemvalue`.

✅ هذا الطلب يقوم تلقائيًا بخصم الكمية من المخزون ويحدّث فاتورة شراء المورد المرتبطة.
""",
    tags=["PreOrder"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "client": {
                    "type": "string",
                    "description": "رقم العميل أو اسمه",
                    "example": "123"
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pno": {"type": "string", "example": "PNO-1001"},
                            "fileid": {"type": "integer", "example": 457},
                            "itemvalue": {"type": "integer", "example": 2}
                        },
                        "required": ["pno", "fileid", "itemvalue"]
                    }
                },
                "for_who": {
                    "type": "string",
                    "description": "منشأ الفاتورة (مثلاً: application)",
                    "example": "application"
                },
                "mobile": {
                    "type": "string",
                    "description": "رقم الهاتف المرتبط بالطلب (اختياري)",
                    "example": "+218912345678"
                },
                "payment_status": {
                    "type": "string",
                    "description": "حالة الدفع (اختياري)",
                    "example": "unpaid"
                }
            },
            "required": ["client", "items"]
        }
    },
    responses={
        201: OpenApiResponse(description="تم إنشاء الفاتورة بنجاح"),
        400: OpenApiResponse(description="حدث خطأ أثناء التحقق من البيانات"),
        403: OpenApiResponse(description="غير مصرح لك بالوصول")
    },
    examples=[
        OpenApiExample(
            name="طلب جديد",
            value={
                "client": "123",
                "items": [
                    {"pno": "PNO-1001", "fileid": 457, "itemvalue": 3},
                    {"pno": "PNO-1002", "fileid": 458, "itemvalue": 1}
                ],
                "for_who": "application",
                "payment_status": "unpaid"
            },
            request_only=True
        )
    ]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def create_preorder_with_item(request):
    data = request.data

    required_fields = ["client", "items"]
    if any(not data.get(f) for f in required_fields):
        return Response({"error": "يرجى تعبئة الحقول المطلوبة: العميل والعناصر."}, status=400)

    if not isinstance(data["items"], list) or not data["items"]:
        return Response({"error": "قائمة العناصر مطلوبة ويجب ألا تكون فارغة."}, status=400)

    try:
        with transaction.atomic():
            # === 1. Get Client ===
            client_identifier = data["client"]
            if str(client_identifier).isdigit():
                client_obj = almogOil_models.AllClientsTable.objects.get(clientid=int(client_identifier))
            else:
                client_obj = almogOil_models.AllClientsTable.objects.get(name=client_identifier)

            balance_data = almogOil_models.TransactionsHistoryTable.objects.filter(
                client_object_id=client_obj.clientid
            ).aggregate(
                total_debt=Sum('debt') or Decimal("0.0000"),
                total_credit=Sum('credit') or Decimal("0.0000")
            )

            total_debt = balance_data.get('total_debt') or Decimal('0.0000')
            total_credit = balance_data.get('total_credit') or Decimal('0.0000')
            client_balance = total_credit - total_debt

            # === 2. Validate All Items First ===
            validated_items = []
            for item in data["items"]:
                pno = item.get("pno")
                fileid = item.get("fileid")
                item_value = item.get("itemvalue")

                if not (pno and fileid and item_value):
                    raise ValueError("أحد العناصر يحتوي على بيانات غير مكتملة.")

                product = almogOil_models.Mainitem.objects.select_for_update().get(pno=pno, fileid=fileid)

                if int(item_value) > product.showed:
                    raise ValueError(
    f"الكمية المطلوبة للمنتج {product.itemname} (رقم القطعة: {product.pno}) غير متوفرة. الكمية المتاحة: {product.showed}"
)


                validated_items.append((product, int(item_value)))

            # === 3. Create Invoice ===
            last_receipt_no = get_last_PreOrderTable_no()
            for_who = "application" if data.get("for_who") == "application" else None

            invoice_data = {
                'invoice_no': last_receipt_no,
                'client': client_obj.clientid,
                'client_id': client_obj.clientid,
                'client_name': client_obj.name,
                'client_rate': client_obj.category,
                'client_category': client_obj.subtype,
                'client_limit': client_obj.loan_limit,
                'client_balance': client_balance,
                'invoice_date': timezone.now(),
                'invoice_status': "لم تشتري",
                'payment_status': data.get("payment_status"),
                'for_who': for_who,
                'date_time': timezone.now(),
                'price_status': "",
                'mobile': data.get("mobile") if data.get("mobile") else False,
                'amount': 0,
                'net_amount': 0
            }

            invoice_serializer = almogOil_serializers.PreOrderSerializer(data=invoice_data)
            invoice_serializer.is_valid(raise_exception=True)
            invoice = invoice_serializer.save()

            # === 4. Process Each Item ===
            total_amount = Decimal("0.000")
            for product, item_value in validated_items:
                buy_price = Decimal(item.get("sellprice") or product.buyprice or 0)

                discount = Decimal(client_obj.discount or 0)
                delivery_price = Decimal(client_obj.delivery_price or 0)

                # Update stock
                product.showed -= item_value
                product.save()

                dinar_total_price = buy_price * item_value
                total_amount += dinar_total_price

                # Save PreOrder Item
                item_data = {
                    'invoice_instance': invoice.autoid,
                    'invoice_no': invoice.invoice_no,
                    'item_no': product.oem_numbers,
                    'pno': product.pno,
                    'main_cat': product.itemmain,
                    'sub_cat': product.itemsubmain,
                    'name': product.itemname,
                    'company': product.companyproduct,
                    'company_no': product.replaceno,
                    'quantity': item_value,
                    'date': timezone.now(),
                    'place': product.itemplace,
                    'dinar_unit_price': product.buyprice,
                    'dinar_total_price': dinar_total_price,
                    'prev_quantity': product.showed + item_value,
                    "remaining": 0,
                    "returned": 0,
                    'current_quantity': product.showed,
                }
                 # When creating or updating buy_invoice items:
                print("itemname length:", len(product.itemname or ""), product.itemname)
                print("company length:", len(product.companyproduct or ""), product.companyproduct)
                print("company_no length:", len(product.replaceno or ""), product.replaceno)
 

    
                item_serializer = almogOil_serializers.PreOrderItemsSerializer(data=item_data)
                item_serializer.is_valid(raise_exception=True)
                item_serializer.save()
                
                # Update/Create Buy Invoice (same logic as before...)
                source_name = product.source.name if product.source else "Unknown"
                source_obj = product.source
                cost_price = Decimal(product.costprice or 0)
                

                buy_invoice = almogOil_models.OrderBuyinvoicetable.objects.filter(
                    source=source_name,
                    send=False,
                    confirmed=False
                ).first()

                if not buy_invoice:
                    shared_invoice_no = get_next_buy_invoice_no()
                    buy_invoice = almogOil_models.OrderBuyinvoicetable.objects.create(
                        source=source_name,
                        invoice_date=timezone.now(),
                        amount=0,
                        net_amount=0,
                        invoice_no=shared_invoice_no,
                        source_obj=product.source
                    )

                buy_invoice.related_preorders.add(invoice)

                existing_buy_item = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(
                    invoice_no=buy_invoice,
                    pno=product.pno
                ).first()

                if existing_buy_item:
                    new_total_quantity = existing_buy_item.Asked_quantity + item_value
                    existing_buy_item.Asked_quantity = new_total_quantity
                    existing_buy_item.dinar_total_price = new_total_quantity * buy_price
                    existing_buy_item.cost_total_price = new_total_quantity * cost_price
                    existing_buy_item.invoice_no2 = buy_invoice.invoice_no
                    existing_buy_item.date = timezone.now().date()
                    existing_buy_item.prev_quantity = product.itemvalue
                    existing_buy_item.main_cat = product.itemmain
                    existing_buy_item.sub_cat = product.itemsubmain
                    existing_buy_item.source = source_obj
                    existing_buy_item.save()
                else:
                    almogOil_models.OrderBuyInvoiceItemsTable.objects.create(
                        item_no=product.oem_numbers,
                        pno=product.pno,
                        sourrce_pno=product.source_pno,
                        oem=product.oem_numbers,
                        name=product.itemname,
                        company=product.companyproduct,
                        company_no=product.replaceno,
                        Asked_quantity=item_value,
                        date=timezone.now().date(),
                        quantity_unit="",
                        dinar_unit_price=product.costprice,
                        dinar_total_price=item_value * cost_price,
                        cost_unit_price=cost_price,
                        cost_total_price=item_value * cost_price,
                        prev_quantity=product.itemvalue,
                        current_buy_price=product.buyprice,
                        invoice_no2=buy_invoice.invoice_no,
                        invoice_no=buy_invoice,
                        main_cat=product.itemmain,
                        sub_cat=product.itemsubmain,
                        source=source_obj
                    )



                
                buy_invoice.buy_net_amount = total_amount
                buy_invoice.amount += item_value * cost_price
                buy_invoice.net_amount = buy_invoice.amount
                buy_invoice.save()
                invoice.related_buyorders.add(buy_invoice)

                # Optional: WhatsApp
               
                message = f"✅ تم إضافة {product.itemname}، الكمية {item_value}، لفاتورتك رقم {invoice.invoice_no}."
                send_whatsapp_message_via_green_api(invoice.client.mobile, message)

            # === 5. Finalize Invoice Total ===
            if total_amount < 300:
                    return Response({"error": "لا يمكن إنشاء الفاتورة لأن المبلغ الإجمالي أقل من 300 دينار."}, status=400)
            else:
                invoice.amount = total_amount
                invoice.net_amount = total_amount - (discount * total_amount) + delivery_price
                invoice.save()

            return Response({
                "success": True,
                "message": "تم إنشاء الفاتورة بنجاح.",
                "invoice_no": invoice.invoice_no,
            }, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

@extend_schema(
    summary="تحميل قائمة التعبئة للمورد",
    description="""
ينشئ ملف Excel يحتوي على بيانات قائمة التعبئة (Packing List) لفاتورة شراء محددة.

- يجب إرسال `invoice_no` كجزء من الطلب.
- يجب أن تكون الفاتورة مرتبطة بمورد (source_obj).
- يتم تضمين جميع العناصر المرتبطة بالفاتورة في ملف Excel المولد.

📦 يتم تحميل الملف بصيغة `.xlsx`.
""",
    tags=["Supplier Orders"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "invoice_no": {
                    "type": "string",
                    "example": "B12345",
                    "description": "رقم فاتورة الشراء المطلوبة لقائمة التعبئة"
                }
            },
            "required": ["invoice_no"]
        }
    },
    responses={
        200: OpenApiResponse(description="تم إنشاء ملف Excel لقائمة التعبئة"),
        400: OpenApiResponse(description="حقل invoice_no مفقود أو غير صالح"),
        404: OpenApiResponse(description="لم يتم العثور على الفاتورة أو العناصر المرتبطة"),
        500: OpenApiResponse(description="خطأ غير متوقع أثناء إنشاء الملف")
    },
    examples=[
        OpenApiExample(
            name="طلب صالح",
            value={"invoice_no": "B12345"},
            request_only=True
        )
    ]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def create_supplier_packing_list_api(request):
    if not request.user.has_perm('almogOil.hozma_BuyInvoices'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    invoice_no = request.data.get('invoice_no')
    
    if not invoice_no:
        return Response({'error': 'invoice_no is required'}, status=400)

    try:
        record = almogOil_models.OrderBuyinvoicetable.objects.get(
            invoice_no=invoice_no, 
            source_obj__isnull=False
        )
    except almogOil_models.OrderBuyinvoicetable.DoesNotExist:
        return Response({'error': 'Invoice not found'}, status=404)

    try:
        items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no=record)
        if not items.exists():
            return Response({'error': 'No items found for this invoice'}, status=404)

        # Prepare the packing list data
        invoice_date = record.send_date or timezone.now().date()
        packing_list_data = {
            'invoice_no': record.invoice_no,
            'date': invoice_date,
            'customer_name': record.source_obj.name if record.source_obj else '',
            'items': []
        }

        for item in items:
            packing_list_data['items'].append({
                'pno': item.pno,
                'name': item.name,
                'company': item.company,
                'Asked_quantity': item.Asked_quantity,
                'internal_code': getattr(item, 'sourrce_pno', ''),
                'company_code': getattr(item, 'company_no', ''),
                'original_code': getattr(item, 'oem', ''),
            })

        # Create the packing list Excel file
        excel_buffer = create_supplier_packing_list(packing_list_data)

        # Create response with the Excel file
        response = HttpResponse(
            excel_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=packing_list_{invoice_no}.xlsx'
        
        return response

    except Exception as e:
        return Response({'error': f'Error processing packing list: {str(e)}'}, status=500)


def create_supplier_packing_list(invoice_data):
    excel_buffer = BytesIO()
    workbook = xlsxwriter.Workbook(excel_buffer)
    worksheet = workbook.add_worksheet('قائمة تعبيئة')

    # Page setup for A4
    worksheet.set_paper(9)  # A4 paper
    worksheet.set_portrait()
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    worksheet.set_print_scale(90)
    worksheet.hide_gridlines(2)
    worksheet.fit_to_pages(1, 1)

    rtl_format = {'reading_order': 2}

    # Title format - larger font and more prominent
    title_format = workbook.add_format({
        **rtl_format,
        'bold': True,
        'font_size': 22,  # Increased from 18
        'align': 'center',
        'valign': 'vcenter',
        'font_name': 'Arial',
        'font_color': '#003366'
    })

    # Header info format - larger font
    header_format = workbook.add_format({
        **rtl_format,
        'font_size': 16,  # Increased from 14
        'align': 'right',
        'font_name': 'Arial',
        'valign': 'vcenter'
    })

    # Table header format - larger font
    table_header_format = workbook.add_format({
        **rtl_format,
        'bold': True,
        'font_size': 14,  # Increased from 12
        'bg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'font_name': 'Arial'
    })

    # Item cell formats - larger font
    item_cell_center = workbook.add_format({
        **rtl_format,
        'font_size': 14,  # Increased from 12
        'border': 1,
        'align': 'center',
        'font_name': 'Arial'
    })

    item_cell_right = workbook.add_format({
        **rtl_format,
        'font_size': 14,  # Increased from 12
        'border': 1,
        'align': 'right',
        'font_name': 'Arial'
    })

    # Write title with increased row height
    worksheet.merge_range('A1:G1', 'قائمة تعبيئة (المورد)', title_format)
    worksheet.set_row(0, 40)  # Increased from 30

    # Write header info with increased row heights
    worksheet.write('G2', f'التاريخ : {invoice_data["date"]}', header_format)
    worksheet.set_row(1, 25)  # Added row height
    worksheet.write('G3', f'فاتورة شراء رقم : {invoice_data["invoice_no"]}', header_format)
    worksheet.set_row(2, 25)  # Added row height
    worksheet.write('G4', f'اسم المورد : {invoice_data["customer_name"]}', header_format)
    worksheet.set_row(3, 25)  # Added row height

    # Write empty row for spacing with increased height
    worksheet.set_row(4, 20)  # Increased from 15

    # Table headers
    headers = [
        '(+/-)',
        'جرد',
        'الكمية',
        'الرقم الأصلي',
        'رقم الشركة',
        'بيان الصنف',
        'رقم الصنف م',
        'الرقم الخاص'
    ]

    # Write table headers with increased row height
    for col, header in enumerate(headers):
        worksheet.write(5, col, header, table_header_format)
    worksheet.set_row(5, 30)  # Increased table header row height

    # Write items with increased row heights
    row = 6
    for item in invoice_data['items']:
        worksheet.write(row, 0, '', item_cell_center)  # (+/-)
        worksheet.write(row, 1, '', item_cell_center)  # جرد
        worksheet.write(row, 2, item.get('Asked_quantity', 0), item_cell_center)  # الكمية
        worksheet.write(row, 3, item.get('original_code', ''), item_cell_center)  # الرقم الأصلي
        worksheet.write(row, 4, item.get('company_code', ''), item_cell_center)  # رقم الشركة
        worksheet.write(row, 5, f"{item.get('name', '')} / {item.get('company', '')}", item_cell_right)  # بيان الصنف
        worksheet.write(row, 6, item.get('internal_code', ''), item_cell_center)  # رقم الصنف م
        worksheet.write(row, 7, item.get('pno', ''), item_cell_center)  # الرقم الخاص

        worksheet.set_row(row, 35)  # Increased from 25
        row += 1

    # Set column widths (adjusted slightly for larger fonts)
    worksheet.set_column('H:H', 12)  # (+/-)
    worksheet.set_column('G:G', 12)  # جرد
    worksheet.set_column('F:F', 55)  # الكمية (wider for larger font)
    worksheet.set_column('E:E', 18)  # الرقم الأصلي
    worksheet.set_column('D:D', 18)  # رقم الشركة
    worksheet.set_column('C:C', 12)  # بيان الصنف
    worksheet.set_column('B:B', 12)  # رقم الصنف م
    worksheet.set_column('A:A', 12)  # الرقم الخاص

    workbook.close()
    excel_buffer.seek(0)
    return excel_buffer

@extend_schema(
    summary="تحميل فاتورة شراء",
    description="""
ينشئ ملف Excel يمثل فاتورة شراء معينة بصيغة مفصلة ومنسقة (غالبًا باللغة العربية).

- يجب إرسال `invoice_no` ضمن جسم الطلب لتحديد الفاتورة.
- يجب أن تحتوي الفاتورة على مصدر محدد (`source_obj`).
- يتم استخراج كل العناصر التابعة للفاتورة وتنسيقها في ملف Excel.

📥 يتم إرسال الملف للتحميل مباشرة.
""",
    tags=["Supplier Orders"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "invoice_no": {
                    "type": "string",
                    "example": "INV-2024-0012",
                    "description": "رقم الفاتورة المراد تحميلها"
                }
            },
            "required": ["invoice_no"]
        }
    },
    responses={
        200: OpenApiResponse(description="تم إنشاء الفاتورة وتحميلها بنجاح كملف Excel"),
        400: OpenApiResponse(description="الطلب غير صالح أو رقم الفاتورة مفقود"),
        404: OpenApiResponse(description="لم يتم العثور على الفاتورة أو العناصر"),
        500: OpenApiResponse(description="حدث خطأ أثناء إنشاء ملف الفاتورة")
    },
    examples=[
        OpenApiExample(
            name="مثال طلب صحيح",
            value={"invoice_no": "INV-2024-0012"},
            request_only=True
        )
    ]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def download_invoice(request):
    if not request.user.has_perm('almogOil.hozma_BuyInvoices'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )      

    # Extract the invoice number from the request body
    invoice_no = request.data.get('invoice_no')

    if not invoice_no:
        return Response({'error': 'invoice_no is required'}, status=400)

    try:
        # Fetch the invoice record from the database
        record = almogOil_models.OrderBuyinvoicetable.objects.get(
            invoice_no=invoice_no, 
            source_obj__isnull=False
        )
    except almogOil_models.OrderBuyinvoicetable.DoesNotExist:
        return Response({'error': 'Invoice not found'}, status=404)

    try:
        # Get the invoice items
        items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no=record)
        if not items.exists():
            return Response({'error': 'No items found for this invoice'}, status=404)

        # Prepare the invoice data
        invoice_data = prepare_invoice_data(record, items)

        # Create an Excel file with Arabic formatting
        excel_buffer = create_excel_invoice(invoice_data)

        # Create response with Excel file
        response = HttpResponse(
            excel_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=invoice_{invoice_no}.xlsx'
        return response

    except Exception as e:
        return Response({'error': f'Error generating invoice: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def assign_preorder(request):
    if not request.user.has_perm('almogOil.prepare_input_sellinvoice'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )       
    serializer = wholesale_serializers.AssignPreOrderSerializer(data=request.data)
    if serializer.is_valid():
        preorder = serializer.validated_data['preorder']
        employee = serializer.validated_data['employee']

        preorder.assigned_employee = employee
        preorder.delivery_status = 'assigned'
        preorder.delivery_start_time = timezone.now()
        preorder.save()

        return Response({'success': True, 'message': f"Order assigned to {employee.name}."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def my_assigned_orders(request):
    try:
        emp = almogOil_models.EmployeesTable.objects.get(phone=request.user, type='driver')
    except almogOil_models.EmployeesTable.DoesNotExist:
        return Response({'error': 'Not authorized as delivery employee'}, status=403)

    orders = almogOil_models.PreOrderTable.objects.filter(
    assigned_employee=emp
).exclude(
    delivery_status='delivered'
).order_by('-invoice_date')
    serializer = wholesale_serializers.driverPreOrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def list_drivers(request):
    drivers = almogOil_models.EmployeesTable.objects.filter(type='driver', active=True)
    data = [{'id': d.employee_id, 'name': d.name} for d in drivers]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def list_unassigned_preorders(request):
    preorders = almogOil_models.PreOrderTable.objects.filter(delivery_status='not_assigned')
    data = [{'id': p.autoid, 'invoice_no': p.invoice_no} for p in preorders]
    return Response(data)


@api_view(['GET'])
def get_invoice_items(request, invoice_no):
    items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_no=invoice_no)
    if not items.exists():
        return Response({'error': 'No items found for this invoice.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = wholesale_serializers.DeleveryPreOrderItemSerializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)    

@extend_schema(
    summary="طباعة فواتير البيع",
    description="""
يطبع فواتير البيع إما لفواتير اليوم أو لفاتورة محددة حسب `label`.

- `label = today_sell_invoice`: طباعة كل فواتير اليوم.
- `label = specific_sell_invoice`: يتطلب أيضًا `invoice_no`.

يُرسل التقرير إلى خادم الطباعة المخصص.
""",
    request=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            "طباعة فواتير اليوم",
            value={"label": "today_sell_invoice"},
            request_only=True
        ),
        OpenApiExample(
            "طباعة فاتورة محددة",
            value={"label": "specific_sell_invoice", "invoice_no": "12345"},
            request_only=True
        )
    ],
    responses={200: OpenApiResponse(description="تم إرسال التقرير للطباعة بنجاح")}
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
@authentication_classes([CookieAuthentication])  # Replace with your CookieAuthentication
def print_api_preorder(request):
    label = request.data.get("label")
    by_employee = request.session.get("name", "Unknown User") if request.user.is_authenticated else "Unknown User"
    today = timezone.now().date()

    if label == "today_sell_invoice":
        invoices = almogOil_models.PreOrderTable.objects.filter(date_time__date=today)
        serializer = wholesale_serializers.PREORDERPRINTSerializer(invoices, many=True)

        PRINTABLE_FIELDS = {
            "invoice_no": "رقم الفاتورة",
            "date_time": "تاريخ الفاتورة",
            "client_name": "اسم الزبون",
            "amount": "المبلغ",
            "discount": "الخصم",
            "net_amount": "الصافي",
        }

        filtered_data = filter_fields(serializer.data, PRINTABLE_FIELDS, date_fields=["date_time"])
        total = sum(inv.amount for inv in invoices) or 0

        payload = {
            "report_title": "فواتير بيع - اليوم",
            "by_employee": by_employee,
            "company_name": "شركة مارين لاستيراد قطع غيار السيارات و زيوتها",
            "document_number": "#",
            "text_statement": "",
            "report_sections": [{
                "title": "فواتير بيع - اليوم",
                "headers": list(filtered_data[0].keys()) if filtered_data else [],
                "rows": [list(d.values()) for d in filtered_data],
                "totals": [{"total": float(total), "total_label": "إجمالي"}],
            }],
        }
        return post_to_print_server(payload, request)

    elif label == "specific_sell_invoice":
        invoice_no = request.data.get("invoice_no")
        if not invoice_no:
            return Response({"error": "invoice_no is required"}, status=400)

        try:
            invoice = almogOil_models.PreOrderTable.objects.get(invoice_no=invoice_no)
            items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance=invoice)
            serializer = wholesale_serializers.PreOrderItemsTableSerializer(items, many=True)

            PRINTABLE_FIELDS = {
                "pno": "ر. خ",
                "name": "اسم الصنف",
                "dinar_unit_price": "سعر القطعة",
                "quantity": "الكمية",
                "dinar_total_price": "الاجمالي",
            }

            filtered_data = filter_fields(serializer.data, PRINTABLE_FIELDS)
            total = sum(item.dinar_total_price or 0 for item in items)

            payload = {
                "report_title": f"فاتورة بيع - {invoice_no}",
                "by_employee": by_employee,
                "company_name": "منصة حزمة",
                "document_number": str(invoice_no),
                "text_statement": f"""
                العميل: {invoice.client_name or "غير محدد"}،
                التاريخ: {invoice.date_time.strftime('%d/%m/%Y') if invoice.date_time else "غير متوفر"}،
                الحالة: {invoice.invoice_status or "غير محددة"}،
               
                """,
                "report_sections": [{
                    "title": f"فاتورة بيع - {invoice_no}",
                    "headers": list(filtered_data[0].keys()) if filtered_data else [],
                    "rows": [list(d.values()) for d in filtered_data],
                    "totals": [{"total": float(total), "total_label": "إجمالي"}],
                }],
            }
            return post_to_print_server(payload, request)
        except almogOil_models.PreOrderTable.DoesNotExist:
            return Response({"error": "Invoice not found"}, status=404)

    

    return Response({"error": "Invalid label"}, status=400)
@extend_schema(
    summary="عرض السائقين المتاحين",
    description="يعرض قائمة السائقين المتاحين للتوصيل لفاتورة محددة.",
    tags=["driver"],
    parameters=[
        OpenApiParameter("invoice_no", OpenApiTypes.INT, OpenApiParameter.PATH, required=True, description="رقم الفاتورة")
    ],
    responses={
        200: OpenApiResponse(description="قائمة السائقين المتاحين والفاتورة"),
        404: OpenApiResponse(description="لم يتم العثور على الفاتورة")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def available_drivers(request, invoice_no):
    if not request.user.has_perm('almogOil.prepare_input_sellinvoice'):  # change 'almogOil' to your app name
       return Response(
        {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
        status=status.HTTP_403_FORBIDDEN
    ) 
    """Get available drivers for a specific order"""
    # First verify the order exists
    order = get_object_or_404(almogOil_models.PreOrderTable, invoice_no=invoice_no)
    
    # Get available drivers
    drivers = almogOil_models.EmployeesTable.objects.filter(
        type='driver',
        
        
        is_available = True
    )
    
    return Response({
        'order':  wholesale_serializers.PreOrderTableSerializer(order).data,
        'available_drivers':  wholesale_serializers.EmployeesTableSerializer(drivers, many=True).data
    })
@extend_schema(
    summary="تعيين سائق للفاتورة",
    description="يعين سائق معين لطلب توصيل باستخدام `driver_id`.",
    tags=["driver"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "driver_id": {"type": "integer", "example": 15}
            },
            "required": ["driver_id"]
        }
    },
    responses={
        200: OpenApiResponse(description="تم تعيين السائق بنجاح"),
        404: OpenApiResponse(description="السائق أو الفاتورة غير موجودة"),
        400: OpenApiResponse(description="مدخلات غير صحيحة")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def assign_driver(request, invoice_no):
    if not request.user.has_perm('almogOil.prepare_input_sellinvoice'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    """Assign a driver to a specific order"""
    order = get_object_or_404(almogOil_models.PreOrderTable, invoice_no=invoice_no)
    driver_id = request.data.get('driver_id')
    
    if not driver_id:
        return Response(
            {"error": "Driver ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    driver = get_object_or_404(almogOil_models.EmployeesTable, pk=driver_id)
    
    # Update order with driver assignment
    order.assigned_employee = driver
    order.delivery_status = 'assigned'
    order.delivery_start_time = timezone.now()
    order.invoice_status = 'في الطريق'

    order.save()
    
    # Update driver status
    driver.has_active_order = True
    driver.is_available = True  # Assuming you want to mark the driver as unavailable
    driver.save()
    
    return Response({
        "message": f"Order {order.invoice_no} assigned to {driver.name}",
        "order": wholesale_serializers.PreOrderTableSerializer(order).data,
        "driver": wholesale_serializers.EmployeesTableSerializer(driver).data
    })

@extend_schema(
    summary="تأكيد تسليم الطلب",
    description="""
يؤكد تسليم الطلب ويحدث كميات العناصر. 
إذا تم تقليل كميات، يتم تحديث كل من SellInvoice و PreOrder، وإرسال إشعار واتساب.

✅ لا حاجة لإرسال بيانات إضافية — يعتمد فقط على `order_id`.
""",
    tags=["driver"],
    parameters=[
        OpenApiParameter("order_id", OpenApiTypes.INT, OpenApiParameter.PATH, required=True)
    ],
    responses={
        200: OpenApiResponse(description="تم التأكيد بنجاح"),
        400: OpenApiResponse(description="حدث خطأ أثناء التأكيد")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def update_items(request):
    if not request.user.has_perm('almogOil.hozma_driver'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )       
    if not request.user.has_perm('almogOil.hozma_driver'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    """Update delivered quantities for order items"""
    try:
        invoice_no = request.data.get('invoice_no')
        items = request.data.get('items', [])
        
        # Validate all items belong to this order and employee
        order = almogOil_models.PreOrderTable.objects.get(
            invoice_no=invoice_no,
            
        )
        
        # Update quantities
        for item_data in items:
            almogOil_models.PreOrderItemsTable.objects.filter(
                pno=item_data['item_id'],
                invoice_instance=order
            ).update(
                confirmed_delevery_quantity=item_data['delivered_quantity']
            )
        
        return Response({'status': 'success'})
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
@extend_schema(
    summary="تحديث الكميات المسلمة للعناصر",
    description="يقوم بتحديث الكمية التي تم تسليمها فعليًا لكل صنف في الفاتورة.",
    tags=["driver"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "invoice_no": {"type": "string", "example": "INV-2025-123"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_id": {"type": "string", "example": "PNO123"},
                            "delivered_quantity": {"type": "integer", "example": 3}
                        }
                    }
                }
            }
        }
    },
    responses={
        200: OpenApiResponse(description="تم التحديث بنجاح"),
        400: OpenApiResponse(description="خطأ في الطلب")
    }
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def confirm_delivery(request, order_id):
    if not request.user.has_perm('almogOil.hozma_driver'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )   
    """Mark an order as delivered with complete quantity handling"""
    if not request.user.has_perm('almogOil.hozma_driver'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        # Get employee and order
        employee = almogOil_models.EmployeesTable.objects.get(phone=request.user)
        order = almogOil_models.PreOrderTable.objects.get(
            autoid=order_id,
            assigned_employee=employee
        )

        # Get all items for this order
        items = almogOil_models.PreOrderItemsTable.objects.filter(
            invoice_instance=order
        )

        # Track if any quantities were reduced
        reduced_items = []
        
        # First pass: Update quantities and check for reductions
        for item in items:
            if item.confirmed_delevery_quantity is None:
                item.confirmed_delevery_quantity = item.confirm_quantity
                item.save()
            elif item.confirmed_delevery_quantity < item.confirm_quantity:
                reduced_items.append(item)
                
        # If any quantities were reduced, process updates
        if reduced_items:
            # 1. Send WhatsApp notification
            message_body = "تم تغيير الكميات في الفاتورة:\n"
            for item in reduced_items:
                quantity_diff = item.confirm_quantity - item.confirmed_delevery_quantity
                reduction_amount = quantity_diff * item.dinar_unit_price
                message_body += (f"- {item.name}: تم تخفيض {quantity_diff} وحدة "
                               f"(قيمة التخفيض: {reduction_amount} دينار)\n")
            
            send_whatsapp_message_via_green_api("218942434823", message_body)

            # 2. Update SellInvoice and SellInvoiceItems
            try:
                sell_invoice = almogOil_models.SellinvoiceTable.objects.get(
                    invoice_no=order.invoice_no
                )
                

                discount = sell_invoice.client_obj.discount or 0
                delivery_price = sell_invoice.client_obj.delivery_price or 0
                # Initialize with current totals
                total_amount = sell_invoice.amount
                net_amount = sell_invoice.net_amount
                
                for item in reduced_items:
                    # Update SellInvoiceItems
                    sell_item = almogOil_models.SellInvoiceItemsTable.objects.get(
                        invoice_instance=sell_invoice,
                        pno=item.pno
                    )
                    
                    # Calculate the quantity difference and reduction amount
                    quantity_diff = item.confirm_quantity - item.confirmed_delevery_quantity
                    reduction_amount = quantity_diff * item.dinar_unit_price
                    
                    # Update the sell invoice item
                    sell_item.quantity = item.confirmed_delevery_quantity
                    sell_item.dinar_total_price = item.dinar_unit_price * item.confirmed_delevery_quantity
                    sell_item.save()
                    
                    # Adjust totals by subtracting the reduction amount
                    total_amount -= reduction_amount
                    net_amount = total_amount - (discount * total_amount) + delivery_price
                
                # Update SellInvoice totals

                sell_invoice.amount = total_amount
                sell_invoice.net_amount = net_amount
                sell_invoice.save()
                
            except Exception as e:
                print(f"Error updating sell invoice: {str(e)}")

            # 3. Update PreOrder and PreOrderItems
            try:
                discount = order.client.discount or 0
                delivery_price = order.client.delivery_price or 0
                # Recalculate PreOrder totals
                total_amount = order.amount
                net_amount = order.net_amount
                
                for item in reduced_items:
                    # Calculate the quantity difference and reduction amount
                    quantity_diff = item.confirm_quantity - item.confirmed_delevery_quantity
                    reduction_amount = quantity_diff * item.dinar_unit_price
                    
                    # Update the preorder item's total price
                    item.dinar_total_price = item.dinar_unit_price * item.confirmed_delevery_quantity
                    item.save()
                    
                    # Adjust totals by subtracting the reduction amount
                    total_amount -= reduction_amount
                    net_amount = total_amount - (discount * total_amount) + delivery_price
                
                # Update PreOrder totals
                order.amount = total_amount
                order.net_amount = net_amount
                order.save()
                item.save()
                
            except Exception as e:
                print(f"Error updating preorder: {str(e)}")

        # Final order status update
        order.delivery_status = 'delivered'
        order.delivery_end_time = timezone.now()
        order.delvery_confirmed = True
        order.payment_status = 'تم الدفع'
        order.invoice_status = 'تم التوصيل'
        order.save()
        
        # Update employee status
        employee.has_active_order = False
        employee.is_available = True
        employee.save()

        return Response({
            'status': 'success',
            'message': 'Order delivered successfully',
            'reduced_items': len(reduced_items),
            'total_reduction': (sell_invoice.amount - total_amount) if reduced_items else 0
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@extend_schema(
    summary="تحديث حالة التوفر للموظف",
    description="يمكن للموظف تحديث حالته كمتاح أو غير متاح بنفسه.",
    tags=["driver"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "is_available": {
                    "type": "boolean",
                    "example": True,
                    "description": "تحديد ما إذا كان الموظف متاحًا حالياً أم لا"
                }
            },
            "required": ["is_available"]
        }
    },
    responses={
        200: OpenApiResponse(description="تم تحديث حالة التوفر بنجاح"),
        400: OpenApiResponse(description="طلب غير صالح"),
        404: OpenApiResponse(description="الموظف غير موجود")
    }
)
@api_view(['POST'])
@authentication_classes([CookieAuthentication])
@permission_classes([IsAuthenticated])
def set_employee_availability(request):
    if not request.user.has_perm('almogOil.hozma_driver'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        employee = almogOil_models.EmployeesTable.objects.get(phone=request.user)
    except almogOil_models.EmployeesTable.DoesNotExist:
        return Response({"detail": "الموظف غير موجود."}, status=status.HTTP_404_NOT_FOUND)

    serializer = wholesale_serializers.EmployeeAvailabilitySerializer(employee, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "تم تحديث حالة التوفر بنجاح."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    summary="التحقق من حالة توفر الموظف",
    description="يعرض ما إذا كان الموظف الحالي متاحًا أو غير متاح.",
    tags=["employee"],
    responses={
        200: OpenApiResponse(description="تم جلب حالة التوفر بنجاح"),
        404: OpenApiResponse(description="الموظف غير موجود"),
        401: OpenApiResponse(description="غير مصرح")
    }
)
@api_view(['GET'])
@authentication_classes([CookieAuthentication])
@permission_classes([IsAuthenticated])
def check_employee_availability(request):
    if not request.user.has_perm('almogOil.hozma_driver'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        employee = almogOil_models.EmployeesTable.objects.get(phone=request.user)
    except almogOil_models.EmployeesTable.DoesNotExist:
        return Response({"detail": "الموظف غير موجود."}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "is_available": employee.is_available,
        "message": "تم جلب حالة التوفر بنجاح."
    }, status=status.HTTP_200_OK)

    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def update_delivery_status(request, order_id):
    if not request.user.has_perm('almogOil.hozma_driver'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    """Update delivery status (e.g., to 'in_progress')"""
    try:
        employee = almogOil_models.EmployeesTable.objects.get(phone=request.user.username)
        
        order = almogOil_models.PreOrderTable.objects.get(
            autoid=order_id,
            assigned_employee=employee
        )
        
        status = request.data.get('status')
        if status in ['assigned', 'in_progress', 'delivered', 'cancelled']:
            order.delivery_status = status
            
            if status == 'in_progress' and not order.delivery_start_time:
                order.delivery_start_time = timezone.now()
            
            order.save()
        
        return Response({'status': 'success'})
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def update_client_price_discount(request, clientid):
    if not request.user.has_perm('almogOil.hozma_Clients'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        client = almogOil_models.AllClientsTable.objects.get(clientid=clientid)
    except almogOil_models.AllClientsTable.DoesNotExist:
        return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = wholesale_serializers.ClientPriceDiscountSerializer(client, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def client_details(request, clientId):
    try:
        client = almogOil_models.AllClientsTable.objects.get(clientid=clientId)
    except almogOil_models.AllClientsTable.DoesNotExist:
        return Response({'detail': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = wholesale_serializers.ClientDetailsSerializer(client)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def daily_report(request):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Base queryset for today sales
    today_sales_qs = almogOil_models.SellinvoiceTable.objects.filter(invoice_date__date=today)
    yesterday_sales_qs = almogOil_models.SellinvoiceTable.objects.filter(invoice_date__date=yesterday)

    # Aggregate total sales and invoices for today
    agg_basic = today_sales_qs.aggregate(
        total_sales=Sum('net_amount'),
        total_invoices=Count('invoice_no'),
    )

    # Sum paid_amount safely
    paid_amount_sum = today_sales_qs.aggregate(
        total_paid=Sum('paid_amount')
    )['total_paid']

    # Calculate remaining amount with ExpressionWrapper to avoid aggregate conflict
    remaining_amount_sum = today_sales_qs.aggregate(
        total_remaining=Sum(
            ExpressionWrapper(
                F('net_amount') - F('paid_amount'),
                output_field=DecimalField()
            )
        )
    )['total_remaining']

    today_sales = {
        'total_sales': agg_basic['total_sales'],
        'total_invoices': agg_basic['total_invoices'],
        'paid_amount': paid_amount_sum,
        'remaining_amount': remaining_amount_sum,
    }

    yesterday_sales = yesterday_sales_qs.aggregate(
        total_sales=Sum('net_amount')
    )

    total_sales = today_sales['total_sales'] or 0
    total_invoices = today_sales['total_invoices'] or 0
    average_sale = total_sales / total_invoices if total_invoices > 0 else 0

    sales_growth = 0
    if yesterday_sales['total_sales'] and today_sales['total_sales']:
        sales_growth = ((today_sales['total_sales'] - yesterday_sales['total_sales']) / yesterday_sales['total_sales']) * 100

    # Inventory Status
    low_stock_items = almogOil_models.Mainitem.objects.filter(itemvalue__lt=5).count()
    out_of_stock_items = almogOil_models.Mainitem.objects.filter(itemvalue=0).count()

    # Client Activity
    new_clients_today = almogOil_models.AllClientsTable.objects.filter(last_transaction=today).count()
    active_clients_today = almogOil_models.AllClientsTable.objects.filter(last_activity__date=today).count()

    top_clients = almogOil_models.AllClientsTable.objects.filter(
        sellinvoicetable_set__invoice_date__date=today
    ).annotate(
        total_spent=Sum('sellinvoicetable_set__net_amount')
    ).order_by('-total_spent')[:5]



    # Supplier Activity
    new_suppliers_today = almogOil_models.AllSourcesTable.objects.filter(last_transaction=today).count()
    purchase_orders_today = almogOil_models.Buyinvoicetable.objects.filter(invoice_date__date=today).aggregate(
        total_purchases=Sum('net_amount'),
        count=Count('invoice_no')
    )

    # Employee Performance
    employees_active_today = almogOil_models.EmployeesTable.objects.filter(
        attendance_table__date=today,
        attendance_table__absent=False
    ).count()

    top_performing_employees = almogOil_models.EmployeesTable.objects.filter(
        sellinvoicetable__invoice_date__date=today
    ).annotate(
        sales_count=Count('sellinvoicetable'),
        sales_amount=Sum('sellinvoicetable__net_amount')
    ).order_by('-sales_amount')[:3]

    # Financial Overview
    returns_today = almogOil_models.return_permission.objects.filter(date=today).aggregate(
        total_returns=Sum('amount')
    )
    buy_returns_today = almogOil_models.buy_return_permission.objects.filter(date=today).aggregate(
        total_returns=Sum('amount')
    )

    # Delivery Status
    deliveries_today = almogOil_models.SellinvoiceTable.objects.filter(
        delivered_date__date=today
    ).aggregate(
        delivered=Count('invoice_no', filter=Q(delivery_status='delivered')),
        pending=Count('invoice_no', filter=Q(delivery_status='pending')),
        in_progress=Count('invoice_no', filter=Q(delivery_status='in_progress'))
    )

    # Pre-Orders Status (Hozma)
    pre_orders_today = almogOil_models.PreOrderTable.objects.filter(invoice_date__date=today).aggregate(
        total=Count('invoice_no'),
        confirmed=Count('invoice_no', filter=Q(is_confirmed_by_client=True)),
        declined=Count('invoice_no', filter=Q(is_declined_by_client=True)),
        processing=Count('invoice_no', filter=Q(processing_status='processing')),
        waiting=Count('invoice_no', filter=Q(processing_status='waiting')),
        done=Count('invoice_no', filter=Q(processing_status='done'))
    )

    order_buy_orders = almogOil_models.OrderBuyinvoicetable.objects.filter(invoice_date__date=today).aggregate(
        total=Count('invoice_no'),
        amount=Sum('net_amount')
    )

    report = {
        "date": today,
        "sales_summary": {
            "today": today_sales,
            "average_sale": average_sale,
            "yesterday": yesterday_sales,
            "growth_percentage": sales_growth
        },
        "inventory": {
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items
        },
        "clients": {
            "new_clients_today": new_clients_today,
            "active_clients_today": active_clients_today,
            "top_clients": [
                {
                    "id": client.clientid,
                    "name": client.name,
                    "total_spent": client.total_spent
                } for client in top_clients
            ]
        },
        "suppliers": {
            "new_suppliers_today": new_suppliers_today,
            "purchase_orders": purchase_orders_today
        },
        "employees": {
            "active_today": employees_active_today,
            "top_performers": [
                {
                    "id": emp.employee_id,
                    "name": emp.name,
                    "sales_count": emp.sales_count,
                    "sales_amount": emp.sales_amount
                } for emp in top_performing_employees
            ]
        },
        "financials": {
            "returns": {
                "customer_returns": returns_today,
                "supplier_returns": buy_returns_today
            }
        },
        "deliveries": deliveries_today,
        "hozma_operations": {
            "pre_orders": pre_orders_today,
            "order_buy_orders": order_buy_orders
        }
    }

    return Response(report)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def employee_profile(request):
    try:
        # Assuming request.user is a phone number or user_id mapped to employee
        employee = almogOil_models.EmployeesTable.objects.get(phone=request.user)
        serializer = wholesale_serializers.EmployeeProfileSerializer(employee, context={'request': request})
        return Response(serializer.data)
    except almogOil_models.EmployeesTable.DoesNotExist:
        return Response({'detail': 'Employee not found.'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def delivery_history(request):
    if not request.user.has_perm('almogOil.hozma_driver'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    user_phone = str(request.user)

    # Get the employee
    try:
        employee = almogOil_models.PreOrderTable._meta.get_field('assigned_employee').related_model.objects.get(phone=user_phone)
    except almogOil_models.PreOrderTable._meta.get_field('assigned_employee').related_model.DoesNotExist:
        return Response([], status=200)

    # Filter only orders assigned to this employee
    orders = almogOil_models.PreOrderTable.objects.filter(
    assigned_employee=employee,
    delivery_status__in=['delivered', 'canceled']
).order_by('-invoice_date')


    # Optional filtering via query params
    filter_by = request.query_params.get('filter', 'all')
    now_time = now()
    today_start = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now_time - timedelta(days=7)

    if filter_by == 'delivered':
        orders = orders.filter(delivery_status='delivered')
    elif filter_by == 'cancelled':
        orders = orders.filter(delivery_status='cancelled')  # Make sure this status exists in your system
    elif filter_by == 'today':
        orders = orders.filter(Q(delivery_end_time__gte=today_start) | Q(invoice_date__gte=today_start))
    elif filter_by == 'week':
        orders = orders.filter(Q(delivery_end_time__gte=week_ago) | Q(invoice_date__gte=week_ago))
    
    serialized = wholesale_serializers.PreOrderSerializerOfDelvery(orders.order_by('-date_time'), many=True)
    return Response(serialized.data)        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_client_discount_and_delivery(request):

    user_identifier = str(request.user)  # يمكن أن يكون رقم الهاتف أو username حسب إعداداتك

    try:
        # البحث عن العميل بناءً على username أو phone
        client = almogOil_models.AllClientsTable.objects.get(phone=user_identifier)
    except almogOil_models.AllClientsTable.DoesNotExist:
        return Response({"error": "العميل غير موجود"}, status=404)

    discount = float(client.discount or 0)
    delivery_price = float(client.delivery_price or 0)

    return Response({
        "discount": discount,  # مثال: 0.1 يعني 10٪
        "delivery": delivery_price  # السعر الفعلي للتوصيل
    })   

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def create_mainitem_by_source_test(request):
    if not request.user.has_perm('almogOil.hozma_Products'):  # change 'almogOil' to your app name
        return Response(
            {"error": "ليس لديك الصلاحية لتأكيد ٫٫."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    data = request.data.copy()

    # Define required fields and their Arabic labels
    required_fields = {
        'oem_number': 'رقم OEM',
        'companyproduct': 'الشركة المصنعة',
        'buyprice': 'سعر الشراء',
        'showed': 'الكمية المعروضة',
        'source': 'المصدر', 
        'quantity_type': 'نوع الكمية'
    }

    # Check for missing fields
    missing = [arabic for key, arabic in required_fields.items() if not data.get(key)]
    
    if missing:
        return Response({'error': f'الحقول التالية مفقودة: {", ".join(missing)}'}, status=400)
       # ---------------------------------------------------------------------
    # 1) Handle quantity_type variations
    quantity_type = str(data.get('quantity_type', '')).strip().lower()
    if quantity_type not in {'single', 'box', 'pair'}:
        return Response(
            {'error': 'نوع الكمية يجب أن يكون single أو box أو pair'},
            status=400
        )

    # --- BOX -------------------------------------------------------------
    if quantity_type == 'box':
        itemperbox = data.get('itemperbox')
        try:
            itemperbox_int = int(itemperbox)
            if itemperbox_int <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {'error': 'يرجى إدخال itemperbox كعدد صحيح أكبر من صفر عند اختيار الكمية = box'},
                status=400
            )
        data['itemperbox'] = itemperbox_int          # keep as int
        data.pop('paired_oem', None)                 # not relevant

    # --- PAIR ------------------------------------------------------------
    elif quantity_type == 'pair':
        data.pop('itemperbox', None)
        
        oem_number = str(data.get('oem_number', '')).strip()
        paired_oem = str(data.get('paired_oem', '')).strip()

        if not oem_number:
            return Response({'error': 'رقم OEM مطلوب للعنصر الجديد.'}, status=400)

        if paired_oem:
            if paired_oem == oem_number:
                return Response({'error': 'لا يمكن إقران العنصر بنفسه'}, status=400)
            
            # Just store the OEM reference - signals will handle the linking
            data['paired_oem'] = paired_oem
            data.pop('paired_item', None)  # Let signal set this
    else:
        data.pop('paired_oem', None)
        data.pop('paired_item', None)

    try:
        
        company = str(data.get('companyproduct', '')).strip()
        company_validation = validate_company_name(company)
        if company_validation:
           return company_validation
        original_buyprice = Decimal(str(data.get('buyprice', '0'))).quantize(Decimal('0.0000'))
        showed = data.get('showed')
        source = str(data.get('source', '')).strip()
        discount = Decimal(str(data.get('discount') or '0'))
        discount_type = str(data.get('discount-type', 'source')).strip().lower()
        category_type = str(data.get('category_type', '')).strip()
        pno = str(data.get('pno') or '').strip()
        source_pno = str(data.get('source_pno') or pno).strip()
        oem_in = str(data.get('oem_number', ''))
        external_oem = str(data.get('external_oem', ''))
        all_oems = safe_csv(oem_in) + safe_csv(external_oem)
        oem_csv = ",".join(all_oems)


        
        incoming_oems = normalize_oem_list(oem_csv)

        replaceno = str(data.get('replaceno', '')).strip()
        if not almogOil_models.ItemCategory.objects.filter(name__iexact=category_type).exists():
            return Response({'error': f' صنف الفئة "{category_type}" غير موجودة في جدول التصنيفات'}, status=400)
        


        if discount > 0:
            discounted_buyprice = (original_buyprice - (original_buyprice * discount)).quantize(Decimal('0.0000'))
        else:
            discounted_buyprice = original_buyprice

        data['buyprice'] = str(discounted_buyprice)

        try:
            source_obj = almogOil_models.AllSourcesTable.objects.get(clientid__iexact=source)
            commission = Decimal(str(source_obj.commission)).quantize(Decimal('0.0000'))

            if discount_type == 'market':
                # Cost price remains based on original buyprice
                costprice = (original_buyprice - (original_buyprice * commission)).quantize(Decimal('0.0000'))
            else:
                # Default: cost price from discounted buyprice
                costprice = (discounted_buyprice - (discounted_buyprice * commission)).quantize(Decimal('0.0000'))

            data['costprice'] = str(costprice)
        except almogOil_models.AllSourcesTable.DoesNotExist:
            return Response({'error': f'المصدر "{source}" غير موجود في جدول الموردين'}, status=400)
        
        existing_product = almogOil_models.Mainitem.objects.filter(
            source__exact=source,
            source_pno__exact=source_pno
        ).first()

        if existing_product:
            update_data = {
                'showed': showed,
                'costprice': str(costprice),
                'buyprice': str(discounted_buyprice),
                'source_pno': source_pno,
                'oem_numbers': oem_csv
            }
            serializer = products_serializers.MainitemSerializer(
                existing_product,
                data=update_data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'تم تحديث الحقول: الكمية المعروضة، سعر التكلفة، وسعر الشراء للمنتج المطابق لنفس المورد ورقم الخص بالمورد.',
                    'data': data
                }, status=200)
            return Response(serializer.errors, status=400)

               # ❷ ــــ إذا لم يُوجد منتج مطابق لـ (source, source_pno) نتابع إنشاء/تحديث المنطق القديم
        #      يمكنك حذف كتلة if-pno القديمة بالكامل أو إبقاؤها كمعيار ثانوي إن أردت.
        #      هنا مثال سريع لجعلها معياراً ثانوياً:

        if pno:
            with transaction.atomic():
             existing_product = almogOil_models.Mainitem.objects.select_for_update().filter(pno=pno).first()
             if existing_product:
                update_data = {
                    'showed': showed,
                    'costprice': str(costprice),
                    'buyprice': str(discounted_buyprice),
                    'source_pno': source_pno,
                    'oem_numbers': oem_csv
                }
                serializer = products_serializers.MainitemSerializer(
                    existing_product,
                    data=update_data,
                    partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        'message': ' تم تحديث الحقول الكمية المعروضة، وسعر التكلفة، وسعر الشراء للمنتج الموجود مسبقًا',
                        'data': data
                    }, status=200)
                return Response(serializer.errors, status=400)

        with transaction.atomic():
            if not pno:
                last_product = almogOil_models.Mainitem.objects.order_by('-pno').first()
                if last_product:
                    try:
                        last_pno = int(last_product.pno)
                        pno = str(last_pno + 1)
                    except (ValueError, TypeError):
                        pno = '1000'
                else:
                    pno = '1000'
                data['pno'] = pno

            data['source_pno'] = source_pno

            oem_matches = []
            for row in almogOil_models.Oemtable.objects.all():
                existing_oems = normalize_oem_list(row.oemno) 
                if incoming_oems & existing_oems:  # Check if there is any intersection  
                    oem_matches.append(row) 



            if oem_matches:
                company_oem = None
                for match in oem_matches:
                    if match.cname.lower() == company.lower() or match.cno.lower() == replaceno.lower():
                        company_oem = match
                        break

                if company_oem:
                    all_oems = safe_csv(company_oem.oemno)
                    existing_items = almogOil_models.Mainitem.objects.filter(Q(companyproduct__iexact=company)
                                                                              | Q(replaceno__iexact=replaceno))
                    item_to_update = None
                    for item in existing_items:
                        item_oems = safe_csv(item.oem_numbers)
                        if set(item_oems) & set(all_oems):
                            item_to_update = item
                            break

                    if item_to_update:
                        if Decimal(str(item_to_update.buyprice)) > discounted_buyprice:
                            update_payload = data.copy()
                            update_payload['oem_numbers'] = company_oem.oemno
                            update_payload.pop('pno', None)
                            serializer = products_serializers.MainitemSerializer(
                                item_to_update, data=update_payload, partial=True
                            )
                            if serializer.is_valid():
                                instance = serializer.save()
                                instance.oem_numbers = company_oem.oemno
                                instance.save()
                                return Response({
                                    'message': 'تم تحديث المنتج الحالي بسعر أقل',
                                    'data': data
                                }, status=200)
                            return Response(serializer.errors, status=400)
                        return Response({
                            'message': 'المنتج الموجود لديه نفس السعر أو سعر أفضل',
                            'data': data
                        }, status=200)

                    data['oem_numbers'] = company_oem.oemno
                    data['itemno'] = oem_in  # 👈 ADD HERE
                    serializer = products_serializers.MainitemSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=201)
                    return Response(serializer.errors, status=400)

                else:
                    new_oem_row = almogOil_models.Oemtable.objects.create(
                        cname=company,
                        cno=replaceno,
                        oemno=oem_csv
                    )
                    data['oem_numbers'] = new_oem_row.oemno
                    data['itemno'] = oem_in  # 👈 ADD HERE

                    serializer = products_serializers.MainitemSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=201)
                    return Response(serializer.errors, status=400)

            else:
                new_oem_row = almogOil_models.Oemtable.objects.create(
                    cname=company,
                    cno=replaceno,
                    oemno=oem_csv
                )
                data['oem_numbers'] = new_oem_row.oemno
                data['itemno'] = oem_in  # 👈 ADD HERE
                serializer = products_serializers.MainitemSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=201)
                return Response(serializer.errors, status=400)

    except Exception as e:
        return Response({'error': f'حدث خطأ غير متوقع: {str(e)}'}, status=500)
  
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def update_driver_location(request):
    employee = get_object_or_404(almogOil_models.EmployeesTable, phone=request.user)

    lat = request.data.get('latitude')
    lng = request.data.get('longitude')

    if lat is None or lng is None:
        return Response({'error': 'Missing latitude or longitude'}, status=400)

    employee.current_latitude = lat
    employee.current_longitude = lng
    employee.last_updated = timezone.now()
    employee.save()

    return Response({'status': 'Location updated'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_employee_locations(request):
# Employees with valid location
    employees = almogOil_models.EmployeesTable.objects.filter(
        active=True,
        current_latitude__isnull=False,
        current_longitude__isnull=False
    ).exclude(current_latitude=0).exclude(current_longitude=0)

    # Clients with non-empty geo_location
    clients = almogOil_models.AllClientsTable.objects.filter(
        geo_location__isnull=False
    ).exclude(geo_location='').exclude(geo_location='0,0')

    employee_serializer = wholesale_serializers.EmployeeLocationSerializer(employees, many=True)
    client_serializer = wholesale_serializers.ClientLocationSerializer(clients, many=True)

    return Response({
        "employees": employee_serializer.data,
        "clients": client_serializer.data
    })