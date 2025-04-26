import json
import hashlib
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F, Q, Sum, IntegerField
from django.db.models.functions import Cast
from django.utils.timezone import now, make_aware
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.cache import cache
from django.urls import reverse
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.exceptions import NotFound

from django_q.tasks import async_task

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from reportlab.lib.pagesizes import letter, A3, landscape
from reportlab.pdfgen import canvas
#from reportlab.pdfbase import pdfmetrics, TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib import colors

from bidi.algorithm import get_display
import arabic_reshaper
import pandas as pd

import firebase_admin
from firebase_admin import credentials, messaging
from rest_framework.permissions import IsAuthenticated


# Local imports
from .models import (
    EmployeesTable, CartItem, AllClientsTable, OrderQueue, EmployeeQueue,
    SupportChatConversation, FeedbackMessage, Feedback, SupportChatMessageSys,
    Clientstable, AllSourcesTable, SellInvoiceItemsTable, SellinvoiceTable,
    TransactionsHistoryTable, BuyInvoiceItemsTable, Buyinvoicetable, LostAndDamagedTable,
    Modeltable, Imagetable, Mainitem, MeasurementsTable, Maintypetable, Sectionstable,
    StorageTransactionsTable, Subsectionstable, Subtypetable, Companytable, Manufaccountrytable,
    Oemtable, BuyinvoiceCosts, Clienttypestable, CostTypesTable, CurrenciesTable, enginesTable, ChatMessage
)
from .serializers import (
    CartItemSerializer, SupportChatMessageSysSerializer,
    SupportChatConversationSerializer, SupportChatConversationSerializer1, FeedbackSerializer,
    BuyInvoiceItemsTableSerializer, BuyInvoiceSerializer, TransactionsHistoryTableSerializer, BuyinvoiceCostsSerializer, ClientSerializer, ChatMessageSerializer, FeedbackMessageSerializer
)

import re
import math
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
# Other necessary imports
from .Tasks import assign_orders
from drf_spectacular.utils import extend_schema,OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes, OpenApiSchemaBase

from almogOil import serializers
from products import serializers as product_serializers

from almogOil import models


# Setup logger
logger = logging.getLogger(__name__)

@extend_schema(
description="""get sub sections dropbox data.""",
tags=["Drop Boxes"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subsections(request):
    section_id = request.GET.get('section_id')
    subsections = Subsectionstable.objects.filter(sectionid_id=section_id)
    serializer = product_serializers.SubsectionSerializer(subsections, many=True)
    return Response(serializer.data)

def get_next_buyinvoice_no():
    last_invoice = Buyinvoicetable.objects.last()
    return (last_invoice.invoice_no if last_invoice else 0) + 1

@extend_schema(
description="""Create a new Buy Invoice.""",
tags=["Buy Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def create_buy_invoice(request):
    try:
        data = request.data

        invoice_autoid = data.get("invoice_autoid")
        org_invoice_id = data.get("org_invoice_id")
        source_id = data.get("source")
        invoice_date = parse_date(data.get("invoice_date")) if data.get("invoice_date") else None
        arrive_date = parse_date(data.get("arrive_date")) if data.get("arrive_date") else None
        order_no = data.get("order_no")
        currency = data.get("currency")
        currency_rate = data.get("currency_rate")
        ready_date = parse_date(data.get("ready_date")) if data.get("ready_date") else None
        reminder = data.get("reminder")
        temp_flag = data.get("temp_flag", False)
        multi_source_flag = data.get("multi_source_flag", False)
        source = AllSourcesTable.objects.get(clientid=source_id)

        next_id_no = get_next_buyinvoice_no()

        # Create the invoice
        invoice = Buyinvoicetable.objects.create(
            invoice_no=next_id_no,
            original_no=org_invoice_id,
            source=source.name,
            invoice_date=invoice_date,
            arrive_date=arrive_date,
            order_no=order_no,
            amount=0,
            discount=0,
            expenses=0,
            net_amount=0,
            account_amount=0,
            currency=currency,
            exchange_rate=currency_rate,
            ready_date=ready_date,
            remind_before=reminder,
            temp_flag=temp_flag,
            multi_source_flag=multi_source_flag,
        )

        # Serialize and return the response
        serializer = BuyInvoiceSerializer(invoice)
        return Response({"success": True, "message": "Invoice created successfully.", "id": serializer.data['invoice_no']}, status=201)

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=400)

@extend_schema(
description="""get the product history and movement of a product by pno.""",
tags=["Products","History and Archive"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_clients(request):
    try:
        pno = request.GET.get('pno')

        if not pno:
            return Response({'error': 'Missing pno parameter'}, status=400)

        clients = Clientstable.objects.filter(pno=pno)
        serializer = ClientSerializer(clients, many=True)

        return Response(serializer.data)

    except Exception as e:
        return Response({'error': str(e)}, status=500)


# views.py



@extend_schema(
description="""Filter product history and movements.""",
tags=["Products"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filter_clients_input(request):
    try:
        # Get the filters from the request body (DRF handles JSON parsing)
        filters = request.data  # This will automatically parse the JSON into a dictionary

        # Build the query based on the filters
        queryset = Clientstable.objects.all()
        filters_applied = False

        # Apply filters if they exist in the request
        if filters.get('itemno'):
            queryset = queryset.filter(itemno__icontains=filters['itemno'])
            filters_applied = True
        if filters.get('maintype'):
            queryset = queryset.filter(maintype__icontains=filters['maintype'])
            filters_applied = True
        if filters.get('itemname'):
            queryset = queryset.filter(itemname__icontains=filters['itemname'])
            filters_applied = True
        if filters.get('clientname'):
            queryset = queryset.filter(clientname__icontains=filters['clientname'])
            filters_applied = True
        if filters.get('pno'):
            queryset = queryset.filter(pno__icontains=filters['pno'])
            filters_applied = True

        # Handle date filtering
        fromdate = filters.get('fromdate', '').strip()
        todate = filters.get('todate', '').strip()

        if fromdate and todate:
            try:
                # Parse the date range
                from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)

                # Apply date range filter
                queryset = queryset.filter(date__range=[from_date_obj, to_date_obj])
                filters_applied = True
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        # If no filters are applied, return an empty list
        if not filters_applied:
            return Response([], status=status.HTTP_200_OK)

        # Serialize the filtered data
        serializer = ClientSerializer(queryset, many=True)

        # Return the filtered data as JSON
        return Response(serializer.data, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
description="""Process excell""",
tags=["Excel"],
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_excel_and_import(request):
    if request.method == "POST":
        # Debug: Log the start of the POST request
        logger.debug("Received POST request at /import-tabulator-data/")

        # Handle file upload (Excel)
        if request.FILES.get("fileInput"):
            excel_file = request.FILES["fileInput"]
            try:
                logger.debug(f"Processing file: {excel_file.name}")
                # Read the Excel file into a DataFrame
                data = pd.read_excel(excel_file, engine='openpyxl')
                logger.debug(f"Excel data read: {data.head()}")  # Log the first few rows of the data

                # Process the Excel data and insert into database
                records = []
                for index, row in data.iterrows():
                    try:
                        logger.debug(f"Processing row {index}: {row.to_dict()}")
                        records.append(Mainitem(
                            itemno=row.get("ItemNo", None),
                            itemmain=row.get("ItemMain", None),
                            itemsubmain=row.get("ItemSubMain", None),
                            itemname=row.get("ItemName", "failed"),
                            itemthird=row.get("ItemThird", None),
                            itemsize=row.get("ItemSize", None),
                            companyproduct=row.get("CompanyProduct", None),
                            dateproduct=row.get("DateProduct", None),
                            levelproduct=row.get("LevelProduct", None),
                            itemvalue=row.get("ItemValue", None),
                            itemtemp=row.get("ItemTemp", None),
                            itemplace=row.get("ItemPlace", None),
                            orderlastdate=row.get("OrderLastDate", None),
                            ordersource=row.get("OrderSource", None),
                            orderbillno=row.get("OrderBillNo", None),
                            buylastdate=row.get("BuyLastDate", None),
                            buysource=row.get("BuySource", None),
                            buybillno=row.get("BuyBillNo", None),
                            orgprice=row.get("OrgPrice", None),
                            orderprice=row.get("OrderPrice", None),
                            costprice=row.get("CostPrice", None),
                            buyprice=row.get("BuyPrice", None),
                            memo=row.get("Memo", None),
                            orderstop=row.get("OrderStop", None),
                            buystop=row.get("BuyStop", None),
                            itemtrans=row.get("ItemTrans", None),
                            itemvalueb=row.get("ItemValueB", None),
                            replaceno=row.get("ReplaceNo", None),
                            itemtype=row.get("ItemType", None),
                            barcodeno=row.get("BarcodeNo", None),
                            eitemname=row.get("EItemName", None),
                            currtype=row.get("CurrType", None),
                            lessprice=row.get("LessPrice", None),
                            pno=row.get("PNo", None),
                            currvalue=row.get("CurrValue", None),
                            resvalue=row.get("resValue", None),
                            itemperbox=row.get("ItemPerBox", None),
                            cstate=row.get("CSTate", None),
                        ))
                    except Exception as row_error:
                        logger.error(f"Error processing row {index}: {row_error}")
                        continue

                # Bulk create records in the database
                Mainitem.objects.bulk_create(records)
                logger.debug(f"Successfully inserted {len(records)} records into the database.")

                return JsonResponse({"status": "success", "message": "Excel data imported successfully."}, status=200)

            except Exception as e:
                logger.error(f"Error processing file: {e}")
                return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

        # Handle imported Tabulator data
        if request.data.get("data"):
            data = request.data["data"]
            try:
                logger.debug(f"Received Tabulator data: {data}")
                records = []
                for item in data:
                    try:
                        records.append(Mainitem(
                            itemno=item.get("ItemNo", None),
                            itemmain=item.get("ItemMain", None),
                            itemsubmain=item.get("ItemSubMain", None),
                            itemname=item.get("ItemName", "failed"),
                            itemthird=item.get("ItemThird", None),
                            itemsize=item.get("ItemSize", None),
                            companyproduct=item.get("CompanyProduct", None),
                            dateproduct=item.get("DateProduct", None),
                            levelproduct=item.get("LevelProduct", None),
                            itemvalue=item.get("ItemValue", 0),
                            itemtemp=item.get("ItemTemp", 0),
                            itemplace=item.get("ItemPlace", None),
                            orderlastdate=item.get("OrderLastDate", None),
                            ordersource=item.get("OrderSource", None),
                            orderbillno=item.get("OrderBillNo", None),
                            buylastdate=item.get("BuyLastDate", None),
                            buysource=item.get("BuySource", None),
                            buybillno=item.get("BuyBillNo", None),
                            orgprice=item.get("OrgPrice", 0),
                            orderprice=item.get("OrderPrice", 0),
                            costprice=item.get("CostPrice", 0),
                            buyprice=item.get("BuyPrice", 0),
                            memo=item.get("Memo", None),
                            orderstop=item.get("OrderStop", None),
                            buystop=item.get("BuyStop", None),
                            itemtrans=item.get("ItemTrans", None),
                            itemvalueb=item.get("ItemValueB", 0),
                            replaceno=item.get("ReplaceNo", None),
                            itemtype=item.get("ItemType", None),
                            barcodeno=item.get("BarcodeNo", None),
                            eitemname=item.get("EItemName", None),
                            currtype=item.get("CurrType", None),
                            lessprice=item.get("LessPrice", 0),
                            pno=item.get("PNo", None),
                            currvalue=item.get("CurrValue", None),
                            resvalue=item.get("ResValue", 0),
                            itemperbox=item.get("ItemPerBox", None),
                            cstate=item.get("CSTate", None)
                        ))

                    except Exception as item_error:
                        logger.error(f"Error processing item {item}: {item_error}")
                        continue

                Mainitem.objects.bulk_create(records)
                logger.debug(f"Successfully inserted {len(records)} records from Tabulator data.")
                return JsonResponse({"status": "success", "message": "Tabulator data imported successfully."})

            except Exception as e:
                logger.error(f"Error processing imported data: {e}")
                return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

        return JsonResponse({"status": "error", "message": "Invalid request or missing file."}, status=400)

#until here

# Register the Amiri font
font_path = settings.BASE_DIR / 'staticfiles/Amiri-font/Amiri-Regular.ttf'
#pdfmetrics.registerFont(TTFont('Amiri', str(font_path)))

# Regular expression to detect Arabic text
ARABIC_CHAR_PATTERN = re.compile(r'[\u0600-\u06FF]')

# Header mapping: English to Arabic
HEADER_MAPPING = {
    "fileid": "رقم الملف",
    "itemno": "الرقم الاصلي",
    "itemmain": "البيان الرئيسي",
    "itemsubmain": "البيان الفرعي",
    "itemname": "اسم الصنف",
    "itemthird": "الموديل",
    "itemsize": "بلد الصنع",
    "companyproduct": "الشركة المنتجة",
    "itemvalue": "الرصيد بالمخزن",
    "itemtemp": "الرصيد الاحتياطي",
    "itemplace": "الموقع",
    "buyprice": "سعر البيع",
    "memo": "المواصفات",
    "replaceno": "رقم الشركة",
    "barcodeno": "رقم الباركود",
    "eitemname": "اسم العنصر (إنجليزي)",
    "currtype": "نوع العملة",
    "lessprice": "اقل سعر",
    "pno": "الرقم الخاص",
    "currvalue": "قيمة العملة",
    "itemvalueb": "الرصيد المؤقت",
    "costprice": "سعر التكلفة",
    "resvalue": "الرصيد المحجوز",
    "orderprice": "سعر الشراء",
    "levelproduct": "مستوى المنتج",
    "orderlastdate": "تاريخ آخر طلب",
    "ordersource": "مصدر الطلب",
    "orderbillno": "رقم فاتورة الطلب",
    "buylastdate": "تاريخ آخر شراء",
    "buysource": "مصدر الشراء",
    "buybillno": "رقم فاتورة الشراء",
    "orgprice": "سعر التوريد",
    "orderstop": "إيقاف الطلب",
    "buystop": "إيقاف الشراء",
    "itemtrans": "انتقال العنصر",
    "itemtype": "نوع العنصر",
    "itemperbox": "عدد العناصر بالصندوق",
    "cstate": "حالة العنصر",
    "company": "الشركة المنتجة",
    "companyno": "رقم الشركة",
    "date": "التاريخ",
    "quantity": "الكمية",
    "pno_value": "رقم خاص (FK)",
    "status": "الحالة",
    "user": "المستخدم",
    "name":"الاسم",
    "balance":"الرصيد",
    "loan_limit":"السقف",
    "category":"التصنيف",
    "clientid":"رقم العميل",
    "paid_total":"اجمالي الدفوعات",
    "last_transaction_amount":"قيمة اخر دفعة",
    "last_transaction":"تاريخ اخر دفعة",
}

def format_arabic_text(text):
    """
    Reformat Arabic text for proper rendering in PDFs.
    - Arabic reshaping ensures proper character joining.
    - Bidi reordering ensures correct right-to-left display.
    """
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

@extend_schema(
description="""Generate a pdf file.""",
tags=["PDF"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_pdf(request):
    # Parse the incoming JSON data
    data = request.data  # Using DRF's request.data instead of request.body
    table_data = data.get('data', [])

    if not table_data:  # Handle empty data case
        return Response({'error': 'No data provided for PDF generation'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a response object to return as a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="tabulator_data.pdf"'

    # Custom Tabloid size (11 x 17 inches)
    TABLOID = (2992, 1224)
    doc = SimpleDocTemplate(response, pagesize=landscape(TABLOID))

    # Prepare column headers and row data with RTL ordering
    if table_data:
        original_headers = list(table_data[0].keys())
        column_headers = [HEADER_MAPPING.get(header, header) for header in original_headers][::-1]  # Reverse headers
    else:
        original_headers = []
        column_headers = []

    # Prepare the table data with reversed headers
    data_for_table = [column_headers]  # Add reversed headers as the first row
    for row in table_data:
        # Reverse each row to match RTL column order
        data_for_table.append([row.get(header, '') for header in reversed(original_headers)])

    # Define custom styles for Arabic and English text
    arabic_style = ParagraphStyle(
        name="Arabic",
        fontName="Amiri",  # Use the registered Amiri font
        fontSize=10,  # Font size
        alignment=1,  # Align text to the right for RTL
        leading=12,  # Line spacing
    )

    english_style = ParagraphStyle(
        name="English",
        fontName="Helvetica",  # Default font for English text
        fontSize=10,  # Font size
        alignment=0,  # Align text to the left for LTR
        leading=12,  # Line spacing
    )

    # Convert table data to Paragraphs for proper rendering
    formatted_data = []
    for row_index, row in enumerate(data_for_table):
        formatted_row = []
        for cell in row:
            if isinstance(cell, str):
                # Detect Arabic text
                if ARABIC_CHAR_PATTERN.search(cell) or row_index == 0:  # Headers assumed Arabic
                    arabic_text = format_arabic_text(cell)
                    formatted_row.append(Paragraph(arabic_text, arabic_style))
                else:
                    formatted_row.append(Paragraph(cell, english_style))
            else:
                formatted_row.append(cell)
        formatted_data.append(formatted_row)

    # Dynamically calculate column widths
    page_width, _ = TABLOID
    table_width = page_width - 72  # Leave 1-inch margin on each side
    min_width = 50  # Minimum width in points
    max_width = 350  # Maximum column width
    max_column_widths = []

    for header in column_headers:
        max_length = max(len(str(row.get(header, ''))) for row in table_data) if table_data else 10
        max_length = max(max_length, len(header))
        computed_width = max(min_width, min(max_length * 7, max_width))
        max_column_widths.append(computed_width)

    total_width = sum(max_column_widths)

    # Ensure total width fits within the page by scaling down if necessary
    if total_width > table_width:
        scale_factor = table_width / total_width
        max_column_widths = [math.floor(width * scale_factor) for width in max_column_widths]

    # Table style configuration
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header row background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
        ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),  # Use Amiri font
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
    ])

    # Handle large data by streaming content in batches to avoid memory overload
    max_rows_per_page = 50  # Limit to a number of rows per page to prevent memory issues
    rows = len(formatted_data)
    elements = []

    for i in range(0, rows, max_rows_per_page):
        page_data = formatted_data[i:i + max_rows_per_page]
        if not page_data:
            return Response({'error': 'No data provided for PDF generation'}, status=status.HTTP_400_BAD_REQUEST)
        page_table = Table(page_data, colWidths=max_column_widths)
        page_table.setStyle(table_style)

        elements.append(page_table)

        # Add page break if there are more rows
        if i + max_rows_per_page < rows:
            elements.append(PageBreak())

    # Build the PDF document and return as response
    doc.build(elements)

    return response

def safe_int(value, default=0):
    """Safely convert a value to an integer, or return the default if conversion fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """Safely convert a value to a float, or return the default if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

@extend_schema(
description="""Get all product movements from DB.""",
tags=["Products"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_clients(request):
    try:
        # Query the database for all Clientstable entries
        items = Clientstable.objects.all()
        serializer = ClientSerializer(items, many=True)  # Serialize the queryset
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)         # Return error details in JSON

@extend_schema(
description="""Delete a lost/damaged record from db.""",
tags=["Lost and Damaged","Products"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_lost_damaged(request):
    try:
        data = request.data
        fileid = data.get('fileid')

        if not fileid:
            return Response({'success': False, 'message': 'fileid is required.'}, status=status.HTTP_400_BAD_REQUEST)

        record = LostAndDamagedTable.objects.get(fileid=fileid)
        record.delete()
        return Response({'success': True, 'message': 'Record deleted successfully.'}, status=status.HTTP_200_OK)
    except LostAndDamagedTable.DoesNotExist:
        return Response({'success': False, 'message': f'Record with fileid {fileid} does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""filter all lost/damaged records from db.""",
tags=["Lost and Damaged","Products"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filter_lost_damaged(request):
    try:
        # Get the filters from the request body
        filters = request.data  # DRF automatically parses JSON body

        queryset = LostAndDamagedTable.objects.all()

        fromdate = filters.get('fromdate', '').strip()
        todate = filters.get('todate', '').strip()

        if fromdate and todate:
            try:
                # Parse dates
                from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)

                # Apply date range filter
                queryset = queryset.filter(date__range=[from_date_obj, to_date_obj])
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the filtered data
        serializer = product_serializers.LostAndDamagedTableSerializer(queryset, many=True)
        return Response(serializer.data)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(str(e))
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""fetch all lost/damaged records from db.""",
tags=["Lost and Damaged","Products"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_lost_damaged_data(request):
    # Fetch all data from the model
    data = LostAndDamagedTable.objects.all().values(
        "fileid", "date", "itemno", "companyno", "itemname", "user", "quantity",
        "company", "costprice", "pno", "pno_value", "status"
    )
    return Response(data)

@extend_schema(
description="""Create a new lost/damaged record to db.""",
tags=["Lost and Damaged","Products"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_lost_damaged(request):
    try:
        # Parse the JSON data from the request body
        data = request.data  # DRF automatically parses JSON body

        # Extract data from the request
        itemno = data.get('itemno')
        companyno = data.get('companyno')
        company = data.get('company')
        itemname = data.get('itemname')
        costprice = data.get('costprice')
        quantity = data.get('quantity')
        pno_id = data.get('pno')  # Note that we expect an ID, not the instance itself
        status = data.get('status')
        date = data.get('date')
        itemmain = data.get('itemmain')

        # Validate required fields
        if not all([itemno, companyno, company, itemname, costprice, quantity, pno_id, status]):
            error_message = 'Missing required fields.'
            logger.error(error_message)
            return Response({'success': False, 'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Attempt to fetch the Mainitem instance for the provided pno_id
        try:
            pno_instance = Mainitem.objects.get(pno=pno_id)
            pno_instance.itemvalue -= int(data.get('quantity', 0)) or 0
            pno_instance.save()
        except Mainitem.DoesNotExist:
            error_message = f'Mainitem with pno id {pno_id} does not exist.'
            logger.error(error_message)
            return Response({'success': False, 'message': error_message}, status=status.HTTP_404_NOT_FOUND)

        # Save the record in the LostAndDamagedTable model
        lost_damaged_record = LostAndDamagedTable.objects.create(
            itemno=itemno,
            companyno=companyno,
            company=company,
            itemname=itemname,
            costprice=costprice,
            quantity=quantity,
            pno=pno_instance,  # Use the Mainitem instance, not the ID
            pno_value=pno_instance.pno,  # Save the actual pno value
            status=status,
            date=date
        )

        movement_record = Clientstable.objects.create(
            itemno=itemno,
            itemname=itemname,
            maintype=itemmain,
            currentbalance=pno_instance.itemvalue,
            date=date,
            clientname=status,
            description="فقد او تلف للصنف",
            clientbalance=int(data.get('quantity', 0)) or 0,
            pno_instance=pno_instance,
            pno=pno_instance.pno
        )

        success_message = 'Record added successfully.'
        logger.info(success_message)

        return Response({'success': True, 'message': success_message, "new_balance": pno_instance.itemvalue})

    except json.JSONDecodeError as e:
        error_message = f'Invalid JSON format: {e}'
        logger.error(error_message)
        return Response({'success': False, 'message': 'Invalid JSON format.'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        error_message = f'Unexpected error: {e}'
        logger.error(error_message)
        return Response({'success': False, 'message': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""Get all clients from DB along with their balance""",
tags=["Clients"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_clients(request):
    try:
        # Query the database for all clients
        items = AllClientsTable.objects.all().values(
            'clientid', 'name', 'address', 'email', 'website',
            'phone', 'mobile', 'last_transaction', 'type',
            'category', 'loan_period', 'loan_limit', 'loan_day',
            'subtype', 'client_stop', 'curr_flag', 'permissions',
            'other', 'accountcurr', 'last_transaction_amount'
        )

        # Prepare a list to include balance for each client
        data = []

        for item in items:
            clientid = item['clientid']

            # Calculate balance from TransactionsHistoryTable
            balance_data = TransactionsHistoryTable.objects.filter(object_id=clientid).aggregate(
                total_debt=Sum('debt'),
                total_credit=Sum('credit')
            )

            total_debt = balance_data.get('total_debt') or 0
            total_credit = balance_data.get('total_credit') or 0
            balance = round(total_credit - total_debt, 2)  # Ensure two decimal digits

            # Fetch total credit for specific client_id and where details = "دفعة على حساب"
            specific_credit_data = TransactionsHistoryTable.objects.filter(
                object_id=clientid, details="دفعة على حساب"
            ).aggregate(total_specific_credit=Sum('credit'))

            total_specific_credit = specific_credit_data.get('total_specific_credit') or 0

            # Add balance and specific credit to the client's data
            item['balance'] = balance
            item['paid_total'] = total_specific_credit  # Add the total specific credit
            data.append(item)

        # Pagination parameters from the request
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('size', 100))

        # Create paginator
        paginator = Paginator(data, page_size)
        page_obj = paginator.get_page(page_number)

        # Prepare the response
        response = {
            "data": list(page_obj),  # Convert the current page items to a list
            "last_page": paginator.num_pages,  # Total number of pages
            "total_rows": paginator.count,  # Total number of rows
            "page_size": page_size,
            "page_no": page_number,
        }

        return Response(response)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""create a new client record to DB""",
tags=["Clients"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_client_record(request):
    if request.method == 'POST':
        data = request.data  # DRF will parse the JSON data automatically

        # Validate required fields
        if not data.get('phone') or not data.get('password'):
            return Response({'status': 'error', 'message': 'Phone number and Password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if phone number already exists
        existing_phones = User.objects.values_list('username', flat=True)
        if data.get('phone') in existing_phones:
            return Response({'status': 'error', 'message': 'Phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Encrypt the password
        password = make_password(data.get('password'))

        # Create the client record
        try:
            new_item = AllClientsTable.objects.create(
                name=data.get('client_name', '').strip() or None,
                address=data.get('address', '').strip() or None,
                email=data.get('email', '').strip() or None,
                website=data.get('website', '').strip() or None,
                phone=data.get('phone', '').strip() or None,
                mobile=data.get('mobile', '').strip() or None,
                last_transaction_amount=data.get('last_transaction', '0').strip() or '0',
                accountcurr=data.get('currency', '').strip() or None,
                type="عميل",
                category=data.get('sub_category', '').strip() or None,
                loan_period=int(data.get('limit', '0')) if str(data.get('limit', '0')).isdigit() else None,
                loan_limit=float(data.get('limit_value', '0.0')) if data.get('limit_value') else None,
                loan_day=data.get('installments') or None,
                subtype=data.get('types', '').strip() or None,
                client_stop=True if str(data.get('client_stop', '0')).lower() in ['on', '1', 'true'] else False,
                curr_flag=bool(int(data.get('curr_flag', '0'))) if str(data.get('curr_flag', '0')).isdigit() else False,
                permissions=data.get('permissions', '').strip() or None,
                other=data.get('other', '').strip() or None,
                username=data.get('phone'),
                password=password,
            )

            # Create User instance
            user = User.objects.create_user(username=data.get('phone'), email=data.get('email'), password=data.get('password'))
            user.save()

            return Response({'status': 'success', 'message': 'Record created successfully!'})

        except ValidationError as e:
            return Response({'status': 'error', 'message': f'Validation Error: {e.message_dict}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'status': 'error', 'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
description="""update a client data from DB""",
tags=["Clients"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_client_record(request):
    if request.method == 'POST':
        try:
            data = request.data  # DRF will parse the JSON data automatically
            client_id = data.get('client_id')

            # Retrieve the client record
            client = AllClientsTable.objects.get(clientid=client_id)

            # Update client fields
            client.name = data.get('client_name', client.name)
            client.address = data.get('address', client.address)
            client.email = data.get('email', client.email)
            client.website = data.get('website', client.website)
            client.phone = data.get('phone', client.phone)
            client.mobile = data.get('mobile', client.mobile)
            client.last_transaction = data.get('last_transaction', client.last_transaction)
            client.accountcurr = data.get('currency', client.accountcurr)
            client.type = data.get('account_type', client.type)
            client.category = data.get('sub_category', client.category)
            client.loan_period = (
                int(data['limit']) if data.get('limit') and data['limit'].isdigit() else client.loan_period
            )
            client.loan_limit = float(data['limit_value']) if data.get('limit_value') else client.loan_limit
            client.loan_day = data.get('installments', client.loan_day)
            client.subtype = data.get('types', client.subtype)
            client.client_stop = data.get('client_stop') in ['on', '1', True]
            client.curr_flag = bool(int(data.get('curr_flag', 0)))
            client.permissions = data.get('permissions', client.permissions)
            client.other = data.get('other', client.other)
            client.geo_location = data.get('geo_location') if data.get('geo_location') else None

            client.save()

            return Response({'status': 'success', 'message': 'Record updated successfully!'})

        except AllClientsTable.DoesNotExist:
            return Response({'status': 'error', 'message': 'Client record not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'status': 'error', 'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
description="""delete a client record from DB""",
tags=["Clients"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_client_record(request):
    try:
        # Parse request data
        data = request.data
        client_id = data.get('client_id')

        if not client_id:
            return Response({'status': 'error', 'message': 'Client ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the client instance
        client = AllClientsTable.objects.get(clientid=client_id)

        # Delete the client record
        client.delete()

        return Response({'status': 'success', 'message': 'Record deleted successfully!'}, status=status.HTTP_200_OK)

    except AllClientsTable.DoesNotExist:
        return Response({'status': 'error', 'message': 'Client record not found.'}, status=status.HTTP_404_NOT_FOUND)

    except json.JSONDecodeError:
        return Response({'status': 'error', 'message': 'Invalid JSON in request body.'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
description="""filter all clients from DB""",
tags=["Clients"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filter_all_clients(request):
    try:
        filters = request.data  # Get the filters from the request body

        # Default query
        queryset = AllClientsTable.objects.all()

        # Apply filters (ID, Name, Email, etc.)
        if filters.get("id"):
            queryset = queryset.filter(clientid__icontains=filters["id"])
        if filters.get("name"):
            queryset = queryset.filter(name__icontains=filters["name"])
        if filters.get("email"):
            queryset = queryset.filter(email__icontains=filters["email"])
        if filters.get("phone"):
            queryset = queryset.filter(phone__icontains=filters["phone"])
        if filters.get("mobile"):
            queryset = queryset.filter(mobile__icontains=filters["mobile"])
        if filters.get("subtype"):
            queryset = queryset.filter(category__icontains=filters["subtype"])

        # Date range filter
        fromdate = filters.get('fromdate', '').strip()
        todate = filters.get('todate', '').strip()

        if fromdate and todate:
            try:
                # Parse dates
                from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)

                # Apply date range filter
                queryset = queryset.filter(last_transaction__range=[from_date_obj, to_date_obj])
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the data
        clients_data = []
        for client in queryset:
            client_id = client.clientid
            balance_data = TransactionsHistoryTable.objects.filter(object_id=client_id).aggregate(
                total_debt=Sum("debt"),
                total_credit=Sum("credit"),
            )
            total_debt = balance_data.get("total_debt") or 0
            total_credit = balance_data.get("total_credit") or 0
            balance = round(total_credit - total_debt, 2)

            # Apply balance filters (Paid, Debtor, Creditor)
            filter_type = filters.get("filter")
            if filter_type == "paid" and balance != 0:
                continue  # Skip if balance is not zero
            elif filter_type == "debtor" and balance >= 0:
                continue  # Skip if balance is not negative
            elif filter_type == "creditor" and balance <= 0:
                continue  # Skip if balance is not positive
            if fromdate and todate:
                # Fetch total credit for specific client_id and where details = "دفعة على حساب"
                specific_credit_data = TransactionsHistoryTable.objects.filter(
                    object_id=client_id, details="دفعة على حساب", registration_date__range=[from_date_obj, to_date_obj]
                ).aggregate(total_specific_credit=Sum('credit'))
            else:
                # Fetch total credit for specific client_id and where details = "دفعة على حساب"
                specific_credit_data = TransactionsHistoryTable.objects.filter(
                    object_id=client_id, details="دفعة على حساب"
                ).aggregate(total_specific_credit=Sum('credit'))

            total_specific_credit = specific_credit_data.get('total_specific_credit') or 0

            # Add the filtered client data
            clients_data.append(
                {
                    "clientid": client.clientid,
                    "loan_limit": client.loan_limit,
                    "name": client.name,
                    "address": client.address,
                    "email": client.email,
                    "phone": client.phone,
                    "mobile": client.mobile,
                    "subtype": client.subtype,
                    "category": client.category,
                    "last_transaction_amount": client.last_transaction_amount,
                    "last_transaction": client.last_transaction,
                    "balance": balance,
                    "paid_total": total_specific_credit,
                }
            )

        # Pagination parameters from the request
        page_number = int(filters.get("page") or 1)
        page_size = int(filters.get("size") or 100)

        # Create paginator
        paginator = Paginator(clients_data, page_size)
        page_obj = paginator.get_page(page_number)

        # Prepare the response
        response = {
            "data": list(page_obj),  # Convert the current page items to a list
            "last_page": paginator.num_pages,  # Total number of pages
            "total_rows": paginator.count,  # Total number of rows
            "page_size": page_size,
            "page_no": page_number,
        }
        return Response(response)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
description="""create a new storage record""",
tags=["Storage Transactions"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_storage_record(request):
    try:
        data = request.data  # Django REST framework automatically parses the JSON data

        transaction_date = make_aware(datetime.strptime(data.get("transaction_date"), '%Y-%m-%d'))

        new_record = StorageTransactionsTable(
            reciept_no=data.get("reciept_no", ""),
            transaction_date=transaction_date,
            amount=data.get("amount"),
            issued_for=data.get("for_what", ""),
            note=data.get("note", ""),
            account_type=data.get("type", ""),
            transaction=data.get("transaction", ""),
            place=data.get("place", ""),
            section=data.get("section", ""),
            subsection=data.get("subsection", ""),
            person=data.get("for_who", ""),
            payment=data.get("pay_method", ""),
            daily_status=data.get("daily"),
            bank=data.get("bank"),
            check_no=data.get("checkno"),
        )
        new_record.save()

        client_id = None
        if data.get("for_who"):
            client = AllClientsTable.objects.filter(name=data.get("for_who")).first()
            if not client:
                error_msg = f"Client '{data.get('for_who')}' not found"
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
            client_id = client.clientid

        last_balance = (
            TransactionsHistoryTable.objects.filter(object_id=client_id)
            .order_by("-registration_date")
            .first()
        )
        last_balance_amount = last_balance.current_balance if last_balance else 0
        updated_balance = round(last_balance_amount + data.get("amount"), 2)

        account_statement = TransactionsHistoryTable(
            credit=float(data.get("amount")),
            debt=0.0,
            transaction=data.get("section"),
            details=f"{data.get('subsection')} / {data.get('reciept_no')}",
            registration_date=transaction_date,
            current_balance=updated_balance,  # Updated balance
            content_type=ContentType.objects.get_for_model(client),
            object_id=client_id,  # Client ID
        )
        account_statement.save()

        return Response({"message": "Record created successfully!"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
description="""delete a storage record""",
tags=["Storage Transactions"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_storage_record(request):
    try:
        storage_id = request.data.get("storage_id")

        record = get_object_or_404(StorageTransactionsTable, storageid=storage_id)

        # Delete the record
        record.delete()

        return Response({"message": "Record deleted successfully!"}, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format."}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
description="""Get all storage records""",
tags=["Storage Transactions"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_storage(request):
    try:
        items = StorageTransactionsTable.objects.all().values(
            'storageid', 'account_type', 'transaction', 'transaction_date',
            'reciept_no', 'place', 'section', 'subsection', 'person', 'amount',
            'issued_for', 'payment', 'done_by', 'bank', 'check_no', 'daily_status'
        )

        data = list(items)
        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""filter all storage records""",
tags=["Storage Transactions"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filter_all_storage(request):
    try:
        filters = request.data  # Django REST Framework automatically parses JSON data

        # Default query
        queryset = StorageTransactionsTable.objects.all()

        # Apply filters
        if filters.get("id"):
            queryset = queryset.filter(storageid__icontains=filters["id"])

        if filters.get("client"):
            queryset = queryset.filter(person__icontains=filters["client"])
        if filters.get("account_detail"):
            queryset = queryset.filter(issued_for__icontains=filters["account_detail"])
        if filters.get("section"):
            queryset = queryset.filter(section__icontains=filters["section"])
        if filters.get("subsection"):
            queryset = queryset.filter(subsection__icontains=filters["subsection"])
        if filters.get("type"):
            queryset = queryset.filter(account_type__icontains=filters["type"])
        if filters.get("transaction"):
            queryset = queryset.filter(transaction__icontains=filters["transaction"])
        if filters.get("payment"):
            queryset = queryset.filter(payment__icontains=filters["payment"])
        if filters.get("place"):
            queryset = queryset.filter(place__icontains=filters["place"])

        # Date range filter
        fromdate = filters.get('fromdate', '').strip()
        todate = filters.get('todate', '').strip()

        if fromdate and todate:
            try:
                # Parse dates
                from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)

                # Apply date range filter
                queryset = queryset.filter(transaction_date__range=[from_date_obj, to_date_obj])
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        # Return the filtered results as JSON
        data = list(queryset.values())  # Use `values()` to return only the fields you need
        return Response(data, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""get last auto id from StorageTransactionsTable """,
tags=["Storage Transactions"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_last_reciept_no(request):
    transaction_type = request.GET.get('transactionType')  # Get the transaction type from the query parameter

    if transaction_type in ['ايداع', 'صرف']:
        # Cast `reciept_no` to an integer for proper ordering
        last_transaction = StorageTransactionsTable.objects.annotate(
            reciept_no_int=Cast('reciept_no', IntegerField())
        ).filter(
            transaction=transaction_type
        ).order_by('-reciept_no_int').first()

        last_reciept_no = last_transaction.reciept_no_int if last_transaction else 0
        return Response({'lastRecieptNo': last_reciept_no}, status=status.HTTP_200_OK)

    return Response({'error': 'Invalid transaction type'}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
description="""get last invoice no from Buyinvoicetable """,
tags=["Buy Invoice"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_buyinvoice_no(request):
    try:
        # Get the last autoid by ordering the table by invoice_no in descending order
        last_invoice = Buyinvoicetable.objects.order_by('-invoice_no').first()
        if last_invoice:
            response_data = {'autoid': last_invoice.invoice_no}
        else:
            # Handle the case where the table is empty
            response_data = {'autoid': 0, 'message': 'No invoices found'}
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""get account statement for a client by client id """,
tags=["Clients","Transactions History"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_statement(request):
    client_id = request.GET.get('id')
    if not client_id:
        return Response({'error': 'Client ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    client = None
    content_type = None

    try:
        # Try getting client from AllClientsTable
        client = models.AllClientsTable.objects.get(clientid=client_id)
        content_type = ContentType.objects.get_for_model(models.AllClientsTable)
    except models.AllClientsTable.DoesNotExist:
        try:
            # Try getting client from EmployeesTable
            client = models.EmployeesTable.objects.get(employee_id=client_id)
            content_type = ContentType.objects.get_for_model(models.EmployeesTable)
        except models.EmployeesTable.DoesNotExist:
            raise Http404("Client not found")

    try:
        # Get all transactions related to the client using GenericForeignKey
        items = models.TransactionsHistoryTable.objects.filter(
            content_type=content_type,
            object_id=client_id
        )

        # Serialize the results
        serializer = TransactionsHistoryTableSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""get a specific buy invoice's items """,
tags=["Buy Invoice"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_invoice_items(request):
    invoice_no = request.GET.get("id")
    if not invoice_no:
        return Response({"error": "Invoice number is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        items = BuyInvoiceItemsTable.objects.filter(invoice_no2=invoice_no)
        serializer = BuyInvoiceItemsTableSerializer(items, many=True)
        return Response(serializer.data if items else [], status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def format_number(number):
    return f"{number:,.2f}"


@extend_schema(
description="""create a new record for Costs Table """,
tags=["Costs"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_cost_record(request):
    try:
        # Parse the incoming JSON data
        data = request.data  # Django REST Framework handles the parsing automatically

        # Extract the data fields
        invoice = data.get("invoice")
        cost_type = data.get("type")
        cost = data.get("cost")
        rate = data.get("rate")
        dinar = data.get("dinar")

        # Validate the data
        if not invoice or not cost_type or not cost or not rate or not dinar:
            return Response({"success": False, "message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the invoice object
        try:
            invoice_obj = Buyinvoicetable.objects.get(invoice_no=invoice)
        except Buyinvoicetable.DoesNotExist:
            return Response({"success": False, "message": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        # Create a new record in the BuyinvoiceCosts model
        cost_record = BuyinvoiceCosts.objects.create(
            invoice=invoice_obj,
            cost_for=cost_type,
            cost_price=cost,
            exchange_rate=rate,
            dinar_cost_price=dinar,
            invoice_no=invoice
        )

        # Return a success response with the created cost record's ID
        return Response({"success": True, "message": "Cost record created successfully", "data": {"id": cost_record.autoid}}, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return Response({"success": False, "message": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""fetch all records for Costs Table """,
tags=["Costs"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_costs(request):
    invoice_no = request.GET.get("id")

    if not invoice_no:
        return Response({"error": "Invoice number is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the costs related to the invoice
        costs = BuyinvoiceCosts.objects.filter(invoice_no=invoice_no)
        if not costs:
            return Response([], status=status.HTTP_200_OK)

        # Serialize the results using the BuyinvoiceCostsSerializer
        serializer = BuyinvoiceCostsSerializer(costs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""delete a record for Costs Table """,
tags=["Costs"],
)
@api_view(['DELETE'])
def delete_buyinvoice_cost(request, autoid):
    try:
        # Find the record and delete it
        record = BuyinvoiceCosts.objects.get(autoid=autoid)
        record.delete()
        return Response({'status': 'success', 'message': 'Record deleted successfully!'}, status=status.HTTP_200_OK)

    except BuyinvoiceCosts.DoesNotExist:
        return Response({'status': 'error', 'message': 'Record not found!'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""calculate cost price for a buy invoice """,
tags=["Costs"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_cost(request):
    try:
        # Parse the incoming JSON data
        data = request.data  # Django REST Framework handles the parsing automatically

        cost_total = data.get("cost_total").replace(',', '')
        invoice_total = data.get("invoice_total").replace(',', '')
        invoice_id = data.get("invoice")

        # Validate the data
        if not cost_total or not invoice_total or not invoice_id:
            return Response({"success": False, "message": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the load percentage
        load_percentage = Decimal(cost_total) / Decimal(invoice_total)

        # Get the invoice object
        try:
            invoice = Buyinvoicetable.objects.get(invoice_no=invoice_id)
        except Buyinvoicetable.DoesNotExist:
            return Response({"success": False, "message": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the items associated with the invoice
        items = BuyInvoiceItemsTable.objects.filter(invoice_no2=invoice_id)
        for item in items:
            # Update the cost price based on the load percentage
            item.current_cost_price = item.dinar_unit_price * (1 + load_percentage)
            item.cost_unit_price = item.dinar_unit_price * (1 + load_percentage)
            item.cost_total_price = (item.dinar_unit_price * (1 + load_percentage)) * item.quantity
            item.save()

        # Serialize the updated items and return as response
        serializer = BuyInvoiceItemsTableSerializer(items, many=True)
        return Response({"success": True, "message": "Cost updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""get a specific buy invoice's items by invoice no """,
tags=["Buy Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_invoice_items(request):
    try:
        # Parse incoming data
        data = request.data
        invoice_id = data.get("id")

        if not invoice_id:
            return Response({"error": "Invoice id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch items related to the invoice
        items = BuyInvoiceItemsTable.objects.filter(invoice_no=invoice_id)
        if not items:
            return Response({"error": "Invoice does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the items and return them as response
        serializer = BuyInvoiceItemsTableSerializer(items, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""////""",
tags=["External"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_data(request):
    try:
        # Parse the JSON data sent by the frontend
        data = request.data

        auto_id = data.get("id")
        currency = data.get("currency")
        rate = data.get("rate")

        # Validate data
        if not auto_id or not currency or not rate:
            return Response({"success": False, "message": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Store data in session
        request.session['auto_id'] = auto_id
        request.session['currency'] = currency
        request.session['rate'] = rate

        # Redirect to the target page
        return Response({"success": True, "message": "Data processed successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""////// """,
tags=["External"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_add_data(request):
    try:
        # Parse the JSON data sent by the frontend
        data = request.data

        source = data.get("source")
        invoice = data.get("invoice")
        date = data.get("date")
        currency = data.get("currency")
        rate = data.get("rate")
        temp = data.get("temp")

        # Validate data
        if not invoice or not currency or not rate or not source or not date:
            return Response({"success": False, "message": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Store data in session
        request.session['data'] = data

        # Redirect to the target page
        return Response({"success": True, "message": "Data processed and stored in session"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
description="""delete a specific buy invoice's item by his autoid""",
tags=["Buy Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_buy_invoice_item(request):
    try:
        # Parse the JSON data sent by the frontend
        data = request.data

        item_id = data.get("id")

        # Validate if item_id is provided
        if not item_id:
            return Response({"success": False, "message": "Missing item ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Try to delete the item from the database
        try:
            item = BuyInvoiceItemsTable.objects.get(autoid=item_id)
            item.delete()
        except BuyInvoiceItemsTable.DoesNotExist:
            return Response({"success": False, "message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        # Return success response
        return Response({"success": True, "message": "Item deleted successfully!"}, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle unexpected errors
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""update a specific buy invoice's item data """,
tags=["Buy Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_buyinvoiceitem(request):
    try:
        # Parse the JSON data sent by the frontend
        data = request.data

        id = data.get('id')
        invoice_no = data.get('invoice_no')
        org = Decimal(data.get('org'))
        order = Decimal(data.get('order'))
        quantity = int(data.get('quantity'))

        # Find the item to update
        try:
            item = BuyInvoiceItemsTable.objects.get(autoid=id)
        except BuyInvoiceItemsTable.DoesNotExist:
            return Response({"success": False, "message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the related invoice and update the amount
        try:
            invoice = Buyinvoicetable.objects.get(invoice_no=invoice_no)
            invoice.amount -= item.dinar_total_price
            invoice.amount += order * quantity
            invoice.save()
        except Buyinvoicetable.DoesNotExist:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update the item with new values
        item.org_unit_price = org
        item.dinar_unit_price = order
        item.org_total_price = org * quantity
        item.dinar_total_price = order * quantity
        item.quantity = quantity
        item.save()

        # Return success response with updated item
        serializer = BuyInvoiceItemsTableSerializer(item)
        return Response({"success": True, "message": "Item updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



def excel_date_to_datetime(serial):
    return datetime.datetime(1900, 1, 1) + datetime.timedelta(days=serial - 2)

@extend_schema(
description="""////// """,
tags=["Excel"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_buyInvoice_excel(request):
    try:
        # Debug: Log the start of the POST request
        logger.debug("Received POST request at /process_buyInvoice_excel/")

        # Parse the JSON data from the request body
        body = request.data
        data = json.loads(body['data'])  # Parse the 'data' stringified JSON
        invoice_no = body.get('invoice_no')

        if not invoice_no:
            return Response({"status": "error", "message": "Invoice number is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Attempt to retrieve the invoice from the database
        try:
            invoice = Buyinvoicetable.objects.get(invoice_no=invoice_no)
        except Buyinvoicetable.DoesNotExist:
            return Response({"status": "error", "message": "Invoice not found in the database."}, status=status.HTTP_404_NOT_FOUND)

        # Process the data and insert it into the database
        records = []
        for item in data:
            try:
                # Create a BuyInvoiceItemsTable record for each item
                records.append(BuyInvoiceItemsTable(
                    invoice_no2=invoice_no,
                    invoice_no=invoice,
                    item_no=item.get("الرقم الاصلي"),
                    main_cat=item.get("البيان الرئيسي"),
                    sub_cat=item.get("البيان الفرعي"),
                    name=item.get("اسم الصنف", "failed"),
                    company=item.get("الشركة"),
                    quantity=item.get("الكمية"),
                    place=item.get("مكان التخزين"),
                    buysource=item.get("المصدر"),
                    org_unit_price=item.get("سعر التوريد"),
                    org_total_price=Decimal(item.get("سعر التوريد", 0)) * Decimal(item.get("الكمية", 0)),
                    dinar_unit_price=item.get("سعر الشراء"),
                    dinar_total_price=Decimal(item.get("سعر الشراء", 0)) * Decimal(item.get("الكمية", 0)),
                    cost_unit_price=item.get("سعر التكلفة"),
                    cost_total_price=Decimal(item.get("سعر التكلفة", 0)) * Decimal(item.get("الكمية", 0)),
                    current_buy_price=item.get("سعر البيع"),
                    note=item.get("ملاحظات"),
                    company_no=item.get("رقم الشركة"),
                    barcodeno=item.get("رقم الباركود"),
                    e_name=item.get("الاسم بالانجليزي"),
                    currency=item.get("العملة"),
                    current_less_price=item.get("اقل سعر للبيع"),
                    pno=item.get("الرقم الخاص"),
                    exchange_rate=item.get("سعر الصرف"),
                    date=item.get("التاريخ"),
                ))

                # Check if item exists and create a MainItem if necessary
                exists = item.get("exists")
                if exists == 0:
                    Mainitem.objects.create(
                        itemno=item.get("الرقم الاصلي"),
                        replaceno=item.get("رقم الشركة"),
                        itemname=item.get("اسم الصنف", "failed"),
                        companyproduct=item.get("الشركة"),
                        eitemname=item.get("الاسم بالانجليزي"),
                        orgprice=item.get("سعر التوريد", 0),
                        orderprice=item.get("سعر الشراء", 0),
                        costprice=item.get("سعر التكلفة", 0),
                        itemvalue=item.get("الكمية", 0),
                        itemmain=item.get("البيان الرئيسي"),
                        itemsubmain=item.get("البيان الفرعي"),
                        pno=item.get("الرقم الخاص"),
                        barcodeno=item.get("رقم الباركود"),
                        currtype=item.get("العملة"),
                        lessprice=item.get("اقل سعر للبيع"),
                        currvalue=item.get("سعر الصرف"),
                        memo=item.get("ملاحظات"),
                        itemplace=item.get("مكان التخزين"),
                    )
            except Exception as item_error:
                logger.error(f"Error processing item {item}: {item_error}")
                continue

        # Bulk create records in the database
        BuyInvoiceItemsTable.objects.bulk_create(records)
        logger.debug(f"Successfully inserted {len(records)} records from Tabulator data.")
        return Response({"status": "success", "message": "Tabulator data imported successfully."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error processing imported data: {e}")
        return Response({"status": "error", "message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@extend_schema(
description="""get a specific buy invoice details """,
tags=["Buy Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_temp_confirm(request):
    try:
        # Step 1: Parse the JSON data from the request body
        data = request.data

        # Step 2: Get the invoice number and validate
        invoice_no = data.get('invoice_no')

        if not invoice_no:
            return Response({'status': 'error', 'message': 'Invoice number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Try to fetch invoice items for the given invoice number
        try:
            invoice_items = BuyInvoiceItemsTable.objects.filter(invoice_no=invoice_no)
        except BuyInvoiceItemsTable.DoesNotExist:
            return Response({'status': 'error', 'message': 'Invoice item not found in the BuyInvoiceItemsTable.'}, status=status.HTTP_404_NOT_FOUND)

        # Step 4: Serialize invoice items into a list of dictionaries
        items_data = []
        for item in invoice_items:
            items_data.append({
                'item_no': item.item_no,
                'company': item.company,
                'company_no': item.company_no,
                'name': item.name,
                'dinar_unit_price': item.dinar_unit_price,
                'dinar_total_price': item.dinar_total_price,
                'quantity': item.quantity,
                'note': item.note,
                'cost_unit_price': item.cost_unit_price,
                'org_unit_price': item.org_unit_price,
            })

        # Step 5: Fetch the invoice details from Buyinvoicetable
        try:
            invoice = Buyinvoicetable.objects.get(autoid=invoice_no)

            # Prepare invoice details for response
            invoice_details = {
                'original': invoice.original_no,
                'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else None,
                'arrive_date': invoice.arrive_date.strftime('%Y-%m-%d') if invoice.arrive_date else None,
                'source': invoice.source,
                'invoice_items': items_data,
            }

            return Response({'status': 'success', 'message': 'Invoice details fetched successfully.', 'data': invoice_details}, status=status.HTTP_200_OK)

        except Buyinvoicetable.DoesNotExist:
            return Response({'status': 'error', 'message': 'Invoice not found in the Buyinvoicetable.'}, status=status.HTTP_404_NOT_FOUND)

    except ValueError:
        return Response({'status': 'error', 'message': 'Invalid JSON data.'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
description="""Confirm a pending temp sell invoice""",
tags=["Buy Invoice"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_temp_invoice(request):
    try:
        # Parse the JSON data from the request body
        data = request.data
        invoice_no = data.get('invoice_no')
        item_rows = data.get('table')

        if not invoice_no:
            return Response({'status': 'error', 'message': 'Invoice number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not item_rows or not isinstance(item_rows, list):
            return Response({'status': 'error', 'message': 'Invalid or empty item rows.'}, status=status.HTTP_400_BAD_REQUEST)

        # Process Mainitem updates
        success_count = 0
        error_details = []

        for item in item_rows:
            try:
                # Fetch the invoice using company_no
                main = Mainitem.objects.get(replaceno=item['company_no'])

                # Update fields
                main.itemname = item['name']
                main.itemvalue += int(item['quantity'] or 0)
                main.orderprice = Decimal(item['dinar_unit_price'] or 0)
                main.costprice = (main.costprice + Decimal(item['cost_unit_price'] or 0)) / 2
                main.orgprice = Decimal(item['org_unit_price'] or 0)
                main.itemno = item['item_no']
                main.save()

                movement_Record = Clientstable.objects.create(
                    itemno=main.itemno,
                    itemname=main.itemname,
                    maintype=main.itemmain,
                    currentbalance=main.itemvalue,
                    date=timezone.now(),
                    clientname="فاتورة شراء",
                    billno=invoice_no,
                    description="ترحيل فاتورة شراء",
                    clientbalance=int(item['quantity'] or 0),
                    pno_instance=main,
                    pno=main.pno
                )

                success_count += 1

            except Mainitem.DoesNotExist:
                error_details.append({
                    'company_no': item.get('company_no'),
                    'message': 'Main item not found.'
                })
            except Exception as e:
                error_details.append({
                    'company_no': item.get('company_no'),
                    'message': f'Error processing item: {str(e)}'
                })

        # Process Buyinvoicetable update
        try:
            invoice = Buyinvoicetable.objects.get(autoid=invoice_no)
            invoice.temp_flag = 0
            invoice.save()
        except Buyinvoicetable.DoesNotExist:
            return Response({'status': 'error', 'message': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Consolidate response
        response = {
            'status': 'success' if success_count > 0 else 'error',
            'success_count': success_count,
            'error_count': len(error_details),
            'errors': error_details,
            'message': f'{success_count} items updated successfully and invoice temp_flag set to 0.' if success_count > 0 else 'No items were updated.',
        }
        return Response(response, status=status.HTTP_200_OK)

    except ValueError:
        return Response({'status': 'error', 'message': 'Invalid JSON data.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'status': 'error', 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""create a new buy invoice item""",
tags=["Buy Invoice","Buy Invoice Items"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def BuyInvoiceItemCreateView(request):
    try:
        # Parse the JSON data
        data = request.data

        # Validate required fields
        required_fields = [
            "invoice_id", "itemno", "pno", "itemname", "companyproduct",
            "replaceno", "itemvalue", "currency", "itemplace", "source",
            "orgprice", "buyprice", "orderprice", "lessprice"
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the related invoice
        try:
            invoice = Buyinvoicetable.objects.get(invoice_no=data.get("invoice_id"))
            invoice.amount += (Decimal(data.get("orderprice") or 0) * Decimal(data.get("itemvalue") or 0))
            invoice.save()
        except Buyinvoicetable.DoesNotExist:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            product = Mainitem.objects.get(pno=data.get("pno"))
            submain = product.itemsubmain if product.itemsubmain else None
        except Mainitem.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create a new BuyInvoiceItemsTable instance
        item = BuyInvoiceItemsTable.objects.create(
            invoice_no=invoice,
            invoice_no2=data.get("invoice_id"),
            item_no=data.get("itemno"),
            pno=data.get("pno"),
            main_cat=data.get("main_cat"),
            sub_cat=submain,
            name=data.get("itemname"),
            company=data.get("companyproduct"),
            company_no=data.get("replaceno"),
            quantity=int(data.get("itemvalue") or 0),
            currency=data.get("currency"),
            exchange_rate=float(data.get("rate") or 0) if data.get("rate") not in [None, '', 'null'] else 0,
            date=data.get("date"),
            place=data.get("itemplace"),
            buysource=data.get("source"),
            org_unit_price=float(data.get("orgprice") or 0),
            org_total_price=float(data.get("orgprice") or 0) * int(data.get("itemvalue") or 0),
            dinar_unit_price=float(data.get("orderprice") or 0),
            dinar_total_price=float(data.get("orderprice") or 0) * int(data.get("itemvalue") or 0),
            prev_quantity=int(data.get("prev_quantity") or 0),
            prev_cost_price=float(data.get("prev_cost_price") or 0),
            prev_buy_price=float(data.get("prev_buy_price") or 0),
            prev_less_price=float(data.get("prev_less_price") or 0),
            current_quantity=int(data.get("prev_quantity") or 0) + int(data.get("itemvalue") or 0),
            current_buy_price=float(data.get("buyprice") or 0),
            current_less_price=float(data.get("lessprice") or 0),
        )

        confirm_message = "not confirmed"
        if data.get("isTemp") == 0:
            main = Mainitem.objects.get(replaceno=data.get("replaceno"))
            main.orgprice = float(data.get("orgprice") or 0)
            main.lessprice = float(data.get("lessprice") or 0)
            main.itemvalue += int(data.get("itemvalue") or 0)
            main.itemtemp -= int(data.get("itemvalue") or 0)
            main.itemplace = data.get("itemplace")
            main.buyprice = float(data.get("buyprice") or 0)
            main.save()
            confirm_message = "confirmed"

            movement_Record = Clientstable.objects.create(
                itemno=main.itemno,
                itemname=main.itemname,
                maintype=main.itemmain,
                currentbalance=main.itemvalue,
                date=timezone.now(),
                clientname="فاتورة شراء",
                billno=data.get("invoice_id"),
                description="فاتورة شراء",
                clientbalance=int(data.get("itemvalue") or 0),
                pno_instance=main,
                pno=main.pno
            )

        return Response({"message": "Item created successfully", "item_id": item.autoid, "confirm_status": confirm_message}, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""fetch all buy invoices""",
tags=["Buy Invoice"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_buyinvoices(request):
    records = Buyinvoicetable.objects.all()
    paginator = Paginator(records, int(request.GET.get('size', 100)))

    page_number = int(request.GET.get('page', 1))
    page_obj = paginator.get_page(page_number)

    serializer = BuyInvoiceSerializer(page_obj, many=True)

    total_amount = Buyinvoicetable.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    response = {
        "data": serializer.data,
        "last_page": paginator.num_pages,
        "total_rows": paginator.count,
        "page_size": paginator.per_page,
        "page_no": page_number,
        "total_amount": total_amount,
    }

    return Response(response)

@extend_schema(
description="""filter buy invoices""",
tags=["Buy Invoice",],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filter_buyinvoices(request):
    try:
        filters = request.data  # DRF automatically parses the JSON body
        cache_key = f"filter_{hashlib.md5(str(filters).encode()).hexdigest()}"
        cached_data = cache.get(cache_key)

        if cached_data:
            cached_data["cached_flag"] = True
            return Response(cached_data)

        # Initialize the base Q object for filtering
        filters_q = Q()

        # Build the query based on the filters
        if filters.get('invoice_no'):
            filters_q &= Q(invoice_no__icontains=filters['invoice_no'])

        if filters.get('source'):
            filters_q &= Q(source__icontains=filters['source'])

        # Apply date range filter on `orderlastdate`
        fromdate = filters.get('fromdate', '').strip()
        todate = filters.get('todate', '').strip()

        if fromdate and todate:
            try:
                # Parse dates
                from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)

                # Apply date range filter
                filters_q &= Q(invoice_date__range=[from_date_obj, to_date_obj])

            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        # Now filter the queryset using the combined Q object
        queryset = Buyinvoicetable.objects.filter(filters_q)

        # Pagination parameters from the request
        page_number = filters.get('page', 1)
        page_size = filters.get('size', 20)

        # Pagination setup
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        page_obj = paginator.paginate_queryset(queryset, request)

        # Serialize the filtered data
        serializer = BuyInvoiceSerializer(page_obj, many=True)

        total_amount = queryset.aggregate(Sum('amount'))['amount__sum'] or 0

        # Prepare the response
        response = {
            "data": serializer.data,
            "last_page": paginator.page.paginator.num_pages,  # Total number of pages
            "total_rows": paginator.page.paginator.count,  # Total number of rows
            "page_size": page_size,
            "page_no": page_number,
            "cached_flag": False,
            "total_amount": total_amount,
        }

        # Cache the response for future use
        cache.set(cache_key, response, timeout=300)  # Cache for 5 minutes

        # Return the filtered data as JSON
        return Response(response)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@extend_schema(
description="""get last pno from mainitem table""",
tags=["Products"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_mainItem_last_pno(request):
    try:
        # Get the last pno by ordering the table by pno in descending order
        last_pno = Mainitem.objects.order_by('-pno').first()
        if last_pno:
            response_data = {'pno': last_pno.pno}
        else:
            # Handle the case where the table is empty
            response_data = {'pno': 0, 'message': 'No invoices found'}

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""create a new message""",
tags=["Support Desk"],
)
class SendMessageView(generics.CreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def create(self, request, *args, **kwargs):

     sender_id = request.data.get('sender')
     receiver_id = request.data.get('receiver')
     message_text = request.data.get('message')

     if not sender_id or not receiver_id:
        return Response({"error": "Sender and Receiver IDs are required"}, status=status.HTTP_400_BAD_REQUEST)

     try:
        sender_id = int(sender_id)
        receiver_id = int(receiver_id)
     except ValueError:
        return Response({"error": "Invalid sender or receiver ID"}, status=status.HTTP_400_BAD_REQUEST)

     sender = get_object_or_404(AllClientsTable, clientid=sender_id)
     receiver = get_object_or_404(AllClientsTable, clientid=receiver_id)

     chat_message = ChatMessage.objects.create(sender=sender, receiver=receiver, message=message_text)
     serializer = self.get_serializer(chat_message)

     return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(
description="""get a message by sender id and receiver id""",
tags=["Support Desk"],
)
class GetChatMessagesView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
     sender_id = self.request.query_params.get('sender')
     receiver_id = self.request.query_params.get('receiver')
     return ChatMessage.objects.filter(sender__clientid=sender_id, receiver__clientid=receiver_id) | ChatMessage.objects.filter(sender__clientid=receiver_id, receiver__clientid=sender_id)

@extend_schema(
description="""mark a message as read""",
tags=["Support Desk"],
)
class MarkMessageAsReadView(generics.UpdateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({"message": "Message marked as read"}, status=status.HTTP_200_OK)

@extend_schema(
description="""SupportChatConversation api""",
tags=["Support Desk"],
)
class SupportChatMessageView(APIView):
    def post(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation_id')
        sender_id = request.data.get('sender_id')
        sender_type = request.data.get('sender_type')
        message = request.data.get('message')

        try:
            sender = AllClientsTable.objects.get(clientid=sender_id)
            conversation = SupportChatConversation.objects.get(conversation_id=conversation_id)
        except AllClientsTable.DoesNotExist:
            return Response({'error': 'Sender not found'}, status=status.HTTP_404_NOT_FOUND)
        except SupportChatConversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create new message
        new_message = SupportChatMessageSys(
            conversation=conversation,
            sender=sender,
            sender_type=sender_type,
            message=message,
        )
        new_message.save()

        # Return the newly created message
        serializer = SupportChatMessageSysSerializer(new_message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        conversation_id = request.query_params.get('conversation_id')
        try:
            conversation = SupportChatConversation.objects.get(conversation_id=conversation_id)
        except SupportChatConversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        messages = SupportChatMessageSys.objects.filter(conversation=conversation).order_by('timestamp')
        serializer = SupportChatMessageSysSerializer(messages, many=True)
        return Response(serializer.data)

@extend_schema(
description="""create a new conversation""",
tags=["Support Desk"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    client_id = request.data.get('client_id')
    support_agent_id = request.data.get('support_agent_id')

    try:
        client = AllClientsTable.objects.get(clientid=client_id)
        support_agent = AllClientsTable.objects.get(clientid=support_agent_id)
    except AllClientsTable.DoesNotExist:
        return Response({'error': 'Client or Support Agent not found'}, status=status.HTTP_404_NOT_FOUND)

    conversation = SupportChatConversation(client=client, support_agent=support_agent)
    conversation.save()
    return Response({'conversation_id': conversation.conversation_id}, status=status.HTTP_201_CREATED)

@extend_schema(
description="""fetch all feedbacks""",
tags=["Support Desk"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_all_feedback(request):
    try:
        # Fetch all feedback and related sender data
        feedbacks = Feedback.objects.select_related('sender').all()

        # Group feedback by client ID
        grouped_feedback = {}

        for feedback in feedbacks:
            client_id = feedback.sender.clientid  # Assuming sender is linked to AllClientsTable
            if client_id not in grouped_feedback:
                grouped_feedback[client_id] = {
                    "client_name": feedback.sender.name,
                    "feedbacks": []
                }

            # Append feedback data
            grouped_feedback[client_id]["feedbacks"].append({
                "id": feedback.id,
                "feedback_text": feedback.feedback_text,
                "employee_response": feedback.employee_response,
                "is_resolved": feedback.is_resolved,
                "response_at": feedback.response_at.strftime("%Y-%m-%d %H:%M") if feedback.response_at else None
            })

        return Response(grouped_feedback, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @csrf_exempt
# def fetch_all_feedback(request):
#     """Fetch all feedbacks and their messages grouped by client ID."""
#     feedbacks = Feedback.objects.select_related('sender').prefetch_related('messages').all()

#     grouped_feedback = {}

#     for feedback in feedbacks:
#         client_id = feedback.sender.clientid
#         if client_id not in grouped_feedback:
#             grouped_feedback[client_id] = {
#                 "client_name": feedback.sender.name,
#                 "feedbacks": []
#             }

#         messages = [
#             {
#                 "id": message.id,
#                 "sender_type": message.sender_type,
#                 "message_text": message.message_text,
#                 "sent_at": message.sent_at.strftime("%Y-%m-%d %H:%M")
#             }
#             for message in feedback.messages.all()
#         ]

#         grouped_feedback[client_id]["feedbacks"].append({
#             "id": feedback.id,
#             "feedback_text": feedback.feedback_text,
#             "messages": messages,
#             "created_at": feedback.created_at.strftime("%Y-%m-%d %H:%M"),
#             "is_resolved": feedback.is_resolved  # Include the is_resolved field
#         })

#     return JsonResponse(grouped_feedback, safe=False)

@extend_schema(
description="""add message to feedback in conversation""",
tags=["Support Desk"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_message_to_feedback(request, feedback_id):
    """Allow clients and employees to send multiple messages in a feedback thread."""
    try:
        feedback = Feedback.objects.get(id=feedback_id)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get the data from the request body
    data = request.data
    message_text = data.get("message_text")
    sender_type = data.get("sender_type")  # Can be "client" or "employee"

    if not message_text:
        return Response({"error": "Message text is required."}, status=status.HTTP_400_BAD_REQUEST)
    if sender_type not in ["client", "employee"]:
        return Response({"error": "Invalid sender type."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the new message in the feedback thread
    message = FeedbackMessage.objects.create(
        feedback=feedback,
        sender_type=sender_type,
        message_text=message_text,
        sent_at=timezone.now()
    )

    # Serialize the message and return the response
    message_data = FeedbackMessageSerializer(message).data
    return Response(message_data, status=status.HTTP_201_CREATED)

@extend_schema(
description="""close a feedback thread""",
tags=["Support Desk"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_feedback(request, feedback_id):
    """Close a feedback thread (mark as resolved)."""
    try:
        feedback = Feedback.objects.get(id=feedback_id)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the session role is "employee"
    if request.session.get("role") == "employee":
        feedback.is_resolved = True  # Mark as resolved
        feedback.resolved_at = timezone.now()
        feedback.save()
        return Response({"message": "Feedback closed successfully."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Only employees can close feedback."}, status=status.HTTP_403_FORBIDDEN)

@extend_schema(
description="""delete a feedback thread""",
tags=["Support Desk"],
)
@api_view(['DELETE'])
def delete_feedback(request, feedback_id):
    """Delete a feedback thread."""
    try:
        feedback = Feedback.objects.get(id=feedback_id)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the session role is "employee"
    if request.session.get("role") == "employee":
        feedback.delete()
        return Response({"message": "Feedback deleted successfully."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Only employees can delete feedback."}, status=status.HTTP_403_FORBIDDEN)

@extend_schema(
description="""fetch feedbacks by client id""",
tags=["Support Desk"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_by_user_id(request):
    """Fetch feedback by client ID."""
    clientid = request.GET.get('clientid')

    if not clientid:
        return Response({"detail": "Client ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Try to fetch the client
    try:
        client = AllClientsTable.objects.get(clientid=clientid)
    except AllClientsTable.DoesNotExist:
        return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

    # Fetch feedback for this client
    feedbacks = Feedback.objects.filter(sender=client)

    # If no feedback is found, return an empty list
    if not feedbacks:
        return Response([])

    # Prepare the feedback data
    feedback_data = []
    for feedback in feedbacks:
        feedback_data.append({
            "id": feedback.id,
            "sender": feedback.sender.name,  # Assuming `sender.name` is the client name
            "feedback_text": feedback.feedback_text,
            "created_at": feedback.created_at.isoformat(),
            "employee_response": feedback.employee_response,
            "is_resolved": feedback.is_resolved,
            "response_at": feedback.response_at.isoformat() if feedback.response_at else None
        })

    return Response(feedback_data)

@extend_schema(
description="""fetch feedbacks by feedback id""",
tags=["Support Desk"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_feedback_messages(request, feedback_id):
    """Fetch messages in a feedback thread."""
    feedback_messages = FeedbackMessage.objects.filter(feedback_id=feedback_id).order_by('sent_at')

    messages_data = [
        {
            "id": msg.id,
            "sender_type": msg.sender_type,
            "message_text": msg.message_text,
            "sent_at": msg.sent_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for msg in feedback_messages
    ]

    return Response({"feedback_id": feedback_id, "messages": messages_data})



@extend_schema(
description="""Assign an order manually to an employee.""",
tags=["Delivery"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_order_manual(request):
    """Assign an order manually to an employee."""
    try:
        data = request.data
        employee_id = data.get('employee_id')
        order_id = data.get('order_id')

        if not employee_id or not order_id:
            return Response({'error': 'Employee ID and Order ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Get the selected employee
            employee_queue = get_object_or_404(EmployeeQueue, employee_id=employee_id, is_available=True, is_assigned=False)
            employee = employee_queue.employee

            # Get the order
            order = get_object_or_404(SellinvoiceTable, invoice_no=order_id, is_assigned=False)

            # Assign the order
            employee.is_available = False
            employee.has_active_order = True
            employee.save()

            order.delivery_status = 'جاري التوصيل'
            order.is_assigned = True
            order.save()

            # Add to order queue
            OrderQueue.objects.create(
                employee=employee, order=order, is_accepted=False, is_assigned=True, assigned_at=now()
            )

            # Schedule confirmation check
            async_task('app.tasks.check_order_confirmation', order_id=order_id)

            # Update employee queue
            employee_queue.is_assigned = True
            employee_queue.is_available = False
            employee_queue.assigned_time = now()
            employee_queue.save()

        return Response({'message': 'Order assigned successfully'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""Get a list of available employees.""",
tags=["Delivery"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_employees(request):
    """Get a list of available employees."""
    employees = EmployeeQueue.objects.filter(is_available=True, is_assigned=False).select_related('employee')
    data = [{"id": emp.employee.id, "name": emp.employee.name} for emp in employees]
    return Response(data, status=status.HTTP_200_OK)

@extend_schema(
description="""Get a list of unassigned orders.""",
tags=["Delivery"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unassigned_orders(request):
    """Get a list of unassigned orders."""
    orders = SellinvoiceTable.objects.filter(is_assigned=False)
    data = [{"invoice_no": order.invoice_no} for order in orders]
    return Response(data, status=status.HTTP_200_OK)

@extend_schema(
description="""Get a list of unassigned orders with status.""",
tags=["Delivery"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unassigned_orders_with_status(request):
    """Get a list of unassigned orders with specific delivery status."""
    orders = SellinvoiceTable.objects.filter(
        invoice_status='سلمت',
        delivery_status='جاري التوصيل'
    )

    if not orders.exists():
        return Response({"error": "No matching orders found."}, status=status.HTTP_404_NOT_FOUND)

    data = [{"invoice_no": order.invoice_no} for order in orders]
    return Response(data, status=status.HTTP_200_OK)



@extend_schema(
    request=serializers.AddToCartSerializer,
    responses={
        201: CartItemSerializer,
        400: OpenApiResponse(description="Bad Request (e.g. quantity exceeds itemvalue)"),
        404: OpenApiResponse(description="Client not found"),
    },
    description="Adds an item to the cart. If the item already exists, it updates the quantity if within limit."
)
class AddToCartView(APIView):
    def post(self, request):
        client_id = request.data.get("clientid")
        fileid = request.data.get("fileid")
        itemname = request.data.get("itemname")
        buyprice = request.data.get("buyprice")
        quantity = int(request.data.get("quantity", 1))
        image = request.data.get("image", "")
        logo = request.data.get("logo", "")
        pno = request.data.get("pno", "")
        itemvalue = int(request.data.get("itemvalue", 0))

        # Validate client existence
        try:
            client = AllClientsTable.objects.get(clientid=client_id)
        except AllClientsTable.DoesNotExist:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the item already exists in the cart
        cart_item, created = CartItem.objects.get_or_create(
            client=client,
            fileid=fileid,
            defaults={
                "itemname": itemname,
                "buyprice": buyprice,
                "quantity": quantity,
                "image": image,
                "logo": logo,
                "pno": pno,
                "itemvalue": itemvalue,
            }
        )

        if not created:
            if cart_item.quantity + quantity <= cart_item.itemvalue:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                return Response({"error": f"Cannot add more than {cart_item.itemvalue} items."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

