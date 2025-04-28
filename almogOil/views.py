#import datetime
from decimal import Decimal
import hashlib
from .Tasks import assign_orders
import json
from django.contrib.contenttypes.models import ContentType
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django_q.tasks import async_task
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse,Http404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.db.models import F, Q  # Import F for field comparison
from django.utils.timezone import make_aware
from datetime import datetime, time, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3  # Change to A3 size for wider pages
from reportlab.lib.pagesizes import landscape  # Landscape orientation of Tabloid page
import re
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
import math
from django.db import transaction
from io import BytesIO
import pandas as pd
from django.http import JsonResponse
import logging
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, IntegerField
from django.db.models.functions import Cast
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django.http import JsonResponse
import firebase_admin
from firebase_admin import credentials, messaging
from almogOil import serializers,models
from products import serializers as product_serializers
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from app_sell_invoice import serializers as sell_invoice_serializers





def send_push_notification(title, body, token):
    """
    Send push notification to a specific device using Firebase Cloud Messaging.

    :param title: The title of the notification.
    :param body: The body of the notification.
    :param token: The device token of the user you want to send the notification to.
    :return: The response from Firebase.
    """
    try:
        # Create the notification message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,  # Token of the device you want to send the notification to
        )

        # Send the message
        response = messaging.send(message)
        return response
    except Exception as e:
        #print(f"Error sending notification: {e}")
        return None



def notify_user(request):
    """
    Endpoint to send a push notification to a specific user.
    :param request: The HTTP request.
    :return: JsonResponse with the result of the notification sending.
    """
    if request.method == "POST":
        # Extract parameters from the request
        title = request.POST.get('title')
        body = request.POST.get('body')
        token = request.POST.get('token')

        if not title or not body or not token:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Send the push notification
        response = send_push_notification(title, body, token)

        if response:
            return JsonResponse({"success": "Notification sent successfully", "response": response})
        else:
            return JsonResponse({"error": "Failed to send notification"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def LogInView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        return redirect('home')
        # Logic for authentication can be added here if necessary
    else:
        return render(request, 'login.html')

@login_required
def StorageManagement(req):
    Clients= models.AllClientsTable.objects.all()
    sections = models.Sectionstable.objects.all()
    subSections = models.Subsectionstable.objects.all()
    context = {
        'clients': Clients,
        'sections': sections,
        'subSections': subSections
    }
    return render(req,'storage-management.html',context)

@login_required
def StorageReports(req):
    Clients= models.AllClientsTable.objects.all()
    sections = models.Sectionstable.objects.all()
    subSections = models.Subsectionstable.objects.all()
    context = {
        'clients': Clients,
        'sections': sections,
        'subSections': subSections
    }
    return render(req,'storage-reports.html',context)


@login_required
def MoreDetails(req):
    productId = req.GET.get('product_id')
    item = models.Mainitem.objects.filter(fileid=productId)
    context = {
        'item':item
    }
    return render(req,'more-details.html',context)


@login_required
def BuyInvoicesAdd(request):
    sources = models.AllSourcesTable.objects.all().values('clientid','name')
    Currency = models.CurrenciesTable.objects.all()
    context ={
        'sources':sources,
        'currency': Currency
    }
    return render(request,'add-buy-invoice.html',context)

from django.utils.dateparse import parse_date

@login_required
def ImageView(request):
    # Retrieve all images to display in the template
    product_id = request.GET.get("product_id")
    images = models.Imagetable.objects.filter(productid=product_id)

    if request.method == 'POST':
        if 'delete-id' in request.POST:  # Check if it's a delete request
            delete_id = request.POST.get('delete-id')
            image_to_delete = get_object_or_404(models.Imagetable, fileid=delete_id)
            image_to_delete.delete()
            return JsonResponse({'status': 'success', 'message': 'Image deleted successfully.'})

        # Handle image upload
        product_id = request.POST.get('product-id')
        image = request.FILES.get('image')

        if image and product_id:
            # Create a new Imagetable object
            models.Imagetable.objects.create(productid=product_id, image=image, image_obj=image)
            # Redirect to the same view with the product_id in the query string
            return HttpResponseRedirect(f"{reverse('images')}?product_id={product_id}")

    # Render the image table template
    return render(request, 'image-table.html', {'images': images})

@login_required
def ModelView(request):
    sub_types = models.Subtypetable.objects.all()
    models_ = models.Modeltable.objects.select_related('subtype_fk').all()

    if request.method == 'POST':
        action = request.POST.get('action')
        model_id = request.POST.get('id')
        model_name = request.POST.get('model-name')
        sub_type_id = request.POST.get('model-sub-type')

        if action == 'add':
            if model_name and sub_type_id:
                sub_type = get_object_or_404(models.Subtypetable, fileid=sub_type_id)
                models.Modeltable.objects.create(model_name=model_name, subtype_fk=sub_type)
                messages.success(request, "Model added successfully!")
            else:
                messages.error(request, "All fields are required.")

        elif action == 'edit':
            if model_id and model_name:
                model = get_object_or_404(models.Modeltable, fileid=model_id)
                model.model_name = model_name
                model.save()
                messages.success(request, "Model updated successfully!")
            else:
                messages.error(request, "All fields are required.")

        elif action == 'delete':
            if model_id:
                model = get_object_or_404(models.Modeltable, fileid=model_id)
                model.delete()
                messages.success(request, "Model deleted successfully!")
            else:
                messages.error(request, "Model ID is required.")

        return redirect('models')

    return render(request, 'model-table.html', {
        'subType': sub_types,
        'models': models_,
    })

@login_required
def HomeView(request):
    return render(request, 'home.html')

@login_required
def SectionAndSubSection(request):
    sections = models.Sectionstable.objects.all()
    subSections = models.Subsectionstable.objects.all()

    # Handle POST requests for both sections and subsections
    if request.method == "POST":
        action = request.POST.get("action")

        # Handle Section actions
        if "section" in request.POST:
            section_id = request.POST.get("id")
            section_name = request.POST.get("name")


            if action == "add" and section_name:
                models.Sectionstable.objects.create(section=section_name)
            elif action == "edit" and section_id and section_name:
                section = models.Sectionstable.objects.get(autoid=section_id)
                section.section = section_name
                section.save()
            elif action == "delete" and section_id:
                models.Sectionstable.objects.filter(autoid=section_id).delete()

        # Handle Subsection actions
        elif "subsection" in request.POST:
            subsection_id = request.POST.get("id")
            subsection_name = request.POST.get("name")
            section_fk = request.POST.get("key")

            if action == "add" and subsection_name:
                section_instance = models.Sectionstable.objects.get(autoid=section_fk)  # Assuming autoid is the primary key field

                models.Subsectionstable.objects.create(subsection=subsection_name,sectionid=section_instance)
            elif action == "edit" and subsection_id and subsection_name:
                subsection = models.Subsectionstable.objects.get(autoid=subsection_id)
                subsection.subsection = subsection_name
                subsection.save()
            elif action == "delete" and subsection_id:
                models.Subsectionstable.objects.filter(autoid=subsection_id).delete()

        # Redirect to the same page after action
        return redirect('sections-and-subsections')  # Replace with the actual URL name

    context = {
        'sections': sections,
        'subSections': subSections,
    }
    return render(request, 'section-subsection.html', context)


#until here

@login_required
def MainCat(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name')
        main_id = request.POST.get('id')  # Get the ID from the form

        try:
            if action == 'add':
                models.Maintypetable.objects.create(typename=name)
            elif action == 'edit' and main_id:
                # Correctly fetch the object using `objects.get`
                maintypetable = models.Maintypetable.objects.get(fileid=main_id)
                maintypetable.typename = name  # Update the typename field
                maintypetable.save()
            elif action == 'delete' and main_id:
                # Correctly fetch the object and delete it
                maintypetable = models.Maintypetable.objects.get(fileid=main_id)
                maintypetable.delete()
            else:
                # Handle invalid action or missing data
                raise ValueError("Invalid action or missing ID.")

        except models.Maintypetable.DoesNotExist:
            # Handle the case where the object with the given ID does not exist
            messages.error(request, "The specified measurement does not exist.")
        except Exception as e:
            # Handle other unexpected errors
            messages.error(request, f"An error occurred: {e}")

        return redirect('maintype')

    mainType = models.Maintypetable.objects.all()
    context = {
        'mainType': mainType,
    }
    return render(request, 'main-cat.html', context)

@login_required
def SubCat(request):
    main_types = models.Maintypetable.objects.all()
    subtypes = models.Subtypetable.objects.select_related('maintype_fk').all()

    if request.method == 'POST':
        action = request.POST.get('action')
        sub_type_id = request.POST.get('id')
        sub_type_name = request.POST.get('sub_type-name')
        main_type_id = request.POST.get('sub_type-main-type')

        try:
            if action == 'add':
                if sub_type_name and main_type_id:
                    main_type = get_object_or_404(models.Maintypetable, fileid=int(main_type_id))
                    models.Subtypetable.objects.create(subtypename=sub_type_name, maintype_fk=main_type)
                    messages.success(request, "Subtype added successfully!")
                else:
                    messages.error(request, "All fields are required.")

            elif action == 'edit':
                if sub_type_id and sub_type_name:
                    sub_type = get_object_or_404(models.Subtypetable, fileid=int(sub_type_id))
                    sub_type.subtypename = sub_type_name
                    sub_type.save()
                    messages.success(request, "Subtype updated successfully!")
                else:
                    messages.error(request, "All fields are required.")

            elif action == 'delete':
                if sub_type_id:
                    sub_type = get_object_or_404(models.Subtypetable, fileid=int(sub_type_id))
                    sub_type.delete()
                    messages.success(request, "Subtype deleted successfully!")
                else:
                    messages.error(request, "Model ID is required.")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect(request.path)  # Redirects to the same page after processing

    return render(request, 'sub-cat.html', {
        'main_types': main_types,  # Fixed variable name for template consistency
        'subtypes': subtypes,
    })

@login_required
def manage_companies(request):
    if request.method == 'POST':
        action = request.POST.get('action')  # Get action: add, edit, delete
        name = request.POST.get('name')  # Company name from the form
        company_id = request.POST.get('id')  # Hidden input for company ID

        try:
            if action == 'add':
                # Add a new company
                models.Companytable.objects.create(companyname=name)
                messages.success(request, "تمت إضافة الشركة بنجاح.")
            elif action == 'edit' and company_id:
                # Edit an existing company
                company = get_object_or_404(models.Companytable, pk=company_id)
                company.companyname = name
                company.save()
                messages.success(request, "تم تعديل الشركة بنجاح.")
            elif action == 'delete' and company_id:
                # Delete an existing company
                company = get_object_or_404(models.Companytable, pk=company_id)
                company.delete()
                messages.success(request, "تم حذف الشركة بنجاح.")
            else:
                messages.error(request, "حدث خطأ أثناء معالجة الطلب.")
        except Exception as e:
            messages.error(request, f"خطأ: {e}")

        return redirect('manage_companies')  # Redirect to the same page

    # Fetch all company records for display
    companyTable = models.Companytable.objects.all()
    context = {
        'companyTable': companyTable,
    }
    return render(request, 'company-table.html', context)

@login_required
def manage_countries(request):
    if request.method == "POST":
        action = request.POST.get("action")
        country_id = request.POST.get("id")
        country_name = request.POST.get("name")

        if action == "add" and country_name:
            models.Manufaccountrytable.objects.create(countryname=country_name)

        elif action == "edit" and country_id and country_name:
            country = models.Manufaccountrytable.objects.filter(fileid=country_id).first()
            if country:
                country.countryname = country_name
                country.save()

        elif action == "delete" and country_id:
            models.Manufaccountrytable.objects.filter(fileid=country_id).delete()

        return redirect('manage_countries')

    # Fetch all countries for display
    countries = models.Manufaccountrytable.objects.all().order_by('countryname')
    return render(request, 'countries-table.html', {'countries': countries})

def Measurements(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name')
        measurement_id = request.POST.get('id')

        if action == 'add':
            models.MeasurementsTable.objects.create(name=name)
        elif action == 'edit' and measurement_id:
            measurement = models.MeasurementsTable.objects.get(id=measurement_id)
            measurement.name = name
            measurement.save()
        elif action == 'delete' and measurement_id:
            models.MeasurementsTable.objects.get(id=measurement_id).delete()

        return redirect('measurements')

    measurements = models.MeasurementsTable.objects.all()
    return render(request, 'measurements.html', {'measurements': measurements})

COLUMN_TITLES = {
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
    "dateproduct":"date product"
}

@login_required
def ProductsDetails(req):
    company = models.Companytable.objects.values('fileid', 'companyname')
    measurements = models.MeasurementsTable.objects.all()
    engines = models.enginesTable.objects.all()
    mainType = models.Maintypetable.objects.all()
    subType = models.Subtypetable.objects.all()
    countries = models.Manufaccountrytable.objects.all()
    models_ = models.Modeltable.objects.all()
    columns = [field.name for field in models.Mainitem._meta.fields]
    column_visibility = {
        'pno':True,
        'companyproduct':True,
        'replaceno':True,
        'itemno':True,
        'itemname':True,
        'itemvalue':True,
        'buyprice':True,
        'itemplace':True,
    }
    #print(columns)  # Debugging to check the contents of columns

    context = {
        'company': company,
        'columns': columns,
        'column_visibility': column_visibility,
        'measurements': measurements,
        'mainType': mainType,
        'subType':subType,
        'engines':engines,
        'countries':countries,
        'models':models_,
        'column_titles': COLUMN_TITLES,
    }
    return render(req, 'products-details.html', context)
#until here

@csrf_exempt
def OemNumbers(req):
    if req.method == 'GET':
        company_name = req.session.get('oem_company_name')
        company_no = req.session.get('oem_company_no')
        fileid = req.session.get('oem_file_id')
        oemstring = models.Mainitem.objects.get(fileid=fileid, replaceno=company_no).oem_numbers
        oem_numbers = oemstring.split(';') if oemstring else []

        context = {
            'oem': oem_numbers,
            'company_name': company_name,
            "fileid":fileid,
            'company_no': company_no,
        }
        return render(req, 'oem-table.html', context)
    # Handle form submission for Add, Edit, or Delete actions
    elif req.method == 'POST' and req.POST.get('action'):

        action = req.POST.get('action')
        company_name = req.POST.get('company-name')
        company_no = req.POST.get('company-no')
        oem_no = req.POST.get('oem-no')
        file_id = req.POST.get('id')

        if action == 'add' and file_id and oem_no:
            # Add a new record
            record = models.Mainitem.objects.get(fileid=file_id)
            if record.oem_numbers:
                record.oem_numbers += f";{oem_no}"
            else:
                record.oem_numbers = oem_no  # In case it's the first OEM number
            record.save()

        elif action == 'edit' and file_id and oem_no:
            # Edit an existing OEM number (replace the old one with the new one)
            try:
                record = models.Mainitem.objects.get(fileid=file_id)
                # Split the oem_numbers into a list, replace the old oem_no, and rejoin
                oem_list = record.oem_numbers.split(';')
                if oem_no in oem_list:
                    oem_list[oem_list.index(oem_no)] = oem_no  # Modify the OEM number if needed
                record.oem_numbers = ';'.join(oem_list)
                record.save()
            except models.Mainitem.DoesNotExist:
                pass

        elif action == 'delete' and file_id and oem_no:
            # Delete a specific OEM number from the oem_numbers string
            try:
                record = models.Mainitem.objects.get(fileid=file_id)
                # Split the oem_numbers into a list and remove the specified oem_no
                oem_list = record.oem_numbers.split(';')
                if oem_no in oem_list:
                    oem_list.remove(oem_no)
                    record.oem_numbers = ';'.join(oem_list)
                    record.save()
            except models.Mainitem.DoesNotExist:
                pass
        # Redirect to the same page to reflect the changes
        return redirect('/oem/')
    else:
        data = json.loads(req.body)

        req.session['oem_file_id'] = data.get('fileid')
        req.session['oem_company_name'] = data.get('company')
        req.session['oem_company_no'] = data.get('companyno')

        return redirect('/oem/')



logger = logging.getLogger(__name__)

@csrf_exempt
def process_excel_and_import(request):
    if request.method == "POST":
        # Debug: Log the start of the POST request
        logger.debug("Received POST request at /import-tabulator-data/")

        # Handle file upload
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
                        records.append(models.Mainitem(
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
                models.Mainitem.objects.bulk_create(records)
                logger.debug(f"Successfully inserted {len(records)} records into the database.")

                return JsonResponse({"status": "success", "message": "Excel data imported successfully."},status=200)

            except Exception as e:
                logger.error(f"Error processing file: {e}")
                return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

        # Handle imported data (Tabulator data)
        if request.POST.get("data"):
            data = json.loads(request.POST["data"])
            #print(f"tabulator data {data}")
            try:
                logger.debug(f"Received Tabulator data: {data}")
                records = []
                for item in data:
                    try:
                        records.append(models.Mainitem(
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

                models.Mainitem.objects.bulk_create(records)
                logger.debug(f"Successfully inserted {len(records)} records from Tabulator data.")
                return JsonResponse({"status": "success", "message": "Tabulator data imported successfully."})

            except Exception as e:
                logger.error(f"Error processing imported data: {e}")
                return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

        return JsonResponse({"status": "error", "message": "Invalid request or missing file."})

#until here

# Register the Amiri font
from django.conf import settings
font_path = settings.BASE_DIR / 'staticfiles/Amiri-font/Amiri-Regular.ttf'
pdfmetrics.registerFont(TTFont('Amiri', str(font_path)))

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

@csrf_exempt
def generate_pdf(request):
    if request.method == 'POST':
        # Parse the incoming JSON data
        data = json.loads(request.body)
        table_data = data.get('data', [])
        if not table_data:  # Handle empty data case
            return JsonResponse({'error': 'No data provided for PDF generation'}, status=400)

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
            alignment=TA_RIGHT,  # Align text to the right for RTL
            leading=12,  # Line spacing
        )

        english_style = ParagraphStyle(
            name="English",
            fontName="Helvetica",  # Default font for English text
            fontSize=10,  # Font size
            alignment=TA_LEFT,  # Align text to the left for LTR
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
                return JsonResponse({'error': 'No data provided for PDF generation'}, status=400)
            page_table = Table(page_data, colWidths=max_column_widths)
            page_table.setStyle(table_style)

            elements.append(page_table)

            # Add page break if there are more rows
            if i + max_rows_per_page < rows:
                elements.append(PageBreak())

        # Build the PDF document and return as response
        doc.build(elements)

        return response

    else:
        return HttpResponse(status=405)  # Method Not Allowed if not POST

@login_required
def ImportExcel(request):
    return render(request,'import-excel.html')

@login_required
def StoragePlaces(request):
    company = models.Companytable.objects.all()
    mainType = models.Maintypetable.objects.all()
    subType = models.Subtypetable.objects.all()
    context = {
        'company': company,
        'mainType': mainType,
        'subType':subType,
    }
    return render(request,'storage-placing.html',context)

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

@login_required
def ProductsReports(req):
    if req.method == 'POST':
        return JsonResponse({'message': 'Invalid request method.'}, status=405)
    company = models.Companytable.objects.all()
    mainType = models.Maintypetable.objects.all()
    subType = models.Subtypetable.objects.all()
    countries = models.Manufaccountrytable.objects.all()
    models_ = models.Modeltable.objects.all()
    columns = [field.name for field in models.Mainitem._meta.fields]
    column_visibility = {
    'pno':True,
    'companyproduct':True,
    'replaceno':True,
    'itemno':True,
    'itemname':True,
    'itemvalue':True,
    'buyprice':True,
    'itemplace':True,

    }


    #print(columns)  # Debugging to check the contents of columns
    context = {
        'company': company,
        'columns': columns,
        'mainType': mainType,
        'subType':subType,
        'countries':countries,
        'column_titles': COLUMN_TITLES,
        'column_visibility': column_visibility,
        'models':models_
    }
    return render(req, 'products-reports.html', context)

@login_required
def PartialProductsReports(req):
    users = []  # Fetch users or relevant data from your new model if needed
    context = {'users': users}
    return render(req, 'products-reports.html', context)

@login_required
def ProductsMovementReport(req):
    company = models.Companytable.objects.all()
    mainType = models.Maintypetable.objects.all()
    subType = models.Subtypetable.objects.all()
    context = {
        'company': company,
        'mainType':mainType,
        'subType':subType
        }
    return render(req, 'products-movement.html', context)

@login_required
def ProductsBalance(req):
    company = models.Companytable.objects.all()
    mainType = models.Maintypetable.objects.all()
    subType = models.Subtypetable.objects.all()
    context = {
        'company': company,
        'mainType': mainType,
        'subType': subType,
        }
    return render(req, 'products-balance.html', context)

@login_required
def ClientsManagement(request):
    types = models.Clienttypestable.objects.all().values('fileid', 'tname')
    context = {
        'types': list(types),
    }
    return render(request,'clients-management.html',context)

@login_required
def DataInventory(req):
    users = []  # Fetch users or relevant data from your new model if needed
    context = {'users': users}
    return render(req, 'data-inventory.html', context)


@login_required
def LostDamaged(req):
    company = models.Companytable.objects.all()
    mainType = models.Maintypetable.objects.all()
    subType = models.Subtypetable.objects.all()
    context = {
        'company': company,
        'mainType': mainType,
        'subType': subType,
    }
    return render(req, 'lost-and-damaged.html', context)

@login_required
def ClientsReports(req):
    types = models.Clienttypestable.objects.all()
    context = {
       'types':types,
    }
    return render(req, 'clients-reports.html', context)

@login_required
def EditPrices(req):
    users = []  # Fetch users or relevant data from your new model if needed
    context = {'users': users}
    return render(req, 'edit-prices.html', context)

@login_required
def EmployeesAttendanceView(req):
    employees= models.EmployeesTable.objects.all().values("name","employee_id","salary")
    context = {
        "employees": employees,
    }
    return render(req, 'employees-attendance.html', context)

@login_required
def EmployeesDetailsView(req):
    context = {}
    return render(req, 'employees-details.html', context)

@login_required
def account_statement(request):
    client_id = request.GET.get('id')
    if not client_id:
        raise Http404("Missing client ID")

    client = None
    content_type = None

    try:
        client = models.AllClientsTable.objects.get(clientid=client_id)
        content_type = ContentType.objects.get_for_model(models.AllClientsTable)
    except models.AllClientsTable.DoesNotExist:
        try:
            client = models.EmployeesTable.objects.get(employee_id=client_id)
            content_type = ContentType.objects.get_for_model(models.EmployeesTable)
        except models.EmployeesTable.DoesNotExist:
            raise Http404("Client not found")

    records = models.TransactionsHistoryTable.objects.filter(
        content_type=content_type,
        object_id=client_id
    )

    context = {
        'records': records,
        'client': client,
    }
    return render(request, 'account-statement.html', context)


@login_required
def BuyInvoiceItemsView(request):
    company = models.Companytable.objects.all()
    mainType = models.Maintypetable.objects.all()
    subType = models.Subtypetable.objects.all()
    model = models.Modeltable.objects.all()
    country = models.Manufaccountrytable.objects.all()
    data = request.session.get('data')
    # Convert data to JSON string
    json_data = json.dumps(data)
    context = {
        'company': company,
        'mainType':mainType,
        'subType':subType,
        'country': country,
        'model':model,
        "data":json_data
        }
    return render(request,'add-invoice-items.html',context)

@csrf_exempt
def cost_management(request):
    if request.method == "POST":
        try:
            # Parse the JSON data sent by the frontend
            data = json.loads(request.body)
            #print(data)
            invoice = data.get("invoice")

            # Validate data
            if not invoice:
                return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)

            # Store data in session
            request.session['invoice'] = invoice

            # Redirect to the target page
            return HttpResponseRedirect('/cost-management')

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    elif request.method == "GET":
        # Check if the session contains 'invoice' and use it
        invoice_no = request.session.get('invoice')

        if not invoice_no:
            return JsonResponse({"success": False, "message": "No invoice found in session"}, status=400)


        try:
            # Attempt to retrieve the invoice from the database
            invoice = models.Buyinvoicetable.objects.get(invoice_no=invoice_no)

        except models.Buyinvoicetable.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invoice not found in the database"}, status=404)

        org_total = Decimal(invoice.amount)/Decimal(invoice.exchange_rate)
        costs = models.CostTypesTable.objects.all()
        context = {
            "invoice_no": invoice_no,
            "dinar_total": format_number(invoice.amount),
            "rate": round(invoice.exchange_rate,2),
            "currency":invoice.currency,
            "org_total": format_number(org_total),
            "costs": costs,
        }

        return render(request, "cost-management.html", context)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

def format_number(number):
    return f"{number:,.2f}"

@login_required
def payment_installments(request):
    return render(request,'payment.installments.html')



from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
@csrf_exempt
def process_data(request):
    if request.method == "POST":
        try:
            # Parse the JSON data sent by the frontend
            data = json.loads(request.body)
            #print(data)
            auto_id = data.get("id")
            currency = data.get("currency")
            rate = data.get("rate")

            # Validate data
            if not auto_id or not currency or not rate:
                return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)

            # Store data in session
            request.session['auto_id'] = auto_id
            request.session['currency'] = currency
            request.session['rate'] = rate

            # Redirect to the target page
            return HttpResponseRedirect('/manage-buy-invoice/')

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

@csrf_exempt
def process_add_data(request):
    if request.method == "POST":
        try:
            # Parse the JSON data sent by the frontend
            data = json.loads(request.body)
            #print(data)
            source = data.get("source")
            invoice = data.get("invoice")
            date = data.get("date")
            currency = data.get("currency")
            rate = data.get("rate")
            temp = data.get("temp")


            # Validate data
            if not invoice or not currency or not rate or not source or not date:
                return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)

            # Store data in session
            request.session['data'] = data

            # Redirect to the target page
            return HttpResponseRedirect('/add-invoice-items')

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

@login_required
def manage_buy_invoice(request):
    auto_id = request.session.get('auto_id')
    currency = request.session.get('currency')
    rate = request.session.get('rate')

    item = models.BuyInvoiceItemsTable.objects.get(autoid=auto_id)

    context = {
        'auto_id': auto_id,
        'currency': currency,
        'rate': rate,
        "item":item,
    }

    return render(request, 'manage-buy-invoice.html', context)

def buyInvoice_excell(request):
    if request.method == "POST":
        try:
            # Parse the JSON data sent by the frontend
            data = json.loads(request.body)
            #print(data)
            invoice = data.get("invoice")
            org = data.get('org')

            # Validate data
            if not invoice:
                return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)

            # Store data in session
            request.session['invoice'] = invoice
            request.session['org'] = org

            # Redirect to the target page
            return HttpResponseRedirect('/invoice_excell')

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    elif request.method == "GET":
        # Check if the session contains 'invoice' and use it
        invoice_no = request.session.get('invoice')
        org = request.session.get('org')

        if not invoice_no:
            return JsonResponse({"success": False, "message": "No invoice found in session"}, status=400)


        try:
            # Attempt to retrieve the invoice from the database
            invoice = models.Buyinvoicetable.objects.get(invoice_no=invoice_no)

        except models.Buyinvoicetable.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invoice not found in the database"}, status=404)

        context = {
            "invoice_no": invoice_no,
            "org":org,
        }

        return render(request, "buy-invoice-excell.html", context)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

#until here

import logging

logger = logging.getLogger(__name__)
#import json
#import datetime

def excel_date_to_datetime(serial):
    return datetime.datetime(1900, 1, 1) + datetime.timedelta(days=serial - 2)

@csrf_exempt
def process_buyInvoice_excel(request):
    if request.method == "POST":
        # Debug: Log the start of the POST request
        logger.debug("Received POST request at /process_buyInvoice_excel/")

        # Parse the JSON data from the request body
        try:
            body = json.loads(request.body)
            #print(body)
            data = json.loads(body['data'])  # Parse the 'data' stringified JSON
            invoice_no = body.get('invoice_no')


            if not invoice_no:
                return JsonResponse({"status": "error", "message": "Invoice number is required."})

            # Now you have 'data' as a Python object (list of dictionaries)
            logger.debug(f"Received data: {data}")

            try:
                # Attempt to retrieve the invoice from the database
                invoice = models.Buyinvoicetable.objects.get(invoice_no=invoice_no)
            except models.Buyinvoicetable.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Invoice not found in the database."}, status=404)

            # Process the data and insert it into the database
            records = []
            for item in data:
                try:
                    records.append(models.BuyInvoiceItemsTable(
                        invoice_no2=invoice_no,
                        invoice_no=invoice,
                        item_no=item.get("الرقم الاصلي", None),
                        main_cat=item.get("البيان الرئيسي", None),
                        sub_cat=item.get("البيان الفرعي", None),
                        name=item.get("اسم الصنف", "failed"),
                        company=item.get("الشركة", None),
                        quantity=item.get("الكمية", None),
                        place=item.get("مكان التخزين", None),
                        buysource=item.get("المصدر", None),
                        org_unit_price=item.get("سعر التوريد", None),
                        org_total_price=Decimal(item.get("سعر التوريد", 0))*Decimal(item.get("الكمية", 0)),
                        dinar_unit_price=item.get("سعر الشراء", None),
                        dinar_total_price=Decimal(item.get("سعر الشراء", 0))*Decimal(item.get("الكمية", 0)),
                        cost_unit_price=item.get("سعر التكلفة", None),
                        cost_total_price=Decimal(item.get("سعر التكلفة", 0))*Decimal(item.get("الكمية", 0)),
                        current_buy_price=item.get("سعر البيع", None),
                        note=item.get("ملاحظات", None),
                        company_no=item.get("رقم الشركة", None),
                        barcodeno=item.get("رقم الباركود", None),
                        e_name=item.get("الاسم بالانجليزي", None),
                        currency=item.get("العملة", None),
                        current_less_price=item.get("اقل سعر للبيع", None),
                        pno=item.get("الرقم الخاص", None),
                        exchange_rate=item.get("سعر الصرف", None),
                        date=item.get("التاريخ", None),
                    ))

                    # Check if item exists
                    exists = item.get("exists", None)  # Assuming you get the 'exists' value from somewhere in item

                    # If the 'exists' value is 0, add item to the MainItem model
                    if exists == 0:
                        # Create a MainItem record for the item
                        models.Mainitem.objects.create(
                            itemno=item.get("الرقم الاصلي", None),
                            replaceno=item.get("رقم الشركة", None),
                            itemname=item.get("اسم الصنف", "failed"),
                            companyproduct=item.get("الشركة", None),
                            eitemname=item.get("الاسم بالانجليزي", None),
                            orgprice=item.get("سعر التوريد", 0),
                            orderprice=item.get("سعر الشراء", 0),
                            costprice=item.get("سعر التكلفة", 0),
                            itemvalue=item.get("الكمية", 0),
                            itemmain=item.get("البيان الرئيسي", None),
                            itemsubmain=item.get("البيان الفرعي", None),
                            pno=item.get("الرقم الخاص", None),
                            barcodeno=item.get("رقم الباركود", None),
                            currtype=item.get("العملة", None),
                            lessprice=item.get("اقل سعر للبيع", None),
                            currvalue=item.get("سعر الصرف", None),
                            memo=item.get("ملاحظات", None),
                            itemplace=item.get("مكان التخزين", None),
                            # Add other fields you want to set for MainItem
                        )
                except Exception as item_error:
                    logger.error(f"Error processing item {item}: {item_error}")
                    continue

            # Bulk create records in the database
            models.BuyInvoiceItemsTable.objects.bulk_create(records)
            logger.debug(f"Successfully inserted {len(records)} records from Tabulator data.")
            return JsonResponse({"status": "success", "message": "Tabulator data imported successfully."})

        except Exception as e:
            logger.error(f"Error processing imported data: {e}")
            return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request."})

@login_required
def temp_confirm(request):
    invoices = models.Buyinvoicetable.objects.filter(temp_flag=1)
    context={
        "invoices":invoices,
    }
    return render(request, "temp-confirm.html",context)

@csrf_exempt
def process_temp_confirm(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            #print(data)
            invoice_no = data.get('invoice_no')

            if not invoice_no:
                return JsonResponse({'status': 'error', 'message': 'Invoice number is required.'}, status=400)

            try:
                # Fetch invoice items for the given invoice number
                invoice_items = models.BuyInvoiceItemsTable.objects.filter(invoice_no=invoice_no)
            except models.BuyInvoiceItemsTable.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invoice item not found in the BuyInvoiceItemsTable.'}, status=404)

            # Serialize the invoice items (convert them to a list of dictionaries)
            items_data = []
            for item in invoice_items:
                items_data.append({
                    'item_no': item.item_no,
                    'company': item.company,  # Replace with actual field names
                    'company_no': item.company_no,    # Replace with actual field names
                    'name': item.name,
                    'dinar_unit_price':item.dinar_unit_price,
                    'dinar_total_price':item.dinar_total_price,
                    'quantity':item.quantity,
                    'note':item.note,
                    'cost_unit_price':item.cost_unit_price,
                    'org_unit_price':item.org_unit_price,
                })

            # Fetch the invoice details from the Buyinvoicetable
            try:
                invoice = models.Buyinvoicetable.objects.get(autoid=invoice_no)

                # Prepare invoice details for response
                invoice_details = {
                    'original': invoice.original_no,
                    'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else None,
                    'arrive_date': invoice.arrive_date.strftime('%Y-%m-%d')if invoice.arrive_date else None,
                    'source': invoice.source,
                    'invoice_items': items_data,  # Attach serialized invoice items
                }

                return JsonResponse({'status': 'success', 'message': 'Invoice details fetched successfully.', 'data': invoice_details},status=200)

            except models.Buyinvoicetable.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invoice not found in the Buyinvoicetable.'}, status=404)

        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method. Only POST is allowed.'}, status=405)

@login_required
def buyInvoice_edit_prices(request):
    return render(request,"buy-invoice-edit-price.html")

@login_required
def Buyinvoice_management(request):
    #records = models.Buyinvoicetable.objects.all().values()
    #total_amount = models.Buyinvoicetable.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    #json_data = json.dumps(list(records), default=str)
    sources = models.AllSourcesTable.objects.all().values('clientid','name')
    context = {
        "sources":sources,
        #"data":json_data,
        #"total_amount":total_amount,
    }
    return render(request,"buy-invoice-reports.html",context)


@login_required
def buy_invoice_add_items(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        invoice_id = data.get("id")
        request.session['invoice_id'] = invoice_id
        return redirect('/buy_invoice_add_items')

    invoice_id = request.session.get('invoice_id')
    try:
        invoice = models.Buyinvoicetable.objects.get(autoid=invoice_id)
        invoice_date = invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else ''
        arrive_date = invoice.arrive_date.strftime('%Y-%m-%d') if invoice.arrive_date else ''
        ready_date = invoice.ready_date.strftime('%Y-%m-%d') if invoice.ready_date else ''

    except models.Buyinvoicetable.DoesNotExist:
        invoice = None
        invoice_date = None
        arrive_date = None
        ready_date = None


    context = {
        "invoice":invoice,
        "invoice_id":invoice_id,
        "invoice_date":invoice_date,
        "arrive_date":arrive_date,
        "ready_date":ready_date,
    }
    return render(request,'buy-invoice-add-items.html',context)

@login_required
def sell_invoice_search_storage(request):
    company = models.Companytable.objects.all()
    mainType = models.Maintypetable.objects.all()
    subType = models.Subtypetable.objects.all()
    countries = models.Manufaccountrytable.objects.all()
    context = {
        "company":company,
        "mainType":mainType,
        "subType":subType,
        "countries":countries,
    }
    return render(request,'sell_invoice_search_products.html',context)

@login_required
def sell_invoice_add_invoice(request):
    Clients= models.AllClientsTable.objects.all().values()
    context = {
        "clients":Clients,
    }
    return render(request,'sell_invoice_add_invoice.html',context)

@login_required
def sell_invoice_management(request):
    clients =models.AllClientsTable.objects.all().values('clientid','name')
    client_types = models.Clienttypestable.objects.all()
    context = {
        "clients":clients,
        "types":client_types,
    }
    return render(request,'sell_invoice_management.html',context)


def sell_invoice_add_items(request):
    if request.method == "POST":
        try:
            # Parse the JSON data sent by the frontend
            data = json.loads(request.body)
            #print(data)
            invoice = data.get("invoice")


            # Validate data
            if not invoice:
                return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)

            # Store data in session
            request.session['add_items_invoice'] = invoice

            # Redirect to the target page
            return HttpResponseRedirect('/sell_invoice_add_items')

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)
    invoice = request.session.get('add_items_invoice')
    context = {
        "invoice":invoice,
    }
    return render(request,'sell_invoice_add_items.html',context)

def get_sellinvoice_no(request):
    try:
        # Get the last autoid by ordering the table by autoid in descending order
        last_invoice = models.SellinvoiceTable.objects.order_by('-invoice_no').first()
        if last_invoice:
            response_data = {'autoid': last_invoice.invoice_no}
        else:
            # Handle the case where the table is empty
            response_data = {'autoid': 0, 'message': 'No invoices found'}
    except Exception as e:
        # Handle unexpected errors
        response_data = {'error': str(e)}

    return JsonResponse(response_data)

@login_required
def sell_invoice_prepare_report(request):
    client = models.AllClientsTable.objects.all().values("clientid","name")
    context = {
        "clients":client,
    }
    return render(request,'sell_invoice_prepare_report.html',context)

@login_required
def sell_invoice_storage_management(request):
    id = request.GET.get("inv")
    invoice = models.SellinvoiceTable.objects.get(invoice_no=id)
    employees =  models.EmployeesTable.objects.filter(active=True).values('employee_id','name')
    context = {
        "employees": employees,
        "invoice_no": invoice.invoice_no,
        "invoice_client": invoice.client_name,
        "invoice_status": invoice.invoice_status,
        "preparer_name": invoice.preparer_name or "",
        "preparer_note": invoice.preparer_note  or "",
        "quantity": invoice.quantity  or 0,
        "reviewer_name": invoice.reviewer_name  or "",
        "place": invoice.place  or "",
        "biller_name": invoice.biller_name  or "",
        "delivered_date": invoice.delivered_date.strftime("%Y-%m-%d") if invoice.delivered_date else "",
        "delivered_quantity": invoice.delivered_quantity  or 0,
        "deliverer_name": invoice.deliverer_name  or "",
        "office": invoice.office  or "",
        "bill_no": invoice.office_no  or "",
        "sent_by": invoice.sent_by  or "",
        "final_note": invoice.notes  or "",
    }
    return render(request,'sell_invoice_storage_management.html',context)

@login_required
def sell_invoice_profile(request, id):
    invoice = get_object_or_404(models.SellinvoiceTable, invoice_no=id)

    serializer = sell_invoice_serializers.SellInvoiceSerializer(invoice)
    clients = models.AllClientsTable.objects.all().values()

    context = {
        "clients": clients,
        "invoice": serializer.data,
    }
    return render(request, 'sell_invoice_profile.html', context)


class SendMessageView(generics.CreateAPIView):
    queryset = models.ChatMessage.objects.all()
    serializer_class = serializers.ChatMessageSerializer

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

     sender = get_object_or_404(models.AllClientsTable, clientid=sender_id)
     receiver = get_object_or_404(models.AllClientsTable, clientid=receiver_id)

     chat_message = models.ChatMessage.objects.create(sender=sender, receiver=receiver, message=message_text)
     serializer = self.get_serializer(chat_message)

     return Response(serializer.data, status=status.HTTP_201_CREATED)

class GetChatMessagesView(generics.ListAPIView):
    serializer_class = serializers.ChatMessageSerializer

    def get_queryset(self):
     sender_id = self.request.query_params.get('sender')
     receiver_id = self.request.query_params.get('receiver')
     return models.ChatMessage.objects.filter(sender__clientid=sender_id, receiver__clientid=receiver_id) | models.ChatMessage.objects.filter(sender__clientid=receiver_id, receiver__clientid=sender_id)

class MarkMessageAsReadView(generics.UpdateAPIView):
    queryset = models.ChatMessage.objects.all()
    serializer_class = serializers.ChatMessageSerializer

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({"message": "Message marked as read"}, status=status.HTTP_200_OK)


class SupportChatMessageView(APIView):
    def post(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation_id')
        sender_id = request.data.get('sender_id')
        sender_type = request.data.get('sender_type')
        message = request.data.get('message')

        try:
            sender = models.AllClientsTable.objects.get(clientid=sender_id)
            conversation = models.SupportChatConversation.objects.get(conversation_id=conversation_id)
        except models.AllClientsTable.DoesNotExist:
            return Response({'error': 'Sender not found'}, status=status.HTTP_404_NOT_FOUND)
        except models.SupportChatConversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create new message
        new_message = models.SupportChatMessageSys(
            conversation=conversation,
            sender=sender,
            sender_type=sender_type,
            message=message,
        )
        new_message.save()

        # Return the newly created message
        serializer = serializers.SupportChatMessageSysSerializer(new_message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        conversation_id = request.query_params.get('conversation_id')
        try:
            conversation = models.SupportChatConversation.objects.get(conversation_id=conversation_id)
        except models.SupportChatConversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        messages = models.SupportChatMessageSys.objects.filter(conversation=conversation).order_by('timestamp')
        serializer = serializers.SupportChatMessageSysSerializer(messages, many=True)
        return Response(serializer.data)

@api_view(['POST'])
def create_conversation(request):
    client_id = request.data.get('client_id')
    support_agent_id = request.data.get('support_agent_id')

    try:
        client = models.AllClientsTable.objects.get(clientid=client_id)
        support_agent = models.AllClientsTable.objects.get(clientid=support_agent_id)
    except models.AllClientsTable.DoesNotExist:
        return Response({'error': 'Client or Support Agent not found'}, status=status.HTTP_404_NOT_FOUND)

    conversation = models.SupportChatConversation(client=client, support_agent=support_agent)
    conversation.save()
    return Response({'conversation_id': conversation.conversation_id}, status=status.HTTP_201_CREATED)


def support_dashboard(request):
    # Fetch all clients
    clients = models.AllClientsTable.objects.all()

    # Prepare a list of conversations for each client
    clients_with_conversations = []
    for client in clients:
        # Get conversations associated with each client
        conversations = models.SupportChatConversation.objects.filter(client=client)
        conversations_serializer = serializers.SupportChatConversationSerializer1(conversations, many=True)

        # Add conversations to each client
        clients_with_conversations.append({
            'client': client,
            'conversations': conversations_serializer.data
        })

    return render(request, 'support_dashboard.html', {'clients_with_conversations': clients_with_conversations})



def support_dashboard(request):
    # Fetch all feedbacks
    feedbacks = models.Feedback.objects.all()  # Get all feedback records from the database

    # Pass the feedbacks to the template context
    return render(request, 'support_dashboard.html', {'feedbacks': feedbacks})

def fetch_all_feedback(request):
    """Fetch all feedback and group them by client ID."""
    feedbacks = models.Feedback.objects.select_related('sender').all()

    grouped_feedback = {}

    for feedback in feedbacks:
        client_id = feedback.sender.clientid  # Assuming sender is linked to AllClientsTable
        if client_id not in grouped_feedback:
            grouped_feedback[client_id] = {
                "client_name": feedback.sender.name,
                "feedbacks": []
            }

        grouped_feedback[client_id]["feedbacks"].append({
            "id": feedback.id,
            "feedback_text": feedback.feedback_text,
            "employee_response": feedback.employee_response,
            "is_resolved": feedback.is_resolved,
            "response_at": feedback.response_at.strftime("%Y-%m-%d %H:%M") if feedback.response_at else None
        })

    return JsonResponse(grouped_feedback, safe=False)


@csrf_exempt
def fetch_all_feedback(request):
    """Fetch all feedbacks and their messages grouped by client ID."""
    feedbacks = models.Feedback.objects.select_related('sender').prefetch_related('messages').all()

    grouped_feedback = {}

    for feedback in feedbacks:
        client_id = feedback.sender.clientid
        if client_id not in grouped_feedback:
            grouped_feedback[client_id] = {
                "client_name": feedback.sender.name,
                "feedbacks": []
            }

        messages = [
            {
                "id": message.id,
                "sender_type": message.sender_type,
                "message_text": message.message_text,
                "sent_at": message.sent_at.strftime("%Y-%m-%d %H:%M")
            }
            for message in feedback.messages.all()
        ]

        grouped_feedback[client_id]["feedbacks"].append({
            "id": feedback.id,
            "feedback_text": feedback.feedback_text,
            "messages": messages,
            "created_at": feedback.created_at.strftime("%Y-%m-%d %H:%M"),
            "is_resolved": feedback.is_resolved  # Include the is_resolved field
        })

    return JsonResponse(grouped_feedback, safe=False)


@csrf_exempt
def add_message_to_feedback(request, feedback_id):
    """Allow clients and employees to send multiple messages in a feedback thread."""
    try:
        feedback = models.Feedback.objects.get(id=feedback_id)
    except models.Feedback.DoesNotExist:
        return JsonResponse({"error": "Feedback not found."}, status=404)

    data = json.loads(request.body)
    message_text = data.get("message_text")
    sender_type = data.get("sender_type")  # Can be "client" or "employee"

    if not message_text:
        return JsonResponse({"error": "Message text is required."}, status=400)
    if sender_type not in ["client", "employee"]:
        return JsonResponse({"error": "Invalid sender type."}, status=400)

    message = models.FeedbackMessage.objects.create(
        feedback=feedback,
        sender_type=sender_type,
        message_text=message_text,
        sent_at=timezone.now()
    )

    return JsonResponse({
        "id": message.id,
        "message_text": message.message_text,
        "sender_type": message.sender_type,
        "sent_at": message.sent_at.strftime("%Y-%m-%d %H:%M")
    }, status=201)

@csrf_exempt
def close_feedback(request, feedback_id):
    """Close a feedback thread (mark as resolved)."""
    try:
        feedback = models.Feedback.objects.get(id=feedback_id)
    except models.Feedback.DoesNotExist:
        return JsonResponse({"error": "Feedback not found."}, status=404)

    # Check if the session role is "employee"
    if request.session.get("role") == "employee":
        feedback.is_resolved = True  # Mark as resolved
        feedback.resolved_at = timezone.now()
        feedback.save()
        return JsonResponse({"message": "Feedback closed successfully."}, status=200)
    else:
        return JsonResponse({"error": "Only employees can close feedback."}, status=403)


@csrf_exempt
def delete_feedback(request, feedback_id):
    """Delete a feedback thread."""
    try:
        feedback = models.Feedback.objects.get(id=feedback_id)
    except models.Feedback.DoesNotExist:
        return JsonResponse({"error": "Feedback not found."}, status=404)

    # Check if the session role is "employee"
    if request.session.get("role") == "employee":
        feedback.delete()
        return JsonResponse({"message": "Feedback deleted successfully."}, status=200)
    else:
        return JsonResponse({"error": "Only employees can delete feedback."}, status=403)
@csrf_exempt
def feedback_by_user_id(request):
    # Get the clientid from query parameters
    clientid = request.GET.get('clientid')

    if not clientid:
        return JsonResponse({"detail": "Client ID is required."}, status=400)

    # Try to fetch the client
    try:
        client = models.AllClientsTable.objects.get(clientid=clientid)
    except models.AllClientsTable.DoesNotExist:
        return JsonResponse({"detail": "Client not found."}, status=404)

    # Fetch feedback for this client
    feedbacks = models.Feedback.objects.filter(sender=client)

    # If no feedback is found, return an empty list
    if not feedbacks:
        return JsonResponse([])

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

    return JsonResponse(feedback_data, safe=False)

@csrf_exempt
def feedback_details(request, feedback_id):
    # Get the feedback object
    feedback = get_object_or_404(models.Feedback, id=feedback_id)

    # Access the client (sender) from the feedback model
    client = feedback.sender  # This is the related AllClientsTable object

    # If you want to pass any other data, you can add here
    return render(request, 'feedback_details.html', {'feedback': feedback, 'client': client})

@csrf_exempt
def fetch_feedback_messages(request, feedback_id):
    feedback_messages = models.FeedbackMessage.objects.filter(feedback_id=feedback_id).order_by('sent_at')

    messages_data = [
        {
            "id": msg.id,
            "sender_type": msg.sender_type,
            "message_text": msg.message_text,
            "sent_at": msg.sent_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for msg in feedback_messages
    ]

    return JsonResponse({"feedback_id": feedback_id, "messages": messages_data}, safe=False)


@login_required
def addMoreCatView(request,id):
    item = models.Mainitem.objects.get(pno=id)

    mains = item.itemmain.split(';') if item.itemmain else []
    subs = item.itemsubmain.split(';') if item.itemsubmain else []
    models_ = item.itemthird.split(';') if item.itemthird else []
    engines = item.engine_no.split(';') if item.engine_no else []

    main_select = models.Maintypetable.objects.all().values()
    sub_select = models.Subtypetable.objects.all().values()
    model_select = models.Modeltable.objects.all().values()
    engine_select = models.enginesTable.objects.all().values()

    context = {
        'mains':mains,
        'subs':subs,
        'models':models_,
        'engines':engines,

        'main_select':main_select,
        'sub_select':sub_select,
        'model_select':model_select,
        'engine_select':engine_select,
    }
    #return JsonResponse(context)
    return render(request,'add-more-cat.html',context)

@login_required
def notifications_page(request):
    return render(request, 'notifications.html')

@login_required
def return_items_view(request):
    clients = models.AllClientsTable.objects.all().values('clientid','name')
    invoices = models.SellinvoiceTable.objects.all().values('invoice_no','client_id','client_name')
    context = {
        'clients':clients,
        'invoices':invoices,
    }
    return render(request, 'return-permission-add.html',context)

@login_required
def return_items_report_view(request):
    clients = models.AllClientsTable.objects.all().values('clientid','name')
    context = {
        'clients':clients,
    }
    return render(request, 'return-permission-report.html',context)

@login_required
def engines_view(request):
    engines = models.enginesTable.objects.values('fileid', 'engine_name','subtype_str','maintype_str')
    subtypes =   models.Subtypetable.objects.all().values()
    maintypes =   models.Maintypetable.objects.all().values()

    return render(request, 'engines-table.html', {
        'engines': engines,
        'subType': subtypes,
        'mainType': maintypes,
    })

@login_required
def return_items_add_items(request, id, permission):
    try:
        invoice_items = models.SellInvoiceItemsTable.objects.filter(invoice_no=id)
        serializer = sell_invoice_serializers.SellInvoiceItemsSerializer(invoice_items, many=True)
        invoice_items_data = json.dumps(serializer.data) # Store serialized data
    except models.SellInvoiceItemsTable.DoesNotExist:
        invoice_items_data = {}  # Return an empty list if no records are found

    context = {
        "invoice_items": invoice_items_data,
        "invoice":id,
        "permission":permission,
    }
    return render(request, 'return_permission_add_items.html', context)

@login_required
def request_payment_view(request):
    requests = models.PaymentRequestTable.objects.select_related('client').all()  # Fetch requests with clients
    updated_data = []  # List to store modified request objects

    for req in requests:
        # Calculate balance from TransactionsHistoryTable
        balance_data = models.TransactionsHistoryTable.objects.filter(object_id=req.client_id).aggregate(
            total_debt=Sum('debt'),
            total_credit=Sum('credit')
        )

        total_debt = balance_data.get('total_debt') or 0
        total_credit = balance_data.get('total_credit') or 0
        balance = round(total_credit - total_debt, 2)

        # Convert object to dictionary
        updated_data.append({
            'autoid': req.autoid,
            'client_id': req.client.clientid,
            'client_name': req.client.name,
            'balance': balance,
            'requested_amount': float(req.requested_amount),  # Convert Decimal to float
            'accepted_amount': float(req.accepted_amount),    # Convert Decimal to float
            'employee': req.employee,
            'issue_date': req.issue_date.strftime('%Y-%m-%d') if req.issue_date else None,
            'accept_date': req.accept_date.strftime('%Y-%m-%d') if req.accept_date else None,
        })
    # Pass updated_data as part of context
    context = {
        'requests': updated_data
    }

    return render(request, 'request-payment.html', context)

@login_required
def main_item_add_json_description(request):
    products = models.Mainitem.objects.all().values('pno','itemname','companyproduct').order_by('pno')
    context = {
        'products': products,
    }
    return render(request, 'add-json-description-mainitem.html',context)


@csrf_exempt  # Remove this if using DRF
def assign_order_manual(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        order_id = data.get('order_id')

        with transaction.atomic():
            # Get the selected employee
            employee_queue = get_object_or_404(models.EmployeeQueue, employee_id=employee_id, is_available=True, is_assigned=False)
            employee = employee_queue.employee

            # Get the selected order
            order = get_object_or_404(models.SellinvoiceTable, invoice_no=order_id, is_assigned=False)

            # Assign the order to the employee
            employee.is_available = False
            employee.has_active_order = True
            employee.save()

            order.delivery_status = 'جاري التوصيل'
            order.is_assigned = True
            order.save()

            # Add to the order queue
            models.OrderQueue.objects.create(
                employee=employee, order=order, is_accepted=False, is_assigned=True, assigned_at=datetime.now()
            )

            # Update the employee queue
            employee_queue.is_assigned = True
            employee_queue.is_available = False
            employee_queue.assigned_time = datetime.now()
            employee_queue.save()

        return JsonResponse({'message': 'Order assigned successfully'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_available_employees(request):
    employees = models.EmployeeQueue.objects.filter(is_available=True, is_assigned=False).select_related('employee')
    data = [{"id": emp.employee.employee_id, "name": emp.employee.name} for emp in employees]
    return JsonResponse(data, safe=False)




def get_unassigned_orders(request):
    orders = models.SellinvoiceTable.objects.filter(
    Q(is_assigned=False) & ~Q(invoice_status="سلمت")
)
    data = [{"invoice_no": order.invoice_no} for order in orders]
    return JsonResponse(data, safe=False)

from django.shortcuts import render

@login_required
def assign_order_page(request):
    return render(request, 'assign_order.html')

@login_required
def invoice_notifications(request):
    return render(request, 'WStest.html')

@login_required
def sources_management_View(request):
    context = {}
    return render(request,'sources-management.html',context)


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
            client = models.AllClientsTable.objects.get(clientid=client_id)
        except models.AllClientsTable.DoesNotExist:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the item already exists in the cart
        cart_item, created = models.CartItem.objects.get_or_create(
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

        return Response(serializers.CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

@login_required
def return_permission_profile(request, id):
    return_permission = get_object_or_404(models.return_permission, autoid=id)
    context = {
        "return": return_permission,
        "date": return_permission.date.strftime("%Y-%m-%d"),
        "client_name": return_permission.client.name,
    }
    return render(request, 'return_permission_profile.html', context)

@login_required
def users_management(request):
    permissions_list = [
        "template_productdetails",
        "template_local_item_reports",
        "template_external_item_reports",
        "template_price_modifications",
        "template_item_movement_reports",
        "template_item_revaluation",
        "template_inventory",
        "template_damage_loss",
        "template_storage_locations",
        "template_english_labeling",
        "template_item_reservation",
        "template_revaluation",
        "template_missing_items",
        "template_issue_permits",
        "template_items_with_notes",
        "template_add_item_specifications",
    ]

    permissions = {}
    for perm in permissions_list:
        permissions[perm] = request.user.has_perm(f"almogOil.{perm}")

    context = {
        "Permissions": permissions
    }
    return render(request, "users-management.html", context)

@login_required
def maintype_logo_view(request, id):
    # Retrieve the specific Maintypetable entry
    maintype = get_object_or_404(models.Maintypetable, fileid=id)

    # Ensure the logo exists before trying to access .url
    image_url = maintype.logo_obj.url if maintype.logo_obj else None

    context = {
        "logo": image_url,
        "id":id,
        "maintype": maintype.typename,
    }
    return render(request, "maintype_logo_upload.html", context)

@login_required
def company_logo_view(request, id):
    # Retrieve the specific Maintypetable entry
    company = get_object_or_404(models.Companytable, fileid=id)

    # Ensure the logo exists before trying to access .url
    image_url = company.logo_obj.url if company.logo_obj else None

    context = {
        "logo": image_url,
        "id":id,
        "company": company.companyname,
    }
    return render(request, "company_logo_upload.html", context)

@login_required
def assign_orders_page(request, invoice_id):
    # You can pass any additional context here if needed, e.g., the invoice_id
    return render(request, 'assign_orders.html', {'invoice_id': invoice_id})

@login_required
def employees_report_view(request):
    employees= models.EmployeesTable.objects.all().values("name","employee_id")
    context = {
        "employees": employees,
    }
    return render(request,'employees-report.html',context)

@login_required
def employees_salary_view(request):
    employees= models.EmployeesTable.objects.all().values("name","employee_id")
    context = {
        "employees": employees,
    }
    return render(request,'employees-salary.html',context)

@login_required
def employees_salary_edit_view(request):
    employees= models.EmployeesTable.objects.all().values("name","employee_id")
    context = {
        "employees": employees,
    }
    return render(request,'employees-salary-edit.html',context)

@login_required
def employees_cash_reports_view(request):
    employees= models.EmployeesTable.objects.all().values("name","employee_id")
    context = {
        "employees": employees,
    }
    return render(request,'employees-cash-reports.html',context)

@csrf_exempt
def assign_order_to_employee(request, invoice_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')

        with transaction.atomic():
            # Get the selected employee
            employee_queue = get_object_or_404(models.EmployeeQueue, employee_id=employee_id, is_available=True, is_assigned=False)
            employee = employee_queue.employee

            # Get the selected order using the invoice_id from the URL
            order = get_object_or_404(models.SellinvoiceTable, invoice_no=invoice_id, is_assigned=False)

            # Assign the order to the employee
            employee.is_available = False
            employee.has_active_order = True
            employee.save()

            order.delivery_status = 'جاري التوصيل'
            order.is_assigned = True
            order.save()

            # Add to the order queue
            models.OrderQueue.objects.create(
                employee=employee, order=order, is_accepted=False, is_assigned=True, assigned_at=datetime.now()
            )

            # Update the employee queue
            employee_queue.is_assigned = True
            employee_queue.is_available = False
            employee_queue.assigned_time = datetime.now()
            employee_queue.save()

        return JsonResponse({'message': 'Order assigned successfully'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

        # login for hozma logic

# for hozma
def hozmalogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # You can add authentication logic here using Django's auth system
        # from django.contrib.auth import authenticate, login
        # user = authenticate(request, username=username, password=password)
        # if user is not None:
        #     login(request, user)
        return redirect('item-for-inqury-page')
    else:
        return render(request, 'CarPartsTemplates/hozmalogin.html')