#import datetime
from decimal import Decimal
import hashlib
from .Tasks import assign_orders
import json
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
from .serializers import ChatMessageSerializer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django.http import JsonResponse
import firebase_admin
from firebase_admin import credentials, messaging
from almogOil import serializers,models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password





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

def get_subsections(request):
    section_id = request.GET.get('section_id')  # Get selected section ID from request
    subsections = models.Subsectionstable.objects.filter(sectionid_id=section_id).values('autoid', 'subsection')
    return JsonResponse(list(subsections), safe=False)  # Return JSON response

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
@csrf_exempt
def create_buy_invoice(request):
    try:
        # Parse JSON data from the request
        data = json.loads(request.body.decode("utf-8"))
        #print(data)

        # Extract data from the request
        invoice_autoid = data.get("invoice_autoid")
        org_invoice_id = data.get("org_invoice_id")
        source_id = data.get("source")  # Assuming source is a foreign key
        invoice_date = parse_date(data.get("invoice_date")) if data.get("invoice_date") else None
        arrive_date = parse_date(data.get("arrive_date")) if data.get("arrive_date") else None
        order_no = data.get("order_no")
        currency = data.get("currency")
        currency_rate = data.get("currency_rate")
        ready_date = parse_date(data.get("ready_date")) if data.get("ready_date") else None
        reminder = data.get("reminder")
        temp_flag = data.get("temp_flag", False)
        multi_source_flag = data.get("multi_source_flag", False)
        source = models.AllSourcesTable.objects.get(clientid=source_id)
        # Create a new record in the Buyinvoicetable model
        last_id_response = json.loads(get_buyinvoice_no(request).content)  # Get response data
        last_id_no = last_id_response.get("autoid")
        next_id_no = int(last_id_no) + 1

        invoice = models.Buyinvoicetable.objects.create(
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

        # Return a success response
        return JsonResponse({"success": True, "message": "Invoice created successfully.", "id": invoice.autoid}, status=201)

    except Exception as e:
        # Handle errors and return a failure response
        return JsonResponse({"success": False, "error": str(e)}, status=400)

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

def filter_clients(request):
    try:
        # Get the 'pno' parameter from the request
        pno = request.GET.get('pno')

        if not pno:
            return JsonResponse({'error': 'Missing pno parameter'}, status=400)

        # Filter Clients based on 'pno'
        clients = models.Clientstable.objects.filter(pno=pno).values(
            'fileid', 'itemno', 'maintype','itemname','currentbalance','date','clientname','billno','description', 'clientbalance','pno'
        )



        # Return the filtered clients data as JSON
        return JsonResponse(list(clients), safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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


@csrf_exempt
def delete_record(request):
    if request.method == "POST":
        try:
            # Parse the 'fileid' (primary key or identifier) from the request body
            data = json.loads(request.body)
            fileid = data.get('fileid')  # Get the primary key of the item to delete

            # Check if the fileid is provided
            if not fileid:
                return JsonResponse({"success": False, "message": "No 'fileid' provided."}, status=400)

            # Try to get the object from the database
            record = models.Mainitem.objects.get(fileid=fileid)

            # Delete the record
            record.delete()

            return JsonResponse({"success": True, "message": "Record deleted successfully."})

        except models.Mainitem.DoesNotExist:
            return JsonResponse({"success": False, "message": "Record not found."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

from django.core.cache import cache





@csrf_exempt
def filter_items(request):
    if request.method == "POST":
        try:
            # Get the filters from the request body
            filters = json.loads(request.body.decode('utf-8'))  # Decoding bytes and loading JSON
            cache_key = f"filter_{hashlib.md5(str(filters).encode()).hexdigest()}"
            cached_data = cache.get(cache_key)

            if cached_data:
                cached_data["cached_flag"] = True
                return JsonResponse(cached_data, safe=False)

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
               filters_q &= Q(engine_no__icontains=filters['engine_no'])  # New filter
            if filters.get('itemthird'):
               filters_q &= Q(itemthird__icontains=filters['itemthird'])  # Already exists in 'model'
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

            # Apply the checkbox filters using Q objects
            if filters.get('itemvalue') == "0":
                filters_q &= Q(itemvalue=0)
            if filters.get('itemvalue') == ">0":
                filters_q &= Q(itemvalue__gt=0)
            if filters.get('resvalue') == ">0":
                filters_q &= Q(resvalue__gt=0)
            if filters.get('itemvalue_itemtemp') == "lte":
                filters_q &= Q(itemvalue__lte=F('itemtemp'))  # Compare fields

            # Apply date range filter on `orderlastdate`
            fromdate = filters.get('fromdate', '').strip()
            todate = filters.get('todate', '').strip()

            if fromdate and todate:
                try:
                    # Parse dates
                    from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                    to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)

                    # Apply date range filter
                    filters_q &= Q(orderlastdate__range=[from_date_obj, to_date_obj])

                except ValueError:
                    return JsonResponse({'error': 'Invalid date format'}, status=400)

            # Now filter the queryset using the combined Q object
            queryset = models.Mainitem.objects.filter(filters_q).values(
    'pno', 'fileid', 'itemplace', 'itemmain', 'itemname',
    'companyproduct', 'itemno', 'pno', 'replaceno',
    'itemvalue', 'buyprice', 'itemperbox', 'resvalue',
    'oem_numbers', 'engine_no', 'short_name', 'itemthird',
    'json_description', 'itemsize','memo','itemsubmain'  # Add json_description and itemsubmain here
).order_by('itemname')

            # Serialize the filtered data
            items_data = list(queryset)  # Customize the fields to return as needed

            # Initialize totals
            total_itemvalue = 0
            total_itemvalueb = 0
            total_resvalue = 0
            total_cost = 0
            total_order = 0
            total_buy = 0

            # Single loop to calculate all totals
            for item in items_data:
                # Convert values to numbers to avoid treating them as strings
                itemvalue = float(item.get('itemvalue', 0) or 0)
                itemvalueb = float(item.get('itemvalueb', 0) or 0)
                resvalue = float(item.get('resvalue', 0) or 0)
                costprice = float(item.get('costprice', 0) or 0)
                orderprice = float(item.get('orderprice', 0) or 0)
                buyprice = float(item.get('buyprice', 0) or 0)

                # Perform calculations
                total_itemvalue += itemvalue
                total_itemvalueb += itemvalueb
                total_resvalue += resvalue
                total_cost += itemvalue * costprice
                total_order += itemvalue * orderprice
                total_buy += itemvalue * buyprice

            fullTable = filters.get('fullTable')
            if fullTable:
                # Prepare the response
                response = {
                    "data": list(items_data),  # Convert the current page items to a list
                    "fullTable":True,
                    "last_page": 1,  # Total number of pages
                    "total_rows": queryset.count(),  # Total number of rows
                    "page_no": 1,
                    "total_itemvalue":total_itemvalue,
                    "total_itemvalueb":total_itemvalueb,
                    "total_resvalue":total_resvalue,
                    "total_cost":total_cost,
                    "total_order":total_order,
                    "total_buy":total_buy,
                }
                return JsonResponse(response)
            # Pagination parameters from the request
            page_number = int(filters.get('page') or 1)
            page_size = int(filters.get('size') or 20)

            # Create paginator
            paginator = Paginator(items_data, page_size)
            page_obj = paginator.get_page(page_number)

            # Prepare the response
            response = {
                "data": list(page_obj),  # Convert the current page items to a list
                "last_page": paginator.num_pages,  # Total number of pages
                "total_rows": paginator.count,  # Total number of rows
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

            # Cache the response for future use
            cache.set(cache_key, response, timeout=300)  # Cache for 5 minutes

            # Return the filtered data as JSON
            return JsonResponse(response, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def filter_clients_input(request):
    if request.method == "POST":
        try:
            # Get the filters from the request body
            filters = json.loads(request.body.decode('utf-8'))  # Decoding bytes and loading JSON

            # Build the query based on the filters
            queryset = models.Clientstable.objects.all()

            # Check if any filters are applied
            filters_applied = False

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

            fromdate = filters.get('fromdate', '').strip()
            todate = filters.get('todate', '').strip()

            if fromdate and todate:
                try:
                    # Parse dates
                    from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                    to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)

                    # Apply date range filter
                    queryset = queryset.filter(date__range=[from_date_obj, to_date_obj])
                    filters_applied = True
                except ValueError:
                    return JsonResponse({'error': 'Invalid date format'}, status=400)

            # If no filters are applied, return an empty list
            if not filters_applied:
                return JsonResponse([], safe=False)

            # Serialize the filtered data
            items_data = list(queryset.values())  # You may want to customize what data is returned here

            # Return the filtered data as JSON
            return JsonResponse(items_data, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)




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


@api_view(['GET'])
def get_item_data(request, fileid):
    try:
        # Retrieve the record from the database
        item = models.Mainitem.objects.get(fileid=fileid)

        # Serialize the item data
        serializer = serializers.MainitemSerializer(item)

        # Return the serialized data
        return Response(serializer.data)

    except models.Mainitem.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)

@csrf_exempt
def edit_main_item(request):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            fileid = data.get('fileid')
            item = models.Mainitem.objects.get(fileid=fileid)

            # Function to safely update a field
            def safe_update(field_name, new_value):
                if new_value not in [None, "",0,"0"]:
                    setattr(item, field_name, new_value)

            # Update the model fields with the new data if not empty
            safe_update('itemno', data.get('originalno'))
            safe_update('itemmain', data.get('itemmain'))
            safe_update('itemsubmain', data.get('itemsub'))
            safe_update('itemname', data.get('pnamearabic'))
            safe_update('short_name', data.get('shortname'))
            safe_update('eitemname', data.get('pnameenglish'))
            safe_update('companyproduct', data.get('company'))
            safe_update('replaceno', data.get('companyno'))
            safe_update('engine_no', data.get('engine'))
            safe_update('barcodeno', data.get('barcode'))
            safe_update('memo', data.get('description'))
            safe_update('itemsize', data.get('country'))
            safe_update('itemperbox', data.get('pieces4box'))
            safe_update('itemthird', data.get('model'))
            safe_update('itemvalue', data.get('storage'))
            safe_update('itemtemp', data.get('backup'))
            safe_update('itemvalueb', data.get('temp'))
            safe_update('resvalue', data.get('reserved'))
            safe_update('itemplace', data.get('location'))
            safe_update('orgprice', data.get('originprice'))
            safe_update('orderprice', data.get('buyprice'))
            safe_update('costprice', data.get('expensesprice'))
            safe_update('buyprice', data.get('sellprice'))
            safe_update('lessprice', data.get('lessprice'))
            # Continue updating other fields...

            item.save()  # Save the updated record

            return JsonResponse({'success': True})
        except models.Mainitem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

#until here

@csrf_exempt
def create_main_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        last_pno_response = json.loads(get_mainItem_last_pno(request).content)  # Get response data
        last_pno_no = last_pno_response.get("pno")
        next_pno_no = int(last_pno_no) + 1

        # Create a new MainItem instance
        new_item = models.Mainitem(
                itemno=data.get('originalno') or None,
                itemmain=data.get('itemmain') or None,
                itemsubmain=data.get('itemsub') or None,
                itemname=data.get('pnamearabic'),
                eitemname=data.get('pnameenglish') or None,
                short_name=data.get('shortname') or None,
                companyproduct=data.get('company') or None,
                replaceno=data.get('companyno') or None,
                engine_no=data.get('engine') or None,
                pno=next_pno_no,
                barcodeno=data.get('barcode') or None,
                memo=data.get('description') or None,
                itemplace=data.get('location') or None,
                itemsize=data.get('country') or None,
                itemperbox=int(data.get('pieces4box', 0) or 0),
                itemthird=data.get('model') or None,
                itemvalue=int(data.get('storage', 0) or 0),
                itemtemp=int(data.get('backup', 0) or 0),
                itemvalueb=int(data.get('temp', 0) or 0),
                resvalue=int(data.get('reserved', 0) or 0),
                orgprice=float(data.get('originprice', 0) or 0),
                orderprice=float(data.get('buyprice', 0) or 0),
                costprice=float(data.get('expensesprice', 0) or 0),
                buyprice=float(data.get('sellprice', 0) or 0),
                lessprice=float(data.get('lessprice', 0) or 0),
            )
        new_item.save()

        return JsonResponse({'status': 'success', 'message': 'Record created successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'},status=405)

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

@csrf_exempt  # Only if necessary for your use case
def UpdateUserView(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request
            data = json.loads(request.body)
            user_id = data.get('id')
            column_index = data.get('column')  # Column index of the field being updated
            new_value = data.get('value')  # New value to update

            # Fetch the user instance from your new model
            # user = YourCustomUserModel.objects.get(id=user_id)

            # Update the corresponding field based on the column index
            # if column_index == 0:  # Assuming index 0 is for 'name'
            #     user.name = new_value
            # elif column_index == 1:  # Assuming index 1 is for 'email'
            #     user.email = new_value
            # elif column_index == 2:  # Assuming index 2 is for 'age'
            #     user.age = new_value

            # user.save()  # Save the updated user instance
            return JsonResponse({'message': 'User updated successfully!'}, status=200)

        except Exception as e:
            return JsonResponse({'message': f'Error: {e}'}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)

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





def get_clients(request):
    try:
        # Query the database for all Mainitem entries
        items = models.Clientstable.objects.all().values(
            'fileid', 'itemno', 'maintype','itemname','currentbalance','date','clientname','billno','description', 'clientbalance','pno'
        )# List the fields you need
        data = list(items)  # Convert QuerySet to a list
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)          # Return error details in JSON


def get_data(request):
    try:
        # Fetch all records
        #print(request.body)
        # items = models.Mainitem.objects.all().values(
        #     'fileid', 'itemno', 'itemmain', 'itemsubmain', 'itemname',
        #     'itemthird', 'itemsize', 'companyproduct', 'itemvalue',
        #     'itemtemp', 'itemplace', 'buyprice', 'memo', 'replaceno',
        #     'barcodeno', 'eitemname', 'currtype', 'lessprice', 'pno',
        #     'currvalue', 'itemvalueb', 'costprice', 'resvalue', 'orderprice',
        #     'orderlastdate', 'ordersource', 'orderbillno',
        #     'buylastdate', 'buysource', 'buybillno', 'orgprice','itemperbox','oem_numbers','short_name'
        # ).order_by('itemname')
        items = models.Mainitem.objects.all().values().order_by('itemname')

        total_itemvalue = models.Mainitem.objects.aggregate(total=Sum('itemvalue'))['total']
        total_itemvalueb = models.Mainitem.objects.aggregate(total=Sum('itemvalueb'))['total']
        total_resvalue = models.Mainitem.objects.aggregate(total=Sum('resvalue'))['total']
        total_cost = models.Mainitem.objects.aggregate(total=Sum(F('itemvalue') * F('costprice')))['total']
        total_order = models.Mainitem.objects.aggregate(total=Sum(F('itemvalue') * F('orderprice')))['total']
        total_buy = models.Mainitem.objects.aggregate(total=Sum(F('itemvalue') * F('buyprice')))['total']

        fullTable = request.GET.get('fullTable', None)
        if fullTable:
            # Prepare the response
            response = {
                "data": list(items),  # Convert the current page items to a list
                "fullTable":True,
                "total_itemvalue":total_itemvalue,
                "total_itemvalueb":total_itemvalueb,
                "total_resvalue":total_resvalue,
                "total_cost":total_cost,
                "total_order":total_order,
                "total_buy":total_buy,
            }
            return JsonResponse(response)

        # Pagination parameters from the request
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('size', 20))

        # Create paginator
        paginator = Paginator(items, page_size)
        page_obj = paginator.get_page(page_number)

        # Prepare the response
        response = {
            "data": list(page_obj),  # Convert the current page items to a list
            "last_page": paginator.num_pages,  # Total number of pages
            "total_rows": paginator.count,  # Total number of rows
            "page_size":page_size,
            "page_no":page_number,
            "total_itemvalue":total_itemvalue,
            "total_itemvalueb":total_itemvalueb,
            "total_resvalue":total_resvalue,
            "total_cost":total_cost,
            "total_order":total_order,
            "total_buy":total_buy,
        }
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt  # Disable CSRF validation for this view (use with caution in production)
def update_itemvalue(request):
    if request.method == 'POST':
        try:
            # Get the data from the POST request
            data = json.loads(request.body)
            fileid = data.get('fileid')
            new_itemvalue = data.get('newItemValue')
            old_itemvalue = 0

            # Find the item using the fileid
            item = models.Mainitem.objects.get(fileid=fileid)
            old_itemvalue = item.itemvalue
            # Update the item value
            item.itemvalue = new_itemvalue
            item.save()

            movement_Record = models.Clientstable.objects.create(
                itemno=item.itemno,
                itemname=item.itemname,
                maintype=item.itemmain,
                currentbalance=item.itemvalue,
                date=timezone.now(),
                clientname="اعادة ترصيد",
                #billno="",
                description="اعادة ترصيد للصنف",
                clientbalance=int(new_itemvalue-old_itemvalue) or 0,
                pno_instance=item,
                pno=item.pno
            )

            # Return a successful response
            return JsonResponse({'success': True, 'message': 'Item value updated successfully.'})
        except models.Mainitem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found.'},status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'},status=405)

#until here

@csrf_exempt  # Disable CSRF validation for this view (use with caution in production)
def update_storage(request):
    if request.method == 'POST':
        try:
            # Get the data from the POST request
            data = json.loads(request.body)
            fileid = data.get('fileid')
            storage = data.get('storage')
            #print(fileid)
            #print(storage)

            # Find the item using the fileid
            item = models.Mainitem.objects.get(fileid=fileid)

            # Update the item value
            item.itemplace = storage
            item.save()

            # Return a successful response
            return JsonResponse({'success': True, 'message': 'storage updated successfully.'})
        except models.Mainitem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

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

@csrf_exempt  # Use this only if CSRF protection is not needed (e.g., API endpoints)
def delete_lost_damaged(request):
    if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            fileid = data.get("fileid")

            # Check if fileid is provided
            if not fileid:
                return JsonResponse({'success': False, 'message': 'fileid is required.'}, status=400)

            # Attempt to delete the record
            try:
                record = LostAndDamagedTable.objects.get(fileid=fileid)
                record.delete()
                return JsonResponse({'success': True, 'message': 'Record deleted successfully.'})
            except LostAndDamagedTable.DoesNotExist:
                return JsonResponse({'success': False, 'message': f'Record with fileid {fileid} does not exist.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

@csrf_exempt
def filter_lost_damaged(request):
    if request.method == "POST":
        try:
            # Get the filters from the request body
            filters = json.loads(request.body.decode('utf-8'))  # Decoding bytes and loading JSON

            # Build the query based on the filters
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
                    return JsonResponse({'error': 'Invalid date format'}, status=400)



            # Serialize the filtered data
            items_data = list(queryset.values())  # You may want to customize what data is returned here

            # Return the filtered data as JSON
            return JsonResponse(items_data, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def fetch_lost_damaged_data(request):
    if request.method == "GET":
        # Fetch all data from the model
        data = list(
            LostAndDamagedTable.objects.all().values(
                "fileid",
                "date",
                "itemno",
                "companyno",
                "itemname",
                "user",
                "quantity",
                "company",
                "costprice",
                "pno",
                "pno_value",
                "status",
            )
        )
        return JsonResponse(data, safe=False)

import json
import logging
from django.http import JsonResponse
from .models import LostAndDamagedTable

# Set up logging
logger = logging.getLogger(__name__)
@csrf_exempt
def add_lost_damaged(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            # #print incoming data for debugging
            #print("Received data:", data)

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
                #print(error_message)
                return JsonResponse({'success': False, 'message': error_message}, status=400)

            # Attempt to fetch the Mainitem instance for the provided pno_id
            try:
                pno_instance = models.Mainitem.objects.get(pno=pno_id)
                pno_instance.itemvalue -= int(data.get('quantity',0)) or 0
                pno_instance.save()
            except models.Mainitem.DoesNotExist:
                error_message = f'Mainitem with pno id {pno_id} does not exist.'
                logger.error(error_message)
                #print(error_message)
                return JsonResponse({'success': False, 'message': error_message}, status=404)

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

            movement_Record = models.Clientstable.objects.create(
                itemno=itemno,
                itemname=itemname,
                maintype=itemmain,
                currentbalance=pno_instance.itemvalue,
                date=date,
                clientname=status,
                #billno="",
                description="فقد او تلف للصنف",
                clientbalance=int(data.get('quantity',0)) or 0,
                pno_instance=pno_instance,
                pno=pno_instance.pno
            )

            success_message = 'Record added successfully.'
            logger.info(success_message)
            #print(success_message)

            return JsonResponse({'success': True, 'message': success_message,"new_balance":pno_instance.itemvalue})

        except json.JSONDecodeError as e:
            error_message = f'Invalid JSON format: {e}'
            logger.error(error_message)
            #print(error_message)
            return JsonResponse({'success': False, 'message': 'Invalid JSON format.'}, status=400)

        except Exception as e:
            error_message = f'Unexpected error: {e}'
            logger.error(error_message)
            #print(error_message)
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred.'}, status=500)

    else:
        error_message = 'Invalid request method. Only POST is allowed.'
        logger.warning(error_message)
        #print(error_message)
        return JsonResponse({'success': False, 'message': error_message}, status=405)

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

def ClientsReports(req):
    types = models.Clienttypestable.objects.all()
    context = {
       'types':types,
    }
    return render(req, 'clients-reports.html', context)

def EditPrices(req):
    users = []  # Fetch users or relevant data from your new model if needed
    context = {'users': users}
    return render(req, 'edit-prices.html', context)

@csrf_exempt  # Exempt CSRF for AJAX request (only if necessary)
def AddUserView(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        age = request.POST.get('age')

        # Ensure details are valid and email is unique
        if name and email and age:
            # Replace with your new model logic
            # if not YourCustomUserModel.objects.filter(email=email).exists():
            #     user = YourCustomUserModel(name=name, email=email, age=age)
            #     user.save()
            return JsonResponse({'message': 'User added successfully!'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid data provided.'}, status=400)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)
def get_all_clients(request):
    try:
        # Query the database for all MainItem entries
        items = models.AllClientsTable.objects.all().values(
            'clientid', 'name', 'address', 'email', 'website',
            'phone', 'mobile', 'last_transaction', 'type',
            'category', 'loan_period', 'loan_limit', 'loan_day',
            'subtype', 'client_stop', 'curr_flag', 'permissions',
            'other', 'accountcurr','last_transaction_amount'
        )

        # Prepare a list to include balance for each client
        data = []

        for item in items:
            clientid = item['clientid']

            # Calculate balance from TransactionsHistoryTable
            balance_data = models.TransactionsHistoryTable.objects.filter(client_id_id=clientid).aggregate(
                total_debt=Sum('debt'),
                total_credit=Sum('credit')
            )

            total_debt = balance_data.get('total_debt') or 0
            total_credit = balance_data.get('total_credit') or 0
            balance = round(total_credit - total_debt, 2)  # Ensure two decimal digits

            # Fetch total credit for specific client_id and where details = "دفعة على حساب"
            specific_credit_data = models.TransactionsHistoryTable.objects.filter(
                client_id_id=clientid, details="دفعة على حساب"
            ).aggregate(total_specific_credit=Sum('credit'))

            total_specific_credit = specific_credit_data.get('total_specific_credit') or 0

            # Add balance and specific credit to the client's data
            item['balance'] = balance
            item['paid_total'] = total_specific_credit  # Add the total specific credit
            data.append(item)
        # Pagination parameters from the request
        page_number = int(request.GET.get('page', None) or 1)
        page_size = int(request.GET.get('size', None) or 100)

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

        return JsonResponse(response, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error details in JSON

from django.core.exceptions import ValidationError

@csrf_exempt
def create_client_record(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if not data.get('phone') or not data.get('password'):
            return JsonResponse({'status': 'error', 'message': 'Phone number and Password are required.'}, status=400)

        existing_phones = User.objects.values_list('username', flat=True)  # Extracts a list of phone numbers
        if data.get('phone') in existing_phones:
            return JsonResponse({'status': 'error', 'message': 'Phone number already exists.'}, status=400)

        password = make_password(data.get('password'))
        is_correct = check_password(data.get('password'), password)  # Verify the hash

        # Create a new MainItem instance
        new_item = models.AllClientsTable(
            name=data.get('client_name', '').strip() or None,  # Ensure name is not empty
            address=data.get('address', '').strip() or None,
            email=data.get('email', '').strip() or None,
            website=data.get('website', '').strip() or None,
            phone=data.get('phone', '').strip() or None,
            mobile=data.get('mobile', '').strip() or None,
            last_transaction_amount=data.get('last_transaction', '0').strip() or '0',  # Default to '0' if missing
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
        if new_item:
            user = User.objects.create_user(username=data.get('phone'), email=data.get('email'), password=data.get('password'))

            # Validate before saving
            try:
                user.full_clean()  # Ensure the object is valid before saving
                user.save()
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': f'Validation Error: {e.message_dict}'},status=400)

        # Validate before saving
        try:
            new_item.full_clean()  # Ensure the object is valid before saving
            new_item.save()
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': f'Validation Error: {e.message_dict}'},status=400)


        return JsonResponse({'status': 'success', 'message': 'Record created successfully!','p':password,'is_correct': is_correct})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'},status=400)

#until here

@csrf_exempt
def update_client_record(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            # update client instance
            client = models.AllClientsTable.objects.get(clientid = client_id)

            # Update the client fields
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

            return JsonResponse({'status': 'success', 'message': 'Record updated successfully!'})

        except models.AllClientsTable.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Client record not found.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def delete_client_record(request):
    if request.method == 'POST':
        try:
            # Parse request data
            data = json.loads(request.body)
            client_id = data.get('client_id')

            if not client_id:
                return JsonResponse({'status': 'error', 'message': 'Client ID is required.'})

            # Retrieve the client instance
            client = models.AllClientsTable.objects.get(clientid=client_id)

            # Delete the client record
            client.delete()

            return JsonResponse({'status': 'success', 'message': 'Record deleted successfully!'})

        except models.AllClientsTable.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Client record not found.'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in request body.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

from django.http import JsonResponse
import json
#from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Sum

def filter_all_clients(request):
    if request.method == "POST":
        try:
            filters = json.loads(request.body.decode("utf-8"))  # Decode JSON payload

            # Default query
            queryset = models.AllClientsTable.objects.all()

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
                    return JsonResponse({'error': 'Invalid date format'}, status=400)

            # Prepare the data
            clients_data = []
            for client in queryset:
                client_id = client.clientid
                balance_data = models.TransactionsHistoryTable.objects.filter(client_id_id=client_id).aggregate(
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
                    specific_credit_data = models.TransactionsHistoryTable.objects.filter(
                        client_id_id=client_id, details="دفعة على حساب", registration_date__range=[from_date_obj, to_date_obj]
                    ).aggregate(total_specific_credit=Sum('credit'))
                else:
                    # Fetch total credit for specific client_id and where details = "دفعة على حساب"
                    specific_credit_data = models.TransactionsHistoryTable.objects.filter(
                        client_id_id=client_id, details="دفعة على حساب"
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

            #print(clients_data)
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
            return JsonResponse(response, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)


@csrf_exempt
def create_storage_record(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            #print(data)

            transaction_date = make_aware(datetime.strptime(data.get("transaction_date"), '%Y-%m-%d'))

            new_record = models.StorageTransactionsTable(
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
                daily_status =data.get("daily"),
                bank=data.get("bank"),
                check_no=data.get("checkno"),
            )
            new_record.save()

            client_id = None
            if data.get("for_who"):
                client = models.AllClientsTable.objects.filter(name=data.get("for_who")).first()
                if not client:
                    error_msg = f"Client '{data.get('for_who')}' not found"
                    #print("Client Error:", error_msg)
                    return JsonResponse({"error": error_msg}, status=400)
                client_id = client.clientid

            last_balance = (
                models.TransactionsHistoryTable.objects.filter(client_id_id=client_id)
                .order_by("-registration_date")
                .first()
            )
            last_balance_amount = last_balance.current_balance if last_balance else 0
            updated_balance =  round(last_balance_amount + data.get("amount"), 2)

            # Create a new `TransactionsHistoryTable` record
            account_statement = models.TransactionsHistoryTable(
                credit=float(data.get("amount")),
                debt=0.0,
                transaction=data.get("section"),
                details=f"{data.get('subsection')} / {data.get('reciept_no')}",
                registration_date=transaction_date,
                current_balance=updated_balance,  # Updated balance
                client_id_id=client_id,  # Client ID
            )
            account_statement.save()
            #print(f"statement >>> {account_statement}")

            return JsonResponse({"message": "Record created successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

#until here

@csrf_exempt
def delete_storage_record(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            storage_id = data.get("storage_id")

            # Fetch the record or return a 404 response automatically
            record = get_object_or_404(models.StorageTransactionsTable, storageid=storage_id)

            # Delete the record
            record.delete()
            return JsonResponse({"message": "Record deleted successfully!"}, status=200)

        except Http404:  # Catch the 404 error and return a JSON response
            return JsonResponse({"error": "404 Not Found in db."}, status=404)

        except json.JSONDecodeError:  # If the request body is not valid JSON
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

        except Exception as e:  # Catch all other unexpected errors
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def get_all_storage(request):
    try:
        # Query the database for all Mainitem entries
        items = models.StorageTransactionsTable.objects.all().values(
            'storageid', 'account_type', 'transaction','transaction_date'
            ,'reciept_no','place','section','subsection','person', 'amount'
            ,'issued_for','payment','done_by','bank','check_no','daily_status'
        )# List the fields you need

        data = list(items)  # Convert QuerySet to a list
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error details in JSON

@csrf_exempt
def filter_all_storage(request):
    if request.method == "POST":
        try:
            filters = json.loads(request.body.decode("utf-8"))  # Decode JSON payload
            #print(filters)
            # Default query
            queryset = models.StorageTransactionsTable.objects.all()

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
                    return JsonResponse({'error': 'Invalid date format'}, status=400)
            # Return the filtered results as JSON
            data = list(queryset.values())  # Use `values()` to return only the fields you need
            return JsonResponse(data, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)




def account_statement(request):
    client_id = request.GET['id']
    records = models.TransactionsHistoryTable.objects.filter(client_id_id=client_id)
    client = models.AllClientsTable.objects.get(clientid=client_id)
    context = {
        'records':records,
        'client':client,
    }
    return render(request,'account-statement.html',context)

def get_last_reciept_no(request):
    transaction_type = request.GET.get('transactionType')  # Get the transaction type from the query parameter
    #print(f"type: {transaction_type}")

    if transaction_type in ['ايداع', 'صرف']:
        # Cast `reciept_no` to an integer for proper ordering
        last_transaction = models.StorageTransactionsTable.objects.annotate(
            reciept_no_int=Cast('reciept_no', IntegerField())
        ).filter(
            transaction=transaction_type
        ).order_by('-reciept_no_int').first()

        last_reciept_no = last_transaction.reciept_no_int if last_transaction else 0
        return JsonResponse({'lastRecieptNo': last_reciept_no})

    return JsonResponse({'error': 'Invalid transaction type'}, status=400)


def get_buyinvoice_no(request):
    try:
        # Get the last autoid by ordering the table by autoid in descending order
        last_invoice = models.Buyinvoicetable.objects.order_by('-invoice_no').first()
        if last_invoice:
            response_data = {'autoid': last_invoice.invoice_no}
        else:
            # Handle the case where the table is empty
            response_data = {'autoid': 0, 'message': 'No invoices found'}
    except Exception as e:
        # Handle unexpected errors
        response_data = {'error': str(e)}

    return JsonResponse(response_data)


def get_account_statement(request):
    client_id = request.GET['id']
    try:
         # Query TransactionsHistoryTable with selected fields
        items = models.TransactionsHistoryTable.objects.filter(client_id_id=client_id).values(
            'autoid',
            'transaction',
            'debt',
            'credit',
            'details',
            'registration_date',
            'delivered_date',
            'delivered_for',
            'current_balance',
            'client_id_id',  # ForeignKey, so we get the client_id (or 'client_id_id' to fetch the ID)
        )


        data = list(items)  # Convert QuerySet to a list
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error details in JSON


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
# buy invoice
@csrf_exempt
def fetch_invoice_items(request):
    if request.method == "GET":
        invoice_no = request.GET.get("id")

        if not invoice_no:
            return JsonResponse({"error": "Invoice number is required."}, status=400)


        # Fetch all data from the model
        items = list(
            models.BuyInvoiceItemsTable.objects.filter(invoice_no2=invoice_no).values(
                "autoid",
                "invoice_no",
                "item_no",
                "pno",
                "name",
                "company",
                "company_no",
                "company",
                "quantity",
                "org_unit_price",
                "org_total_price",
                "dinar_unit_price",
                "dinar_total_price",
                "current_buy_price",
                "current_less_price",
                "place",
                "cost_unit_price",
                "cost_total_price",
            )
        )
        if not items:
            return JsonResponse([], safe=False)

        return JsonResponse(items, safe=False)
    else:
        return JsonResponse({"error": "Invalid HTTP method."}, status=405)
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

@csrf_exempt  # Exempt CSRF validation for the API endpoint (use with caution, better to handle CSRF properly in production)
def create_cost_record(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Extract the data fields
            invoice = data.get("invoice")
            type = data.get("type")
            cost = data.get("cost")
            rate = data.get("rate")
            dinar = data.get("dinar")

            invoice_obj = models.Buyinvoicetable.objects.get(invoice_no=invoice)
            # Validate the data
            if not invoice or not type or not cost or not rate or not dinar:
                return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

            # Create a new record in the CostType model
            cost_record = models.BuyinvoiceCosts.objects.create(
                invoice=invoice_obj,
                cost_for=type,
                cost_price=cost,
                exchange_rate=rate,
                dinar_cost_price=dinar,
                invoice_no=invoice
            )

            # Return a success response
            return JsonResponse({"success": True, "message": "Cost record created successfully", "data": {"id": cost_record.autoid}}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

#until here

csrf_exempt
def fetch_costs(request):
    if request.method == "GET":
        invoice_no = request.GET.get("id")

        if not invoice_no:
            return JsonResponse({"error": "Invoice number is required."}, status=400)


        # Fetch all data from the model
        items = list(
            models.BuyinvoiceCosts.objects.filter(invoice_no= invoice_no).values(
                "autoid",
                "invoice_no",
                "cost_for",
                "cost_price",
                "exchange_rate",
                "dinar_cost_price",

            )
        )
        if not items:
           items = []
           return JsonResponse(items, safe=False)

        return JsonResponse(items, safe=False)
    else:
        return JsonResponse({"error": "Invalid HTTP method."}, status=405)

@csrf_exempt
def delete_buyinvoice_cost(request, autoid):
    if request.method == 'DELETE':
        try:
            # Find and delete the record with the given autoid
            record = models.BuyinvoiceCosts.objects.get(autoid=autoid)
            record.delete()
            return JsonResponse({'status': 'success', 'message': 'Record deleted successfully!'},status=200)
        except models.BuyinvoiceCosts.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Record not found!'},status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'},status=405)


def payment_installments(request):
    return render(request,'payment.installments.html')


@csrf_exempt
def calculate_cost(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            cost_total = data.get("cost_total").replace(',', '')
            invoice_total = data.get("invoice_total").replace(',', '')
            invoice_id = data.get("invoice")

            # Validate the data
            if not cost_total or not invoice_total or not invoice_id:
                return JsonResponse({"success": False, "message": "Missing required fields."}, status=400)

            # Calculate the load percentage
            load_percentage = Decimal(cost_total) / Decimal(invoice_total)

            # Get the invoice object
            try:
                invoice = models.Buyinvoicetable.objects.get(invoice_no=invoice_id)
            except models.Buyinvoicetable.DoesNotExist:
                return JsonResponse({"success": False, "message": "Invoice not found."}, status=404)

            # Update the items associated with the invoice
            items = models.BuyInvoiceItemsTable.objects.filter(invoice_no2=invoice_id)
            for item in items:
                # Update the costprice based on the load percentage
                item.current_cost_price = item.dinar_unit_price * (1 + load_percentage)
                item.cost_unit_price = item.dinar_unit_price * (1 + load_percentage)
                item.cost_total_price= (item.dinar_unit_price * (1 + load_percentage))*item.quantity
                #print(f"order {item.dinar_unit_price} , cost {item.current_cost_price}")
                item.save()

            # Return a success response
            return JsonResponse({"success": True, "message": "Cost updated successfully."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

def get_invoice_items(request):
    try:
        data = json.loads(request.body)
        invoice_id = data.get("id")

        if not invoice_id:
            return JsonResponse({"error":"Invoice id is required"},status=400)

        items = models.BuyInvoiceItemsTable.objects.filter(invoice_no = invoice_id)
        if not items:
            return JsonResponse({"error":"Invoice does not exist"},status=400)
        response_data = list(items.values())

        JsonResponse({"data": response_data})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error":str(e)},status=500)


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

@csrf_exempt  # Use if CSRF token is not provided, but it's recommended to use CSRF protection.
def delete_buy_invoice_item(request):
    if request.method == "POST":
        try:
            # Parse the JSON data sent by the frontend
            data = json.loads(request.body)
            item_id = data.get("id")

            # Validate if item_id is provided
            if not item_id:
                return JsonResponse({"success": False, "message": "Missing item ID"}, status=400)

            # Try to delete the item from the database
            item = models.BuyInvoiceItemsTable.objects.get(autoid=item_id)  # Adjust the query based on your model
            item.delete()

            # Return success response
            return JsonResponse({"success": True, "message": "Item deleted successfully!"}, status=200)

        except models.BuyInvoiceItemsTable.DoesNotExist:
            # Item not found
            return JsonResponse({"success": False, "message": "Item not found"}, status=404)
        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

@csrf_exempt  # Temporarily disable CSRF check for this endpoint
def update_buyinvoiceitem(request):
    if request.method == "POST":
        try:
            # Parse the JSON data sent by the frontend
            data = json.loads(request.body)
            id = data.get('id')
            invoice_no = data.get('invoice_no')
            org = Decimal(data.get('org'))
            order = Decimal(data.get('order'))
            quantity = int(data.get('quantity'))



            # Find the item to update (you can use an ID or another identifier)
            item = models.BuyInvoiceItemsTable.objects.get(autoid=id)

              # Get the related invoice
            try:
                invoice = models.Buyinvoicetable.objects.get(invoice_no=invoice_no)
                invoice.amount -= item.dinar_total_price
                invoice.amount += order * quantity

                invoice.save()
            except models.Buyinvoicetable.DoesNotExist:
                return JsonResponse({"error": "Invoice not found"}, status=404)

            # Update the item with new values
            item.org_unit_price = org
            item.dinar_unit_price = order
            item.org_total_price = org * quantity
            item.dinar_total_price = order * quantity
            item.quantity = quantity
            item.save()

            return JsonResponse({"success": True, "message": "Item updated successfully"},status=200)

        except models.BuyInvoiceItemsTable.DoesNotExist:
            return JsonResponse({"success": False, "message": "Item not found"},status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)},status=400)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"},status=405)


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

@csrf_exempt
def check_items(request):
    if request.method == "POST":
        try:
            # Step 1: Parse the incoming JSON data
            # Step 1: Decode the stringified JSON (if necessary)
            body = request.body.decode("utf-8")  # Decode the byte string to a regular string
            data = json.loads(body)
            #print(data)

            # Step 2: Validate that the data is a list (since the request body is already an array of items)
            if not isinstance(data, list):
                return JsonResponse({"status": "error", "message": "Invalid data format. Expected an array."}, status=400)

            # Step 3: Check existence for each item
            results = []
            for item in data:
                # Ensure the necessary field 'company_no' exists in the item
                company_no = item.get("رقم الشركة")
                if not company_no:
                    results.append({"message": "company_no is missing", "exists": 0})
                    continue

                # Check if item exists in Mainitem model based on 'company_no'
                exists = models.Mainitem.objects.filter(replaceno=company_no).exists()
                results.append({"company_no": company_no, "exists": 1 if exists else 0})

            return JsonResponse({"status": "success", "results": results})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

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

def buyInvoice_edit_prices(request):
    return render(request,"buy-invoice-edit-price.html")

@csrf_exempt  # Remove this if you have CSRF protection enabled for AJAX
def confirm_temp_invoice(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            #print(data)
            invoice_no = data.get('invoice_no')
            item_rows = data.get('table')

            if not invoice_no:
                return JsonResponse({'status': 'error', 'message': 'Invoice number is required.'}, status=400)

            if not item_rows or not isinstance(item_rows, list):
                return JsonResponse({'status': 'error', 'message': 'Invalid or empty item rows.'}, status=400)

            # Process Mainitem updates
            success_count = 0
            error_details = []

            for item in item_rows:
                try:
                    # Fetch the invoice using company_no
                    main = models.Mainitem.objects.get(replaceno=item['company_no'])
                    #print(f"old data: {main.itemname} {main.itemvalue} {main.orderprice} {main.costprice} {main.orgprice} {main.itemno}")

                    # Update fields
                    main.itemname = item['name']
                    main.itemvalue += int(item['quantity'] or 0)
                    main.orderprice = Decimal(item['dinar_unit_price'] or 0)
                    main.costprice = (main.costprice + Decimal(item['cost_unit_price'] or 0)) / 2
                    main.orgprice = Decimal(item['org_unit_price'] or 0)
                    main.itemno = item['item_no']
                    main.save()

                    movement_Record = models.Clientstable.objects.create(
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

                    #print(f"new data: {main.itemname} {main.itemvalue} {main.orderprice} {main.costprice} {main.orgprice} {main.itemno}")
                    success_count += 1

                except models.Mainitem.DoesNotExist:
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
                invoice = models.Buyinvoicetable.objects.get(autoid=invoice_no)
                invoice.temp_flag = 0
                invoice.save()
            except models.Buyinvoicetable.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invoice not found.'}, status=404)

            # Consolidate response
            response = {
                'status': 'success' if success_count > 0 else 'error',
                'success_count': success_count,
                'error_count': len(error_details),
                'errors': error_details,
                'message': f'{success_count} items updated successfully and invoice temp_flag set to 0.'
                            if success_count > 0
                            else 'No items were updated.',
            }
            return JsonResponse(response)

        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@csrf_exempt
def BuyInvoiceItemCreateView(request):
    if request.method == "POST":
        try:
            # Parse the JSON data
            data = json.loads(request.body)
            #print(data)

            # Validate required fields
            required_fields = [
                "invoice_id", "itemno", "pno", "itemname", "companyproduct",
                "replaceno", "itemvalue", "currency", "itemplace", "source",
                "orgprice", "buyprice", "orderprice", "lessprice"
            ]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=400
                )

            # Get the related invoice
            try:
                invoice = models.Buyinvoicetable.objects.get(invoice_no=data.get("invoice_id"))
                invoice.amount += (Decimal(data.get("orderprice") or 0) * Decimal(data.get("itemvalue") or 0))
                invoice.save()
            except models.Buyinvoicetable.DoesNotExist:
                return JsonResponse({"error": "Invoice not found"}, status=404)

            try:
                product = models.Mainitem.objects.get(pno=data.get("pno"))
                submain = product.itemsubmain if product.itemsubmain else None
            except models.Mainitem.DoesNotExist:
                return JsonResponse({"error": "product not found"}, status=404)

            # Create a new BuyInvoiceItemsTable instance
            item = models.BuyInvoiceItemsTable.objects.create(
                invoice_no=invoice,
                invoice_no2=data.get("invoice_id"),
                item_no=data.get("itemno"),
                pno=data.get("pno"),
                main_cat=data.get("main_cat"),
                sub_cat=submain,
                name=data.get("itemname"),
                company=data.get("companyproduct"),
                company_no=data.get("replaceno"),
                quantity=int(data.get("itemvalue") or 0),  # Handle None or invalid strings
                currency=data.get("currency"),
                exchange_rate=float(data.get("rate") or 0) if data.get("rate") not in [None, '', 'null'] else 0,  # Handle 'null'
                date=data.get("date"),
                place=data.get("itemplace"),
                buysource=data.get("source"),
                org_unit_price=float(data.get("orgprice") or 0) if data.get("orgprice") not in [None, '', 'null'] else 0,
                org_total_price=(
                    float(data.get("orgprice") or 0) if data.get("orgprice") not in [None, '', 'null'] else 0
                ) * (int(data.get("itemvalue") or 0)),
                dinar_unit_price=float(data.get("orderprice") or 0) if data.get("orderprice") not in [None, '', 'null'] else 0,
                dinar_total_price=(
                    float(data.get("orderprice") or 0) if data.get("orderprice") not in [None, '', 'null'] else 0
                ) * (int(data.get("itemvalue") or 0)),
                prev_quantity=int(data.get("prev_quantity") or 0),
                prev_cost_price=float(data.get("prev_cost_price") or 0) if data.get("prev_cost_price") not in [None, '', 'null'] else 0,
                prev_buy_price=float(data.get("prev_buy_price") or 0) if data.get("prev_buy_price") not in [None, '', 'null'] else 0,
                prev_less_price=float(data.get("prev_less_price") or 0) if data.get("prev_less_price") not in [None, '', 'null'] else 0,
                current_quantity=int(data.get("prev_quantity") or 0) + int(data.get("itemvalue") or 0),
                current_buy_price=float(data.get("buyprice") or 0) if data.get("buyprice") not in [None, '', 'null'] else 0,
                current_less_price=float(data.get("lessprice") or 0) if data.get("lessprice") not in [None, '', 'null'] else 0,
            )



            confirm_message = "not confirmed"
            if(data.get("isTemp")==0):
                main = models.Mainitem.objects.get(replaceno=data.get("replaceno"))
                #print(f"old data: {main.orgprice} / {main.lessprice} /{main.itemvalue} /{main.itemtemp} /{main.itemplace} /{main.buyprice} /")
                main.orgprice = float(data.get("orgprice") or 0)
                main.lessprice=float(data.get("lessprice") or 0)
                main.itemvalue+= int(data.get("itemvalue") or 0)
                main.itemtemp -= int(data.get("itemvalue") or 0)
                main.itemplace= data.get("itemplace")
                main.buyprice=float(data.get("buyprice") or 0)
                main.save()
                confirm_message = "confirmed"
                #print(f"new data: {main.orgprice} / {main.lessprice} /{main.itemvalue} /{main.itemtemp} /{main.itemplace} /{main.buyprice} /")

                movement_Record = models.Clientstable.objects.create(
                itemno=main.itemno,
                itemname=main.itemname,
                maintype=main.itemmain,
                currentbalance=main.itemvalue,
                date=timezone.now(),
                clientname="فاتورة شراء",
                billno=data.get("invoice_id"),
                description="فاتورة شراء",
                clientbalance=int(data.get("itemvalue") or 0) or 0,
                pno_instance=main,
                pno=main.pno
                )
            # Return success response
            return JsonResponse({"message": "Item created successfully", "item_id": item.autoid,"confirm_status":confirm_message}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid HTTP method. Use POST."}, status=405)

#until here

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

def fetch_buyinvoices(request):
    # Fetch all records from Buyinvoicetable
    records = models.Buyinvoicetable.objects.all().values()
    total_amount = models.Buyinvoicetable.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    page_number = int(request.GET.get('page', 1)) #int(filters.get("page") or 1)
    page_size = int(request.GET.get('size', 100)) #int(filters.get("size") or 100)

    # Create paginator
    paginator = Paginator(records, page_size)
    page_obj = paginator.get_page(page_number)

    # Prepare the response
    response = {
        "data": list(page_obj),  # Convert the current page items to a list
        "last_page": paginator.num_pages,  # Total number of pages
        "total_rows": paginator.count,  # Total number of rows
        "page_size": page_size,
        "page_no": page_number,
        "total_amount":format_number(total_amount),
    }
    return JsonResponse(response, safe=False)

@csrf_exempt
def filter_buyinvoices(request):
    if request.method == "POST":
        try:
            # Get the filters from the request body
            filters = json.loads(request.body.decode('utf-8'))  # Decoding bytes and loading JSON
            cache_key = f"filter_{hashlib.md5(str(filters).encode()).hexdigest()}"
            cached_data = cache.get(cache_key)

            if cached_data:
                cached_data["cached_flag"] = True
                return JsonResponse(cached_data, safe=False)

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
                    return JsonResponse({'error': 'Invalid date format'}, status=400)

            # Now filter the queryset using the combined Q object
            queryset = models.Buyinvoicetable.objects.filter(filters_q).values()

            # Serialize the filtered data
            items_data = list(queryset)  # Customize the fields to return as needed

            # Pagination parameters from the request
            page_number = int(filters.get('page') or 1)
            page_size = int(filters.get('size') or 20)

            # Create paginator
            paginator = Paginator(items_data, page_size)
            page_obj = paginator.get_page(page_number)

            total_amount = queryset.aggregate(Sum('amount'))['amount__sum'] or 0

            # Prepare the response
            response = {
                "data": list(page_obj),  # Convert the current page items to a list
                "last_page": paginator.num_pages,  # Total number of pages
                "total_rows": paginator.count,  # Total number of rows
                "page_size": page_size,
                "page_no": page_number,
                "cached_flag": False,
                "total_amount":format_number(total_amount),
            }

            # Cache the response for future use
            cache.set(cache_key, response, timeout=300)  # Cache for 5 minutes

            # Return the filtered data as JSON
            return JsonResponse(response, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


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

def sell_invoice_add_invoice(request):
    Clients= models.AllClientsTable.objects.all().values()
    context = {
        "clients":Clients,
    }
    return render(request,'sell_invoice_add_invoice.html',context)

def sell_invoice_management(request):
    clients =models.AllClientsTable.objects.all().values('clientid','name')
    client_types = models.Clienttypestable.objects.all()
    context = {
        "clients":clients,
        "types":client_types,
    }
    return render(request,'sell_invoice_management.html',context)

#until here

@csrf_exempt
@api_view(["POST"])
def create_sell_invoice(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid HTTP method. Only POST is allowed."}, status=405)

    try:
        data = json.loads(request.body)
        client = None
        balance_data = {"total_debt": Decimal("0.0000"), "total_credit": Decimal("0.0000")}

        # Validate client input
        client_identifier = data.get("client")
        if not client_identifier:
            return JsonResponse({"success": False, "error": "Client is null"}, status=400)

        # Fetch client as a model instance
        try:
            if isinstance(client_identifier, int) or (isinstance(client_identifier, str) and client_identifier.isdigit()):
                client_obj = models.AllClientsTable.objects.get(clientid=int(client_identifier))
            else:
                client_obj = models.AllClientsTable.objects.get(name=client_identifier)

            # Get total debt and credit from TransactionsHistoryTable
            balance_data = models.TransactionsHistoryTable.objects.filter(client_id=client_obj).aggregate(
                total_debt=Sum('debt') or Decimal("0.0000"),
                total_credit=Sum('credit') or Decimal("0.0000")
            )
        except models.AllClientsTable.DoesNotExist:
            return JsonResponse({"success": False, "error": "Client not found"}, status=400)

        # Extract balance values
        total_debt = balance_data.get('total_debt') or Decimal('0.0000')
        total_credit = balance_data.get('total_credit') or Decimal('0.0000')
        client_balance = total_credit - total_debt

        # Get the last receipt number and determine the next one
        last_receipt_response = json.loads(get_sellinvoice_no(request).content)
        last_receipt_no = last_receipt_response.get("autoid", 0)
        next_receipt_no = int(last_receipt_no) + 1

        # Determine 'for_who' field
        for_who = "application" if data.get("for_who") == "application" else None

        # Create the SellInvoice record
        sell_invoice = models.SellinvoiceTable.objects.create(
            invoice_no=next_receipt_no,
            client_obj=client_obj,
            client_id=client_obj.clientid,  # Ensure client is a model instance
            client_name=client_obj.name,
            client_rate=client_obj.category,
            client_category=client_obj.subtype,
            client_limit=client_obj.loan_limit,
            client_balance=client_balance,
            invoice_date=data.get("invoice_date"),
            invoice_status="لم تحضر",
            payment_status=data.get("payment_status"),
            for_who=for_who,
            date_time=timezone.now(),
            price_status="",
            mobile=data.get("mobile") if data.get("mobile") else False,
        )

        # Schedule the background task using Django Q
        async_task('almogOil.Tasks.assign_orders')

        return JsonResponse({
            "success": True,
            "message": "Sell invoice created and order assignment triggered!",
            "invoice_no": sell_invoice.invoice_no,
            "client_balance": sell_invoice.client_balance
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


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

@csrf_exempt
def Sell_invoice_create_item(request):
    if request.method == "POST":
        try:
            # Parse the JSON data
            data = json.loads(request.body)
            #print(data)

            # Validate required fields
            required_fields = ["pno", "fileid", "invoice_id", "itemvalue", "sellprice"]
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return JsonResponse(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=400
                )

            # Get the related product
            try:
                product = models.Mainitem.objects.get(pno=data.get("pno"), fileid=data.get("fileid"))
            except models.Mainitem.DoesNotExist:
                return JsonResponse({"error": "Product not found"}, status=404)

            # Get the related invoice
            try:
                invoice = models.SellinvoiceTable.objects.get(invoice_no=data.get("invoice_id"))
                invoice.amount += (
                    Decimal(product.buyprice or 0) * Decimal(data.get("itemvalue") or 0)
                )
                invoice.save()
            except models.SellinvoiceTable.DoesNotExist:
                return JsonResponse({"error": "Invoice not found"}, status=404)


            # Check if sufficient quantity exists
            item_value = int(data.get("itemvalue") or 0)
            if product.itemvalue < item_value:
                return JsonResponse({"error": "Insufficient product quantity"}, status=400)

            # Create a new SellInvoiceItemsTable instance
            sell_price = Decimal(product.buyprice or 0)
            item = models.SellInvoiceItemsTable.objects.create(
                invoice_instance=invoice,
                invoice_no=data.get("invoice_id"),
                item_no=product.itemno,
                pno=data.get("pno"),
                main_cat=product.itemmain,
                sub_cat=product.itemsubmain,
                name=product.itemname,
                company=product.companyproduct,
                company_no=product.replaceno,
                quantity=item_value,
                date=timezone.now(),
                place=product.itemplace,
                dinar_unit_price=sell_price,
                dinar_total_price=sell_price * item_value,
                prev_quantity=product.itemvalue,
                current_quantity=product.itemvalue - item_value,
            )

            # Update the product quantity
            product.itemvalue -= item_value
            product.save()

            # Record the movement
            models.Clientstable.objects.create(
                itemno=product.itemno,
                itemname=product.itemname,
                maintype=product.itemmain,
                currentbalance=product.itemvalue,
                date=timezone.now(),
                clientname="فاتورة بيع",
                billno=data.get("invoice_id"),
                description="فاتورة بيع",
                clientbalance=item_value,
                pno_instance=product,
                pno=product.pno,
            )
            #test later
            try:
                client_object = invoice.client_obj
            except:
                return JsonResponse({"error": "client not found"}, status=400)

            models.StorageTransactionsTable.objects.create(
                reciept_no=f"ف.ب : {data.get('invoice_id')}",
                transaction_date=timezone.now(),
                amount=sell_price * item_value,
                issued_for="فاتورة بيع",
                note=f" شراء بضائع - ر.خ : {data.get('pno')}",
                account_type="عميل",
                transaction=f" شراء بضائع - ر.خ : {data.get('pno')}",
                place="مارين",
                section="مبيعات",
                subsection="مبيعات",
                person=client_object.name or "",
                payment= "نقدا" if invoice.payment_status == "نقدي" else "اجل",
                daily_status =False,
            )

            last_balance = (
                models.TransactionsHistoryTable.objects.filter(client_id=invoice.client_obj)
                .order_by("-registration_date")
                .first()
            )
            last_balance_amount = last_balance.current_balance if last_balance else 0
            updated_balance =  round(last_balance_amount - (sell_price * item_value), 2)

            account_statement = models.TransactionsHistoryTable.objects.create(
                credit=0.0,
                debt=Decimal(sell_price * item_value),
                transaction=f" شراء بضائع - ر.خ : {data.get('pno')}",
                details=f"شراء بضاتع - فاتورة رقم {data.get('invoice_id')}",
                registration_date=timezone.now(),
                current_balance=updated_balance,  # Updated balance
                client_id=invoice.client_obj,  # Client ID
            )

            if invoice.payment_status == "نقدي":
                models.TransactionsHistoryTable.objects.create(
                credit=Decimal(sell_price * item_value),
                debt=0.0,
                transaction=f"دفع مقابل شراء بضائع - ر.خ : {data.get('pno')}",
                details=f"شراء بضاتع - فاتورة رقم {data.get('invoice_id')}",
                registration_date=timezone.now(),
                current_balance=round(last_balance_amount, 2),  # Updated balance
                client_id=invoice.client_obj,  # Client ID
                )

            if invoice.mobile == True:
                models.TransactionsHistoryTable.objects.create(
                credit=Decimal(sell_price * item_value)*Decimal(0.10),
                debt=0.0,
                transaction=f"نسبة بيع مقابل شراء بضائع - ر.خ : {data.get('pno')}",
                details=f"نسبة بيع 10% مقابل بضاتع - فاتورة رقم {data.get('invoice_id')}",
                registration_date=timezone.now(),
                current_balance=round(last_balance_amount, 2) + (Decimal(sell_price * item_value)*Decimal(0.10)),  # Updated balance
                client_id=invoice.client_obj,  # Client ID
                )

            # Return success response
            return JsonResponse(
                {"message": "Item created successfully", "item_id": item.autoid, "confirm_status": "confirmed"},
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Invalid HTTP method. Use POST."}, status=405)


@csrf_exempt
def fetch_sell_invoice_items(request):
    if request.method == "GET":
        invoice_no = request.GET.get("id")

        if not invoice_no:
            return JsonResponse({"error": "Invoice number is required."}, status=400)


        # Fetch all data from the model
        items = list(
            models.SellInvoiceItemsTable.objects.filter(invoice_no= invoice_no).values()
        )
        if not items:
            return JsonResponse([], safe=False)

        return JsonResponse(items, safe=False)
    else:
        return JsonResponse({"error": "Invalid HTTP method."}, status=405)


from django.utils.timezone import now
def fetch_sellinvoices(request):
    try:
        today = now().date()
        # Fetch all sell invoice records
        records = models.SellinvoiceTable.objects.filter(invoice_date__date=today).values()

        # Aggregate total, cash, and loan amounts in a single query for efficiency
        aggregates = models.SellinvoiceTable.objects.aggregate(
            total_amount=Sum('amount'),
            cash_amount=Sum('amount', filter=Q(payment_status="نقدي")),
            loan_amount=Sum('amount', filter=Q(payment_status="اجل")),
            total_discount=Sum('discount'),
            total_returned=Sum('returned')
        )

        total_amount = aggregates["total_amount"] or 0
        cash_amount = aggregates["cash_amount"] or 0
        loan_amount = aggregates["loan_amount"] or 0
        total_discount = aggregates["total_discount"] or 0
        total_returned = aggregates["total_returned"] or 0

        # Get pagination parameters with defaults
        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("size", 100)

        try:
            page_number = int(page_number)
            page_size = int(page_size)
        except ValueError:
            return JsonResponse({"error": "Invalid page or size parameter"}, status=400)

        # Paginate the records
        paginator = Paginator(records, page_size)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        # Prepare and return the response
        return JsonResponse({
            "data": list(page_obj),  # Convert the current page items to a list
            "last_page": paginator.num_pages,  # Total number of pages
            "total_rows": paginator.count,  # Total number of rows
            "page_size": page_size,
            "page_no": page_number,
            "total_amount": format_number(total_amount),
            "cash_amount": format_number(cash_amount),
            "loan_amount": format_number(loan_amount),
            "total_discount": format_number(total_discount),
            "total_returned": format_number(total_returned),
        }, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

from django.core.serializers import serialize

@csrf_exempt
def filter_sellinvoices(request):
    if request.method == "POST":
        try:
            # Get the filters from the request body
            filters = json.loads(request.body.decode('utf-8'))
            cache_key = f"sell_invoice_filter_{str(filters)}"
            cached_data = cache.get(cache_key)

            if cached_data:
                cached_data["cached_flag"] = True
                return JsonResponse(cached_data, safe=False)

            # Initialize the base Q object for filtering
            filters_q = Q()

            # Apply filters based on request data
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


            # Date range filter on `invoice_date`
            fromdate = filters.get('fromdate', '').strip()
            todate = filters.get('todate', '').strip()

            if fromdate and todate:
                try:
                    from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                    to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)
                    filters_q &= Q(invoice_date__range=[from_date_obj, to_date_obj])
                except ValueError:
                    return JsonResponse({'error': 'Invalid date format'}, status=400)

            # Filter queryset
            invoices_qs = models.SellinvoiceTable.objects.filter(filters_q).values().order_by("-invoice_date")

            # Aggregate total amounts
            totals = invoices_qs.aggregate(
                total_amount=Sum('amount', default=0),
                cash_amount=Sum('amount', filter=Q(payment_status="نقدي"), default=0),
                loan_amount=Sum('amount', filter=Q(payment_status="اجل"), default=0),
                total_discount=Sum('discount', default=0),
                total_returned=Sum('returned', default=0)
            )


            # Pagination
            page_number = int(filters.get('page') or 1)
            page_size = int(filters.get('size') or 20)
            paginator = Paginator(invoices_qs, page_size)
            page_obj = paginator.get_page(page_number)


            # Prepare the response
            response = {
                "data": list(page_obj),  # Serialized invoices
                "last_page": paginator.num_pages,  # Total number of pages
                "total_rows": paginator.count,  # Total number of rows
                "page_size": page_size,
                "page_no": page_number,
                "cached_flag": False,
                "total_amount": format_number(Decimal(totals["total_amount"])),
                "cash_amount": format_number(Decimal(totals["cash_amount"])),
                "loan_amount": format_number(Decimal(totals["loan_amount"])),
                "total_discount": format_number(Decimal(totals["total_discount"])),
                "total_returned": format_number(Decimal(totals["total_returned"])),
            }

            # Cache response for 5 minutes
            cache.set(cache_key, response, timeout=300)

            return JsonResponse(response, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
#until here

def sell_invoice_prepare_report(request):
    client = models.AllClientsTable.objects.all().values("clientid","name")
    context = {
        "clients":client,
    }
    return render(request,'sell_invoice_prepare_report.html',context)

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

def sell_invoice_profile(request, id):
    invoice = get_object_or_404(models.SellinvoiceTable, invoice_no=id)

    serializer = serializers.SellInvoiceSerializer(invoice)
    clients = models.AllClientsTable.objects.all().values()

    context = {
        "clients": clients,
        "invoice": serializer.data,
    }
    return render(request, 'sell_invoice_profile.html', context)

@csrf_exempt
def prepare_sell_invoice(request):
    if request.method == "POST":
        try:
            # Get the data from the request body
            data = json.loads(request.body.decode('utf-8'))
            name = data.get('name')
            note = data.get('note')
            invoice_id = data.get('invoice_id')

            # Get the invoice object
            invoice = models.SellinvoiceTable.objects.get(invoice_no=invoice_id)

            # Update invoice fields
            invoice.preparer_name = name
            invoice.preparer_note = note
            invoice.invoice_status = "جاري التحضير"

            # Save the updated invoice
            invoice.save()

            return JsonResponse({'status': 'success', 'message': 'Invoice updated successfully'})
        except invoice.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invoice not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
@csrf_exempt
def validate_sell_invoice(request):
    if request.method == "POST":
        try:
            # Get the data from the request body
            data = json.loads(request.body.decode('utf-8'))
            reviewer = data.get('reviewer')
            place = data.get('place')
            invoice_no = data.get('invoice_id')
            size = data.get('size')
            final_note = data.get('final_note')

            # Get the invoice object
            invoice = models.SellinvoiceTable.objects.get(invoice_no=invoice_no)

           # Update invoice fields
            invoice.reviewer_name = reviewer
            invoice.place = place
            invoice.quantity = size
            invoice.notes = final_note
            invoice.invoice_status = "روجعت"

            # Save the updated invoice
            invoice.save()

            return JsonResponse({'status': 'success', 'message': 'Invoice updated successfully'})
        except invoice.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invoice not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def deliver_sell_invoice(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
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

            invoice = models.SellinvoiceTable.objects.get(invoice_no=invoice_id)

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
            user_id = invoice.client # Make sure this field exists on your model.
            room_group_name = f'user_{user_id}'
            message = f"تم تحديث حالة الفاتورة رقم {invoice_id} إلى {status}."

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    "type": "send_notification",
                    "message": message,
                }
            )

            async_task('almogOil.Tasks.assign_orders')  # Adjust as needed

            return JsonResponse({'status': 'success', 'message': 'Invoice updated successfully'})

        except models.SellinvoiceTable.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invoice not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def cancel_sell_invoice(request):
    if request.method == "POST":
        try:
            # Get the data from the request body
            data = json.loads(request.body.decode('utf-8'))
            invoice_no = data.get('invoice_id')

            # Get the invoice object
            invoice = models.SellinvoiceTable.objects.get(invoice_no=invoice_no)

           # Update invoice fields
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

            return JsonResponse({'status': 'success', 'message': 'Invoice cancelled successfully'})
        except invoice.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invoice not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def get_mainItem_last_pno(request):
    try:
        # Get the last autoid by ordering the table by autoid in descending order
        last_pno = models.Mainitem.objects.order_by('-pno').first()
        if last_pno:
            response_data = {'pno': last_pno.pno}
        else:
            # Handle the case where the table is empty
            response_data = {'pno': 0, 'message': 'No invoices found'}
    except Exception as e:
        # Handle unexpected errors
        response_data = {'error': str(e)}

    return JsonResponse(response_data)

class SendMessageView(generics.CreateAPIView):
    queryset = models.ChatMessage.objects.all()
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

     sender = get_object_or_404(models.AllClientsTable, clientid=sender_id)
     receiver = get_object_or_404(models.AllClientsTable, clientid=receiver_id)

     chat_message = models.ChatMessage.objects.create(sender=sender, receiver=receiver, message=message_text)
     serializer = self.get_serializer(chat_message)

     return Response(serializer.data, status=status.HTTP_201_CREATED)

class GetChatMessagesView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
     sender_id = self.request.query_params.get('sender')
     receiver_id = self.request.query_params.get('receiver')
     return models.ChatMessage.objects.filter(sender__clientid=sender_id, receiver__clientid=receiver_id) | models.ChatMessage.objects.filter(sender__clientid=receiver_id, receiver__clientid=sender_id)

class MarkMessageAsReadView(generics.UpdateAPIView):
    queryset = models.ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

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

def notifications_page(request):
    return render(request, 'notifications.html')


def return_items_view(request):
    clients = models.AllClientsTable.objects.all().values('clientid','name')
    invoices = models.SellinvoiceTable.objects.all().values('invoice_no','client_id','client_name')
    context = {
        'clients':clients,
        'invoices':invoices,
    }
    return render(request, 'return-permission-add.html',context)

def return_items_report_view(request):
    clients = models.AllClientsTable.objects.all().values('clientid','name')
    context = {
        'clients':clients,
    }
    return render(request, 'return-permission-report.html',context)


def engines_view(request):
    engines = models.enginesTable.objects.values('fileid', 'engine_name','subtype_str','maintype_str')
    subtypes =   models.Subtypetable.objects.all().values()
    maintypes =   models.Maintypetable.objects.all().values()

    return render(request, 'engines-table.html', {
        'engines': engines,
        'subType': subtypes,
        'mainType': maintypes,
    })

def return_items_add_items(request, id, permission):
    try:
        invoice_items = models.SellInvoiceItemsTable.objects.filter(invoice_no=id)
        serializer = serializers.SellInvoiceItemsSerializer(invoice_items, many=True)
        invoice_items_data = json.dumps(serializer.data) # Store serialized data
    except models.SellInvoiceItemsTable.DoesNotExist:
        invoice_items_data = {}  # Return an empty list if no records are found

    context = {
        "invoice_items": invoice_items_data,
        "invoice":id,
        "permission":permission,
    }
    return render(request, 'return_permission_add_items.html', context)

def request_payment_view(request):
    requests = models.PaymentRequestTable.objects.select_related('client').all()  # Fetch requests with clients
    updated_data = []  # List to store modified request objects

    for req in requests:
        # Calculate balance from TransactionsHistoryTable
        balance_data = models.TransactionsHistoryTable.objects.filter(client_id=req.client_id).aggregate(
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

def assign_order_page(request):
    return render(request, 'assign_order.html')


def invoice_notifications(request):
    return render(request, 'WStest.html')

def sources_management_View(request):
    context = {}
    return render(request,'sources-management.html',context)


#from .firebase_config import send_firebase_notification

#def test_send_notification(request):
  #  try:
        # Fetch the client you want to notify (example: client with id=14)
  #      client = models.AllClientsTable.objects.get(clientid=14)  # Ensure 'clientid' is correct

        # Create a mock invoice to simulate a status change
   #     invoice = models.SellinvoiceTable.objects.create(
    #        client=client,
     #       invoice_no="12345",
      #      invoice_status="تم التوصيل"
       # )

        # Send notification
        #if client.fcm_token:  # Check if the client has a valid FCM token
         #   send_firebase_notification(
          #      client.fcm_token,
           #     "Order Update",
            #    f"Your order #{invoice.invoice_no} is now {invoice.invoice_status}."
            #)
            #return JsonResponse({"status": "Notification sent"})
        #else:
         #   return JsonResponse({"status": "Client FCM token not available"}, status=400)
    #except models.AllClientsTable.DoesNotExist:
     #   return JsonResponse({"status": "Client not found"}, status=404)
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

def return_permission_profile(request, id):
    return_permission = get_object_or_404(models.return_permission, autoid=id)
    context = {
        "return": return_permission,
        "date": return_permission.date.strftime("%Y-%m-%d"),
        "client_name": return_permission.client.name,
    }
    return render(request, 'return_permission_profile.html', context)


def users_management(request):
    context = {}
    return render(request,"users-management.html",context)

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

def assign_orders_page(request, invoice_id):
    # You can pass any additional context here if needed, e.g., the invoice_id
    return render(request, 'assign_orders.html', {'invoice_id': invoice_id})


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
