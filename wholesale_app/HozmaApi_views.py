from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import json
import random
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

def get_last_PreOrderTable_no():
    last_invoice = almogOil_models.PreOrderTable.objects.order_by("-invoice_no").first()
    return last_invoice.invoice_no if last_invoice else 0


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
            'invoice_date': data.get("invoice_date"),
            'invoice_status': "لم تحضر",
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
            return Buyhandle_confirm_action(preorder)

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




def Buyhandle_confirm_action(preorder):
    
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
                invoice.amount += Decimal(product.buyprice or 0) * Decimal(data.get("itemvalue") or 0)
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
                'company_no': product.replaceno,
                'quantity': item_value,
                'date': timezone.now(),
                'place': product.itemplace,
                'dinar_unit_price': product.buyprice,
                'dinar_total_price': dinar_total_price,
                'prev_quantity': product.showed,
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
                        invoice_no=int(timezone.now().timestamp()) ,
                        source_obj= product.source

                          # unique
                    )

                # Check if item already exists in BuyInvoiceItemsTable
                existing_buy_item = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(
                    invoice_no=buy_invoice,
                    pno=product.pno
                ).first()

                if existing_buy_item:
                    existing_buy_item.Asked_quantity = (existing_buy_item.Asked_quantity or 0) + item_value
                    existing_buy_item.dinar_total_price = (existing_buy_item.dinar_total_price or Decimal(0)) + buy_dinar_total_price

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
                        name=product.itemname,
                        company=product.companyproduct,
                        company_no=product.replaceno,
                        Asked_quantity=buyitem_value,
                        date=str(timezone.now().date()),
                        dinar_unit_price=buy_dinar_unit_price,
                        dinar_total_price=buy_dinar_total_price,
                        prev_quantity=product.itemvalue,
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
        preorder_item.save()

    # After updating the quantities for all items, recalculate the total amount for the PreOrder
    total_amount = sum([item.dinar_total_price for item in preorder_items])  # Sum the dinar_total_price of all items

    # Update the total amount in PreOrderTable
    preorder.amount = total_amount
    preorder.net_amount= total_amount
    preorder.save()

    return Response({"success": True, "message": "PreOrder items updated with new quantities."}, status=status.HTTP_200_OK)

def Buyhandle_confirm_action(preorder):
    # Prevent confirmation unless preorder.send is True
    if not preorder.send:
        return Response({"success": False, "message": "Cannot confirm preorder. 'send' must be True."}, status=status.HTTP_400_BAD_REQUEST)

    # Confirm the PreOrder and move items to BuyInvoiceMainItem
    source = preorder.source_obj
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

    # Process the preorder items and move them to BuyInvoiceItemsTable
    preorder_items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no=preorder.autoid)
    for item in preorder_items:
        if item.Confirmed_quantity is None:
            item.Confirmed_quantity = item.Asked_quantity
            item.save()

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
            exchange_rate=Decimal('1.0000'),
            buysource=preorder.source_obj,
            prev_quantity=item.prev_quantity or 0,
            current_quantity=item.current_quantity or 0,
            source=item.source if hasattr(item, "source") else None
        )

        # Update Mainitem quantity
        try:
            mainitem = almogOil_models.Mainitem.objects.get(pno=item.pno)
            mainitem.itemvalue = max(mainitem.itemvalue + item.Confirmed_quantity, 0)
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
            'pno': item.pno,
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


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def create_mainitem_by_source(request):
    source_id = request.data.get("source")

    if not source_id:
        return Response({"error": "Source ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        source = almogOil_models.AllSourcesTable.objects.get(pk=source_id)
    except almogOil_models.AllSourcesTable.DoesNotExist:
        return Response({"error": "Source not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data["source"] = source.clientid  # Set actual client ID

    # Compute costprice
    try:
        commission = float(source.commission or 0)
        buyprice = float(data.get("buyprice") or 0)
        costprice = buyprice - (buyprice * commission)
        data["costprice"] = costprice
    except (TypeError, ValueError):
        return Response({"error": "Invalid buyprice or commission."}, status=status.HTTP_400_BAD_REQUEST)

    pno = data.get("pno")
    if not pno:
        return Response({"error": "pno is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Try to get an existing Mainitem with same pno and source
    try:
        existing_item = almogOil_models.Mainitem.objects.get(pno=pno, source=source)
        serializer = products_serializers.MainitemSerializer(existing_item, data=data, partial=True)
    except almogOil_models.Mainitem.DoesNotExist:
        serializer = products_serializers.MainitemSerializer(data=data)

    if serializer.is_valid():
        serializer.save(source=source)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
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