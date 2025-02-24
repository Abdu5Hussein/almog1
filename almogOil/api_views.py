from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
import json
from django.core.exceptions import FieldError
from . import models  # Adjust this import to match your project structure
from . import serializers
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated



@api_view(["POST"])
def sign_in(request):
    try:
        if request.method == "POST":
            try:
                # Parse JSON request body
                body = json.loads(request.body)

                # Extract fields
                username = body.get("username")
                password = body.get("password")
                role = body.get("role")

                # Check required fields
                if not username or not password or not role:
                    return Response({"error": "[username, password, role] fields are required"}, status=status.HTTP_400_BAD_REQUEST)

                # Role-based authentication
                user = None  # Default value
                user_id = None

                if role == "client":
                    try:
                        user = models.AllClientsTable.objects.get(username=username)
                        user_id = f"c-{user.clientid}"
                    except models.AllClientsTable.DoesNotExist:
                        return Response({"error": "لم يتم التعرف على العميل", "message": "لم يتم التعرف على العميل"}, status=status.HTTP_404_NOT_FOUND)

                elif role == "employee":
                    try:
                        user = models.EmployeesTable.objects.get(username=username)
                        user_id = f"e-{user.employee_id}"
                    except models.EmployeesTable.DoesNotExist:
                        return Response({"error": "لم يتم التعرف على الموظف", "message": "لم يتم التعرف على الموظف"}, status=status.HTTP_404_NOT_FOUND)

                elif role == "source":
                    try:
                        user = models.AllSourcesTable.objects.get(username=username)
                        user_id = f"s-{user.clientid}"
                    except models.AllSourcesTable.DoesNotExist:
                        return Response({"error": "لم يتم التعرف على المصدر", "message": "لم يتم التعرف على المصدر"}, status=status.HTTP_404_NOT_FOUND)

                else:
                    return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

                # Verify user in Django's auth_user table
                try:
                    auth_user = User.objects.get(username=username)
                    if not check_password(password, auth_user.password):
                        return Response({"error": "Incorrect password", "message": "كلمة السر غير صحيحة"}, status=status.HTTP_400_BAD_REQUEST)
                except User.DoesNotExist:
                    return Response({"error": "User not found in authentication system", "message": "المستخدم غير مسجل"}, status=status.HTTP_404_NOT_FOUND)

                # Generate JWT tokens
                refresh = RefreshToken.for_user(auth_user)
                access_token = str(refresh.access_token)

                # Log the user in
                login(request, auth_user)  # ✅ Fix: Using `auth_user` instead of `authed_user`

                # Store session variables
                request.session["username"] = user.username
                request.session["name"] = user.name
                request.session["role"] = role  # Store role for later use
                request.session["user_id"] = user_id
                request.session["is_authenticated"] = True  # Useful for templates
                request.session.set_expiry(3600)  # ✅ Optional: Set session expiry (1 hour)

                # Successful response with token
                return Response({
                    "message": "Signed in successfully",
                    "role": role,
                    "access_token": access_token,
                    "refresh_token": str(refresh),
                    "session_data": {
                        "username": request.session.get("username"),
                        "name": request.session.get("name"),
                        "role": request.session.get("role"),
                        "user_id": request.session.get("user_id"),
                        "is_authenticated": request.session.get("is_authenticated")
                    }
                }, status=status.HTTP_200_OK)


            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Only POST method is allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    except FieldError:
        return Response({"error": "Field does not exist in the model"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["GET"])
def get_dropboxes(request):
    model = models.Modeltable.objects.all()
    serialized_model = serializers.ModelSerializer(model, many=True)

    engines = models.enginesTable.objects.all()
    serialized_engines = serializers.EngineSerializer(engines, many=True)

    main = models.Maintypetable.objects.all()
    serialized_main = serializers.MainTypeSerializer(main, many=True)

    sub = models.Subtypetable.objects.all()
    serialized_sub = serializers.SubTypeSerializer(sub, many=True)

    return Response({
        'models':serialized_model.data,
        'engines': serialized_engines.data,
        'sub_types': serialized_sub.data,
        'main_types': serialized_main.data,
        })

@api_view(['GET'])
def GetClientInvoices(request, id):
    # Filter invoices based on the client ID
    str_id = str(id)
    invoices = models.SellinvoiceTable.objects.filter(client=str_id)

    if not invoices.exists():
        return Response({'error': 'No invoices found for the provided client ID.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the invoices
    serializer = serializers.SellInvoiceSerializer(invoices, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)  # Return the serialized data

#####################

# API to list all support messages (for the support team)
