from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status

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
    
def item_filter_page(request):
    return render(request, 'CarPartsTemplates/items_page.html')

def CarParts_page(request):
    return render(request, 'CarPartsTemplates/Brands.html')

def CarPartsHome_page(request):
    return render(request, 'CarPartsTemplates/index.html')

def Dashbord_page(request):
    return render(request, 'CarPartsTemplates/Dashboard.html')

def Cart_page(request):
    return render(request, 'CarPartsTemplates/Cart.html')

def my_account(request):
    return render(request, 'CarPartsTemplates/my_account.html')

def track_order(request):
    return render(request, 'CarPartsTemplates/track_order.html')

def return_policy(request):
    return render(request, 'CarPartsTemplates/return_policy.html')

def faq(request):
    return render(request, 'CarPartsTemplates/faq.html')

def terms_conditions(request):
    return render(request, 'CarPartsTemplates/terms_conditions.html')


def dashboard(request):
    return render(request, 'CarPartsTemplates/preorder-dashboard.html')  # This will render the dashboard page

def preorder_detail(request, invoice_no):
    return render(request, 'CarPartsTemplates/preorder-detail.html', {'invoice_no': invoice_no})  # This will render the PreOrder details page



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

def preorder_buy_detail(request, invoice_no):
  return render(request, 'CarPartsTemplates/show_preordersBuyDetails.html', {'invoice_no': invoice_no})  # This will render the PreOrder details page



def preorders_buy_page(request):
    return render(request, 'CarPartsTemplates/show_preordersBuy.html')


class MainitemViewSet(viewsets.ModelViewSet):
    queryset = almogOil_models.Mainitem.objects.all()
    serializer_class = products_serializers.MainitemSerializer

    def perform_create(self, serializer):
        # Here you can customize or log the creation process if needed
        serializer.save()

    def perform_update(self, serializer):
        # Here you can customize or log the update process if needed
        serializer.save()



def mainitem_create_page(request, clientid):
    return render(request, 'CarPartsTemplates/source/mainitem_create.html')         


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



def source_dashboard(request):
    return render(request, 'CarPartsTemplates/source/edit-source.html')