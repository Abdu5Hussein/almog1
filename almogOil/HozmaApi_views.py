from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import json
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import FieldError
from . import models  # Adjust this import to match your project structure
from . import serializers
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
from rest_framework.exceptions import NotFound
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
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework import generics, mixins,viewsets
from rest_framework import viewsets, status
from rest_framework.response import Response
from decimal import Decimal
from . import models, serializers
from .models import AllClientsTable, SellinvoiceTable
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from firebase_admin import messaging
from .models import EmployeesTable, AllClientsTable
import firebase_admin
from firebase_admin import credentials
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema_view,extend_schema,OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes, OpenApiSchemaBase

def get_last_sellinvoice_no():
    last_invoice = SellinvoiceTable.objects.order_by("-invoice_no").first()
    return last_invoice.invoice_no if last_invoice else 0


@extend_schema(
    description="""create a new pre-order item""",
    tags=["PreOrder", "PreOrder Items"],
)
@api_view(["POST"])
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
                client_obj = AllClientsTable.objects.get(clientid=int(client_identifier))
            else:
                client_obj = AllClientsTable.objects.get(name=client_identifier)

            balance_data = models.TransactionsHistoryTable.objects.filter(object_id=client_obj.clientid).aggregate(
                total_debt=Sum('debt') or Decimal("0.0000"),
                total_credit=Sum('credit') or Decimal("0.0000")
            )
        except AllClientsTable.DoesNotExist:
            return Response({"success": False, "error": "Client not found"}, status=status.HTTP_400_BAD_REQUEST)

        total_debt = balance_data.get('total_debt') or Decimal('0.0000')
        total_credit = balance_data.get('total_credit') or Decimal('0.0000')
        client_balance = total_credit - total_debt

        # Preferably refactor this function
        last_receipt_no = get_last_sellinvoice_no() + 1

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

        serializer = serializers.PreOrderSerializer(data=invoice_data)
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

def get_sellinvoice_no(request):
    try:
        # Get the last autoid by ordering the table by invoice_no in descending order
        last_invoice = models.PreOrderTable.objects.order_by('-invoice_no').first()
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

def Sell_invoice_create_item(request):
    if request.method == "POST":
        try:
            data = request.data

            required_fields = ["pno", "fileid", "invoice_id", "itemvalue", "sellprice"]
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Get the related product
            try:
                product = models.Mainitem.objects.get(pno=data.get("pno"), fileid=data.get("fileid"))
            except models.Mainitem.DoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get the related invoice
            try:
                invoice = models.PreOrder.objects.get(invoice_no=data.get("invoice_id"))
                invoice.amount += (Decimal(product.buyprice or 0) * Decimal(data.get("itemvalue") or 0))
                invoice.save()
            except models.PreOrder.DoesNotExist:
                return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if sufficient quantity exists
            item_value = int(data.get("itemvalue") or 0)
            if product.itemvalue < item_value:
                return Response({"error": "Insufficient product quantity"}, status=status.HTTP_400_BAD_REQUEST)

            # Prepare the data for creating a new SellInvoiceItemsTable instance
            item_data = {
                'invoice_instance': invoice,
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
            serializer = serializers.PreOrderItemsSerializer(data=item_data)
            if serializer.is_valid():
                serializer.save()

                # Update the product quantity
                product.itemvalue -= item_value
                product.save()

                return Response({
                    "message": "Item created successfully",
                    "item_id": serializer.instance.autoid,
                    "confirm_status": "confirmed"
                }, status=status.HTTP_201_CREATED)

            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Invalid HTTP method. Only POST is allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
