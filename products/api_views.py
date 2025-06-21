""" Mainitem Api's """

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from almogOil.authentication import CookieAuthentication  # Your custom cookie authentication
from drf_spectacular.utils import extend_schema_view,extend_schema,OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes, OpenApiSchemaBase
import hashlib
from django.core.cache import cache
from rest_framework.decorators import api_view
import json
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import FieldError
from almogOil import models as almogOil_Models # Adjust this import to match your project structure
from almogOil import serializers as almogOil_Serializers
from products import serializers as products_serializers
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, mixins,viewsets
from rest_framework import viewsets, status
from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from almogOil import models
from django.db.models import F, Q, Sum, IntegerField
from django.core.paginator import Paginator
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

""" Mainitem / Products Api's """

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def UpdateItemsItemmainApiView(request, item_id):
    if not request.user.has_perm('almogOil.change_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)
    try:
        # Retrieve the item by its ID
        item = almogOil_Models.Mainitem.objects.get(pno=item_id)
    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Add or remove values from itemmain based on action in request
        action = request.data.get("action")  # "add" or "remove"
        value = request.data.get("value")

        # Make sure we have the action and value
        if not action or not value:
            return Response({"detail": "Action and value are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Split the current itemmain into a list
        itemmain_list = item.itemmain.split(";") if item.itemmain else []

        if action == "add":
            # Add value to list if not already present
            if value not in itemmain_list:
                itemmain_list.append(value)
                item.itemmain = ";".join(itemmain_list)
                item.save()
                return Response(products_serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        elif action == "remove":
            # Remove value from list
            if value in itemmain_list:
                itemmain_list.remove(value)
                item.itemmain = ";".join(itemmain_list)
                item.save()
                return Response(products_serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    # Default GET method to show current itemmain value
    elif request.method == 'GET':
        s_data = products_serializers.MainitemSerializer(item).data
        itemmain = s_data['itemmain']
        return Response({'itemmain': itemmain}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def UpdateItemsSubmainApiView(request, item_id):

    if not request.user.has_perm('almogOil.change_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)


    try:
        # Retrieve the item by its ID
        item = almogOil_Models.Mainitem.objects.get(pno=item_id)
    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Add or remove values from itemmain based on action in request
        action = request.data.get("action")  # "add" or "remove"
        value = request.data.get("value")

        # Make sure we have the action and value
        if not action or not value:
            return Response({"detail": "Action and value are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Split the current itemmain into a list
        itemsub_list = item.itemsubmain.split(";") if item.itemsubmain else []

        if action == "add":
            # Add value to list if not already present
            if value not in itemsub_list:
                itemsub_list.append(value)
                item.itemsubmain = ";".join(itemsub_list)
                item.save()
                return Response(products_serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        elif action == "remove":
            # Remove value from list
            if value in itemsub_list:
                itemsub_list.remove(value)
                item.itemsubmain = ";".join(itemsub_list)
                item.save()
                return Response(products_serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    # Default GET method to show current itemmain value
    elif request.method == 'GET':
        s_data = products_serializers.MainitemSerializer(item).data
        itemsubmain = s_data['itemsubmain']
        return Response({'itemsub': itemsubmain}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def UpdateItemsModelApiView(request, item_id):

    if not request.user.has_perm('almogOil.change_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)


    try:
        # Retrieve the item by its ID
        item = almogOil_Models.Mainitem.objects.get(pno=item_id)
    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Add or remove values from itemmain based on action in request
        action = request.data.get("action")  # "add" or "remove"
        value = request.data.get("value")

        # Make sure we have the action and value
        if not action or not value:
            return Response({"detail": "Action and value are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Split the current itemmain into a list
        model_list = item.itemthird.split(";") if item.itemthird else []

        if action == "add":
            # Add value to list if not already present
            if value not in model_list:
                model_list.append(value)
                item.itemthird = ";".join(model_list)
                item.save()
                return Response(products_serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        elif action == "remove":
            # Remove value from list
            if value in model_list:
                model_list.remove(value)
                item.itemthird = ";".join(model_list)
                item.save()
                return Response(products_serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    # Default GET method to show current itemmain value
    elif request.method == 'GET':
        s_data = products_serializers.MainitemSerializer(item).data
        itemthird = s_data['itemthird']
        return Response({'models': itemthird}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def UpdateItemsEngineApiView(request, item_id):

    if not request.user.has_perm('almogOil.change_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)


    try:
        # Retrieve the item by its ID
        item = almogOil_Models.Mainitem.objects.get(pno=item_id)
    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Add or remove values from itemmain based on action in request
        action = request.data.get("action")  # "add" or "remove"
        value = request.data.get("value")

        # Make sure we have the action and value
        if not action or not value:
            return Response({"detail": "Action and value are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Split the current itemmain into a list
        engine_list = item.engine_no.split(";") if item.engine_no else []

        if action == "add":
            # Add value to list if not already present
            if value not in engine_list:
                engine_list.append(value)
                item.engine_no = ";".join(engine_list)
                item.save()
                return Response(products_serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        elif action == "remove":
            # Remove value from list
            if value in engine_list:
                engine_list.remove(value)
                item.engine_no = ";".join(engine_list)
                item.save()
                return Response(products_serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    # Default GET method to show current itemmain value
    elif request.method == 'GET':
        s_data = products_serializers.MainitemSerializer(item).data
        engines = s_data['engine_no']
        return Response({'engines': engines}, status=status.HTTP_200_OK)

@api_view(['GET'])
def app_filter_Items(request):
    # Extract the filter parameters from the request body
    itemmain = request.data.get('itemmain', None)
    itemsubmain = request.data.get('itemsubmain', None)
    itemthird = request.data.get('itemthird', None)
    engine_no = request.data.get('engine_no', None)

    # Build the query dynamically based on provided parameters
    filters = {}
    if itemmain:
        filters['itemmain__icontains'] = itemmain  # Case-insensitive search
    if itemsubmain:
        filters['itemsubmain__icontains'] = itemsubmain  # Case-insensitive search
    if itemthird:
        filters['itemthird__icontains'] = itemthird  # Case-insensitive search
    if engine_no:
        filters['engine_no__icontains'] = engine_no  # Case-insensitive search

    # Apply the filters to the Mainitem model
    items = almogOil_Models.Mainitem.objects.filter(**filters)

    # Check if any items are found
    if not items.exists():
        return Response({"message": "No items found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)

    # Apply pagination
    paginator = CustomPagination()
    paginated_items = paginator.paginate_queryset(items, request)

    # Serialize the filtered and paginated items
    serializer = products_serializers.MainitemSerializer(paginated_items, many=True)

    # Return the paginated data as the response
    return paginator.get_paginated_response(serializer.data)
# API to list all support messages (for the support team)

"""Pagination Related"""
class CustomPagination(PageNumberPagination):
    page_size = 10  # Limit the results to 10 per page
    page_size_query_param = 'page_size'
    max_page_size = 100



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_product_images(request, id):

    if not request.user.has_perm('almogOil.category_products'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        product = almogOil_Models.Mainitem.objects.get(pno=id)
    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({"error": "Product not found!"}, status=404)  # Added return and status

    images = almogOil_Models.Imagetable.objects.filter(productid=product.fileid)  # Ensure `productid` is correct
    serializer = products_serializers.productImageSerializer(images, many=True)

    return Response(serializer.data)  # Added return statement


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def mainitem_add_json_desc(request, id):

    if not request.user.has_perm('almogOil.template_add_item_specifications'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    """Add JSON description to a Mainitem product"""
    try:
        data = request.data
        json_data = data.get('json')

        # Parse the JSON data
        parsed_json = json.loads(json_data) if isinstance(json_data, str) else json_data

        # Retrieve the product
        product = almogOil_Models.Mainitem.objects.get(pno=id)
        product.json_description = parsed_json  # Assuming this field is a JSONField
        product.save()

        return Response({"message": "JSON description updated successfully"}, status=status.HTTP_200_OK)

    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#####################


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_item_data(request, fileid):

    if not request.user.has_perm('almogOil.category_products'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        # Retrieve the record from the database
        item = almogOil_Models.Mainitem.objects.get(fileid=fileid)

        # Serialize the item data
        serializer = products_serializers.MainitemSerializer(item)

        # Return the serialized data
        return Response(serializer.data)

    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def edit_main_item(request):
    if not request.user.has_perm('almogOil.change_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    if request.method == 'PATCH':
        try:
            data = request.data  # DRF automatically parses JSON into a Python dict
            fileid = data.get('fileid')
            item = almogOil_Models.Mainitem.objects.get(fileid=fileid)

            # Function to safely update a field
            def safe_update(field_name, new_value):
                if new_value not in [None, "", 0, "0"]:
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

            item.save()  # Save the updated record

            return Response({'success': True}, status=status.HTTP_200_OK)
        except almogOil_Models.Mainitem.DoesNotExist:
            return Response({'success': False, 'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_mainItem_last_pno(request):
    if not request.user.has_perm('almogOil.category_products'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        # Get the last autoid by ordering the table by autoid in descending order
        last_pno = almogOil_Models.Mainitem.objects.order_by('-pno').first()
        if last_pno:
            response_data = {'pno': last_pno.pno}
        else:
            # Handle the case where the table is empty
            response_data = {'pno': 0, 'message': 'No invoices found'}
    except Exception as e:
        # Handle unexpected errors
        response_data = {'error': str(e)}

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
@csrf_exempt
def create_main_item(request):
    if not request.user.has_perm('almogOil.add_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    if request.method == 'POST':
        data = request.data

        # Get the last PNO number
        last_pno_response = json.loads(get_mainItem_last_pno(request).content)
        last_pno_no = last_pno_response.get("pno")
        next_pno_no = int(last_pno_no) + 1

        # Map incoming data fields to model fields
        mapped_data = {
            "itemno": data.get('originalno') or None,
            "itemmain": data.get('itemmain') or None,
            "itemsubmain": data.get('itemsub') or None,
            "itemname": data.get('pnamearabic'),
            "eitemname": data.get('pnameenglish') or None,
            "short_name": data.get('shortname') or None,
            "companyproduct": data.get('company') or None,
            "replaceno": data.get('companyno') or None,
            "engine_no": data.get('engine') or None,
            "pno": next_pno_no,
            "barcodeno": data.get('barcode') or None,
            "memo": data.get('description') or None,
            "itemplace": data.get('location') or None,
            "itemsize": data.get('country') or None,
            "itemperbox": int(data.get('pieces4box', 0) or 0),
            "itemthird": data.get('model') or None,
            "itemvalue": int(data.get('storage', 0) or 0),
            "itemtemp": int(data.get('backup', 0) or 0),
            "itemvalueb": int(data.get('temp', 0) or 0),
            "resvalue": int(data.get('reserved', 0) or 0),
            "orgprice": float(data.get('originprice', 0) or 0),
            "orderprice": float(data.get('buyprice', 0) or 0),
            "costprice": float(data.get('expensesprice', 0) or 0),
            "buyprice": float(data.get('sellprice', 0) or 0),
            "lessprice": float(data.get('lessprice', 0) or 0),
        }

        # Use the serializer with the mapped data
        serializer = products_serializers.MainitemSerializer(data=mapped_data)

        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'message': 'Record created successfully!'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'error', 'message': 'Invalid request method.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_data(request):

    if not request.user.has_perm('almogOil.category_products'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        items = almogOil_Models.Mainitem.objects.all().order_by('itemname')
        serializer = products_serializers.MainitemSerializer(items, many=True)

        total_itemvalue = almogOil_Models.Mainitem.objects.aggregate(total=Sum('itemvalue'))['total']
        total_itemvalueb = almogOil_Models.Mainitem.objects.aggregate(total=Sum('itemvalueb'))['total']
        total_resvalue = almogOil_Models.Mainitem.objects.aggregate(total=Sum('resvalue'))['total']
        total_cost = almogOil_Models.Mainitem.objects.aggregate(total=Sum(F('itemvalue') * F('costprice')))['total']
        total_order = almogOil_Models.Mainitem.objects.aggregate(total=Sum(F('itemvalue') * F('orderprice')))['total']
        total_buy = almogOil_Models.Mainitem.objects.aggregate(total=Sum(F('itemvalue') * F('buyprice')))['total']

        fullTable = request.GET.get('fullTable', None)
        if fullTable:
            response = {
                "data": serializer.data,
                "fullTable": True,
                "total_itemvalue": total_itemvalue,
                "total_itemvalueb": total_itemvalueb,
                "total_resvalue": total_resvalue,
                "total_cost": total_cost,
                "total_order": total_order,
                "total_buy": total_buy,
            }
            return Response(response, status=status.HTTP_200_OK)

        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('size', 20))
        paginator = Paginator(items, page_size)
        page_obj = paginator.get_page(page_number)
        page_serializer = products_serializers.MainitemSerializer(page_obj, many=True)

        response = {
            "data": page_serializer.data,
            "last_page": paginator.num_pages,
            "total_rows": paginator.count,
            "page_size": page_size,
            "page_no": page_number,
            "total_itemvalue": total_itemvalue,
            "total_itemvalueb": total_itemvalueb,
            "total_resvalue": total_resvalue,
            "total_cost": total_cost,
            "total_order": total_order,
            "total_buy": total_buy,
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def update_itemvalue(request):
    if not request.user.has_perm('almogOil.change_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        data = request.data
        fileid = data.get('fileid')
        new_itemvalue = data.get('newItemValue')
        old_itemvalue = 0

        item = almogOil_Models.Mainitem.objects.get(fileid=fileid)
        old_itemvalue = item.itemvalue
        item.itemvalue = new_itemvalue
        item.save()

        movement_Record = almogOil_Models.ProductsMovementHistory.objects.create(
            itemno=item.itemno,
            itemname=item.itemname,
            maintype=item.itemmain,
            currentbalance=item.itemvalue,
            date=timezone.now(),
            clientname="اعادة ترصيد",
            description="اعادة ترصيد للصنف",
            clientbalance=int(new_itemvalue - old_itemvalue) or 0,
            pno_instance=item,
            pno=item.pno
        )

        return Response({'success': True, 'message': 'Item value updated successfully.'}, status=status.HTTP_200_OK)
    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({'success': False, 'message': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#until here

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def update_storage(request):
    if not request.user.has_perm('almogOil.change_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        data = request.data
        fileid = data.get('fileid')
        storage = data.get('storage')

        item = almogOil_Models.Mainitem.objects.get(fileid=fileid)
        item.itemplace = storage
        item.save()

        return Response({'success': True, 'message': 'Storage updated successfully.'}, status=status.HTTP_200_OK)
    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({'success': False, 'message': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def check_items(request):
    if not request.user.has_perm('almogOil.category_products'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)


    try:
        # Step 1: Parse the incoming JSON data
        data = request.data

        # Step 2: Validate that the data is a list (since the request body is already an array of items)
        if not isinstance(data, list):
            return Response({"status": "error", "message": "Invalid data format. Expected an array."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Check existence for each item
        results = []
        for item in data:
            # Ensure the necessary field 'company_no' exists in the item
            company_no = item.get("رقم الشركة")
            if not company_no:
                results.append({"message": "company_no is missing", "exists": 0})
                continue

            # Check if item exists in Mainitem model based on 'company_no'
            exists = almogOil_Models.Mainitem.objects.filter(replaceno=company_no).exists()
            results.append({"company_no": company_no, "exists": 1 if exists else 0})

        return Response({"status": "success", "results": results}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
@csrf_exempt
def delete_record(request):
    if not request.user.has_perm('almogOil.delete_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        data = request.data
        fileid = data.get('fileid')

        if not fileid:
            return Response({"success": False, "message": "No 'fileid' provided."}, status=400)

        record = almogOil_Models.Mainitem.objects.get(fileid=fileid)
        record.delete()

        return Response({"success": True, "message": "Record deleted successfully."})

    except almogOil_Models.Mainitem.DoesNotExist:
        return Response({"success": False, "message": "Record not found."}, status=404)

    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def web_filter_items(request):
     if not request.user.has_perm('almogOil.category_products'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

     if request.method == "POST":
         try:
             # Get the filters from the request body
             filters = request.data  # Decoding bytes and loading JSON
             cache_key = f"filter_{hashlib.md5(str(filters).encode()).hexdigest()}"
             cached_data = cache.get(cache_key)

             if cached_data:
                 cached_data["cached_flag"] = True
                 return Response(cached_data, status=status.HTTP_200_OK)

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
                 filters_q &= Q(engine_no__icontains=filters['engine_no'])
             if filters.get('itemthird'):
                 filters_q &= Q(itemthird__icontains=filters['itemthird'])
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

             # Original filters
             if filters.get('itemvalue') == "0":
                 filters_q &= Q(itemvalue=0)
             if filters.get('itemvalue') == ">0":
                 filters_q &= Q(itemvalue__gt=0)

             # New availability logic (switch-case style)
             availability = filters.get('availability')
             if availability == "not_available":
                 filters_q &= Q(itemvalue=0)
             elif availability == "limited":
                 filters_q &= Q(itemvalue__lte=10, itemvalue__gt=0)
             elif availability == "available":
                 filters_q &= Q(itemvalue__gt=10)

             if filters.get('resvalue') == ">0":
                 filters_q &= Q(resvalue__gt=0)
             if filters.get('itemvalue_itemtemp') == "lte":
                 filters_q &= Q(itemvalue__lte=F('itemtemp'))  # Compare fields

             # Apply date range filter on `orderlastdate`
             fromdate = filters.get('fromdate', '').strip()
             todate = filters.get('todate', '').strip()

             if fromdate and todate:
                 try:
                     from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                     to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)
                     filters_q &= Q(orderlastdate__range=[from_date_obj, to_date_obj])
                 except ValueError:
                     return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

             # Now filter the queryset using the combined Q object
             queryset = almogOil_Models.Mainitem.objects.filter(filters_q).order_by('itemname')

             # Serialize the filtered data
             serializer = products_serializers.MainitemSerializer(queryset, many=True)
             items_data = serializer.data

             # Initialize totals
             total_itemvalue = total_itemvalueb = total_resvalue = total_cost = total_order = total_buy = 0

             # Calculate totals
             for item in items_data:
                    # Use safe conversion functions
                 itemvalue = float(item.get('itemvalue') or 0)
                 itemvalueb = float(item.get('itemvalueb') or 0)
                 resvalue = float(item.get('resvalue') or 0)
                 costprice = float(item.get('costprice') or 0)
                 orderprice = float(item.get('orderprice') or 0)
                 buyprice = float(item.get('buyprice') or 0)


                 total_itemvalue += itemvalue
                 total_itemvalueb += itemvalueb
                 total_resvalue += resvalue
                 total_cost += itemvalue * costprice
                 total_order += itemvalue * orderprice
                 total_buy += itemvalue * buyprice

             fullTable = filters.get('fullTable')
             if fullTable:
                 response = {
                     "data": items_data,
                     "fullTable": True,
                     "last_page": 1,
                     "total_rows": queryset.count(),
                     "page_no": 1,
                     "total_itemvalue": total_itemvalue,
                     "total_itemvalueb": total_itemvalueb,
                     "total_resvalue": total_resvalue,
                     "total_cost": total_cost,
                     "total_order": total_order,
                     "total_buy": total_buy,
                 }
                 return Response(response)

             # Pagination
             page_number = int(filters.get('page') or 1)
             page_size = int(filters.get('size') or 20)
             paginator = Paginator(items_data, page_size)
             page_obj = paginator.get_page(page_number)

             response = {
                 "data": list(page_obj),
                 "last_page": paginator.num_pages,
                 "total_rows": paginator.count,
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

             cache.set(cache_key, response, timeout=300)
             return Response(response)

         except json.JSONDecodeError:
             return Response({'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)
         except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@extend_schema(
description="""Upload a logo for maintype ,ex: logo for Mercedes.""",
tags=["Main Types"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def upload_maintype_logo(request, id):
    if not request.user.has_perm('almogOil.change_mainitem'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    if 'logo' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    image = request.FILES['logo']

    try:
        maintype = almogOil_Models.Maintypetable.objects.get(fileid=id)
        maintype.logo_obj = image  # Assign the file object directly
        maintype.save()
        return Response({"message": "Logo uploaded successfully!"}, status=status.HTTP_200_OK)

    except almogOil_Models.Maintypetable.DoesNotExist:
        return Response({"error": "Maintypetable entry not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
description="""Get the company's logo by product's pno number.""",
tags=["Companies","Products"],
)
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def get_logo_by_pno(request, id):
    if not request.user.has_perm('almogOil.category_products'):
        return Response({"detail": "User permission denied, user does not have proper permissions."}, status=403)

    try:
        product = get_object_or_404(almogOil_Models.Mainitem, pno=id)
        company = get_object_or_404(almogOil_Models.Companytable, companyname=product.companyproduct)

        logo = company.logo_obj
        if logo:
            logo_url = request.build_absolute_uri(logo.url)  # 👈 Full URL
            return Response({"logo_url": logo_url}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Logo not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def create_item_category(request):
    serializer = products_serializers.ItemCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Category created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def list_item_categories(request):
# This is an auto-generated Django model module.
# This is an auto-generated Django model module.
    categories = almogOil_Models.ItemCategory.objects.all().order_by('-id')  # optional: newest first
    serializer = products_serializers.ItemCategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(["POST"])
@authentication_classes([CookieAuthentication])
@permission_classes([IsAuthenticated])
def upload_and_assign_images(request):
    parser_classes = [MultiPartParser]

    if not request.FILES:
        return Response({'error': 'لم يتم رفع أي صور'}, status=status.HTTP_400_BAD_REQUEST)

    response_data = []

    try:
        for file_key in request.FILES:
            try:
                image_file = request.FILES[file_key]
                original_name = os.path.splitext(image_file.name)[0].strip()

                try:
                    matched_items = almogOil_Models.Mainitem.objects.filter(oem_numbers__icontains=original_name)
                except Exception as e:
                    response_data.append({
                        'image_name': image_file.name,
                        'status': f'خطأ في البحث عن المنتج: {str(e)}'
                    })
                    continue

                if matched_items.exists():
                    for item in matched_items:
                        try:
                            saved_path = default_storage.save(
                                f'product_images/{image_file.name}',
                                ContentFile(image_file.read())
                            )

                            almogOil_Models.Imagetable.objects.create(
                                productid=item.fileid,
                                image=image_file.name,
                                image_obj=saved_path
                            )

                            response_data.append({
                                'pno': item.pno,
                                'oem_number_match': original_name,
                                'status': f'تم ربط الصورة بنجاح بالقطعة رقم {item.pno}'
                            })
                        except Exception as e:
                            response_data.append({
                                'pno': item.pno,
                                'status': f'فشل في حفظ الصورة أو ربطها: {str(e)}'
                            })
                else:
                    response_data.append({
                        'image_name': image_file.name,
                        'status': 'لم يتم العثور على منتج يطابق رقم OEM'
                    })
            except Exception as e:
                response_data.append({
                    'image_key': file_key,
                    'status': f'فشل في معالجة الصورة: {str(e)}'
                })

    except Exception as general_error:
        return Response({'error': f'حدث خطأ غير متوقع: {str(general_error)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response_data, status=status.HTTP_200_OK)

@extend_schema(
description="""edit prices for product api.""",
tags=["price","Products"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def modify_price(request):
    try:
        data = request.data
        product_id = data.get("product_id")
        price_type = data.get("priceType")
        value = data.get("value")
        is_percentage = data.get("isPercentage")
        operation = data.get("operation")

        if not all([product_id, price_type, operation]) or value is None:
            return Response({"error": "Missing required data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            value = Decimal(str(value))
        except:
            return Response({"error": "Invalid value format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = models.Mainitem.objects.get(pno=product_id)
        except models.Mainitem.DoesNotExist:
            return Response({"error": "المنتج غير موجود"}, status=status.HTTP_404_NOT_FOUND)

        if price_type not in ["orgprice", "orderprice", "costprice", "buyprice"]:
            return Response({"error": "نوع السعر غير صالح"}, status=status.HTTP_400_BAD_REQUEST)

        current_price = getattr(item, price_type) or Decimal("0.0")

        if is_percentage:
            if operation == "+":
                new_price = current_price + (current_price * value / 100)
            elif operation == "-":
                new_price = current_price - (current_price * value / 100)
            else:
                return Response({"error": "عملية غير صالحة"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if operation == "+":
                new_price = current_price + value
            elif operation == "-":
                new_price = current_price - value
            elif operation == "=":
                new_price = value
            else:
                return Response({"error": "عملية غير صالحة"}, status=status.HTTP_400_BAD_REQUEST)

        setattr(item, price_type, new_price)
        item.save()

        return Response({
            "message": f"تم تحديث {price_type} بنجاح إلى {new_price:.2f}"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)