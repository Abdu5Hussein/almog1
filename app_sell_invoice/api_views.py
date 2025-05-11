from rest_framework.decorators import api_view, permission_classes, authentication_classes
from almogOil.authentication import CookieAuthentication
from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import F, Q, Sum, IntegerField
from django.http import JsonResponse
from almogOil.Tasks import assign_orders
from django.core.paginator import Paginator
from django_q.tasks import async_task
from django.utils.timezone import now, make_aware
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from almogOil import models as almogOil_models
from almogOil import serializers as almogOil_serializers
from app_sell_invoice import serializers as sell_invoice_serializers
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema_view,extend_schema,OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes, OpenApiSchemaBase



""" Sell Invoice Api's """

@extend_schema(
description='''
Get a specific invoice's data.
''',
tags=["Sell Invoice"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_invoice_data(request, autoid):
    if not request.user.has_perm('almogOil.category_sell_invoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        # Fetch the data using the provided autoid (primary key)
        invoice_data = almogOil_models.SellinvoiceTable.objects.get(autoid=autoid)
        serializer = almogOil_serializers.OrderSerializer(invoice_data)
        return Response(serializer.data)
    except almogOil_models.SellinvoiceTable.DoesNotExist:
        return Response({"error": "Invoice not found"}, status=404)

@extend_schema(
description='''
Get Specific Client's sell invoices.
''',
tags=["Sell Invoice","Clients"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def GetClientInvoices(request, id):
    if not request.user.has_perm('almogOil.category_sell_invoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    # Filter invoices based on the client ID
    str_id = str(id)
    invoices = almogOil_models.SellinvoiceTable.objects.filter(client_id=str_id)

    if not invoices.exists():
        return Response({'error': 'No invoices found for the provided client ID.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the invoices
    serializer = sell_invoice_serializers.SellInvoiceSerializer(invoices, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)  # Return the serialized data
######
@extend_schema(
description='''
Get Specific sell invoice's data by invoice no.
''',
tags=["Sell Invoice"],
)
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def GetClientInvoicesByInvoiceNo(request, id):
    if not request.user.has_perm('almogOil.category_sell_invoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    # Filter invoices based on the client ID
    str_id = str(id)
    invoices = almogOil_models.SellinvoiceTable.objects.filter(invoice_no=str_id)

    if not invoices.exists():
        return Response({'error': 'No invoices found for the provided client ID.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the invoices
    serializer = sell_invoice_serializers.SellInvoiceSerializer(invoices, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)  # Return the serialized data



@extend_schema(
description="""get last sell invoice no""",
tags=["Sell Invoice"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_sellinvoice_no(request):
    if not request.user.has_perm('almogOil.category_sell_invoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        # Get the last autoid by ordering the table by invoice_no in descending order
        last_invoice = almogOil_models.SellinvoiceTable.objects.order_by('-invoice_no').first()
        if last_invoice:
            return Response({'autoid': last_invoice.invoice_no}, status=status.HTTP_200_OK)
        else:
            # Handle the case where the table is empty
            return Response({'autoid': 0, 'message': 'No invoices found'}, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_last_sellinvoice_no():
    last_invoice = almogOil_models.SellinvoiceTable.objects.order_by("-invoice_no").first()
    return last_invoice.invoice_no if last_invoice else 0

@extend_schema(
description="""create a new sell invoice""",
tags=["Sell Invoice"],
)
@api_view(["POST"])
#@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def create_sell_invoice(request):
    if not request.user.has_perm('almogOil.add_sellinvoicetable'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    if request.method == "POST":
        try:
            data = request.data
            client_identifier = data.get("client")
            if not client_identifier:
                return Response({"success": False, "error": "Client is null"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch client
            try:
                if isinstance(client_identifier, int) or (isinstance(client_identifier, str) and client_identifier.isdigit()):
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

            last_receipt_no = get_last_sellinvoice_no()
            next_receipt_no = int(last_receipt_no) + 1

            for_who = "application" if data.get("for_who") == "application" else None

            # Prepare the data for creating a new invoice
            invoice_data = {
                'invoice_no': next_receipt_no,
                'client_obj': client_obj.clientid,
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

            # Use serializer to create the SellinvoiceTable record
            serializer = sell_invoice_serializers.SellInvoiceSerializer(data=invoice_data)
            if serializer.is_valid():
                serializer.save()

                # Trigger background task
                async_task('almogOil.Tasks.assign_orders')

                return Response({
                    "success": True,
                    "message": "Sell invoice created and order assignment triggered!",
                    "invoice_no": serializer.instance.invoice_no,
                    "client_balance": serializer.instance.client_balance
                }, status=status.HTTP_201_CREATED)

            return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Invalid HTTP method. Only POST is allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@extend_schema(
description="""create a new sell invoice item""",
tags=["Sell Invoice","Sell Invoice Items"],
)
@api_view(["POST"])
#@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def Sell_invoice_create_item(request):
    if not request.user.has_perm('almogOil.add_sellinvoicetable'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    if request.method == "POST":
        try:
            data = request.data

            required_fields = ["pno", "fileid", "invoice_id", "itemvalue", "sellprice"]
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Get the related product
            try:
                product = almogOil_models.Mainitem.objects.get(pno=data.get("pno"), fileid=data.get("fileid"))
            except almogOil_models.Mainitem.DoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get the related invoice
            try:
                invoice = almogOil_models.SellinvoiceTable.objects.get(invoice_no=data.get("invoice_id"))
                invoice.amount += (Decimal(product.buyprice or 0) * Decimal(data.get("itemvalue") or 0))
                invoice.save()
            except almogOil_models.SellinvoiceTable.DoesNotExist:
                return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if sufficient quantity exists
            item_value = int(data.get("itemvalue") or 0)
            if product.itemvalue < item_value:
                return Response({"error": "Insufficient product quantity"}, status=status.HTTP_400_BAD_REQUEST)

            sell_price = Decimal(data.get("sellprice")) if data.get("sellprice") else Decimal(product.buyprice or 0)
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
                'date': f"{timezone.now().date()}",
                'place': product.itemplace,
                'dinar_unit_price': Decimal(sell_price or 0),
                'dinar_total_price': Decimal(sell_price or 0) * item_value,
                'prev_quantity': product.itemvalue,
                'current_quantity': product.itemvalue - item_value,
            }

            # Use serializer to create the SellInvoiceItemsTable record
            serializer = sell_invoice_serializers.SellInvoiceItemsSerializer(data=item_data)
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


@extend_schema(
description="""fetch all sell invoice items by invoice no""",
tags=["Sell Invoice","Sell Invoice Items"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def fetch_sell_invoice_items(request):
    if not request.user.has_perm('almogOil.category_sell_invoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    invoice_no = request.GET.get("id")

    if not invoice_no:
        return Response({"error": "Invoice number is required."}, status=status.HTTP_400_BAD_REQUEST)

    items = almogOil_models.SellInvoiceItemsTable.objects.filter(invoice_no=invoice_no)
    if not items.exists():
        return Response([], status=status.HTTP_200_OK)

    serializer = sell_invoice_serializers.SellInvoiceItemsSerializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
description="""fetch all sell invoices""",
tags=["Sell Invoice"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def fetch_sellinvoices(request):
    if not request.user.has_perm('almogOil.category_sell_invoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        today = now().date()
        records = almogOil_models.SellinvoiceTable.objects.filter(invoice_date__date=today)
        aggregates = almogOil_models.SellinvoiceTable.objects.aggregate(
            total_amount=Sum('amount'),
            cash_amount=Sum('amount', filter=Q(payment_status="نقدي")),
            loan_amount=Sum('amount', filter=Q(payment_status="اجل")),
            total_discount=Sum('discount'),
            total_returned=Sum('returned')
        )

        # Pagination logic
        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("size", 100)

        paginator = Paginator(records, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = sell_invoice_serializers.SellInvoiceSerializer(page_obj, many=True)

        return Response({
            "data": serializer.data,
            "last_page": paginator.num_pages,
            "total_rows": paginator.count,
            "total_amount": aggregates["total_amount"] or 0,
            "cash_amount": aggregates["cash_amount"] or 0,
            "loan_amount": aggregates["loan_amount"] or 0,
            "total_discount": aggregates["total_discount"] or 0,
            "total_returned": aggregates["total_returned"] or 0,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""filter sell invoices""",
tags=["Sell Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def filter_sellinvoices(request):
    if not request.user.has_perm('almogOil.category_sell_invoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        filters = request.data

        filters_q = Q()
        if filters.get('client'):
            filters_q &= Q(client_name__icontains=filters['client'])
        if filters.get('client_rate'):
            filters_q &= Q(client_rate__icontains=filters['client_rate'])
        if filters.get('invoice_no'):
            filters_q &= Q(invoice_no__icontains=filters['invoice_no'])
        if filters.get('for_who'):
            filters_q &= Q(for_who__icontains=filters['for_who'])
        if filters.get('payment_status'):
            filters_q &= Q(payment_status__icontains=filters['payment_status'])
        if filters.get('price_status'):
            filters_q &= Q(price_status__icontains=filters['price_status'])
        if filters.get('invoice_status'):
            filters_q &= Q(invoice_status__icontains=filters['invoice_status'])

        fromdate = filters.get('fromdate', '').strip()
        todate = filters.get('todate', '').strip()

        if fromdate and todate:
            from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
            to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)
            filters_q &= Q(invoice_date__range=[from_date_obj, to_date_obj])

        invoices_qs = almogOil_models.SellinvoiceTable.objects.filter(filters_q).order_by("-invoice_date")
        totals = invoices_qs.aggregate(
            total_amount=Sum('amount', default=0),
            cash_amount=Sum('amount', filter=Q(payment_status="نقدي"), default=0),
            loan_amount=Sum('amount', filter=Q(payment_status="اجل"), default=0),
            total_discount=Sum('discount', default=0),
            total_returned=Sum('returned', default=0)
        )

        page_number = int(filters.get('page') or 1)
        page_size = int(filters.get('size') or 20)
        paginator = Paginator(invoices_qs, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = sell_invoice_serializers.SellInvoiceSerializer(page_obj, many=True)

        response = {
            "data": serializer.data,
            "last_page": paginator.num_pages,
            "total_rows": paginator.count,
            "page_size": page_size,
            "page_no": page_number,
            "total_amount": totals["total_amount"],
            "cash_amount": totals["cash_amount"],
            "loan_amount": totals["loan_amount"],
            "total_discount": totals["total_discount"],
            "total_returned": totals["total_returned"],
        }

        return Response(response, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
description="""set sell invoice status as preparing""",
tags=["Sell Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def prepare_sell_invoice(request):
    if not request.user.has_perm('almogOil.prepare_input_sellinvoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        # Get the data from the request body
        data = request.data
        name = data.get('name')
        note = data.get('note')
        invoice_id = data.get('invoice_id')

        # Get the invoice object
        invoice = almogOil_models.SellinvoiceTable.objects.get(invoice_no=invoice_id)

        # Update invoice fields
        invoice.preparer_name = name
        invoice.preparer_note = note
        invoice.invoice_status = "جاري التحضير"

        # Save the updated invoice
        invoice.save()

        return Response({'status': 'success', 'message': 'Invoice updated successfully'}, status=status.HTTP_200_OK)

    except almogOil_models.SellinvoiceTable.DoesNotExist:
        return Response({'status': 'error', 'message': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""set sell invoice status as validated""",
tags=["Sell Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def validate_sell_invoice(request):
    if not request.user.has_perm('almogOil.prepare_input_sellinvoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        # Get the data from the request body
        data = request.data
        reviewer = data.get('reviewer')
        place = data.get('place')
        invoice_no = data.get('invoice_id')
        size = data.get('size')
        final_note = data.get('final_note')

        # Get the invoice object
        invoice = almogOil_models.SellinvoiceTable.objects.get(invoice_no=invoice_no)

        # Update invoice fields
        invoice.reviewer_name = reviewer
        invoice.place = place
        invoice.quantity = size
        invoice.notes = final_note
        invoice.invoice_status = "روجعت"

        # Save the updated invoice
        invoice.save()

        return Response({'status': 'success', 'message': 'Invoice updated successfully'}, status=status.HTTP_200_OK)

    except almogOil_models.SellinvoiceTable.DoesNotExist:
        return Response({'status': 'error', 'message': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""set sell invoice status as Delivered""",
tags=["Sell Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def deliver_sell_invoice(request):
    if not request.user.has_perm('almogOil.prepare_input_sellinvoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        data = request.data
        # Extract the data from the request.
        biller = data.get('biller')
        sent = data.get('sent')
        office = data.get('office')
        size = data.get('size')
        deliverer = data.get('deliverer')
        deliverer_date = data.get('deliverer_date', None)
        invoice_id = data.get('invoice_id')
        bill = data.get('bill')
        status = data.get('status')
        final_note = data.get('final_note')

        invoice = almogOil_models.SellinvoiceTable.objects.get(invoice_no=invoice_id)

        invoice.biller_name = biller
        invoice.notes = final_note
        invoice.sent_by = sent
        invoice.office = office
        invoice.delivered_quantity = size
        invoice.deliverer_name = deliverer
        invoice.delivered_date = deliverer_date or None
        invoice.office_no = bill
        invoice.invoice_status = status
        invoice.delivery_status = "جاري التوصيل" if invoice.mobile else "في المحل"

        invoice.save()

        # Send notification to the user associated with this invoice.
        user_id = invoice.client  # Make sure this field exists on your model.
        room_group_name = f'user_{user_id}'
        message = f"تم تحديث حالة الفاتورة رقم {invoice_id} إلى {status}."

        # Send message to the user
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "send_notification",
                "message": message,
            }
        )

        async_task('almogOil.Tasks.assign_orders')  # Adjust as needed

        return Response({'status': 'success', 'message': 'Invoice updated successfully'}, status=status.HTTP_200_OK)

    except almogOil_models.SellinvoiceTable.DoesNotExist:
        return Response({'status': 'error', 'message': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""cancel sell invoice preparing""",
tags=["Sell Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def cancel_sell_invoice(request):
    if not request.user.has_perm('almogOil.prepare_input_sellinvoice'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        # Get the data from the request body
        data = request.data
        invoice_no = data.get('invoice_id')

        # Get the invoice object
        invoice = almogOil_models.SellinvoiceTable.objects.get(invoice_no=invoice_no)

        # Update invoice fields to cancel the sell invoice
        invoice.reviewer_name = None
        invoice.place = None
        invoice.quantity = 0
        invoice.preparer_name = None
        invoice.preparer_note = None
        invoice.biller_name = None
        invoice.sent_by = None
        invoice.office = None
        invoice.delivered_quantity = 0
        invoice.deliverer_name = None
        invoice.delivered_date = None
        invoice.office_no = None
        invoice.notes = None
        invoice.invoice_status = "لم تحضر"

        # Save the updated invoice
        invoice.save()

        return Response({'status': 'success', 'message': 'Invoice cancelled successfully'}, status=status.HTTP_200_OK)

    except almogOil_models.SellinvoiceTable.DoesNotExist:
        return Response({'status': 'error', 'message': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
