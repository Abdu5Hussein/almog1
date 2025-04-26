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