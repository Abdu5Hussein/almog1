from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
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
from rest_framework.decorators import api_view, permission_classes


@api_view(["GET"])
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


@api_view(['GET'])
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

@api_view(['GET'])
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

@api_view(['GET'])
def brand_items(request, brand):
    try:
        items = almogOil_models.Mainitem.objects.filter(itemmain=brand)
        logger.info(f"Brand items accessed for brand {brand}")
        return render(request, 'CarPartsTemplates/brand-item.html', {'items': items, 'brand': brand})
    except Exception as e:
        logger.error(f"Error accessing brand items for brand {brand}: {str(e)}")
        return render(request, 'CarPartsTemplates/brand-item.html', {})
@api_view(['GET'])
def brand_items(request, brand):
    items = almogOil_models.Mainitem.objects.filter(itemmain=brand)
    return render(request, 'CarPartsTemplates/brand-item.html', {'items': items, 'brand': brand})



# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_images(request, id):
    try:
        product = almogOil_models.Mainitem.objects.get(pno=id)
    except almogOil_models.Mainitem.DoesNotExist:
        return Response({"error": "Product not found!"}, status=404)  # Added return and status

    images = almogOil_models.Imagetable.objects.filter(productid=product.fileid)  # Ensure `productid` is correct
    serializer = products_serializers.productImageSerializer(images, many=True)

    return Response(serializer.data)  # Added return statement

@api_view(['GET'])
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

@api_view(['GET'])
def show_preorders(request):
    invoice_no = request.query_params.get('invoice_no')  # Get the invoice_no from query params
    
    if invoice_no:
        # Filter by invoice_no and where shop_confirm is False
        preorders = almogOil_models.PreOrderTable.objects.filter(invoice_no=invoice_no, shop_confrim=False)
        preorder_items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance__invoice_no=invoice_no, invoice_instance__shop_confrim=False)
    else:
        # If no invoice_no is provided, fetch all preorders where shop_confirm is False
        preorders = almogOil_models.PreOrderTable.objects.filter(shop_confrim=False)
        preorder_items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance__shop_confrim=False)
    
    preorder_serializer = wholesale_serializers.PreOrderTableSerializer(preorders, many=True)
    preorder_items_serializer = wholesale_serializers.PreOrderItemsTableSerializer(preorder_items, many=True)
    
    return Response({
        'preorders': preorder_serializer.data,
        'preorder_items': preorder_items_serializer.data
    })


