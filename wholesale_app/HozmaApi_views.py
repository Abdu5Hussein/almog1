from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import json
import random
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Count, Sum, Avg, F, Q, Case, When, Value,FloatField,  ExpressionWrapper, DurationField,CharField ,Min,Max,StdDev
from django.db.models.functions import TruncMonth, TruncDay
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import F, Q, Sum, IntegerField
from django.http import JsonResponse
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

def get_last_PreOrderTable_no():
    last_preorder = almogOil_models.PreOrderTable.objects.order_by("-invoice_no").first()
    last_sell = almogOil_models.SellinvoiceTable.objects.order_by("-invoice_no").first()

    last_preorder_no = last_preorder.invoice_no if last_preorder else 0
    last_sell_no = last_sell.invoice_no if last_sell else 0

    # Get the maximum of the two and add 1 to ensure uniqueness
    next_unique_invoice_no = max(last_preorder_no, last_sell_no) + 1

    return next_unique_invoice_no



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

            balance_data = almogOil_models.TransactionsHistoryTable.objects.filter(object_id=client_obj.clientid).aggregate(
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

@extend_schema(
description="""create a new pre-order item""",
tags=["PreOrder","PreOrder Items"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
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
                'item_no': product.itemno,
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
            item_no=item.item_no,
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

@api_view(["POST"])
@permission_classes([AllowAny])  # Allow access for any user
@authentication_classes([])  # No authentication required for this view
def send_test_whatsapp_message(request):
    """
    A REST API endpoint to send a WhatsApp message using Green API.
    This endpoint expects `to` and `body` parameters in the request body.
    """
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

 # Assuming you have this function
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def full_Sell_invoice_create_item(request):
    if request.method == "POST":
        try:
            data = request.data

            required_fields = ["pno", "fileid", "invoice_id", "itemvalue", "sellprice"]
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                product = almogOil_models.Mainitem.objects.get(pno=data.get("pno"), fileid=data.get("fileid"))
            except almogOil_models.Mainitem.DoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)



            try:
             invoice = almogOil_models.PreOrderTable.objects.get(invoice_no=data.get("invoice_id"))

             item_value = Decimal(data.get("itemvalue") or 0)
             buy_price = Decimal(product.buyprice or 0)
             line_total = buy_price * item_value

 
             invoice.amount += line_total

  
             discount = Decimal(invoice.client.discount or 0)
             delivery_price = Decimal(invoice.client.delivery_price or 0)
             amount = invoice.amount
             invoice.net_amount = amount - (discount * amount) + delivery_price

             invoice.save()
            except almogOil_models.PreOrderTable.DoesNotExist:
                return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

            item_value = int(data.get("itemvalue") or 0)
            if item_value > product.showed:
                # Handle insufficient quantity
                return Response({"error": "Insufficient quantity available"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if item_value < product.showed:
                  product_showed = product.showed - item_value
                  product.showed  = product_showed
                  product.save()
                  dinar_unit_price = Decimal(product.buyprice or 0)
                  dinar_total_price = dinar_unit_price * item_value

            # Create Sell Item
            item_data = {
                'invoice_instance': invoice.autoid,
                'invoice_no': data.get("invoice_id"),
                'item_no': product.itemno,
                'pno': data.get("pno"),
                'main_cat': product.itemmain,
                'sub_cat': product.itemsubmain,
                'name': product.itemname,
                'company': product.companyproduct,
                'company_no': product.eitemname,
                'quantity': item_value,
                'date': timezone.now(),
                'place': product.itemplace,
                'dinar_unit_price': product.buyprice,
                'dinar_total_price': dinar_total_price,
                'prev_quantity': product.showed,
                "remaining": 0,
                "returned": 0,
                'current_quantity': product.showed - item_value,
            }
            client_phone = invoice.client.mobile if invoice.client and invoice.client.mobile else "218942434823"
            source_name = product.source.name if product.source else "Unknown"


            serializer = almogOil_serializers.PreOrderItemsSerializer(data=item_data)
            if serializer.is_valid():
                serializer.save()

                # === BUY INVOICE LOGIC START ===
                source_obj = product.source

                buyitem_value = int(data.get("itemvalue") or 0)
                buy_dinar_unit_price = Decimal(product.costprice or 0)
                buy_dinar_total_price = buy_dinar_unit_price * buyitem_value

                # Try to get unconfirmed invoice for the source
                buy_invoice = almogOil_models.OrderBuyinvoicetable.objects.filter(
                    source=source_name,
                    send=False,
                    confirmed=False
                ).first()

                # If invoice would exceed 200, mark it as sent and create a new one

                    # force creation of new invoice

                # If no valid invoice exists, create a new one
                if not buy_invoice:
                   buy_invoice = almogOil_models.OrderBuyinvoicetable.objects.create(
                   source=source_name,
                   invoice_date=timezone.now(),
                   amount=0,
                   net_amount=0,
                   invoice_no=int(timezone.now().timestamp()),
                   source_obj=product.source
                   )

# Always add the preorder to the buy invoice (even if it already exists)
                buy_invoice.related_preorders.add(invoice)




                # Check if item already exists in BuyInvoiceItemsTable
                existing_buy_item = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(
                    invoice_no=buy_invoice,
                    pno=product.pno
                ).first()

                if existing_buy_item:
                    new_total_quantity = existing_buy_item.Asked_quantity + item_value
                    existing_buy_item.Asked_quantity = new_total_quantity
                    existing_buy_item.dinar_total_price = Decimal(new_total_quantity) * Decimal(product.buyprice or 0)
                    existing_buy_item.cost_total_price = Decimal(new_total_quantity) * Decimal(product.costprice or 0)
                    existing_buy_item.invoice_no2 = buy_invoice.invoice_no
                    existing_buy_item.date = timezone.now().date()
                    existing_buy_item.prev_quantity = product.itemvalue
                    existing_buy_item.main_cat = product.itemmain
                    existing_buy_item.sub_cat = product.itemsubmain
                    existing_buy_item.source = source_obj

                    existing_buy_item.save()
                else:
                    almogOil_models.OrderBuyInvoiceItemsTable.objects.create(
                        item_no=product.itemno,
                        pno=product.pno,
                        sourrce_pno=product.source_pno,
                        name=product.itemname,
                        company=product.companyproduct,
                        company_no=product.eitemname,
                        Asked_quantity=buyitem_value,
                        date=str(timezone.now().date()),
                        quantity_unit="",
                        dinar_unit_price=product.costprice,
                        dinar_total_price=buyitem_value * buy_dinar_unit_price,
                        cost_unit_price=buy_dinar_unit_price,
                        cost_total_price=buyitem_value * buy_dinar_unit_price,
                        prev_quantity=product.itemvalue,
                        current_buy_price=product.buyprice,
                        invoice_no2=buy_invoice.invoice_no,
                        invoice_no=buy_invoice,
                        main_cat=product.itemmain,
                        sub_cat=product.itemsubmain,
                        source=source_obj
                    )

                # Add total and save
                buy_invoice.amount = (buy_invoice.amount or 0) + buy_dinar_total_price
                buy_invoice.net_amount = buy_invoice.amount
                buy_invoice.save()

                # === BUY INVOICE LOGIC END ===

                message_body = (
                      f"👋 مرحبًا، تمت إضافة المنتج ({product.itemname}) إلى فاتورتك رقم {data.get('invoice_id')}.\n"
                      f"الكمية: {item_value}\n"
                      f"السعر للوحدة: {product.buyprice}\n"
                      f"الإجمالي: {dinar_total_price}\n"
                      f"📦 شكراً لتعاملك معنا!"
                        )


                response = send_whatsapp_message_via_green_api(client_phone, message_body)

                return Response({
                    "message": "Item created successfully.",
                    "item_id": serializer.instance.autoid,
                    "whatsapp_sent": "idMessage" in response if response else False,
                    "phone_number": client_phone,
                    "buy_invoice_send": buy_invoice.send,
                    "confirmation": buy_invoice.confirmed,
                    "buy_invoice_id": buy_invoice.invoice_no,
                    "source_name" : source_name,
                    "left item": product.showed
                }, status=status.HTTP_201_CREATED)

            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Invalid HTTP method. Only POST is allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
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
@permission_classes([AllowAny])
@authentication_classes([])
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
@permission_classes([AllowAny])
@authentication_classes([])
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
@permission_classes([AllowAny])
@authentication_classes([])
def confirm_or_update_preorderBuy_items(request):
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

    return Response({"success": True, "message": "PreOrder items confirmed and moved to buyinvoice."}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([AllowAny])  # Allow access for any user
@authentication_classes([])  # No authentication for this view
def send_unsent_invoices(request):
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
    invoice_date = record.send_date or timezone.now().date(),
    total_amount = float(record.amount) if hasattr(record, 'amount') else 0

    # Convert total amount to words (Libyan Dinar)
    total_in_words = num2words(total_amount, lang='ar') + ' دينار ليبي فقط لا غير'

    invoice_data = {
        'company_name': 'شركة مارين لاستيراد قطع غيار السيارات و زيوتها',
        'invoice_no': record.invoice_no,
        'date': invoice_date,
        'payment_type':  'آجلة',
        'customer_name': record.source_obj.name if record.source_obj else '',
        'customer_info': record.source_obj.address if record.source_obj else '',
        'items': [],
        'total': total_amount,
        'total_in_words': total_in_words,
        'notes': [
            '💻 زر موقعنا الإلكتروني الآن واستمتع بالعروض الحصرية: [www.hozma.com]',
    '📞 لمزيد من التفاصيل، يمكنك الاتصال بنا على الرقم: 123-456-7890.'
        ]
    }

    for item in items:
        invoice_data['items'].append({
            'pno': item.sourrce_pno,
            'name': item.name,
            'company': item.company,
            'Asked_quantity': item.Asked_quantity,
            'Confirmed_quantity': item.Confirmed_quantity,
            'dinar_unit_price': item.dinar_unit_price,
            'main_cat': item.main_cat,
            'sub_cat': item.sub_cat
        })

    return invoice_data


def create_excel_invoice(invoice_data):
    # Generate the Excel file
    excel_buffer = BytesIO()
    workbook = xlsxwriter.Workbook(excel_buffer)
    worksheet = workbook.add_worksheet('فاتورة')

    # Arabic formatting styles
    arabic_header_format = workbook.add_format({
        'bold': True,
        'font_size': 16,
        'align': 'center',
        'valign': 'vcenter',
        'font_name': 'Arial'
    })

    arabic_company_format = workbook.add_format({
        'bold': True,
        'font_size': 18,
        'align': 'center',
        'valign': 'vcenter',
        'font_name': 'Arial'
    })

    arabic_info_format = workbook.add_format({
        'font_size': 14,
        'align': 'right',
        'font_name': 'Arial'
    })

    arabic_table_header_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'bg_color': '#DDDDDD',
        'border': 1,
        'align': 'center',
        'font_name': 'Arial'
    })

    arabic_cell_format = workbook.add_format({
        'font_size': 12,
        'border': 1,
        'align': 'center',
        'font_name': 'Arial'
    })

    arabic_right_align_format = workbook.add_format({
        'font_size': 12,
        'border': 1,
        'align': 'right',
        'font_name': 'Arial'
    })

    arabic_currency_format = workbook.add_format({
        'font_size': 12,
        'border': 1,
        'align': 'center',
        'num_format': '#,##0.00 "د.ل"',
        'font_name': 'Arial'
    })

    # Write company header (bigger font)
    worksheet.merge_range('A1:F1', invoice_data['company_name'], arabic_company_format)

    # Write invoice info (bigger cells for invoice number)
    worksheet.merge_range('A3:B3', f'فاتورة شراء رقم : {invoice_data["invoice_no"]}', arabic_info_format)
    worksheet.write('C3', f'التاريخ : {invoice_data["date"]}', arabic_info_format)
    worksheet.write('D3', invoice_data['payment_type'], arabic_info_format)

    # Write customer info (bigger cells for customer name)
    worksheet.merge_range('A4:B4', f'اسم المورد : {invoice_data["customer_name"]}', arabic_info_format)
    worksheet.write('C4', invoice_data['customer_info'], arabic_info_format)

    # Write table headers
    headers = ['رقم الصنف', 'بيان الصنف', 'الكمية المطلوبة', 'الكمية المؤكدة', 'سعر الوحدة', 'التصنيف']
    for col, header in enumerate(headers):
        worksheet.write(5, col, header, arabic_table_header_format)

    # Write items
    row = 6
    for item in invoice_data['items']:
        worksheet.write(row, 0, item['pno'], arabic_cell_format)
        worksheet.write(row, 1, f"{item['name']} / {item['company'] if item['company'] else ''}", arabic_right_align_format)
        worksheet.write(row, 2, item['Asked_quantity'], arabic_cell_format)
        worksheet.write(row, 3, item['Confirmed_quantity'] if item['Confirmed_quantity'] else '-', arabic_cell_format)
        worksheet.write(row, 4, item['dinar_unit_price'], arabic_currency_format)
        worksheet.write(row, 5, f"{item['main_cat']} / {item['sub_cat']}", arabic_cell_format)
        row += 1

    # Write total amount in Libyan Dinar
    worksheet.write(row, 3, 'المبلغ الإجمالي:', arabic_table_header_format)
    worksheet.write(row, 4, invoice_data['total'], arabic_currency_format)
    row += 2

    # Write total in words (Libyan Dinar)
    worksheet.merge_range(f'A{row+1}:F{row+1}', f'فقط {invoice_data["total_in_words"]}', arabic_info_format)
    row += 2

    # Write notes
    for note in invoice_data['notes']:
        worksheet.write(row, 0, note, arabic_right_align_format)
        row += 1

    # Adjust column widths (larger for Arabic text)
    worksheet.set_column('A:A', 15)  # Wider for item numbers
    worksheet.set_column('B:B', 40)  # Much wider for Arabic descriptions
    worksheet.set_column('C:C', 20)  # Quantity columns wider
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 20)  # Price column
    worksheet.set_column('F:F', 25)  # Category column

    workbook.close()
    excel_buffer.seek(0)

    return excel_buffer



@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
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


@api_view(["PUT", "PATCH"])
@permission_classes([AllowAny])
@authentication_classes([])
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



@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])  # No authentication required
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


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def show_all_sources(request):
    sources = almogOil_models.AllSourcesTable.objects.all()
    serializer = almogOil_serializers.SourcesSerializer(sources, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def show_source_details(request, source_id):
    try:
        source = almogOil_models.AllSourcesTable.objects.get(clientid=source_id)
    except almogOil_models.AllSourcesTable.DoesNotExist:
        return Response({"detail": "Source not found."}, status=404)

    serializer = almogOil_serializers.SourcesSerializer(source)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([AllowAny])
@authentication_classes([])
def edit_source_info(request, source_id):
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
    return [v.strip() for v in (value or '').split(',') if v.strip()]


def normalize_oem_list(oem_string):
    return set(o.strip() for o in str(oem_string).split(',') if o.strip())


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def create_mainitem_by_source(request):
    data = request.data.copy()
    required = ['oem_number', 'companyproduct', 'buyprice', 'showed', 'source']
    if missing := [f for f in required if not data.get(f)]:
        return Response({'error': f'الحقول المفقودة: {", ".join(missing)}'}, status=400)

    try:
        
        company = str(data.get('companyproduct', '')).strip()
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
        oem_csv = ",".join(filter(None, [oem_in.strip(), external_oem.strip()]))

        
        incoming_oems = normalize_oem_list(oem_csv)

        eitemname = str(data.get('eitemname', '')).strip()
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
            return Response({'error': f'المصدر "{source}" غير موجود في جدول AllSourcesTable'}, status=400)
        
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
                    'message': 'تم تحديث الحقول showed و costprice و buyprice للمنتج المطابق لنفس المصدر و source_pno',
                    'data': data
                }, status=200)
            return Response(serializer.errors, status=400)

               # ❷ ــــ إذا لم يُوجد منتج مطابق لـ (source, source_pno) نتابع إنشاء/تحديث المنطق القديم
        #      يمكنك حذف كتلة if-pno القديمة بالكامل أو إبقاؤها كمعيار ثانوي إن أردت.
        #      هنا مثال سريع لجعلها معياراً ثانوياً:

        if pno:
            existing_product = almogOil_models.Mainitem.objects.filter(pno=pno).first()
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
                        'message': 'تم تحديث الحقول showed و costprice و buyprice للمنتج الموجود مسبقاً',
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
                    if match.cname.lower() == company.lower() or match.cno.lower() == eitemname.lower():
                        company_oem = match
                        break

                if company_oem:
                    all_oems = safe_csv(company_oem.oemno)
                    existing_items = almogOil_models.Mainitem.objects.filter(Q(companyproduct__iexact=company)
                                                                              | Q(eitemname__iexact=eitemname))
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
                    serializer = products_serializers.MainitemSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=201)
                    return Response(serializer.errors, status=400)

                else:
                    new_oem_row = almogOil_models.Oemtable.objects.create(
                        cname=company,
                        cno=eitemname,
                        oemno=oem_csv
                    )
                    data['oem_numbers'] = new_oem_row.oemno
                    serializer = products_serializers.MainitemSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=201)
                    return Response(serializer.errors, status=400)

            else:
                new_oem_row = almogOil_models.Oemtable.objects.create(
                    cname=company,
                    cno=eitemname,
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
@permission_classes([AllowAny])
@authentication_classes([])  # anonymous OK
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

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def web_filter_items(request):
     if request.method == "POST":
         try:
             # Get the filters from the request body
             filters = request.data  # Decoding bytes and loading JSON
             cache_key = f"filter_{hashlib.md5(str(filters).encode()).hexdigest()}"
             cached_data = cache.get(cache_key)

             if cached_data:
                 cached_data["cached_flag"] = True
                 return Response(cached_data, status=status.HTTP_200_OK)

             # Initialize the base Q object for filtering
             filters_q = Q()

             # Build the query based on the filters
             if filters.get('fileid'):
                 filters_q &= Q(fileid__icontains=filters['fileid'])
             if filters.get('itemno'):
                 filters_q &= Q(itemno__icontains=filters['itemno'])
             if filters.get('itemmain'):
                 filters_q &= Q(itemmain__icontains=filters['itemmain'])
             if filters.get('itemsubmain'):
                 filters_q &= Q(itemsubmain__icontains=filters['itemsubmain'])
             if filters.get('engine_no'):
                 filters_q &= Q(engine_no__icontains=filters['engine_no'])
             if filters.get('itemthird'):
                 filters_q &= Q(itemthird__icontains=filters['itemthird'])
             if filters.get('companyproduct'):
                 filters_q &= Q(companyproduct__icontains=filters['companyproduct'])
             if filters.get('itemname'):
                 filters_q &= Q(itemname__icontains=filters['itemname'])
             if filters.get('eitemname'):
                 filters_q &= Q(eitemname__icontains=filters['eitemname'])
             if filters.get('companyno'):
                 filters_q &= Q(replaceno__icontains=filters['companyno'])
             if filters.get('pno'):
                 filters_q &= Q(pno__icontains=filters['pno'])
             if filters.get('source'):
                 filters_q &= Q(ordersource__icontains=filters['source'])
             if filters.get('model'):
                 filters_q &= Q(itemthird__icontains=filters['model'])
             if filters.get('country'):
                 filters_q &= Q(itemsize__icontains=filters['country'])
             if filters.get('oem'):
                 filters_q &= Q(oem_numbers__icontains=filters['oem'])
             if filters.get('category'):
                 filters_q &= Q(category__icontains=filters['category'])
             if filters.get("item_type"):
                 filters_q &= Q(item_category__name__iexact=filters['item_type'])    
             if filters.get('discount') == "available":
                 filters_q &= Q(discount__isnull=False) & ~Q(discount=0)
             if filters.get("oem_combined"):
                 filters_q &= (
                       Q(oem_numbers__icontains=filters['oem_combined']) |
                       Q(eitemname__icontains=filters['oem_combined']))
                               

           # Original filters (replacing itemvalue with showed)
             if filters.get('showed') == "0":
                filters_q &= Q(showed=0)
             if filters.get('showed') == ">0":
                 filters_q &= Q(showed__gt=0)

# New availability logic (based on 'showed' field)
             availability = filters.get('availability')
             if availability == "not_available":
                filters_q &= Q(showed=0)
             elif availability == "limited":
                 filters_q &= Q(showed__lte=10, showed__gt=0)
             elif availability == "available":
                  filters_q &= Q(showed__gt=10)

# Replacing itemvalue-related logic
             if filters.get('resvalue') == ">0":
                 filters_q &= Q(rshowed__gt=0)
             if filters.get('showed_itemtemp') == "lte":
                 filters_q &= Q(showed__lte=F('itemtemp'))  # Compare fields

             # Apply date range filter on `orderlastdate`
             fromdate = filters.get('fromdate', '').strip()
             todate = filters.get('todate', '').strip()

             if fromdate and todate:
                 try:
                     from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                     to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)
                     filters_q &= Q(orderlastdate__range=[from_date_obj, to_date_obj])
                 except ValueError:
                     return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

             # Now filter the queryset using the combined Q object
             queryset = almogOil_models.Mainitem.objects.filter(filters_q).order_by('itemname')

             # Serialize the filtered data
             serializer = products_serializers.MainitemSerializer(queryset, many=True)
             items_data = serializer.data

             # Initialize totals
             total_itemvalue = total_itemvalueb = total_resvalue = total_cost = total_order = total_buy = 0

             # Calculate totals
             for item in items_data:
                    # Use safe conversion functions
                 itemvalue = float(item.get('itemvalue') or 0)
                 itemvalueb = float(item.get('itemvalueb') or 0)
                 resvalue = float(item.get('resvalue') or 0)
                 costprice = float(item.get('costprice') or 0)
                 orderprice = float(item.get('orderprice') or 0)
                 buyprice = float(item.get('buyprice') or 0)


                 total_itemvalue += itemvalue
                 total_itemvalueb += itemvalueb
                 total_resvalue += resvalue
                 total_cost += itemvalue * costprice
                 total_order += itemvalue * orderprice
                 total_buy += itemvalue * buyprice

             fullTable = filters.get('fullTable')
             if fullTable:
                 response = {
                     "data": items_data,
                     "fullTable": True,
                     "last_page": 1,
                     "total_rows": queryset.count(),
                     "page_no": 1,
                     "total_itemvalue": total_itemvalue,
                     "total_itemvalueb": total_itemvalueb,
                     "total_resvalue": total_resvalue,
                     "total_cost": total_cost,
                     "total_order": total_order,
                     "total_buy": total_buy,
                 }
                 return Response(response)

             # Pagination
             page_number = int(filters.get('page') or 1)
             page_size = int(filters.get('size') or 20)
             paginator = Paginator(items_data, page_size)
             page_obj = paginator.get_page(page_number)

             response = {
                 "data": list(page_obj),
                 "last_page": paginator.num_pages,
                 "total_rows": paginator.count,
                 "page_size": page_size,
                 "page_no": page_number,
                 "total_itemvalue": total_itemvalue,
                 "total_itemvalueb": total_itemvalueb,
                 "total_resvalue": total_resvalue,
                 "total_cost": total_cost,
                 "total_order": total_order,
                 "total_buy": total_buy,
                 "cached_flag": False,
             }

             cache.set(cache_key, response, timeout=300)
             return Response(response)

         except json.JSONDecodeError:
             return Response({'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)
         except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
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





@api_view(['DELETE'])
@permission_classes([AllowAny])
@authentication_classes([])
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
@permission_classes([AllowAny])
@authentication_classes([])
def delete_all_preorders_and_items(request):
    # Delete all preorder items first (to avoid FK issues)
    items_deleted, _ = almogOil_models.PreOrderItemsTable.objects.all().delete()
    orders_deleted, _ = almogOil_models.PreOrderTable.objects.all().delete()

    return Response({
        "message": f"Deleted {orders_deleted} orders and {items_deleted} items."
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([AllowAny])
@authentication_classes([])
def delete_all_preordersBuy_and_items(request):
    # Delete all preorder items first (to avoid FK issues)
    items_deleted, _ = almogOil_models.OrderBuyInvoiceItemsTable.objects.all().delete()
    orders_deleted, _ = almogOil_models.OrderBuyinvoicetable.objects.all().delete()

    return Response({
        "message": f"Deleted {orders_deleted} orders and {items_deleted} items."
    }, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def get_buy_invoices_for_preorder(request, invoice_no):
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
@permission_classes([AllowAny])
@authentication_classes([])
def get_preorders_for_buy_invoice(request, buy_invoice_no):
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
@permission_classes([AllowAny])
@authentication_classes([])
def get_related_preorders(request, buy_invoice_id):
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
@permission_classes([AllowAny])
@authentication_classes([])  # Adjust if any authentication is needed
def api_auto_confirm_preorder(request):
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
@permission_classes([AllowAny])
@authentication_classes([])
def invoice_summary(request):
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
@permission_classes([AllowAny])
@authentication_classes([])
def invoice_statistics(request):
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
@permission_classes([AllowAny])
@authentication_classes([])
def item_analytics(request):
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
@permission_classes([AllowAny])
@authentication_classes([])
def item_category_analysis(request):
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
@permission_classes([AllowAny])
@authentication_classes([])
def item_price_analysis(request):
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
@permission_classes([AllowAny])
@authentication_classes([])
def item_source_analysis(request):
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
@permission_classes([AllowAny])
@authentication_classes([])
def SalesAnalysisView(request):
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
@permission_classes([AllowAny])
@authentication_classes([])
def purchase_analysis(request):
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
@permission_classes([AllowAny])
@authentication_classes([])  # Allow anonymous access
def unique_company_products(request):
    company_products = almogOil_models.Mainitem.objects \
        .exclude(companyproduct__isnull=True) \
        .exclude(companyproduct__exact='') \
        .values_list('companyproduct', flat=True) \
        .distinct()

    return Response(list(company_products))    
   
@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def item_detail_api(request, pno):
    item = get_object_or_404(almogOil_models.Mainitem, pno=pno)
    return Response(products_serializers.MainitemSerializer(item).data)


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
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
@permission_classes([AllowAny])
@authentication_classes([])
def get_client_preorders(request):
    client_id = request.query_params.get("client_id")

    if not client_id:
        return Response({"error": "client_id is required"}, status=400)

    preorders = almogOil_models.PreOrderTable.objects.filter(client=client_id)

    if not preorders.exists():
        return Response({"error": "No preorders found for this client"}, status=404)

   
    serializer = wholesale_serializers.SimplePreOrderSerializer(preorders, many=True)
    return Response(serializer.data)



@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
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


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])  # No authentication
def get_oem_table_data(request):
    oem_data = almogOil_models.Oemtable.objects.all()
    serializer = wholesale_serializers.OemTableSerializer(oem_data, many=True)
    return Response(serializer.data)









CACHE_TTL = 60 * 5   # 5 دقائق


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def cached_oemtable_list(request):
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
@permission_classes([AllowAny])
@authentication_classes([])
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

@api_view(["POST"])
@permission_classes([AllowAny])              # Allow anyone to access
@authentication_classes([])                  # No authentication required
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

