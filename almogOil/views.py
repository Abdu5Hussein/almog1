import datetime
from decimal import Decimal
import json
import os
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import AllClientsTable, AllSourcesTable, BalanceAndTransactions, BuyInvoiceItems, BuyInvoiceTable, Clients, LostAndDamaged, Modeltable,Imagetable, Mainitem,Measurement,Maintypetable, Sections, StorageTransactions, SubSections,Subtypetable,Companytable,Manufaccountrytable,Oemtable, buyInvoice_costs, clientTypes, cost_types, currency
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.db.models import F, Q  # Import F for field comparison
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
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
from io import BytesIO
import pandas as pd
from django.http import JsonResponse
from .models import Mainitem
import logging
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, IntegerField
from django.db.models.functions import Cast

# Define your custom User model or replace it with appropriate logic
# from .models import YourCustomUserModel  # Update this line to use your new model if needed

def LogInView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        return redirect('home')
        # Logic for authentication can be added here if necessary
    else:  
        return render(request, 'login.html')

def StorageManagement(req):
    Clients= AllClientsTable.objects.all()
    sections = Sections.objects.all()
    subSections = SubSections.objects.all()
    context = {
        'clients': Clients,
        'sections': sections,
        'subSections': subSections
    }
    return render(req,'storage-management.html',context)

def StorageReports(req):
    Clients= AllClientsTable.objects.all()
    sections = Sections.objects.all()
    subSections = SubSections.objects.all()
    context = {
        'clients': Clients,
        'sections': sections,
        'subSections': subSections
    }
    return render(req,'storage-reports.html',context)

def get_subsections(request):
    section_id = request.GET.get('section_id')  # Get selected section ID from request
    subsections = SubSections.objects.filter(sectionid_id=section_id).values('autoid', 'subsection')
    return JsonResponse(list(subsections), safe=False)  # Return JSON response

def TestView(request):
    if request.method == 'POST':
        # Assuming you're creating a new user or a similar entity
        if request.POST.get('password') and request.POST.get('email'):
            try:
                # Replace with your new model instance
                # user = YourCustomUserModel()  # Replace with your new model
                # user.name = request.POST.get('name')
                # user.email = request.POST.get('email')
                # user.age = request.POST.get('age')  # If age is provided
                # user.password = request.POST.get('password')  # Hash the password
                # user.save()

                # Add a success message
                messages.success(request, 'User created successfully!')
            except Exception as e:
                # Add an error message if saving fails
                messages.error(request, f'Error creating user: {e}')
        else:
            # Add an error message if required fields are missing
            messages.error(request, 'Please fill in all required fields.')

    return render(request, 'main.html')

def MoreDetails(req):
    productId = req.GET.get('product_id')
    item = Mainitem.objects.filter(fileid=productId)
    context = {
        'item':item
    }
    return render(req,'more-details.html',context)

def UsersView(request):
    query = request.GET.get('q')  # Get search query from URL parameters
    users = []  # Update this to reflect how you will fetch users if at all
    # Example if you're using a new model
    # if query:
    #     users = YourCustomUserModel.objects.filter(name__icontains=query)
    # else:
    #     users = YourCustomUserModel.objects.all()
        
    # Check if the request is AJAX by looking at the header
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Format user data as needed
        user_list = []  # Replace with logic to fetch data
        return JsonResponse({'users': user_list})  # Return JSON response
    
    context = {'users': users}
    return render(request, "users.html", context)

def BuyInvoicesAdd(request):
    sources = AllSourcesTable.objects.all().values('clientid','name')
    Currency = currency.objects.all()
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
        print(data)
        
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
        source = AllSourcesTable.objects.get(clientid=source_id)
        # Create a new record in the BuyInvoiceTable model
        invoice = BuyInvoiceTable.objects.create(
            invoice_no=invoice_autoid,
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
    

def ImageView(request):
    # Retrieve all images to display in the template
    product_id = request.GET.get("product_id")
    images = Imagetable.objects.filter(productid=product_id)

    if request.method == 'POST':        
        if 'delete-id' in request.POST:  # Check if it's a delete request
            delete_id = request.POST.get('delete-id')
            image_to_delete = get_object_or_404(Imagetable, fileid=delete_id)
            image_to_delete.delete()
            return JsonResponse({'status': 'success', 'message': 'Image deleted successfully.'})
        
        # Handle image upload
        product_id = request.POST.get('product-id')
        image = request.FILES.get('image')

        if image and product_id:
            # Create a new Imagetable object
            Imagetable.objects.create(productid=product_id, image=image)
            # Redirect to the same view with the product_id in the query string
            return HttpResponseRedirect(f"{reverse('images')}?product_id={product_id}")

    # Render the image table template
    return render(request, 'image-table.html', {'images': images})

def ModelView(request):
    main_types = Maintypetable.objects.all()
    models = Modeltable.objects.select_related('maintype').all()

    if request.method == 'POST':
        action = request.POST.get('action')
        model_id = request.POST.get('id')
        model_name = request.POST.get('model-name')
        main_type_id = request.POST.get('model-main-type')

        if action == 'add':
            if model_name and main_type_id:
                main_type = get_object_or_404(Maintypetable, fileid=main_type_id)
                Modeltable.objects.create(sname=model_name, maintype=main_type)
                messages.success(request, "Model added successfully!")
            else:
                messages.error(request, "All fields are required.")

        elif action == 'edit':
            if model_id and model_name:
                model = get_object_or_404(Modeltable, fileid=model_id)
                model.sname = model_name
                model.save()
                messages.success(request, "Model updated successfully!")
            else:
                messages.error(request, "All fields are required.")

        elif action == 'delete':
            if model_id:
                model = get_object_or_404(Modeltable, fileid=model_id)
                model.delete()
                messages.success(request, "Model deleted successfully!")
            else:
                messages.error(request, "Model ID is required.")

        return redirect('models')

    return render(request, 'model-table.html', {
        'mainType': main_types,
        'models': models,
    })  

def HomeView(request):
    return render(request, 'home.html')

def SectionAndSubSection(request):
    sections = Sections.objects.all()
    subSections = SubSections.objects.all()

    # Handle POST requests for both sections and subsections
    if request.method == "POST":
        action = request.POST.get("action")
        
        # Handle Section actions
        if "section" in request.POST:
            section_id = request.POST.get("id")
            section_name = request.POST.get("name")
            
            
            if action == "add" and section_name:
                Sections.objects.create(section=section_name)
            elif action == "edit" and section_id and section_name:
                section = Sections.objects.get(autoid=section_id)
                section.section = section_name
                section.save()
            elif action == "delete" and section_id:
                Sections.objects.filter(autoid=section_id).delete()

        # Handle Subsection actions
        elif "subsection" in request.POST:
            subsection_id = request.POST.get("id")
            subsection_name = request.POST.get("name")
            section_fk = request.POST.get("key")
            
            if action == "add" and subsection_name:
                section_instance = Sections.objects.get(autoid=section_fk)  # Assuming autoid is the primary key field

                SubSections.objects.create(subsection=subsection_name,sectionid=section_instance)
            elif action == "edit" and subsection_id and subsection_name:
                subsection = SubSections.objects.get(autoid=subsection_id)
                subsection.subsection = subsection_name
                subsection.save()
            elif action == "delete" and subsection_id:
                SubSections.objects.filter(autoid=subsection_id).delete()

        # Redirect to the same page after action
        return redirect('sections-and-subsections')  # Replace with the actual URL name
    
    context = {
        'sections': sections,
        'subSections': subSections,
    }
    return render(request, 'section-subsection.html', context)



    

def MainCat(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name')
        main_id = request.POST.get('id')  # Get the ID from the form

        try:
            if action == 'add':
                Maintypetable.objects.create(typename=name)
            elif action == 'edit' and main_id:
                # Correctly fetch the object using `objects.get`
                maintypetable = Maintypetable.objects.get(fileid=main_id)
                maintypetable.typename = name  # Update the typename field
                maintypetable.save()
            elif action == 'delete' and main_id:
                # Correctly fetch the object and delete it
                maintypetable = Maintypetable.objects.get(fileid=main_id)
                maintypetable.delete()
            else:
                # Handle invalid action or missing data
                raise ValueError("Invalid action or missing ID.")

        except Maintypetable.DoesNotExist:
            # Handle the case where the object with the given ID does not exist
            messages.error(request, "The specified measurement does not exist.")
        except Exception as e:
            # Handle other unexpected errors
            messages.error(request, f"An error occurred: {e}")

        return redirect('maintype')

    mainType = Maintypetable.objects.all()
    context = {
        'mainType': mainType,
    }
    return render(request, 'main-cat.html', context)

def SubCat(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name')
        sub_id = request.POST.get('id')  # Get the ID from the form

        try:
            if action == 'add':
                Subtypetable.objects.create(subtypename=name)
            elif action == 'edit' and sub_id:
                # Correctly fetch the object using `objects.get`
                subtypetable = Subtypetable.objects.get(fileid=sub_id)
                subtypetable.subtypename = name  # Update the typename field
                subtypetable.save()
            elif action == 'delete' and sub_id:
                # Correctly fetch the object and delete it
                subtypetable = Subtypetable.objects.get(fileid=sub_id)
                subtypetable.delete()
            else:
                # Handle invalid action or missing data
                raise ValueError("Invalid action or missing ID.")

        except Subtypetable.DoesNotExist:
            # Handle the case where the object with the given ID does not exist
            messages.error(request, "The specified measurement does not exist.")
        except Exception as e:
            # Handle other unexpected errors
            messages.error(request, f"An error occurred: {e}")

        return redirect('subtype')

    subType = Subtypetable.objects.all()
    context = {
        'subType': subType,
    }
    return render(request, 'sub-cat.html', context)
def manage_companies(request):
    if request.method == 'POST':
        action = request.POST.get('action')  # Get action: add, edit, delete
        name = request.POST.get('name')  # Company name from the form
        company_id = request.POST.get('id')  # Hidden input for company ID

        try:
            if action == 'add':
                # Add a new company
                Companytable.objects.create(companyname=name)
                messages.success(request, "تمت إضافة الشركة بنجاح.")
            elif action == 'edit' and company_id:
                # Edit an existing company
                company = get_object_or_404(Companytable, pk=company_id)
                company.companyname = name
                company.save()
                messages.success(request, "تم تعديل الشركة بنجاح.")
            elif action == 'delete' and company_id:
                # Delete an existing company
                company = get_object_or_404(Companytable, pk=company_id)
                company.delete()
                messages.success(request, "تم حذف الشركة بنجاح.")
            else:
                messages.error(request, "حدث خطأ أثناء معالجة الطلب.")
        except Exception as e:
            messages.error(request, f"خطأ: {e}")

        return redirect('manage_companies')  # Redirect to the same page

    # Fetch all company records for display
    companyTable = Companytable.objects.all()
    context = {
        'companyTable': companyTable,
    }
    return render(request, 'company-table.html', context)

def manage_countries(request):
    if request.method == "POST":
        action = request.POST.get("action")
        country_id = request.POST.get("id")
        country_name = request.POST.get("name")

        if action == "add" and country_name:
            Manufaccountrytable.objects.create(countryname=country_name)

        elif action == "edit" and country_id and country_name:
            country = Manufaccountrytable.objects.filter(fileid=country_id).first()
            if country:
                country.countryname = country_name
                country.save()

        elif action == "delete" and country_id:
            Manufaccountrytable.objects.filter(fileid=country_id).delete()

        return redirect('manage_countries')

    # Fetch all countries for display
    countries = Manufaccountrytable.objects.all().order_by('countryname')
    return render(request, 'countries-table.html', {'countries': countries})

def Measurements(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name')
        measurement_id = request.POST.get('id')

        if action == 'add':
            Measurement.objects.create(name=name)
        elif action == 'edit' and measurement_id:
            measurement = Measurement.objects.get(id=measurement_id)
            measurement.name = name
            measurement.save()
        elif action == 'delete' and measurement_id:
            Measurement.objects.get(id=measurement_id).delete()

        return redirect('measurements')

    measurements = Measurement.objects.all()
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

def ProductsDetails(req):
    
    company = Companytable.objects.all()
    measurements = Measurement.objects.all()
    mainType = Maintypetable.objects.all()
    subType = Subtypetable.objects.all()
    countries = Manufaccountrytable.objects.all()
    models = Modeltable.objects.all()
    columns = [field.name for field in Mainitem._meta.fields]
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
    

    print(columns)  # Debugging to check the contents of columns
    context = {        
        'company': company,
        'columns': columns,
        'column_visibility': column_visibility,
        'measurements': measurements,
        'mainType': mainType,
        'subType':subType,
        'countries':countries,
        'models':models,
        'column_titles': COLUMN_TITLES,
    }
    return render(req, 'products-details.html', context)

def filter_clients(request):
    try:
        # Get the 'pno' parameter from the request
        pno = request.GET.get('pno')

        if not pno:
            return JsonResponse({'error': 'Missing pno parameter'}, status=400)
        
        # Filter Clients based on 'pno'
        clients = Clients.objects.filter(pno=pno).values(
            'fileid', 'itemno', 'maintype','itemname','currentbalance','date','clientname','billno','description', 'clientbalance','pno'
        )
        


        # Return the filtered clients data as JSON
        return JsonResponse(list(clients), safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def OemNumbers(req):
    company_name = req.GET.get('company_name')
    company_no = req.GET.get('company_no')
    oem = Oemtable.objects.filter(cname=company_name, cno=company_no)
    # Handle form submission for Add, Edit, or Delete actions
    if req.method == 'POST':
        action = req.POST.get('action')
        company_name = req.POST.get('company-name')
        company_no = req.POST.get('company-no')
        oem_no = req.POST.get('oem-no')
        file_id = req.POST.get('id')

        if action == 'add':
            # Add a new record
            Oemtable.objects.create(cname=company_name, cno=company_no, oemno=oem_no)
        elif action == 'edit' and file_id:
            # Edit an existing record
            try:
                oem_record = Oemtable.objects.get(fileid=file_id)
                oem_record.cname = company_name
                oem_record.cno = company_no
                oem_record.oemno = oem_no
                oem_record.save()
            except Oemtable.DoesNotExist:
                pass
        elif action == 'delete' and file_id:
            # Delete an existing record
            try:
                oem_record = Oemtable.objects.get(fileid=file_id)
                oem_record.delete()
            except Oemtable.DoesNotExist:
                pass

        # Redirect to the same page to reflect the changes
        return redirect(f'/oem/?company_name={company_name}&company_no={company_no}')  # Assuming the name of the view is 'oem_numbers'
    context = {'oem': oem}
    return render(req, 'oem-table.html', context)

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
            record = Mainitem.objects.get(fileid=fileid)

            # Delete the record
            record.delete()

            return JsonResponse({"success": True, "message": "Record deleted successfully."})

        except Mainitem.DoesNotExist:
            return JsonResponse({"success": False, "message": "Record not found."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

@csrf_exempt 
def filter_items(request):
    if request.method == "POST":
        try:
            # Get the filters from the request body
            filters = json.loads(request.body.decode('utf-8'))  # Decoding bytes and loading JSON

            # Build the query based on the filters
            queryset = Mainitem.objects.all()

            if filters.get('itemno'):
                queryset = queryset.filter(itemno__icontains=filters['itemno'])
            if filters.get('itemmain'):
                queryset = queryset.filter(itemmain__icontains=filters['itemmain'])
            if filters.get('itemsubmain'):
                queryset = queryset.filter(itemsubmain__icontains=filters['itemsubmain'])
            if filters.get('companyproduct'):
                queryset = queryset.filter(companyproduct__icontains=filters['companyproduct'])
            if filters.get('itemname'):
                queryset = queryset.filter(itemname__icontains=filters['itemname'])
            if filters.get('eitemname'):
                queryset = queryset.filter(eitemname__icontains=filters['eitemname'])
            if filters.get('companyno'):
                queryset = queryset.filter(replaceno__icontains=filters['companyno'])
            if filters.get('pno'):
                queryset = queryset.filter(pno__icontains=filters['pno'])
            if filters.get('source'):
                queryset = queryset.filter(ordersource__icontains=filters['source'])
            if filters.get('model'):
                queryset = queryset.filter(itemthird__icontains=filters['model'])
            if filters.get('country'):
                queryset = queryset.filter(itemsize__icontains=filters['country']) 

             # Apply the checkbox filters
            if filters.get('itemvalue') == "0":
                queryset = queryset.filter(itemvalue=0)
            if filters.get('itemvalue') == ">0":
                queryset = queryset.filter(itemvalue__gt=0)
            if filters.get('resvalue') == ">0":
                queryset = queryset.filter(resvalue__gt=0)  
            if filters.get('itemvalue_itemtemp') == "lte":
                queryset = queryset.filter(itemvalue__lte=F('itemtemp'))  # Compare fields  
                               
              # Apply date range filter on `orderlastdate`
            
            fromdate = filters.get('fromdate', '').strip()
            todate = filters.get('todate', '').strip()
            
            #print(f'from date {fromdate} to date {todate}')

            if fromdate and todate:
                try:
                    # Parse dates
                    #print(f'from date inner {fromdate} to date {todate}')
                    # Parse fromdate and todate
                    from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                    to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)

                    print(f"Filtering from {from_date_obj} to {to_date_obj}")   
                                    
                    # Apply date range filter
                    queryset = queryset.filter(orderlastdate__range=[from_date_obj, to_date_obj])
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
    

@csrf_exempt 
def filter_clients_input(request):
    if request.method == "POST":
        try:
            # Get the filters from the request body
            filters = json.loads(request.body.decode('utf-8'))  # Decoding bytes and loading JSON

            # Build the query based on the filters
            queryset = Clients.objects.all()

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
                data = pd.read_excel(excel_file)

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

                return JsonResponse({"status": "success", "message": "Excel data imported successfully."})

            except Exception as e:
                logger.error(f"Error processing file: {e}")
                return JsonResponse({"status": "error", "message": f"Error: {str(e)}"})

        # Handle imported data (Tabulator data)
        elif request.POST.get("data"):
            data = json.loads(request.POST["data"])
            print(f"tabulator data {data}")
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

        return JsonResponse({"status": "error", "message": "Invalid request or missing file."})



# Register the Amiri font
pdfmetrics.registerFont(TTFont('Amiri', 'static/amiri-font/Amiri-Regular.ttf'))

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


def ImportExcel(request):
    return render(request,'import-excel.html')

def StoragePlaces(request):
    company = Companytable.objects.all()
    mainType = Maintypetable.objects.all()
    subType = Subtypetable.objects.all()
    context = {
        'company': company,
        'mainType': mainType,
        'subType':subType,
    }
    return render(request,'storage-placing.html',context)

def get_item_data(request, fileid):
    try:
        # Retrieve the record from the database
        item = Mainitem.objects.get(fileid=fileid)

        # Prepare the data to send back
        data = {
            "fileid": item.fileid,
            "itemno": item.itemno,
            "itemmain": item.itemmain,
            "itemsubmain": item.itemsubmain,
            "itemname": item.itemname,
            "eitemname": item.eitemname,
            "companyproduct": item.companyproduct,
            "replaceno": item.replaceno,
            "pno": item.pno,
            "barcodeno": item.barcodeno,
            "memo": item.memo,
            "itemsize": item.itemsize,
            "itemperbox": item.itemperbox,
            "itemthird": item.itemthird,
            "itemvalue": item.itemvalue,
            "itemtemp": item.itemtemp,
            "itemvalueb": item.itemvalueb,
            "reservedvalue": item.resvalue,
            "itemplace": item.itemplace,
            "orgprice": item.orgprice,
            "orderprice": item.orderprice,
            "costprice": item.costprice,
            "buyprice": item.buyprice,
            "lessprice": item.lessprice
        }

        return JsonResponse(data)

    except Mainitem.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)
    

def edit_main_item(request):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            fileid = data.get('fileid')
            item = Mainitem.objects.get(fileid=fileid)
            
            # Update the model fields with the new data
            item.itemno  = data.get('originalno', item.itemno)
            item.itemmain = data.get('itemmain', item.itemmain)
            item.itemsubmain  = data.get('itemsub', item.itemsubmain)
            item.itemname = data.get('pnamearabic', item.itemname)
            item.eitemname = data.get('pnameenglish', item.eitemname)
            item.companyproduct = data.get('company', item.companyproduct)
            item.replaceno = data.get('companyno', item.replaceno)
            item.pno = data.get('pno', item.pno)
            item.barcodeno = data.get('barcode', item.barcodeno)
            item.memo = data.get('description', item.memo)
            item.itemsize = data.get('country', item.itemsize)
            item.itemperbox  = data.get('pieces4box', item.itemperbox)
            item.itemthird = data.get('model', item.itemthird)
            item.itemvalue = data.get('storage', item.itemvalue)
            item.itemtemp = data.get('backup', item.itemtemp)
            item.itemvalueb = data.get('temp', item.itemvalueb)
            item.resvalue = data.get('reserved', item.resvalue)
            item.itemplace = data.get('location', item.itemplace)
            item.orgprice = data.get('originprice', item.orgprice)
            item.orderprice = data.get('buyprice', item.orderprice)
            item.costprice = data.get('expensesprice', item.costprice)
            item.buyprice = data.get('sellprice', item.buyprice)
            item.lessprice = data.get('lessprice', item.lessprice)
            # Continue updating other fields...

            item.save()  # Save the updated record

            return JsonResponse({'success': True})
        except Mainitem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def create_main_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Create a new MainItem instance
        new_item = Mainitem(
            itemno=data.get('originalno'),
            itemmain=data.get('itemmain'),
            itemsubmain=data.get('itemsub'),
            itemname=data.get('pnamearabic'),
            eitemname=data.get('pnameenglish'),
            companyproduct=data.get('company'),
            replaceno=data.get('companyno'),
            pno=data.get('pno'),
            barcodeno=data.get('barcode'),
            memo=data.get('description'),
            itemplace=data.get('location'),
            itemsize=data.get('country'),
            itemperbox=int(data.get('pieces4box', 0)),
            itemthird=data.get('model'),
            itemvalue=int(data.get('storage', 0)),
            itemtemp=int(data.get('backup', 0)),
            itemvalueb=int(data.get('temp', 0)),
            resvalue=int(data.get('reserved', 0)),
            orgprice=float(data.get('originprice', 0)),
            orderprice=float(data.get('buyprice', 0)),
            costprice=float(data.get('expensesprice', 0)),
            buyprice=float(data.get('sellprice', 0)),
            lessprice=float(data.get('lessprice', 0)),
        )
        new_item.save()

        return JsonResponse({'status': 'success', 'message': 'Record created successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

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


def ProductsReports(req):
    company = Companytable.objects.all()
    mainType = Maintypetable.objects.all()
    subType = Subtypetable.objects.all()
    countries = Manufaccountrytable.objects.all()
    models = Modeltable.objects.all()
    columns = [field.name for field in Mainitem._meta.fields]
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
    

    print(columns)  # Debugging to check the contents of columns
    context = {        
        'company': company,
        'columns': columns,
        'mainType': mainType,
        'subType':subType,
        'countries':countries,
        'column_titles': COLUMN_TITLES,
        'column_visibility': column_visibility,
        'models':models
    }
    return render(req, 'products-reports.html', context)


def PartialProductsReports(req):
    users = []  # Fetch users or relevant data from your new model if needed
    context = {'users': users}
    return render(req, 'products-reports.html', context)


def ProductsMovementReport(req):
    company = Companytable.objects.all()
    mainType = Maintypetable.objects.all()
    subType = Subtypetable.objects.all()
    context = {
        'company': company,
        'mainType':mainType,
        'subType':subType
        }
    return render(req, 'products-movement.html', context)





def get_clients(request):
    try:
        # Query the database for all Mainitem entries
        items = Clients.objects.all().values(
            'fileid', 'itemno', 'maintype','itemname','currentbalance','date','clientname','billno','description', 'clientbalance','pno'
        )# List the fields you need
 
        data = list(items)  # Convert QuerySet to a list
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error details in JSON 
    
def get_data(request):
    try:
        # Query the database for all Mainitem entries
        items = Mainitem.objects.all().values(
            'fileid', 'itemno', 'itemmain', 'itemsubmain', 'itemname', 
            'itemthird', 'itemsize', 'companyproduct', 'itemvalue', 
            'itemtemp', 'itemplace', 'buyprice', 'memo', 'replaceno', 
            'barcodeno', 'eitemname', 'currtype', 'lessprice', 'pno', 
            'currvalue', 'itemvalueb', 'costprice', 'resvalue', 'orderprice',
            'levelproduct', 'orderlastdate', 'ordersource', 'orderbillno', 
            'buylastdate', 'buysource', 'buybillno', 'orgprice', 'orderstop', 
            'buystop', 'itemtrans', 'itemtype', 'itemperbox', 'cstate'
        )# List the fields you need
  
        
        data = list(items)  # Convert QuerySet to a list
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error details in JSON

@csrf_exempt  # Disable CSRF validation for this view (use with caution in production)
def update_itemvalue(request):
    if request.method == 'POST':
        try:
            # Get the data from the POST request
            data = json.loads(request.body)
            fileid = data.get('fileid')
            new_itemvalue = data.get('newItemValue')

            # Find the item using the fileid
            item = Mainitem.objects.get(fileid=fileid)
            
            # Update the item value
            item.itemvalue = new_itemvalue
            item.save()

            # Return a successful response
            return JsonResponse({'success': True, 'message': 'Item value updated successfully.'})
        except Mainitem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt  # Disable CSRF validation for this view (use with caution in production)
def update_storage(request):
    if request.method == 'POST':
        try:
            # Get the data from the POST request
            data = json.loads(request.body)
            fileid = data.get('fileid')
            storage = data.get('storage')
            print(fileid)
            print(storage)

            # Find the item using the fileid
            item = Mainitem.objects.get(fileid=fileid)
            
            # Update the item value
            item.itemplace = storage
            item.save()

            # Return a successful response
            return JsonResponse({'success': True, 'message': 'storage updated successfully.'})
        except Mainitem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def ProductsBalance(req):
    company = Companytable.objects.all()
    mainType = Maintypetable.objects.all()
    subType = Subtypetable.objects.all()
    context = {
        'company': company,
        'mainType': mainType,
        'subType': subType,
        }
    return render(req, 'products-balance.html', context)

def ClientsManagement(request):
    types = clientTypes.objects.all().values('fileid', 'tname')
    context = {
        'types': list(types),
    }
    return render(request,'clients-management.html',context)


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
                record = LostAndDamaged.objects.get(fileid=fileid)
                record.delete()
                return JsonResponse({'success': True, 'message': 'Record deleted successfully.'})
            except LostAndDamaged.DoesNotExist:
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
            queryset = LostAndDamaged.objects.all()
            
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
            LostAndDamaged.objects.all().values(
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
from .models import LostAndDamaged

# Set up logging
logger = logging.getLogger(__name__)
@csrf_exempt
def add_lost_damaged(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))
            
            # Print incoming data for debugging
            print("Received data:", data)

            # Extract data from the request
            itemno = data.get('itemno')
            companyno = data.get('companyno')
            company = data.get('company')
            itemname = data.get('itemname')
            costprice = data.get('costprice')
            quantity = data.get('quantity')
            pno_id = data.get('pno')  # Note that we expect an ID, not the instance itself
            status = data.get('status')

            # Validate required fields
            if not all([itemno, companyno, company, itemname, costprice, quantity, pno_id, status]):
                error_message = 'Missing required fields.'
                logger.error(error_message)
                print(error_message)
                return JsonResponse({'success': False, 'message': error_message}, status=400)

            # Attempt to fetch the Mainitem instance for the provided pno_id
            try:
                pno_instance = Mainitem.objects.get(pno=pno_id)
            except Mainitem.DoesNotExist:
                error_message = f'Mainitem with id {pno_id} does not exist.'
                logger.error(error_message)
                print(error_message)
                return JsonResponse({'success': False, 'message': error_message}, status=404)

            # Save the record in the LostAndDamaged model
            lost_damaged_record = LostAndDamaged.objects.create(
                itemno=itemno,
                companyno=companyno,
                company=company,
                itemname=itemname,
                costprice=costprice,
                quantity=quantity,
                pno=pno_instance,  # Use the Mainitem instance, not the ID
                pno_value=pno_instance.pno,  # Save the actual pno value
                status=status
            )

            success_message = 'Record added successfully.'
            logger.info(success_message)
            print(success_message)

            return JsonResponse({'success': True, 'message': success_message})

        except json.JSONDecodeError as e:
            error_message = f'Invalid JSON format: {e}'
            logger.error(error_message)
            print(error_message)
            return JsonResponse({'success': False, 'message': 'Invalid JSON format.'}, status=400)
        
        except Exception as e:
            error_message = f'Unexpected error: {e}'
            logger.error(error_message)
            print(error_message)
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred.'}, status=500)
    
    else:
        error_message = 'Invalid request method. Only POST is allowed.'
        logger.warning(error_message)
        print(error_message)
        return JsonResponse({'success': False, 'message': error_message}, status=405)

def LostDamaged(req):
    company = Companytable.objects.all()
    mainType = Maintypetable.objects.all()
    subType = Subtypetable.objects.all()
    context = {
        'company': company,
        'mainType': mainType,
        'subType': subType,
    }
    return render(req, 'lost-and-damaged.html', context)

def ClientsReports(req):
    types = clientTypes.objects.all()
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
        items = AllClientsTable.objects.all().values(
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
            balance_data = BalanceAndTransactions.objects.filter(client_id_id=clientid).aggregate(
                total_debt=Sum('debt'),
                total_credit=Sum('credit')
            )
            
            total_debt = balance_data.get('total_debt') or 0
            total_credit = balance_data.get('total_credit') or 0
            balance = round(total_credit - total_debt, 2)  # Ensure two decimal digits
            
            # Fetch total credit for specific client_id and where details = "دفعة على حساب"
            specific_credit_data = BalanceAndTransactions.objects.filter(
                client_id_id=clientid, details="دفعة على حساب" 
            ).aggregate(total_specific_credit=Sum('credit'))

            total_specific_credit = specific_credit_data.get('total_specific_credit') or 0

            # Add balance and specific credit to the client's data
            item['balance'] = balance
            item['paid_total'] = total_specific_credit  # Add the total specific credit
            data.append(item)
            

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error details in JSON

def create_client_record(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Create a new MainItem instance
        new_item = AllClientsTable(
            name=data.get('client_name'),
            address=data.get('address'),
            email=data.get('email'),
            website=data.get('website'),
            phone=data.get('phone'),
            mobile=data.get('mobile'),
            last_transaction=data.get('last_transaction'),
            accountcurr=data.get('currency'),
            type=data.get('account_type'),
            category=data.get('sub_category'),
            loan_period=int(data.get('limit', 0)) if data.get('limit') and data.get('limit').isdigit() else None,
            loan_limit = float(data.get('limit_value')) if data.get('limit_value') else None,
            loan_day=data.get('installments'),
            subtype=data.get('types'),
            client_stop = True if data.get('client_stop') in ['on', '1', True] else False,
            curr_flag=bool(int(data.get('curr_flag', 0))),
            permissions=data.get('permissions'),
            other=data.get('other'),
        )
        new_item.save()

        return JsonResponse({'status': 'success', 'message': 'Record created successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def update_client_record(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            # update client instance
            client = AllClientsTable.objects.get(clientid = client_id)

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
            
            client.save()

            return JsonResponse({'status': 'success', 'message': 'Record updated successfully!'})
        
        except AllClientsTable.DoesNotExist:
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
            client = AllClientsTable.objects.get(clientid=client_id)

            # Delete the client record
            client.delete()

            return JsonResponse({'status': 'success', 'message': 'Record deleted successfully!'})

        except AllClientsTable.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Client record not found.'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in request body.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

from django.http import JsonResponse
import json
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Sum

def filter_all_clients(request):
    if request.method == "POST":
        try:
            filters = json.loads(request.body.decode("utf-8"))  # Decode JSON payload

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
                queryset = queryset.filter(subtype__icontains=filters["subtype"])

            # Date range filter
            fromdate = filters.get('fromdate', '').strip()
            todate = filters.get('todate', '').strip()

            if fromdate and todate:
                try:
                    # Parse dates
                    from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                    to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)

                    # Apply date range filter
                    #queryset = queryset.filter(last_transaction__range=[from_date_obj, to_date_obj])
                except ValueError:
                    return JsonResponse({'error': 'Invalid date format'}, status=400)

            # Prepare the data
            clients_data = []
            for client in queryset:
                client_id = client.clientid
                balance_data = BalanceAndTransactions.objects.filter(client_id_id=client_id).aggregate(
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
                    specific_credit_data = BalanceAndTransactions.objects.filter(
                        client_id_id=client_id, details="دفعة على حساب", registration_date__range=[from_date_obj, to_date_obj]
                    ).aggregate(total_specific_credit=Sum('credit'))
                else:
                    # Fetch total credit for specific client_id and where details = "دفعة على حساب"
                    specific_credit_data = BalanceAndTransactions.objects.filter(
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
            print(clients_data)
            return JsonResponse(clients_data, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)


@csrf_exempt
def create_storage_record(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
     
            transaction_date = make_aware(datetime.strptime(data.get("transaction_date"), '%Y-%m-%d'))

            new_record = StorageTransactions(
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
                client = AllClientsTable.objects.filter(name=data.get("for_who")).first()
                if not client:
                    error_msg = f"Client '{data.get('for_who')}' not found"
                    print("Client Error:", error_msg)
                    return JsonResponse({"error": error_msg}, status=400)
                client_id = client.clientid

            last_balance = (
                BalanceAndTransactions.objects.filter(client_id_id=client_id)
                .order_by("-registration_date")
                .first()
            )
            last_balance_amount = last_balance.current_balance if last_balance else 0
            updated_balance =  round(last_balance_amount + data.get("amount"), 2)

            # Create a new `BalanceAndTransactions` record
            account_statement = BalanceAndTransactions(
                credit=float(data.get("amount")),
                debt=0.0,
                transaction=data.get("section"),
                details=f"{data.get('subsection')} / {data.get('reciept_no')}",
                registration_date=transaction_date,
                current_balance=updated_balance,  # Updated balance
                client_id_id=client_id,  # Client ID
            )
            account_statement.save()
            print(f"statement >>> {account_statement}")

            return JsonResponse({"message": "Record created successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def delete_storage_record(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            storage_id = data.get("storage_id")
            record = get_object_or_404(StorageTransactions, storageid=storage_id)
            record.delete()
            return JsonResponse({"message": "Record deleted successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

def get_all_storage(request):
    try:
        # Query the database for all Mainitem entries
        items = StorageTransactions.objects.all().values(
            'storageid', 'account_type', 'transaction','transaction_date'
            ,'reciept_no','place','section','subsection','person', 'amount'
            ,'issued_for','payment','done_by','bank','check_no','daily_status'
        )# List the fields you need
 
        data = list(items)  # Convert QuerySet to a list
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error details in JSON 
    

def filter_all_storage(request):
    if request.method == "POST":
        try:
            filters = json.loads(request.body.decode("utf-8"))  # Decode JSON payload
            print(filters)
            # Default query
            queryset = StorageTransactions.objects.all()

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
    records = BalanceAndTransactions.objects.filter(client_id_id=client_id)
    client = AllClientsTable.objects.get(clientid=client_id)
    context = {
        'records':records,
        'client':client,
    }
    return render(request,'account-statement.html',context)      

def get_last_reciept_no(request):
    transaction_type = request.GET.get('transactionType')  # Get the transaction type from the query parameter
    print(f"type: {transaction_type}")

    if transaction_type in ['ايداع', 'صرف']:
        # Cast `reciept_no` to an integer for proper ordering
        last_transaction = StorageTransactions.objects.annotate(
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
        last_invoice = BuyInvoiceTable.objects.order_by('-invoice_no').first()
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
         # Query BalanceAndTransactions with selected fields
        items = BalanceAndTransactions.objects.filter(client_id_id=client_id).values(
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
    company = Companytable.objects.all()
    mainType = Maintypetable.objects.all()
    subType = Subtypetable.objects.all()
    model = Modeltable.objects.all()
    country = Manufaccountrytable.objects.all()
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
def fetch_invoice_items(request):
    if request.method == "GET":
        invoice_no = request.GET.get("id")

        if not invoice_no:
            return JsonResponse({"error": "Invoice number is required."}, status=400)


        # Fetch all data from the model
        items = list(
            BuyInvoiceItems.objects.filter(invoice_no2= invoice_no).values(
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
            )
        )
        if not items:
            return JsonResponse({"message": "No items found for the given invoice number."}, status=404)

        return JsonResponse(items, safe=False)
    else:
        return JsonResponse({"error": "Invalid HTTP method."}, status=405)
@csrf_exempt
def cost_management(request):
    if request.method == "POST":
        try:
            # Parse the JSON data sent by the frontend
            data = json.loads(request.body)
            print(data)
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
            invoice = BuyInvoiceTable.objects.get(invoice_no=invoice_no)

        except BuyInvoiceTable.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invoice not found in the database"}, status=404)
        
        dinar_total = Decimal(invoice.amount)*Decimal(invoice.exchange_rate)
        costs = cost_types.objects.all()
        context = {
            "invoice_no": invoice_no,
            "org_total": round(invoice.amount, 2),
            "rate": round(invoice.exchange_rate,2),
            "currency":invoice.currency,
            "dinar_total": round(dinar_total,2),
            "costs": costs,
        }
        
        return render(request, "cost-management.html", context)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

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
            
            invoice_obj = BuyInvoiceTable.objects.get(invoice_no=invoice)
            # Validate the data
            if not invoice or not type or not cost or not rate or not dinar:
                return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

            # Create a new record in the CostType model
            cost_record = buyInvoice_costs.objects.create(
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

csrf_exempt
def fetch_costs(request):
    if request.method == "GET":
        invoice_no = request.GET.get("id")

        if not invoice_no:
            return JsonResponse({"error": "Invoice number is required."}, status=400)


        # Fetch all data from the model
        items = list(
            buyInvoice_costs.objects.filter(invoice_no= invoice_no).values(
                "autoid",
                "invoice_no",
                "cost_for",
                "cost_price",
                "exchange_rate",
                "dinar_cost_price",
                
            )
        )
        if not items:
            return JsonResponse({"message": "No items found for the given invoice number."}, status=404)

        return JsonResponse(items, safe=False)
    else:
        return JsonResponse({"error": "Invalid HTTP method."}, status=405)




def payment_installments(request):
    return render(request,'payment.installments.html')


@csrf_exempt    
def calculate_cost(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            cost_total = data.get("cost_total")
            invoice_total = data.get("invoice_total")
            invoice_id = data.get("invoice")

            # Validate the data
            if not cost_total or not invoice_total or not invoice_id:
                return JsonResponse({"success": False, "message": "Missing required fields."}, status=400)

            # Calculate the load percentage
            load_percentage = Decimal(cost_total) / Decimal(invoice_total)

            # Get the invoice object
            try:
                invoice = BuyInvoiceTable.objects.get(invoice_no=invoice_id)
            except BuyInvoiceTable.DoesNotExist:
                return JsonResponse({"success": False, "message": "Invoice not found."}, status=404)

            # Update the items associated with the invoice
            items = BuyInvoiceItems.objects.filter(invoice_no2=invoice_id)
            for item in items:
                # Update the costprice based on the load percentage
                item.current_cost_price = item.dinar_unit_price * (1 + load_percentage)
                item.cost_unit_price = item.dinar_unit_price * (1 + load_percentage)
                item.cost_total_price= (item.dinar_unit_price * (1 + load_percentage))*item.quantity
                print(f"order {item.dinar_unit_price} , cost {item.current_cost_price}")
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

        items = BuyInvoiceItems.objects.filter(invoice_no = invoice_id)
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
            print(data)
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
            print(data)
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

    item = BuyInvoiceItems.objects.get(autoid=auto_id)

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
            item = BuyInvoiceItems.objects.get(autoid=item_id)  # Adjust the query based on your model
            item.delete()

            # Return success response
            return JsonResponse({"success": True, "message": "Item deleted successfully!"}, status=200)

        except BuyInvoiceItems.DoesNotExist:
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
            item = BuyInvoiceItems.objects.get(autoid=id)

              # Get the related invoice
            try:
                invoice = BuyInvoiceTable.objects.get(invoice_no=invoice_no)
                invoice.amount -= item.dinar_total_price
                invoice.amount += order * quantity

                invoice.save()
            except BuyInvoiceTable.DoesNotExist:
                return JsonResponse({"error": "Invoice not found"}, status=404)
            
            # Update the item with new values
            item.org_unit_price = org
            item.dinar_unit_price = order
            item.org_total_price = org * quantity
            item.dinar_total_price = order * quantity
            item.quantity = quantity
            item.save()

            return JsonResponse({"success": True, "message": "Item updated successfully"})

        except BuyInvoiceItems.DoesNotExist:
            return JsonResponse({"success": False, "message": "Item not found"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"})


def buyInvoice_excell(request):
    if request.method == "POST":
        try:
            # Parse the JSON data sent by the frontend
            data = json.loads(request.body)
            print(data)
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
            invoice = BuyInvoiceTable.objects.get(invoice_no=invoice_no)

        except BuyInvoiceTable.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invoice not found in the database"}, status=404)
        
        context = {
            "invoice_no": invoice_no,
            "org":org,
        }
        
        return render(request, "buy-invoice-excell.html", context)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)
import logging

logger = logging.getLogger(__name__)
import json
import datetime

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
            print(body)
            data = json.loads(body['data'])  # Parse the 'data' stringified JSON
            invoice_no = body.get('invoice_no')
            

            if not invoice_no:
                return JsonResponse({"status": "error", "message": "Invoice number is required."})

            # Now you have 'data' as a Python object (list of dictionaries)
            logger.debug(f"Received data: {data}")

            try:
                # Attempt to retrieve the invoice from the database
                invoice = BuyInvoiceTable.objects.get(invoice_no=invoice_no)
            except BuyInvoiceTable.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Invoice not found in the database."}, status=404)

            # Process the data and insert it into the database
            records = []
            for item in data:
                try:
                    records.append(BuyInvoiceItems(
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
                        Mainitem.objects.create(
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
            BuyInvoiceItems.objects.bulk_create(records)
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
            print(data)

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
                exists = Mainitem.objects.filter(replaceno=company_no).exists()
                results.append({"company_no": company_no, "exists": 1 if exists else 0})

            return JsonResponse({"status": "success", "results": results})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)
    
def temp_confirm(request):
    invoices = BuyInvoiceTable.objects.filter(temp_flag=1)
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
            print(data)
            invoice_no = data.get('invoice_no')

            if not invoice_no:
                return JsonResponse({'status': 'error', 'message': 'Invoice number is required.'}, status=400)
            
            try:
                # Fetch invoice items for the given invoice number
                invoice_items = BuyInvoiceItems.objects.filter(invoice_no=invoice_no)
            except BuyInvoiceItems.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invoice not found in the BuyInvoiceTable.'}, status=404)
            
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

            # Fetch the invoice details from the BuyInvoiceTable
            try:
                invoice = BuyInvoiceTable.objects.get(autoid=invoice_no)
                
                # Prepare invoice details for response
                invoice_details = {
                    'original': invoice.original_no,
                    'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else None,
                    'arrive_date': invoice.arrive_date.strftime('%Y-%m-%d')if invoice.arrive_date else None,
                    'source': invoice.source,
                    'invoice_items': items_data,  # Attach serialized invoice items
                }

                return JsonResponse({'status': 'success', 'message': 'Invoice details fetched successfully.', 'data': invoice_details})

            except BuyInvoiceTable.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invoice not found in the BuyInvoiceTable.'}, status=404)

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
            print(data)
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
                    main = Mainitem.objects.get(replaceno=item['company_no'])
                    print(f"old data: {main.itemname} {main.itemvalue} {main.orderprice} {main.costprice} {main.orgprice} {main.itemno}")

                    # Update fields
                    main.itemname = item['name']
                    main.itemvalue += int(item['quantity'] or 0)
                    main.orderprice = Decimal(item['dinar_unit_price'] or 0)
                    main.costprice = (main.costprice + Decimal(item['cost_unit_price'] or 0)) / 2
                    main.orgprice = Decimal(item['org_unit_price'] or 0)
                    main.itemno = item['item_no']
                    main.save()

                    print(f"new data: {main.itemname} {main.itemvalue} {main.orderprice} {main.costprice} {main.orgprice} {main.itemno}")
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

            # Process BuyInvoiceTable update
            try:
                invoice = BuyInvoiceTable.objects.get(autoid=invoice_no)
                invoice.temp_flag = 0
                invoice.save()
            except BuyInvoiceTable.DoesNotExist:
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
            print(data)

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
                invoice = BuyInvoiceTable.objects.get(invoice_no=data.get("invoice_id"))
                invoice.amount += (Decimal(data.get("orderprice") or 0) * Decimal(data.get("itemvalue") or 0))
                invoice.save()
            except BuyInvoiceTable.DoesNotExist:
                return JsonResponse({"error": "Invoice not found"}, status=404)
            
            try:
                product = Mainitem.objects.get(pno=data.get("pno"))
                submain = product.itemsubmain if product.itemsubmain else None
            except Mainitem.DoesNotExist:
                return JsonResponse({"error": "product not found"}, status=404)
            
            # Create a new BuyInvoiceItems instance
            item = BuyInvoiceItems.objects.create(
                invoice_no=invoice,
                invoice_no2=data.get("invoice_id"),
                item_no=data.get("itemno"),
                pno=data.get("pno"),
                main_cat= data.get("main_cat"),
                sub_cat=submain,
                name=data.get("itemname"),
                company=data.get("companyproduct"),
                company_no=data.get("replaceno"),
                quantity=int(data.get("itemvalue") or 0),  # Use `or 0` to handle None
                currency=data.get("currency"),
                exchange_rate=float(data.get("rate") or 0),  # Use `or 0` to handle None
                date=data.get("date"),
                place=data.get("itemplace"),
                buysource=data.get("source"),
                org_unit_price=float(data.get("orgprice") or 0),  # Use `or 0` to handle None
                org_total_price=(float(data.get("orgprice") or 0) * int(data.get("itemvalue") or 0)),  # Handle None
                dinar_unit_price=float(data.get("orderprice") or 0),  # Use `or 0` to handle None
                dinar_total_price=(float(data.get("orderprice") or 0) * int(data.get("itemvalue") or 0)),  # Handle None
                prev_quantity=int(data.get("prev_quantity") or 0),  # Use `or 0` to handle None
                prev_cost_price=float(data.get("prev_cost_price") or 0),  # Use `or 0` to handle None
                prev_buy_price=float(data.get("prev_buy_price") or 0),  # Use `or 0` to handle None
                prev_less_price=float(data.get("prev_less_price") or 0),  # Use `or 0` to handle None
                current_quantity=int(data.get("prev_quantity") or 0) + int(data.get("itemvalue") or 0),  # Handle None
                current_buy_price=float(data.get("buyprice") or 0),  # Use `or 0` to handle None
                current_less_price=float(data.get("lessprice") or 0), 
            )
            confirm_message = "not confirmed"
            if(data.get("isTemp")==0):
                main = Mainitem.objects.get(replaceno=data.get("replaceno"))
                print(f"old data: {main.orgprice} / {main.lessprice} /{main.itemvalue} /{main.itemtemp} /{main.itemplace} /{main.buyprice} /")
                main.orgprice = float(data.get("orgprice") or 0)
                main.lessprice=float(data.get("lessprice") or 0)
                main.itemvalue+= int(data.get("itemvalue") or 0)
                main.itemtemp -= int(data.get("itemvalue") or 0)
                main.itemplace= data.get("itemplace") 
                main.buyprice=float(data.get("buyprice") or 0)
                main.save()
                confirm_message = "confirmed"
                print(f"new data: {main.orgprice} / {main.lessprice} /{main.itemvalue} /{main.itemtemp} /{main.itemplace} /{main.buyprice} /")
            # Return success response
            return JsonResponse({"message": "Item created successfully", "item_id": item.autoid,"confirm_status":confirm_message}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid HTTP method. Use POST."}, status=405)