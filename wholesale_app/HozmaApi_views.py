from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import json
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
from .whatsapp_service import send_whatsapp_message_via_green_api
from wholesale_app import serializers as wholesale_serializers

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
            return handle_update_action(preorder, item_quantities)

        # Process the 'confirm' action
        elif action_type == "confirm":
            return handle_confirm_action(preorder)

        else:
            return Response({"error": "Invalid action_type. Use 'confirm' or 'update'."}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_update_action(preorder, item_quantities):
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

            source_phone = product.source.mobile if product.source and product.source.mobile else "218942434823"
            source_name = product.source.name if product.source else "Unknown"

            try:
                invoice = almogOil_models.PreOrderTable.objects.get(invoice_no=data.get("invoice_id"))
                invoice.amount += Decimal(product.buyprice or 0) * Decimal(data.get("itemvalue") or 0)
                invoice.save()
            except almogOil_models.PreOrderTable.DoesNotExist:
                return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

            item_value = int(data.get("itemvalue") or 0)
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
                'prev_quantity': product.itemvalue,
                'current_quantity': product.itemvalue - item_value,
            }

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
                        invoice_no=int(timezone.now().timestamp())  # unique
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

                # Send WhatsApp
                buy_items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no=buy_invoice)

                items_details = "\n".join([
                    f"- {item.name} | الكمية: {item.Asked_quantity} | السعر: {item.dinar_unit_price} | الإجمالي: {item.dinar_total_price}"
                    for item in buy_items
                ])

                message_body = (
                    f"تمت إضافة منتج {product.itemname} إلى فاتورة البيع رقم {data.get('invoice_id')}.\n"
                    f"📦 تفاصيل فاتورة الشراء رقم {buy_invoice.invoice_no}:\n"
                    f"{items_details}\n"
                    f"المجموع الكلي: {buy_invoice.amount}"
                )

                response = send_whatsapp_message_via_green_api(source_phone, message_body)

                return Response({
                    "message": "Item created successfully.",
                    "item_id": serializer.instance.autoid,
                    "whatsapp_sent": "idMessage" in response if response else False,
                    "phone_number": source_phone,
                    "buy_invoice_send": buy_invoice.send,
                    "confirmation": buy_invoice.confirmed,
                    "buy_invoice_id": buy_invoice.invoice_no
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