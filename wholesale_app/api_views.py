from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from almogOil.authentication import CookieAuthentication
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_200_OK
from rest_framework import status
from decimal import Decimal
from almogOil import models as almogOil_models
from wholesale_app import models as hozma_models
from wholesale_app import serializers as wholesale_serializers
from almogOil import serializers as almogOil_serializers
from products import serializers as products_serializers
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema_view,extend_schema,OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes, OpenApiSchemaBase
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(["GET"])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def item_detail_view(request, pno):
    item = get_object_or_404(almogOil_models.Mainitem, pno=pno)
    context = {
        'itemmain': item.itemmain,
        'itemsubmain': item.itemsubmain,
        'itemname': item.itemname,
        'itemthird': item.itemthird,
        'itemsize': item.itemsize,
        'companyproduct': item.companyproduct,
        'buyprice': item.buyprice,
        'memo': item.memo,
        'json_description': item.json_description,
        'engine_no': item.engine_no,
        'pno': item.pno,
        'itemvalue':item.itemvalue,
    }
    return render(request, 'CarPartsTemplates/item_detail.html', context)


@api_view(["GET"])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def get_employee_details(request, employee_id):
    try:
        employee = almogOil_models.EmployeesTable.objects.get(employee_id=employee_id)
        data = {
            'employee_id': employee.employee_id,
            'name': employee.name,
            'identity_doc': employee.identity_doc,
            'nationality': employee.nationality,
            'last_transaction': employee.last_transaction,
            'salary': str(employee.salary),
            'start_date': employee.start_date,
            'end_date': employee.end_date,
            'daily_start_time': employee.daily_start_time,
            'daily_end_time': employee.daily_end_time,
            'active': employee.active,
            'category': employee.category,
            'notes': employee.notes,
            'phone': employee.phone,
            'address': employee.address,
            'bank_details': employee.bank_details,
            'bank_account_no': employee.bank_account_no,
            'bank_iban_no': employee.bank_iban_no,
            'is_available': employee.is_available,
            'has_active_order': employee.has_active_order,
            'fcm_token': employee.fcm_token,
        }
        return Response(data)
    except almogOil_models.EmployeesTable.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

import logging

# Create a logger
logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def item_detail_view(request, pno):
    try:
        item = get_object_or_404(almogOil_models.Mainitem, pno=pno)
        context = {
            'itemmain': item.itemmain,
            'itemsubmain': item.itemsubmain,
            'itemname': item.itemname,
            'itemthird': item.itemthird,
            'itemsize': item.itemsize,
            'companyproduct': item.companyproduct,
            'buyprice': item.buyprice,
            'memo': item.memo,
            'json_description': item.json_description,
            'engine_no': item.engine_no,
            'pno': item.pno,
            'itemvalue':item.itemvalue,
        }
        logger.info(f"Item detail view accessed for item {pno}")
        return render(request, 'CarPartsTemplates/item_detail.html', context)
    except Exception as e:
        logger.error(f"Error accessing item detail view for item {pno}: {str(e)}")
        return render(request, 'CarPartsTemplates/item_detail.html', {})

@api_view(["GET"])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def get_employee_details(request, employee_id):
    try:
        employee = almogOil_models.EmployeesTable.objects.get(employee_id=employee_id)
        data = {
            'employee_id': employee.employee_id,
            'name': employee.name,
            'identity_doc': employee.identity_doc,
            'nationality': employee.nationality,
            'last_transaction': employee.last_transaction,
            'salary': str(employee.salary),
            'start_date': employee.start_date,
            'end_date': employee.end_date,
            'daily_start_time': employee.daily_start_time,
            'daily_end_time': employee.daily_end_time,
            'active': employee.active,
            'category': employee.category,
            'notes': employee.notes,
            'phone': employee.phone,
            'address': employee.address,
            'bank_details': employee.bank_details,
            'bank_account_no': employee.bank_account_no,
            'bank_iban_no': employee.bank_iban_no,
            'is_available': employee.is_available,
            'has_active_order': employee.has_active_order,
            'fcm_token': employee.fcm_token,
        }
        logger.info(f"Employee details accessed for employee {employee_id}")
        return Response(data)
    except almogOil_models.EmployeesTable.DoesNotExist:
        logger.error(f"Employee not found for employee {employee_id}")
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error accessing employee details for employee {employee_id}: {str(e)}")
        return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def brand_items(request, brand):
    try:
        items = almogOil_models.Mainitem.objects.filter(itemmain=brand)
        logger.info(f"Brand items accessed for brand {brand}")
        return render(request, 'CarPartsTemplates/brand-item.html', {'items': items, 'brand': brand})
    except Exception as e:
        logger.error(f"Error accessing brand items for brand {brand}: {str(e)}")
        return render(request, 'CarPartsTemplates/brand-item.html', {})
@api_view(["GET"])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def brand_items(request, brand):
    items = almogOil_models.Mainitem.objects.filter(itemmain=brand)
    return render(request, 'CarPartsTemplates/brand-item.html', {'items': items, 'brand': brand})



# Create your views here.
@api_view(["GET"])
@authentication_classes([CookieAuthentication])
@permission_classes([IsAuthenticated])
def get_product_images(request, id):
    try:
        product = almogOil_models.Mainitem.objects.get(pno=id)
    except almogOil_models.Mainitem.DoesNotExist:
        return Response({"error": "Product not found!"}, status=404)  # Added return and status

    images = almogOil_models.Imagetable.objects.filter(productid=product.fileid)  # Ensure `productid` is correct
    serializer = products_serializers.productImageSerializer(images, many=True)

    return Response(serializer.data)  # Added return statement

@api_view(["GET"])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def show_all_preorders(request):
    # Filter PreOrderTable for invoices where shop_confirm is False
    preorders = almogOil_models.PreOrderTable.objects.filter(shop_confrim=False)

    # Filter PreOrderItemsTable based on the related PreOrderTable invoice_no
    preorder_items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance__shop_confrim=False)

    # Serialize the data
    preorder_serializer = wholesale_serializers.PreOrderTableSerializer(preorders, many=True)
    preorder_items_serializer = wholesale_serializers.PreOrderItemsTableSerializer(preorder_items, many=True)

    # Return the response
    return Response({
        'preorders': preorder_serializer.data,
        'preorder_items': preorder_items_serializer.data
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def show_preorders(request):
    invoice_no = request.query_params.get('invoice_no')  # Get the invoice_no from query params
    
    if invoice_no:
        # Filter only by invoice_no
        preorders = almogOil_models.PreOrderTable.objects.filter(invoice_no=invoice_no)
        preorder_items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance__invoice_no=invoice_no)
    else:
        # Fetch all preorders and preorder items
        preorders = almogOil_models.PreOrderTable.objects.all()
        preorder_items = almogOil_models.PreOrderItemsTable.objects.all()
    
    preorder_serializer = wholesale_serializers.PreOrderTableSerializer(preorders, many=True)
    preorder_items_serializer = wholesale_serializers.PreOrderItemsTableSerializer(preorder_items, many=True)
    
    return Response({
        'preorders': preorder_serializer.data,
        'preorder_items': preorder_items_serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def show_preorders_v2(request):
    # Get filters from request data
    data = request.data
    page = int(data.get('page', 1))
    page_size = int(data.get('page_size', 10))
    sort_by = data.get('sort_by', 'date_desc')  # Options: date_desc, date_asc, amount_desc, amount_asc, confirm_first, pending_first
    status_filter = data.get('status_filter', 'all')  # confirmed, pending, all
    date_filter = data.get('date_filter', 'all')  # today, week, month, all

    queryset = almogOil_models.PreOrderTable.objects.all()

    # Apply status filter
    if status_filter == 'confirmed':
        queryset = queryset.filter(shop_confrim=True)
    elif status_filter == 'pending':
        queryset = queryset.filter(shop_confrim=False)

    # Apply date filter
    if date_filter == 'today':
        today = now().replace(hour=0, minute=0, second=0, microsecond=0)
        queryset = queryset.filter(date_time__gte=today)
    elif date_filter == 'week':
        start_of_week = now() - timedelta(days=now().weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        queryset = queryset.filter(date_time__gte=start_of_week)
    elif date_filter == 'month':
        start_of_month = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        queryset = queryset.filter(date_time__gte=start_of_month)

    # Apply sorting
    if sort_by == 'date_desc':
        queryset = queryset.order_by('-date_time')
    elif sort_by == 'date_asc':
        queryset = queryset.order_by('date_time')
    elif sort_by == 'amount_desc':
        queryset = queryset.order_by('-amount')
    elif sort_by == 'amount_asc':
        queryset = queryset.order_by('amount')
    elif sort_by == 'confirm_first':
        queryset = queryset.order_by('-shop_confrim')
    elif sort_by == 'pending_first':
        queryset = queryset.order_by('shop_confrim')

    # Summary stats (before pagination)
    total_count = queryset.count()
    confirmed_count = queryset.filter(shop_confrim=True).count()
    pending_count = total_count - confirmed_count

    # Pagination
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    serializer = wholesale_serializers.PreOrderTableSerializer(page_obj, many=True)

    return Response({
        'preorders': serializer.data,
        'summary': {
            'total_orders': total_count,
            'confirmed_orders': confirmed_count,
            'pending_orders': pending_count
        },
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
@authentication_classes([CookieAuthentication])
def Hozma_Login(request):
    try:
        if request.method == "POST":
            # Parse JSON request body
            body = json.loads(request.body)

            # Extract fields
            username = body.get("username")
            password = body.get("password")
            role = body.get("role")

            if not username or not password or not role:
                return Response({"error": "[username, password, role] fields are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Authenticate the user based on the role
            user = None
            user_id = None
            if role == "client":
                try:
                    user = almogOil_models.AllClientsTable.objects.get(phone=username)
                    user_id = f"e-{user.clientid}"
                except almogOil_models.AllClientsTable.DoesNotExist:
                    return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

            # Authenticate against the main User model
            auth_user = authenticate(username=username, password=password)

            if auth_user is None:
                return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

            # If authentication successful, login the user (create session)
            login(request, auth_user)

            # Store session variables
            request.session["username"] = user.username
            request.session["name"] = user.name
            request.session["role"] = role  # Store role for later use
            request.session["user_id"] = user_id
            request.session["is_authenticated"] = True  # Useful for templates
            request.session.set_expiry(3600)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(auth_user)
            access_token = str(refresh.access_token)

            # Create the response object
            response = Response({
                "message": "Signed in successfully",
                "role": role,
                "emp_id": user_id,
                "user_id": auth_user.id,
                "access_token": access_token,
                "refresh_token": str(refresh),
            })

            # Set the access token cookie (15 minutes expiry)
            response.set_cookie(
                'access_token', access_token,
                httponly=True,
                max_age=7*60*60,  # 7 hours
                path='/'
            )

            # Set the refresh token cookie (7 days expiry)
            response.set_cookie(
                'refresh_token', str(refresh),
                httponly=True,
                max_age=7*24*60*60,  # 7 days
                path='/'
            )

            return response

    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
