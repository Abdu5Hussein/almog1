from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib import messages
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
from .forms import ReturnPolicyForm ,TermsAndConditionsForm
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
from almogOil import models as almogOil_models
from wholesale_app import models as hozma_models
from almogOil import serializers as almogOil_serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from products import serializers as products_serializers



from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema_view,extend_schema,OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes, OpenApiSchemaBase



# for hozma
@login_required
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
@login_required   
def item_filter_page(request):
    return render(request, 'CarPartsTemplates/items_page.html')
@login_required
def CarParts_page(request):
    return render(request, 'CarPartsTemplates/Brands.html')
@login_required
def CarPartsHome_page(request):
    return render(request, 'CarPartsTemplates/index.html')
@login_required
def Dashbord_page(request):
    return render(request, 'CarPartsTemplates/Dashboard.html')
@login_required
def Cart_page(request):
    return render(request, 'CarPartsTemplates/Cart.html')
@login_required
def my_account(request):
    return render(request, 'CarPartsTemplates/my_account.html')
@login_required
def track_order(request):
    return render(request, 'CarPartsTemplates/track_order.html')
@login_required
def contact(request):
    return render(request, 'CarPartsTemplates/contact.html')
@login_required
def return_policy(request):

     # Get the active return policy or create a default one if none exists
    policy = almogOil_models.ReturnPolicy.objects.filter(is_active=True).first()
    
    if not policy:
        # Create a default policy if none exists
        policy = almogOil_models.ReturnPolicy.objects.create(
            title="سياسة الإرجاع والاستبدال",
            overview="نسعى لتوفير تجربة تسوق مرضية لجميع عملائنا",
            general_conditions="الشروط العامة للإرجاع...",
            non_returnable_items="المنتجات غير القابلة للإرجاع...",
            return_steps="خطوات إرجاع المنتج...",
            refund_policy="المبالغ المستردة...",
            exchange_policy="سياسة الاستبدال...",
            warranty_info="الضمانات...",
            contact_info="هل لديك استفسارات حول إرجاع منتج؟...",
            is_active=True
        )
    return render(request, 'CarPartsTemplates/return_policy.html', {'policy': policy})

@login_required
def edit_return_policy(request):
    return render(request, 'CarPartsTemplates/edit_return_policy.html')

@login_required
def faq(request):
    categories = almogOil_models.FAQ.CATEGORY_CHOICES                     # [(value, label), ...]
    
    # تجميع الأسئلة في قاموس {category_value: [faq, faq, ...]}
    grouped = {key: [] for key, _ in categories}
    for f in almogOil_models.FAQ.objects.all().order_by('created_at'):
        grouped[f.category].append(f)

    context = {
        'categories':     categories,
        'grouped_faqs':   grouped,
        'icon_map':       ICON_MAP,      # ← ليظهر رمز كلّ تصنيف
    }
    return render(request, 'CarPartsTemplates/faq.html', context)
@login_required
def faq_delete(request, faq_id):
    faq = get_object_or_404(almogOil_models.FAQ, id=faq_id)
    faq.delete()
    return redirect('wholesale_app:faq_edit')


# لو لديك حقل choices في الموديل
CATEGORY_CHOICES = almogOil_models.FAQ.CATEGORY_CHOICES      # [(value, label), …]
ICON_MAP = {                # إذا أردت أيقونات لكل تصنيف
    'orders':   'truck',
    'returns':  'arrow-left-right',
    'products': 'box',
    'payments': 'credit-card',
}
@login_required
def faq_edit(request):
    if request.method == 'POST':
        qid      = request.POST.get('id') or None
        question = request.POST['question']
        answer   = request.POST['answer']
        category = request.POST['category']

        if qid:                         # تعديل
            try:
                faq = almogOil_models.FAQ.objects.get(pk=qid)
                faq.question, faq.answer, faq.category = question, answer, category
                faq.save()
                messages.success(request, 'تم تحديث السؤال بنجاح')
            except almogOil_models.FAQ.DoesNotExist:
                messages.error(request, 'السؤال غير موجود')
        else:                           # إضافة
            almogOil_models.FAQ.objects.create(question=question, answer=answer, category=category)
            messages.success(request, 'تمت إضافة السؤال بنجاح')

        return redirect('wholesale_app:faq_edit')

    # GET
    faqs = almogOil_models.FAQ.objects.all().order_by('category', 'question')
    context = {
        'faqs': faqs,
        'categories': CATEGORY_CHOICES,
        'icon_map': ICON_MAP,
    }
    return render(request, 'CarPartsTemplates/faq_edit.html', context)
@login_required
def terms_conditions(request):
    terms = almogOil_models.TermsAndConditions.objects.filter(is_active=True).first()
    
    if not terms:
        # Create default terms with 11 sections
        default_sections = [
            {"title": "1. المقدمة والقبول", "content": "مرحباً بكم في موقع حزمة (hozma.ly)..."},
            {"title": "2. تعريفات", "content": "في هذه الوثيقة، المصطلحات التالية لها المعاني..."},
            # Add more default sections as needed
        ]
        terms = almogOil_models.TermsAndConditions.objects.create(
            title="الشروط والأحكام",
            introduction="مرحباً بكم في موقع حزمة (hozma.ly)...",
            acceptance_text="باستخدام هذا الموقع أو إجراء أي عمليات شراء...",
            contact_info="فريق الدعم القانوني لدينا مستعد للإجابة على جميع استفساراتكم",
            sections=default_sections,
            is_active=True
        )
    
    return render(request, 'CarPartsTemplates/terms_conditions.html', {'terms': terms})


@login_required
def edit_terms_and_conditions(request):
    return render(request, "CarPartsTemplates/edit_terms_and_conditions.html")
@login_required
def dashboard(request):
    return render(request, 'CarPartsTemplates/preorder-dashboard.html') 
@login_required
def order_view(request):
    return render(request, 'CarPartsTemplates/order.html') 
@login_required
def preorder_detail(request, invoice_no):
    return render(request, 'CarPartsTemplates/preorder-detail.html', {'invoice_no': invoice_no})  # This will render the PreOrder details page
@login_required
def invoice(request, invoice_no):
    context = {
        'invoice_no': invoice_no
    }
    return render(request, 'CarPartsTemplates/invoice.html', context)
@login_required
def Buyinvoice_management(request):
    #records = models.Buyinvoicetable.objects.all().values()
    #total_amount = models.Buyinvoicetable.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    #json_data = json.dumps(list(records), default=str)
    sources = almogOil_models.AllSourcesTable.objects.all().values('clientid','name')
    context = {
        "sources":sources,
        #"data":json_data,
        #"total_amount":total_amount,
    }
    return render(request,"buy-invoice-reports.html",context)
@login_required
def preorder_buy_detail(request, invoice_no):
  return render(request, 'CarPartsTemplates/show_preordersBuyDetails.html', {'invoice_no': invoice_no})  # This will render the PreOrder details page


@login_required
def preorders_buy_page(request):
    return render(request, 'CarPartsTemplates/show_preordersBuy.html')

@login_required
def Admin_Dashboard(request):
    return render(request, 'CarPartsTemplates/e-commerce admin panel.html')
@login_required
def Item_Dashboard(request):
    return render(request, 'CarPartsTemplates/Hozma_Item_Mangment.html')

class MainitemViewSet(viewsets.ModelViewSet):
    queryset = almogOil_models.Mainitem.objects.all()
    serializer_class = products_serializers.MainitemSerializer

    def perform_create(self, serializer):
        # Here you can customize or log the creation process if needed
        serializer.save()

    def perform_update(self, serializer):
        # Here you can customize or log the update process if needed
        serializer.save()


@login_required
def mainitem_create_page(request, clientid):
    return render(request, 'CarPartsTemplates/source/mainitem_create.html')         

@login_required
def source_register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        # Check if username already exists
        if almogOil_models.AllSourcesTable.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'source_register.html')

        # Create the source user
        almogOil_models.AllSourcesTable.objects.create(
            username=username,
            password=make_password(password),
            name=name,
            email=email,
            mobile=mobile,
            type='source'
        )
        messages.success(request, 'Source user registered successfully!')
        return redirect('source-register')  # Reload the form or redirect elsewhere

    return render(request, 'CarPartsTemplates/source/source_register.html')


@login_required
def source_dashboard(request):
    return render(request, 'CarPartsTemplates/source/edit-source.html')
@login_required
def edit_dashboard(request):
    return render(request, 'CarPartsTemplates/edit_dashboard.html')

@login_required
def Settings(request):
    return render(request, 'CarPartsTemplates/Settings.html')

@login_required
def uploadimages(request):
    return render(request, 'CarPartsTemplates/source/images_uploaders.html')


@login_required
def hozmaclient(request):
    return render(request, 'CarPartsTemplates/hozmaclient.html')


