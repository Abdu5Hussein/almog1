from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import json
from rest_framework.pagination import PageNumberPagination
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
from rest_framework.exceptions import NotFound
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
from . import models, serializers
from .models import AllClientsTable, SellinvoiceTable
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from firebase_admin import messaging
from .models import EmployeesTable, AllClientsTable
import firebase_admin
from firebase_admin import credentials
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser

""" Log Out,Login And Authentication Api's"""

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Log out the user by clearing the session (for session-based authentication)
    logout(request)

    # Handle JWT refresh token blacklisting
    refresh_token = request.data.get("refresh")  # Get the refresh token from the request body
    if not refresh_token:
        return Response({"message": "Refresh token is required to logout", "session": False}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  # Blacklist the token using SimpleJWT's built-in method

        return Response(
            {"message": "Successfully logged out", "session": False},
            status=status.HTTP_200_OK  # This sets the status code to 200 OK
        )
    except Exception as e:
        return Response({"message": "Invalid or expired refresh token", "error": str(e), "session": False}, status=status.HTTP_400_BAD_REQUEST)

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


"""Drop Boxes"""
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



class EnginesTableViewSet(viewsets.ModelViewSet):
    queryset = models.enginesTable.objects.all()
    serializer_class = serializers.EnginesTableSerializer


@api_view(["GET"])
def get_models(request):
    models_data = models.Modeltable.objects.all()
    serialized_data = serializers.ModelSerializer(models_data, many=True)
    return Response({'models': serialized_data.data})

@api_view(["GET"])
def get_engines(request):
    engines_data = models.enginesTable.objects.all()
    serialized_data = serializers.EngineSerializer(engines_data, many=True)
    return Response({'engines': serialized_data.data})

@api_view(["GET"])
def get_main_types(request):
    main_types_data = models.Maintypetable.objects.all()
    serialized_data = serializers.MainTypeSerializer(main_types_data, many=True)
    return Response({'main_types': serialized_data.data})

@api_view(["GET"])
def get_sub_types(request):
    sub_types_data = models.Subtypetable.objects.all()
    serialized_data = serializers.SubTypeSerializer(sub_types_data, many=True)
    return Response({'sub_types': serialized_data.data})

""" Sell Invoice Api's """


@api_view(['GET'])
def get_invoice_data(request, autoid):
    try:
        # Fetch the data using the provided autoid (primary key)
        invoice_data = SellinvoiceTable.objects.get(autoid=autoid)
        serializer = serializers.OrderSerializer(invoice_data)
        return Response(serializer.data)
    except SellinvoiceTable.DoesNotExist:
        return Response({"error": "Invoice not found"}, status=404)

@api_view(['GET'])
def GetClientInvoices(request, id):
    # Filter invoices based on the client ID
    str_id = str(id)
    invoices = models.SellinvoiceTable.objects.filter(client_id=str_id)

    if not invoices.exists():
        return Response({'error': 'No invoices found for the provided client ID.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the invoices
    serializer = serializers.SellInvoiceSerializer(invoices, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)  # Return the serialized data


# class InvoiceStatusViewSet(viewsets.ViewSet):
#     """
#     A viewset to handle updating invoice status or delivery status
#     and send notifications when the status changes.
#     """

#     def update_status(self, request, pk=None):
#         try:
#             invoice_item = SellInvoiceItemsTable.objects.get(pk=pk)
#             status_type = request.data.get('status_type')  # invoice_status or delivery_status
#             new_status = request.data.get('new_status')  # The new status value

#             if status_type not in ['invoice_status', 'delivery_status']:
#                 return Response({"error": "Invalid status type"}, status=status.HTTP_400_BAD_REQUEST)

#             # Update status based on type
#             setattr(invoice_item, status_type, new_status)
#             invoice_item.save()

#             # Send notification based on status change
#             # send_notification(invoice_item, status_type, new_status)

#             return Response(
#                 SellInvoiceSerializer(invoice_item).data,
#                 status=status.HTTP_200_OK,
#             )
#         except SellInvoiceItemsTable.DoesNotExist:
#             return Response({"error": "Invoice item not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
def update_invoice_status(request, invoice_no):
    """Update invoice status and set delivered_date if status is 'تم التوصيل'."""
    try:
        invoice = SellinvoiceTable.objects.get(invoice_no=invoice_no)  # Direct get()
    except SellinvoiceTable.DoesNotExist:
        return Response({"error": "Invoice not found."}, status=404)

    new_status = request.data.get("delivery_status")

    if new_status in ["جاري التوصيل", "تم التوصيل"]:
        invoice.delivery_status = new_status
        if new_status == "تم التوصيل":

            invoice.delivered_date = now()  # Set the current timestamp
        invoice.save()
        send_invoice_notification(invoice, new_status)
        return Response({"message": "Status updated successfully."})

    return Response({"error": "Invalid status."}, status=400)

@csrf_exempt
@api_view(['GET'])
def get_delivery_invoices(request):
    """Fetch all invoices with status 'حضرت'."""
    invoices = SellinvoiceTable.objects.filter(invoice_status="سلمت",mobile=True,is_assigned=False,delivery_status="جاري التوصيل")
    serializer = serializers.SellInvoiceSerializer(invoices, many=True)
    return Response(serializer.data)

#####################

# API to list all support messages (for the support team)
"""Pagination Related"""
class CustomPagination(PageNumberPagination):
    page_size = 10  # Limit the results to 10 per page
    page_size_query_param = 'page_size'
    max_page_size = 100



""" Support Dashboard Api's """

@api_view(['GET'])
def support_conversations(request):
    if request.method == 'GET':
        conversations = models.SupportChatConversation.objects.all()
        serializer = serializers.SupportChatConversationSerializer1(conversations, many=True)
        return Response({'conversations': serializer.data})

# Get Messages in a Conversation
@api_view(['GET'])
def get_conversation_messages(request, conversation_id):
    if request.method == 'GET':
        try:
            conversation = models.SupportChatConversation.objects.get(conversation_id=conversation_id)
            messages = models.SupportChatMessageSys.objects.filter(conversation=conversation)
            serializer = serializers.SupportChatMessageSysSerializer1(messages, many=True)
            return Response({'messages': serializer.data})
        except models.SupportChatConversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

# Create a New Message in a Conversation
@api_view(['POST'])
@api_view(['POST'])
def send_message(request, conversation_id=None):
    if request.method == 'POST':
        message_text = request.data.get('message')
        sender_type = request.data.get('sender_type')  # Always 'client' in this case

        # Check if message is not empty
        if not message_text:
            return Response({'error': 'Message cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate sender type, it must be 'client'
        if sender_type != 'client':
            return Response({'error': 'Sender must be a client'}, status=status.HTTP_400_BAD_REQUEST)

        # If conversation_id is provided, fetch the existing conversation
        if conversation_id:
            try:
                conversation = models.SupportChatConversation.objects.get(conversation_id=conversation_id)
            except models.SupportChatConversation.DoesNotExist:
                return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If no conversation_id, create a new conversation (assuming client sends message)
            client_id = request.data.get('client_id')  # Expect client_id in the request if no conversation_id
            try:
                client = AllClientsTable.objects.get(clientid=client_id)
                # Create a new conversation without support agent
                conversation = models.SupportChatConversation.objects.create(
                    client=client,
                    support_agent=None  # No support agent in this conversation
                )
            except AllClientsTable.DoesNotExist:
                return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create the message
        message = models.SupportChatMessageSys.objects.create(
            conversation=conversation,
            sender=conversation.client,  # Only the client is sending the message
            sender_type='client',  # 'client' is the sender type
            message=message_text,
            timestamp=timezone.now(),
            is_read=False
        )

        message_serializer = serializers.SupportChatMessageSysSerializer1(message)

        return Response({
            'message': 'Message sent successfully',
            'message_data': message_serializer.data
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def start_conversation(request, client_id):
    if request.method == 'POST':
        try:
            # Get the client
            client = AllClientsTable.objects.get(clientid=client_id)

            # Check if there's already an existing conversation with the client
            existing_conversation = models.SupportChatConversation.objects.filter(client=client)
            if existing_conversation.exists():
                return Response({'error': 'Conversation already exists with this client'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new conversation with the support agent (request.user)
            conversation = models.SupportChatConversation.objects.create(
                client=client,
                support_agent=request.user
            )

            # Now, send the first message to start the conversation
            first_message = request.data.get('message')
            if not first_message:
                return Response({'error': 'Message is required to start a conversation'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the first message in the conversation
            message = models.SupportChatMessageSys.objects.create(
                conversation=conversation,
                sender=request.user,  # Assuming the support agent is the sender
                sender_type='support',  # Type 'support' for the agent
                message=first_message,
                timestamp=timezone.now(),
                is_read=False
            )

            message_serializer = serializers.SupportChatMessageSysSerializer1(message)

            return Response({
                'message': 'Conversation started successfully',
                'message_data': message_serializer.data
            }, status=status.HTTP_201_CREATED)

        except AllClientsTable.DoesNotExist:
            return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def send_feedback(request):
    client_id = request.data.get('client_id')
    feedback_text = request.data.get('feedback_text')

    # Validate input
    if not client_id:
        return Response({"error": "Client ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    if not feedback_text:
        return Response({"error": "Feedback text is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Get the client by client_id from the AllClientsTable model
    try:
        client = AllClientsTable.objects.get(clientid=client_id)  # Query by clientid, not id
    except AllClientsTable.DoesNotExist:
        return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create the feedback entry
    feedback = models.Feedback(sender=client, feedback_text=feedback_text)
    feedback.save()

    # Return the created feedback data in response
    return Response(serializers.FeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def respond_to_feedback(request, client_id):
    if request.method == 'POST':
        try:
            client = AllClientsTable.objects.get(id=client_id)
            feedback = models.Feedback.objects.filter(sender=client).last()  # Get latest feedback
        except (AllClientsTable.DoesNotExist, models.Feedback.DoesNotExist):
            return JsonResponse({"error": "Client or Feedback not found."}, status=404)

        # Parse JSON request body
        try:
            data = json.loads(request.body)
            response_text = data.get("response_text", "").strip()
        except json.JSONDecodeError:
            response_text = request.POST.get("response_text", "").strip()

        if not response_text:
            return JsonResponse({"error": "Response text is required."}, status=400)

        # Save the response
        feedback.employee_response = response_text
        feedback.is_resolved = True
        feedback.response_at = timezone.now()
        feedback.save()

        return JsonResponse({"message": "Response saved successfully.", "response_text": response_text}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

""" Client Related Api's """

@api_view(['GET'])
def get_all_clients1(request,id=None):
    if request.method == 'GET':
        clients = AllClientsTable.objects.all().filter(clientid=id)
        serializer = serializers.AllClientsTableSerializer(clients, many=True)
        return Response({'clients': serializer.data})


""" Delivery Related Api's """

@api_view(['GET'])
def get_employee_order(request, employee_id):
    """Assign an order directly to an employee while ensuring a fair and accurate queue system."""
    try:
        # Get the employee
        employee = EmployeesTable.objects.get(employee_id=employee_id)

        if not employee.is_available:
            return Response({"message": "Employee is not available."}, status=400)

        if employee.has_active_order:
            return Response({"message": "Employee already has an active order and cannot be assigned a new one."}, status=400)

        # Get all available employees sorted by employee_id (ensuring queue order)
        employee_queue = list(EmployeesTable.objects.filter(is_available=True).order_by('employee_id'))

        if not employee_queue:
            return Response({"message": "No available employees in the queue."}, status=400)

        # Get all pending orders that are not assigned yet
        pending_orders = list(SellinvoiceTable.objects.filter(invoice_status='سلمت', delivery_status='جاري التوصيل', is_assigned=False).order_by('autoid'))

        if not pending_orders:
            return Response({"message": "No pending orders available."}, status=400)

        # Ensure every employee gets their fair share of orders based on queue order
        employee_count = len(employee_queue)
        order_count = len(pending_orders)

        if order_count == 0:
            return Response({"message": "No orders available to assign."}, status=400)

        # Assign orders in a round-robin fashion to match employees correctly
        assigned_order = None
        for index, emp in enumerate(employee_queue):
            if emp.employee_id == employee_id:
                if index < order_count:
                    assigned_order = pending_orders[index]  # Assign the corresponding order
                else:
                    return Response({"message": "No order assigned at this moment."}, status=400)
                break

        if not assigned_order:
            return Response({"message": "No matching order found for this employee."}, status=400)

        # Update employee status
        employee.is_available = False
        employee.has_active_order = True
        employee.save()

        # Update order status
        assigned_order.delivery_status = 'جاري التوصيل'
        assigned_order.is_assigned = True
        assigned_order.save()

        # Create an order queue record and automatically accept it
        order_queue = models.OrderQueue.objects.create(employee=employee, order=assigned_order, is_accepted=True)

        return Response({
            "message": "Order assigned successfully.",
            "order": {
                "order_id": assigned_order.autoid,
                "invoice_no": assigned_order.invoice_no,
                "client": assigned_order.client,
                "amount": str(assigned_order.amount),
                "delivery_status": assigned_order.delivery_status
            },
            "action": {
                "decline": f"/decline-order/{order_queue.id}/"
            }
        })

    except EmployeesTable.DoesNotExist:
        return Response({"error": "Employee not found."}, status=404)


@api_view(['POST'])
def accept_order(request, queue_id):
    try:
        # Fetch the order queue entry by ID
        order_queue = models.OrderQueue.objects.get(id=queue_id)

        # Mark the order as accepted
        order_queue.is_accepted = True
        order_queue.save()

        # Update the order's delivery status to 'جاري التوصيل'
        order = order_queue.order
        order.delivery_status = 'كهجاري التوصيل'
        order.save()

        # Mark the employee as unavailable and set the active order flag
        employee = order_queue.employee
        employee.is_available = False
        employee.has_active_order = True  # Set the active order flag
        employee.save()

        return Response({
            "message": "Order accepted successfully.",
            "order_id": order.autoid,
            "invoice_no": order.invoice_no,
            "client": order.client,
            "delivery_status": order.delivery_status
        })

    except models.OrderQueue.DoesNotExist:
        return Response({"error": "Order queue entry not found."}, status=404)


@api_view(['POST'])
def decline_order(request, queue_id):
    try:
        # Fetch the order queue entry by ID
        order_queue = models.OrderQueue.objects.get(id=queue_id)

        if order_queue.is_accepted or order_queue.is_completed:
            return Response({"message": "Order has already been accepted or completed."}, status=400)

        # Mark the order as declined
        order_queue.is_declined = True
        order_queue.save()

        # Mark the order's delivery status back to 'معلقة'
        order = order_queue.order
        order.delivery_status = 'معلقة'
        order.save()

        # Reassign the order to the next employee in the queue
        next_available_employee = EmployeesTable.objects.filter(is_available=True, has_active_order=False).first()

        if next_available_employee:
            # Assign the order to the next available employee
            models.OrderQueue.objects.create(employee=next_available_employee, order=order)

        # Mark the employee as available again and reset the active order flag
        employee = order_queue.employee
        employee.is_available = True
        employee.has_active_order = False  # Reset the active order flag
        employee.save()

        return Response({
            "message": "Order declined. The next available employee will take it."
        })

    except models.OrderQueue.DoesNotExist:
        return Response({"error": "Order queue entry not found."}, status=404)

@api_view(['POST'])
def deliver_order(request, queue_id):
    try:
        # Fetch the order queue entry by ID
        order_queue = models.OrderQueue.objects.get(id=queue_id)

        # Check if the order has already been delivered or is in the process of being delivered
        if order_queue.order.delivery_status == 'تم التوصيل':
            return Response({"message": "Order has already been delivered."}, status=400)

        # Update the order's delivery status to 'تم التوصيل'
        order = order_queue.order
        order.delivery_status = 'تم التوصيل'
        order.save()

        # Mark the employee as available again and reset the active order flag
        employee = order_queue.employee
        employee.is_available = True
        employee.has_active_order = False  # Reset the active order flag
        employee.save()

        # Mark the order as completed
        order_queue.is_completed = True
        order_queue.save()

        return Response({
            "message": "Order has been successfully delivered.",
            "order_id": order.autoid,
            "invoice_no": order.invoice_no,
            "client": order.client,
            "delivery_status": order.delivery_status
        })

    except models.OrderQueue.DoesNotExist:
        return Response({"error": "Order queue entry not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def skip_order(request, queue_id):
    try:
        # Fetch the order queue entry by ID
        order_queue = models.OrderQueue.objects.get(id=queue_id)

        # Skip the order and mark the order queue entry as completed
        order_queue.is_completed = True
        order_queue.save()

        # Remove the order from the employee's current queue and make the employee available again
        employee = order_queue.employee
        employee.is_available = True
        employee.save()

        # Reassign the order to the next available delivery person
        next_available_employee = EmployeesTable.objects.filter(is_available=True).first()

        if not next_available_employee:
            return Response({"message": "No available employees to take the order."}, status=400)

        # Reassign the order to the next employee in the queue
        models.OrderQueue.objects.create(employee=next_available_employee, order=order_queue.order)

        return Response({
            "message": "Order skipped. The next available employee will take it."
        })

    except models.OrderQueue.DoesNotExist:
        return Response({"error": "Order queue entry not found."}, status=404)



@csrf_exempt
@api_view(['POST'])
def update_delivery_availability(request):
    """Toggle the availability of the delivery person based on their employee ID and update their queue position."""

    # Get the delivery person ID from the request data
    delivery_person_id = request.data.get('employee_id')

    if not delivery_person_id:
        return Response({"error": "Employee ID is required."}, status=400)

    try:
        # Get the delivery person using the provided ID
        employee = EmployeesTable.objects.get(employee_id=delivery_person_id)
    except EmployeesTable.DoesNotExist:
        return Response({"error": "Employee not found."}, status=404)

    # Toggle the availability status
    employee.is_available = not employee.is_available
    employee.save()

    # If the employee is available, add them to the queue
    if employee.is_available:
        # Check if the employee is already in the queue
        if not models.EmployeeQueue.objects.filter(employee=employee).exists():
            # Get the number of available employees in the queue to set the position
            queue_position = models.EmployeeQueue.objects.filter(is_available=True).count() + 1
            # Add to queue
            models.EmployeeQueue.objects.create(employee=employee, position=queue_position, is_assigned=False, is_available=True)
            message = f"Employee {employee.employee_id} is now available and added to the queue as position {queue_position}."
        else:
            message = f"Employee {employee.employee_id} is already in the queue."
    else:
        # If the employee is unavailable, remove them from the queue
        queue_entry = models.EmployeeQueue.objects.filter(employee=employee, is_available=True).first()
        if queue_entry:
            queue_entry.delete()
            message = f"Employee {employee.employee_id} is now unavailable and removed from the queue."
        else:
            message = f"Employee {employee.employee_id} was not in the queue."

    return Response({
        "message": message,
        "is_available": employee.is_available
    })


@api_view(['POST'])
def assign_orders(request):
    with transaction.atomic():
        available_employees = EmployeesTable.objects.filter(is_available=True)
        pending_orders = SellinvoiceTable.objects.filter(delivery_status="معلقة").order_by("invoice_date")

        assigned_orders = []

        for order in pending_orders:
            if available_employees.exists():
                employee = available_employees.first()
                order.deliverer_name = employee.name
                order.delivery_status = "جاري التوصيل"  # In Progress
                order.save()

                employee.is_available = False  # Mark employee as busy
                employee.save()

                assigned_orders.append({
                    "invoice_id": order.autoid,
                    "deliverer": employee.name
                })
            else:
                break  # Stop if no available employees

        return Response({"assigned_orders": assigned_orders}, status=200)


# 📌 Complete a delivery and assign a new order
@api_view(['POST'])
def complete_delivery(request, invoice_id):
    with transaction.atomic():
        try:
            order = SellinvoiceTable.objects.get(autoid=invoice_id)
            order.delivery_status = "تم التوصيل"  # Mark as delivered
            order.save()

            # Make the employee available again
            employee = EmployeesTable.objects.filter(name=order.deliverer_name).first()
            if employee:
                employee.is_available = True
                employee.save()

            # Assign new orders to available employees
            assign_orders(request)

            return Response({"message": f"Order {invoice_id} marked as delivered and new orders assigned."}, status=200)

        except SellinvoiceTable.DoesNotExist:
            return Response({"error": "Order not found."}, status=404)


# 📌 View all pending orders
@api_view(['GET'])
def pending_orders(request):
    orders = SellinvoiceTable.objects.filter(delivery_status="معلقة")
    serializer = serializers.OrderSerializer(orders, many=True)
    return Response(serializer.data, status=200)





@api_view(['POST'])
def set_available(request):
    """Mark employee as available and add to queue"""
    delivery_person_id = request.data.get('employee_id')

    if not delivery_person_id:
        return Response({"error": "Employee ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        employee = EmployeesTable.objects.get(employee_id=delivery_person_id)
    except EmployeesTable.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

    if employee.is_available:
        return Response({"message": f"Employee {employee.employee_id} is already available."})

    # Update availability
    employee.is_available = True
    employee.save()

    # Check if the employee is already in the queue
    if models.EmployeeQueue.objects.filter(employee=employee).exists():
        # If employee is already in the queue, stop the process and return the message
        return Response({"message": f"Employee {employee.employee_id} is already in the queue."})

    # Add to queue if not already present
    queue_position = models.EmployeeQueue.objects.filter(is_available=True).count() + 1
    models.EmployeeQueue.objects.create(employee=employee, position=queue_position, is_assigned=False, is_available=True)

    return Response({
        "message": f"Employee {employee.employee_id} is now available and added to the queue at position {queue_position}.",
        "is_available": employee.is_available
    })



@api_view(['POST'])
def set_unavailable(request):
    """Mark employee as unavailable and remove from queue"""
    delivery_person_id = request.data.get('employee_id')

    if not delivery_person_id:
        return Response({"error": "Employee ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        employee = EmployeesTable.objects.get(employee_id=delivery_person_id)
    except EmployeesTable.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

    if not employee.is_available:
        return Response({"message": f"Employee {employee.employee_id} is already unavailable."})

    # Update availability
    employee.is_available = False
    employee.save()

    # Remove from queue
    queue_entry = models.EmployeeQueue.objects.filter(employee=employee, is_available=True).first()
    if queue_entry:
        queue_entry.delete()
        message = f"Employee {employee.employee_id} is now unavailable and removed from the queue."
    else:
        message = f"Employee {employee.employee_id} was not in the queue."

    return Response({
        "message": message,
        "is_available": employee.is_available
    })


@api_view(['POST'])
def clear_queue(request):
    """Clear all employees and orders from the queue, set all employees as unavailable, and reset invoice assignments."""

    # Clear employee queue
    deleted_employee_queue, _ = models.EmployeeQueue.objects.all().delete()

    # Clear order queue
    deleted_order_queue, _ = models.OrderQueue.objects.all().delete()

    # Set all employees as unavailable
    EmployeesTable.objects.filter(is_available=True).update(is_available=False)
    EmployeesTable.objects.filter(has_active_order=True).update(has_active_order=False)

    # Reset assign_to field in InvoiceTable


    return Response({
        "message": "Employee and order queues have been cleared. All employees are now unavailable, and invoice assignments have been reset.",
        "deleted_employee_queue_entries": deleted_employee_queue,
        "deleted_order_queue_entries": deleted_order_queue,

    }, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_employee_orders(request, employee_id):
    try:
        # Fetch the employee
        employee = EmployeesTable.objects.filter(employee_id=employee_id).first()
        if not employee:
            return Response({"error": "Employee not found."}, status=404)

        # Get the latest assigned active order for the employee
        order = models.OrderQueue.objects.filter(
            employee=employee,
            is_accepted=True,
            order__delivery_status='جاري التوصيل'
        ).select_related('order').first()

        if not order:
            return Response({"message": "No active orders assigned to you."}, status=400)

        # Return order details
        return Response({
            "order_id": order.order.autoid,
            "invoice_no": order.order.invoice_no,
            "client": order.order.client_id,  # Ensure consistency with client structure
            "amount": str(order.order.amount),
            "delivery_status": order.order.delivery_status,
            "action": {
                "decline": f"/decline-order/{order.id}/"
            }
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["POST"])
def complete_order(request, autoid):
    try:
        # Get the OrderQueue using the autoid field of the related order
        order_queue = models.OrderQueue.objects.get(order__autoid=autoid)
        employee = order_queue.employee

        # Update order status
        order_queue.order.delivery_status = 'تم التسليم'
        order_queue.is_completed = True

        # Save the updated order and order queue
        order_queue.order.save()
        order_queue.save()

        # Update employee status
        employee.is_available = False  # Mark as available for new orders
        employee.has_active_order = False

        # Remove the employee from the EmployeeQueue
        models.EmployeeQueue.objects.filter(employee=employee).delete()

        # Save the employee model
        employee.save()

        # Archive the order in the OrderArchive model
        models.OrderArchive.objects.create(
            order=order_queue.order,  # Store the original order
            employee=employee,  # Store the employee who completed the order
            delivery_status=order_queue.order.delivery_status,  # 'تم التسليم'
            is_completed=True,  # The order is completed
        )

        return Response({"message": "Order completed successfully and archived."})

    except models.OrderQueue.DoesNotExist:
        return Response({"error": "Order not found."}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(["GET"])
def get_available_employees(request):
    # Get all employees who are available

    available_employees = EmployeesTable.objects.filter(is_available=True)

    # Serialize the employee data along with their orders
    serializer = serializers.EmployeeWithOrderSerializer(available_employees, many=True)

    # Return the serialized data in the response
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def check_assign_status(request):
    # Run asynchronous task to assign orders
    async_task('almogOil.Tasks.assign_orders')

    # Fetch available employees
    available_employees = EmployeesTable.objects.filter(is_available=True)

    # Fetch pending orders that have not been assigned yet
    pending_orders = SellinvoiceTable.objects.filter(invoice_status='سلمت', delivery_status='جاري التوصيل', is_assigned=False)

    # Get orders that have been assigned
    assigned_orders = models.OrderQueue.objects.filter(is_assigned=True)

    # Get orders that have been accepted but not assigned
    accepted_orders = models.OrderQueue.objects.filter(is_accepted=True)

    # Prepare the response data
    data = {
        "available_employees": [employee.employee_id for employee in available_employees],
        "pending_orders": [
            {
                "invoice_no": order.invoice_no,
                "client": order.client_name,
                "status": order.delivery_status,
            }
            for order in pending_orders
        ],
        "assigned_orders": [
            {
                "order_id": order.order.autoid,
                "invoice_number": order.order.invoice_no,
                "employee_id": order.employee.employee_id,
                "status": order.order.delivery_status,
            }
            for order in assigned_orders
        ],
        "accepted_orders": [
            {
                "order_id": order.order.autoid,
                "invoice_number": order.order.invoice_no,
                "employee_id": order.employee.employee_id,
                "status": order.order.delivery_status,
            }
            for order in accepted_orders
        ],
    }

    return Response(data)

@api_view(["GET"])
def check_assign_statusss(request, employee_id):
    try:
        # Get the employee

        async_task('almogOil.Tasks.assign_orders')

        employee = EmployeesTable.objects.filter(employee_id=employee_id).first()
        if not employee:
            return Response({"error": "Employee not found."}, status=404)

        # Fetch assigned orders for this employee
        assigned_orders = models.OrderQueue.objects.filter(employee=employee, is_accepted=True).select_related('order')

        # Prepare response data
        data = {
            "employee_id": employee.employee_id,
            "employee_name": employee.name,  # Assuming there's a `name` field
            "is_available": employee.is_available,
            "assigned_orders": [
                {
                    "order_id": order.order.autoid,
                    "invoice_no": order.order.invoice_no,
                    "client": order.order.client_name,
                    "client_id": order.order.client,  # Ensure correct field for client
                    "amount": str(order.order.amount),
                    "delivery_status": order.order.delivery_status,
                    "payment_status": order.order.payment_status,
                    "invoice_date": order.order.invoice_date.strftime('%Y-%m-%d %H:%M:%S'),  # Format datetime
                } for order in assigned_orders
            ]
        }

        return Response(data, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def confirm_order(request, order_id):
    try:
        # Get the order queue where the order is not accepted
        order_queue = models.OrderQueue.objects.get(order_id=order_id, is_accepted=False)

        # Update the order queue to mark it as accepted
        order_queue.is_accepted = True
        order_queue.save()

        # Get the related sell invoice and update its status to 'جاري التوصيل'
        sell_invoice = SellinvoiceTable.objects.get(invoice_no=order_queue.order.invoice_no)
        sell_invoice.delivery_status = "جاري التوصيل"  # Update the invoice status
        sell_invoice.save()

        # Return success response
        return Response({"success": True, "message": "Order confirmed successfully and invoice status updated."})

    except models.OrderQueue.DoesNotExist:
        return Response({"error": "Order not found or already confirmed."}, status=404)

    except SellinvoiceTable.DoesNotExist:
        return Response({"error": "Sell invoice not found."}, status=404)




@api_view(["POST"])
def decline_order(request, order_id):
    try:
        # Get the order queue that is not yet accepted
        order_queue = models.OrderQueue.objects.get(order_id=order_id, is_accepted=False)
        employee = order_queue.employee
        assigned_order = order_queue.order

        # Make employee available again
        employee.is_available = False
        employee.has_active_order = False
        employee.save()

        # Remove the employee from the EmployeeQueue, regardless of their assignment status
        models.EmployeeQueue.objects.filter(employee=employee).delete()

        # Mark the assigned order as unassigned and move it to pending
        assigned_order.is_assigned = False
        assigned_order.delivery_status = 'جاري التوصيل'  # Or the appropriate status for pending orders
        assigned_order.save()

        # Delete the order from the queue
        order_queue.delete()

        # Ensure that unassigned orders are processed again
        # Re-run the assignment for unassigned orders
        async_task('almogOil.Tasks.assign_orders')

        return Response({"success": True, "message": "Order declined, employee marked as available, and reassignment triggered."})

    except models.OrderQueue.DoesNotExist:
        return Response({"error": "Order not found or already processed."}, status=404)




@api_view(["GET"])
def monitor_order_assignments(request):
    try:
        # Fetch available employees
        available_employees = EmployeesTable.objects.filter(is_available=True)

        # Fetch pending orders that are waiting for delivery
        pending_orders = SellinvoiceTable.objects.filter(invoice_status='سلمت', delivery_status='جاري التوصيل', is_assigned=False)

        # Fetch all assigned orders
        assigned_orders = models.OrderQueue.objects.select_related('employee', 'order').all()

        # Split assigned orders into confirmed and unconfirmed
        confirmed_orders = []
        unconfirmed_orders = []

        for order_queue in assigned_orders:
            order = order_queue.order
            employee = order_queue.employee

            if order_queue.is_accepted:
                confirmed_orders.append({
                    "order_id": order.autoid,
                    "invoice_number": order.invoice_no,
                    "employee_id": employee.employee_id,
                    "employee_name": employee.name,
                    "status": order.delivery_status,
                    "confirmation_status": "Confirmed",
                })
            else:
                unconfirmed_orders.append({
                    "order_id": order.autoid,
                    "invoice_number": order.invoice_no,
                    "employee_id": employee.employee_id,
                    "employee_name": employee.name,
                    "status": order.delivery_status,
                    "confirmation_status": "Pending",
                })

        # Prepare the response data
        data = {
            "available_employees": [employee.employee_id for employee in available_employees],
            "pending_orders": [
                {"invoice_no": order.invoice_no, "client": order.client_name, "status": order.delivery_status}
                for order in pending_orders
            ],
            "assigned_orders": {
                "confirmed": confirmed_orders,
                "unconfirmed": unconfirmed_orders,
            }
        }

        # Return the response with data
        return Response({
            "status": "success",
            "data": data
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
def employee_order_info(request, employee_id):
    try:
        # Get employee object by employee_id
        employee = EmployeesTable.objects.get(employee_id=employee_id)

        # Fetch the employee's assigned orders
        assigned_orders = models.OrderQueue.objects.filter(employee=employee).select_related('order')

        # Prepare a list to hold order details
        order_details = []

        # Iterate over the assigned orders and add the relevant details
        for idx, order_queue in enumerate(assigned_orders):
            order = order_queue.order
            order_details.append({
                "order_id": order.autoid,
                "invoice_number": order.invoice_no,
                "client": order.client_name,
                "delivery_status": order.delivery_status,
                "order_status": order.invoice_status,
                "is_confirmed": order_queue.is_accepted,
                "position_in_queue": idx + 1,  # Position in the queue (1-based index)
                "confirmation_status": "Confirmed" if order_queue.is_accepted else "Pending"
            })

        # Prepare the response data
        data = {
            "employee_id": employee.employee_id,
            "employee_name": employee.name,
            "assigned_orders": order_details
        }

        return Response({
            "status": "success",
            "data": data
        })

    except EmployeesTable.DoesNotExist:
        return Response({"error": "Employee not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def employee_current_order_info(request, employee_id):
    try:
        # Get employee object by employee_id
        employee = EmployeesTable.objects.get(employee_id=employee_id)

        # Fetch the employee's assigned orders excluding those with "تم التوصيل" delivery status
        assigned_orders = models.OrderQueue.objects.filter(employee=employee).select_related('order').order_by('assigned_at')
        assigned_orders = assigned_orders.exclude(order__delivery_status="تم التسليم")

        # Get the current order for the employee
        current_order = None
        if assigned_orders.exists():
            current_order = assigned_orders.first()  # The first assigned order is considered the "current" order

        # Get the position of the employee in the queue
        employee_position_in_queue = models.OrderQueue.objects.filter(is_accepted=False).count() + 1

        if current_order:
            order = current_order.order
            current_order_details = {
                "order_id": order.autoid,
                "invoice_number": order.invoice_no,
                "client": order.client_name,
                "delivery_status": order.delivery_status,
                "order_status": order.invoice_status,
                "amount": order.amount,
                "is_confirmed": current_order.is_accepted,
                "confirmation_status": "Confirmed" if current_order.is_accepted else "Pending",
                "position_in_queue": employee_position_in_queue
            }
        else:
            current_order_details = None

        # Prepare the response data
        data = {
            "employee_id": employee.employee_id,
            "employee_name": employee.name,
            "current_order": current_order_details,
            "position_in_queue": employee_position_in_queue
        }

        return Response({
            "status": "success",
            "data": data
        })

    except EmployeesTable.DoesNotExist:
        return Response({"error": "Employee not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# views.py

@api_view(["POST"])
def confirm_order_arrival(request, order_id):
    try:
        # Find the order in the queue which is assigned but not confirmed
        order_queue = models.OrderQueue.objects.get(order_id=order_id, is_accepted=True)

        # Find the actual order linked to this queue entry
        order = order_queue.order

        # Confirm that the order has arrived

        order.delivery_status = 'تم التوصيل'  # Mark the order as delivered
        order.save()

        order_queue.is_completed = True  # Set the is_completed field to True
        order_queue.save()
        # Make employee available again
        employee = order_queue.employee
        employee.is_available = False
        employee.has_active_order = False
        employee.save()

        # Delete the order queue entry, since the order is now confirmed
        order_queue.delete()

        return Response({"success": True, "message": "Order confirmed as arrived."}, status=200)
    except models.OrderQueue.DoesNotExist:
        return Response({"error": "Order not found or already confirmed."}, status=404)


@api_view(["GET"])
def get_all_confirmed_orders(request):
    confirmed_orders = SellinvoiceTable.objects.filter(delivery_status='تم التوصيل')

    data = [
        {
            "invoice_no": order.invoice_no,
            "client": order.client_name,
            "status": order.delivery_status,
            "employee_id": order.employee_id,
            "amount": order.amount,
            "payment_status": order.payment_status,
            "invoice_date": order.invoice_date.strftime('%Y-%m-%d %H:%M:%S')  # Format the date
        }
        for order in confirmed_orders
    ]

    return Response(data, status=200)

@api_view(["GET"])
def get_employee_confirmed_orders(request):
    # Get all orders that have been confirmed as arrived by the employee
    confirmed_orders = SellinvoiceTable.objects.filter(
        orderqueue__is_completed=True,
        delivery_status='تم التوصيل'
    ).distinct()

    data = [
        {
            "invoice_no": order.invoice_no,
            "client": order.client_name,
            "status": order.delivery_status,
            "employee_id": order.employee_id,  # Assuming employee_id is stored in SellinvoiceTable
            "amount": order.amount,
            "payment_status": order.payment_status,
            "invoice_date": order.invoice_date.strftime('%Y-%m-%d %H:%M:%S')  # Format the date
        }
        for order in confirmed_orders
    ]

    return Response(data, status=200)



@api_view(["GET"])
def get_archived_orders(request, employee_id):
    try:
        # Fetch the orders archived for the specific employee
        archived_orders = models.OrderArchive.objects.filter(employee_id=employee_id)

        # If no archived orders found
        if not archived_orders:
            return Response({"message": "No archived orders found for this employee."}, status=404)

        # Serialize the archived orders data
        serialized_orders = [
            {
                "order_id": archived_order.order.id,
                "employee_name": archived_order.employee.name,
                "delivery_status": archived_order.delivery_status,
                "is_completed": archived_order.is_completed,
                "order_date": archived_order.order_date,
                "completion_date": archived_order.completion_date,
            }
            for archived_order in archived_orders
        ]

        return Response({"archived_orders": serialized_orders})

    except Exception as e:
        return Response({"error": str(e)}, status=500)


""" Return invoice Api's """

class ReturnPermissionViewSet(viewsets.ModelViewSet):
    queryset = models.return_permission.objects.all()
    serializer_class = serializers.ReturnPermissionSerializer
    lookup_field = 'autoid'

    def create(self, request, *args, **kwargs):
        data = request.data

        # Convert and validate foreign keys
        client_id = data.get("client")
        invoice_id = data.get("invoice")

        if not AllClientsTable.objects.filter(clientid=client_id).exists():
            return Response({"error": "Client not found"}, status=status.HTTP_400_BAD_REQUEST)

        if not SellinvoiceTable.objects.filter(invoice_no=invoice_id).exists():
            return Response({"error": "Invoice not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch related objects
        client = AllClientsTable.objects.get(clientid=client_id)
        invoice = SellinvoiceTable.objects.get(invoice_no=invoice_id)

        # Create the return permission
        return_permission_instance = models.return_permission.objects.create(
            client=client,
            employee=data.get("employee"),
            invoice_obj=invoice,
            invoice_no=invoice.invoice_no,
            payment=data.get("payment", ""),  # Default to empty if not provided
        )

        # Serialize and return the created object
        serializer = self.get_serializer(return_permission_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class ReturnPermissionItemsViewSet(viewsets.ModelViewSet):
    queryset = models.return_permission_items.objects.all()
    serializer_class = serializers.ReturnPermissionItemsSerializer
    lookup_field = 'autoid'

    def create(self, request, *args, **kwargs):
        data = request.data

        # Convert and validate foreign keys
        invoice_id = data.get("invoice_no")
        pno = data.get("pno")
        autoid = data.get("autoid")
        permission = data.get("permission")

        if not SellinvoiceTable.objects.filter(invoice_no=invoice_id).exists():
            return Response({"error": "Invoice not found"}, status=status.HTTP_400_BAD_REQUEST)

        if not models.SellInvoiceItemsTable.objects.filter(autoid=autoid).exists():
            return Response({"error": "Client not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch related objects
        invoice = models.SellinvoiceTable.objects.get(invoice_no=invoice_id)
        invoice_item = models.SellInvoiceItemsTable.objects.get(autoid=autoid)
        permission_obj = models.return_permission.objects.get(autoid=permission)

        if int(data.get("returned_quantity")) > (invoice_item.current_quantity_after_return if invoice_item.current_quantity_after_return is not None else invoice_item.quantity):
            return Response({"error": "Returned quantity greater than original quantity"}, status=status.HTTP_400_BAD_REQUEST)
        # Create the return permission
        returned_item_instance = models.return_permission_items.objects.create(
            pno=invoice_item.pno,
            company_no=invoice_item.company_no,
            company=invoice_item.company,
            item_name=invoice_item.name,
            org_quantity=invoice.quantity,
            returned_quantity=data.get("returned_quantity") if data.get("returned_quantity") else invoice.quantity,
            price=invoice_item.dinar_unit_price,
            invoice_obj=invoice,
            invoice_no=invoice.invoice_no,
            permission_obj=permission_obj,
        )
        permission_obj.amount += returned_item_instance.total
        permission_obj.quantity+= int(data.get("returned_quantity")) if data.get("returned_quantity") else invoice.quantity
        permission_obj.save()

        if invoice_item.current_quantity_after_return is not None and invoice_item.current_quantity_after_return > 0:
            # Decrease the current quantity after return
            invoice_item.current_quantity_after_return -= int(data.get("returned_quantity"))
            invoice_item.save()
        elif invoice_item.current_quantity_after_return in (None, 0):
            # Set the current quantity after return to the original quantity minus returned quantity
            invoice_item.current_quantity_after_return = invoice_item.quantity - int(data.get("returned_quantity"))
            invoice_item.save()

        try:
            mainitem = models.Mainitem.objects.get(pno=pno if pno else invoice_item.pno)
            mainitem.itemvalue += data.get("returned_quantity") if data.get("returned_quantity") else invoice.quantity
            mainitem.save()
        except models.Mainitem.DoesNotExist:
            return Response({"error": "Product not found in products"}, status=status.HTTP_400_BAD_REQUEST)
        except models.Mainitem.MultipleObjectsReturned:
            return Response({"error": "Api returned multiple objects for pno"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Product in products caused an error!"}, status=status.HTTP_400_BAD_REQUEST)


        last_balance = (
            models.TransactionsHistoryTable.objects.filter(client_id_id=invoice.client_id)
            .order_by("-registration_date")
            .first()
        )
        last_balance_amount = last_balance.current_balance if last_balance else 0

        try:
            models.TransactionsHistoryTable.objects.create(
                credit=Decimal(returned_item_instance.total),
                debt=0.0,
                transaction=f"ترجيع بضائع - ر.خ : {invoice_item.pno}",
                details=f"ترجيع بضاتع - فاتورة رقم {invoice_item.invoice_no}",
                registration_date=timezone.now(),
                current_balance=round(last_balance_amount, 2) + Decimal(returned_item_instance.total),  # Updated balance
                client_id_id=invoice.client_id,  # Client ID
            )
        except:
            return Response({"error": "error in transaction saving!"}, status=status.HTTP_400_BAD_REQUEST)


        if permission_obj.payment == "نقدي":
            try:
                client_object = AllClientsTable.objects.get(clientid=invoice.client_id)
                models.StorageTransactionsTable.objects.create(
                    reciept_no=f"ف.ب : {invoice_item.invoice_no}",
                    transaction_date=timezone.now(),
                    amount=Decimal(returned_item_instance.total),
                    issued_for="اذن ترجيع",
                    note=f" ترجيع بضائع - ر.خ : {invoice_item.pno}",
                    account_type="عميل",
                    transaction=f" ترجيع بضائع - ر.خ : {invoice_item.pno}",
                    place="مارين",
                    section="ترجيع",
                    subsection="ترجيع",
                    person=client_object.name or "",
                    payment= "نقدا" if permission_obj.payment == "نقدي" else "اجل",
                    daily_status =False,
                )
            except:
                return Response({"error": "error in storage saving!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            movement_Record = models.Clientstable.objects.create(
                itemno=mainitem.itemno,
                itemname=mainitem.itemname,
                maintype=mainitem.itemmain,
                currentbalance=mainitem.itemvalue,
                date=timezone.now(),
                clientname=client_object.name or "",
                #billno="",
                description="ترجيع صنف من فاتورة بيع",
                clientbalance=int(data.get("returned_quantity")) or 0,
                pno_instance=mainitem,
                pno=mainitem.pno,
            )
        except Exception as e:
            return Response({
                "message": "Error in product history saving!",
                "error": str(e)  # Convert the exception to a string for better readability
            }, status=status.HTTP_400_BAD_REQUEST)
        # Serialize and return the created object
        serializer = self.get_serializer(returned_item_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(['GET'])
def get_invoice_returned_items(request,id):
    returned_items = models.return_permission_items.objects.filter(invoice_no=id)
    invoice = SellinvoiceTable.objects.get(invoice_no=id)
    serializer = serializers.ReturnPermissionItemsSerializer(returned_items,many=True)
    return Response({
        'data':serializer.data,
        'invoice_total':invoice.amount,
        'invoice_paid':invoice.paid_amount,
        }, status=status.HTTP_200_OK)



@api_view(["POST"])
def filter_return_reqs(request):
    try:
        filters = request.data  # DRF automatically parses the JSON body
        query_filter = Q()  # Initialize an empty Q object for combining filters

        # Apply client-name filter if provided
        if 'client' in filters:
            query_filter &= Q(client__clientid__icontains=filters['client'])

        # Apply payment filter if provided
        if 'payment' in filters:
            query_filter &= Q(payment__icontains=filters['payment'])

        # Apply date range filter if fromdate and todate are provided
        fromdate = filters.get('fromdate', '').strip()
        todate = filters.get('todate', '').strip()

        if fromdate and todate:
            try:
                from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)
                query_filter &= Q(date__range=[from_date_obj, to_date_obj])
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        # Query the model with the combined filters
        queryset = models.return_permission.objects.filter(query_filter)
        serializer = serializers.ReturnPermissionSerializer(queryset,many=True)

        # If no matching records, return an empty list
        if not queryset.exists():
            return Response([], status=status.HTTP_200_OK)

        # Serialize and return the filtered data
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

""" Employee Related Api's """
# 📌 View all available employees
@api_view(['GET'])
def available_employees(request):
    employees = EmployeesTable.objects.filter(is_available=True)
    serializer = serializers.EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=200)



""" Payment Request Api's """


@api_view(["POST"])
def accept_payment_req(request, id):
    """Accept or reject a payment request from a client."""
    try:
        # Get loan amount from request body
        data = request.data
        loan_amount = Decimal(data.get('loan_amount', 0))

        # Fetch the payment request from the database
        req = models.PaymentRequestTable.objects.get(autoid=id)

        # Check action type (accept/reject)
        if data.get('action') == "accept":
            if loan_amount <= 0:
                return Response({"error": "Invalid loan amount."}, status=status.HTTP_400_BAD_REQUEST)

            # Start a database transaction to ensure atomicity
            with transaction.atomic():
                req.accepted_amount = loan_amount
                req.accepted = True
                req.rejected = False
                req.accept_date = timezone.now()
                req.save()

                # Fetch last balance
                last_balance = (
                    models.TransactionsHistoryTable.objects.filter(client_id_id=req.client.clientid)
                    .order_by("-registration_date")
                    .first()
                )
                last_balance_amount = last_balance.current_balance if last_balance else 0

                # Save the transaction record
                try:
                    models.TransactionsHistoryTable.objects.create(
                        credit=0.0,
                        debt=loan_amount,
                        transaction="طلب قيمة مالية",
                        details="طلب قيمة مالية",
                        registration_date=timezone.now(),
                        current_balance=round(last_balance_amount + loan_amount, 2),  # Updated balance
                        client_id_id=req.client.clientid,  # Client ID
                    )
                except Exception as e:
                    return Response({"error": f"Error in transaction saving: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Payment request accepted successfully"})

        elif data.get('action') == "reject":
            with transaction.atomic():
                req.rejected = True
                req.accepted = False
                req.accepted_amount = 0
                req.accept_date = timezone.now()
                req.save()

            return Response({"message": "Payment request has been rejected!"})

        else:
            return Response({"error": "Invalid action. Action must be 'accept' or 'reject'."},
                            status=status.HTTP_400_BAD_REQUEST)

    except models.PaymentRequestTable.DoesNotExist:
        return Response({"error": "Payment request not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


""" Sources Related Api's """


@api_view(['POST'])
def create_source_record(request):
    data = request.data  # Use DRF's request.data

    # Ensure the phone number is provided
    if not data.get('phone'):
        return Response({'status': 'error', 'message': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the phone number already exists
    existing_phones = User.objects.values_list('username', flat=True)
    if data.get('phone') in existing_phones:
        return Response({'status': 'error', 'message': 'Phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    # Hash the password
    password = make_password(data.get('password'))
    is_correct = check_password(data.get('password'), password)

    # Create and save the user
    try:
        user = User.objects.create_user(username=data.get('phone'), email=data.get('email'), password=data.get('password'))
        user.full_clean()  # Validate user fields
        user.save()
    except ValidationError as e:
        return Response({'status': 'error', 'message': f'Validation Error: {e.message_dict}'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new source record (AllSourcesTable)
    new_item = models.AllSourcesTable(
        name=data.get('client_name', '').strip() or None,
        address=data.get('address', '').strip() or None,
        email=data.get('email', '').strip() or None,
        website=data.get('website', '').strip() or None,
        phone=data.get('phone', '').strip() or None,
        mobile=data.get('mobile', '').strip() or None,
        last_transaction_amount=data.get('last_transaction', '0').strip() or '0',
        accountcurr=data.get('currency', '').strip() or None,
        type="مورد",
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

    # Validate and save the new source record (AllSourcesTable)
    try:
        new_item.full_clean()  # Ensure the object is valid before saving
        new_item.save()
    except ValidationError as e:
        return Response({'status': 'error', 'message': f'Validation Error: {e.message_dict}'}, status=status.HTTP_400_BAD_REQUEST)

    # Return success response
    return Response({'status': 'success', 'message': 'Record created successfully!', 'p': password, 'is_correct': is_correct}, status=status.HTTP_201_CREATED)



# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

""" Notifications Related Api's """

@api_view(['POST'])
def register_fcm_token(request):
    """
    Register an FCM token for a user (Employee or Client).
    """
    user_id = request.data.get('user_id')
    user_type = request.data.get('user_type')  # 'employee' or 'client'
    fcm_token = request.data.get('fcm_token')

    if not user_id or not user_type or not fcm_token:
        return Response({"error": "Missing user_id, user_type, or fcm_token"}, status=400)

    if user_type == 'employee':
        user = EmployeesTable.objects.filter(employee_id=user_id).first()
    elif user_type == 'client':
        user = AllClientsTable.objects.filter(clientid=user_id).first()
    else:
        return Response({"error": "Invalid user_type"}, status=400)

    if not user:
        return Response({"error": "User not found"}, status=404)

    user.fcm_token = fcm_token
    user.save()
    return Response({"message": "FCM token registered successfully"}, status=200)


@api_view(['POST'])
def send_notification(request):
    """
    Send an FCM notification to an Employee or Client.
    """
    user_id = request.data.get('user_id')
    user_type = request.data.get('user_type')  # 'employee' or 'client'
    title = request.data.get('title')
    body = request.data.get('body')

    if not user_id or not user_type or not title or not body:
        return Response({"error": "Missing required fields"}, status=400)

    if user_type == 'employee':
        user = EmployeesTable.objects.filter(employee_id=user_id).first()
    elif user_type == 'client':
        user = AllClientsTable.objects.filter(clientid=user_id).first()
    else:
        return Response({"error": "Invalid user_type"}, status=400)

    if not user or not user.fcm_token:
        return Response({"error": "User not found or no FCM token"}, status=404)

    # Construct the Firebase message
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=user.fcm_token
    )

    try:
        response = messaging.send(message)
        return Response({"message": "Notification sent successfully", "firebase_response": response}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

def send_invoice_notification(invoice, status_message):
    """Send a notification when invoice status changes."""
    channel_layer = get_channel_layer()

    # Group send to 'notifications' channel group
    async_to_sync(channel_layer.group_send)(
        "notifications",  # The name of the WebSocket group
        {
            "type": "send_notification",  # This corresponds to a function in your consumer to handle the message
            "message": f"Invoice {invoice.invoice_no} status changed to {status_message}",
            "invoice_id": invoice.invoice_no,
            "new_status": status_message
        }
    )

@api_view(['POST'])
def store_fcm_token(request):
    if request.method == 'POST':
        # Extract the data from the request
        user_id = request.data.get('user_id')
        fcm_token = request.data.get('fcm_token')
        role = request.data.get('role')

        # Validate that necessary fields are provided
        if not user_id or not fcm_token or not role:
            return Response({"error": "user_id, fcm_token, and role are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Based on the role, store the FCM token in the appropriate table
        if role == 'client':
            try:
                # Try to find the client in AllClientsTable
                client = AllClientsTable.objects.get(clientid=user_id)
                client.fcm_token = fcm_token
                client.save()

                return Response({"message": "FCM Token successfully stored for client."}, status=status.HTTP_200_OK)
            except AllClientsTable.DoesNotExist:
                return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

        elif role == 'employee':
            try:
                # Try to find the employee in EmployeesTable
                employee = EmployeesTable.objects.get(employee_id=user_id)
                employee.fcm_token = fcm_token
                employee.save()

                return Response({"message": "FCM Token successfully stored for employee."}, status=status.HTTP_200_OK)
            except EmployeesTable.DoesNotExist:
                return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"error": "Invalid role. Role should be 'client' or 'employee'."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def upload_maintype_logo(request, id):
    if 'logo' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    image = request.FILES['logo']

    try:
        maintype = models.Maintypetable.objects.get(fileid=id)
        maintype.logo_obj = image  # Assign the file object directly
        maintype.save()
        return Response({"message": "Logo uploaded successfully!"}, status=status.HTTP_200_OK)

    except models.Maintypetable.DoesNotExist:
        return Response({"error": "Maintypetable entry not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def upload_company_logo(request, id):
    if 'logo' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    image = request.FILES['logo']

    try:
        company = models.Companytable.objects.get(fileid=id)
        company.logo_obj = image  # Assign the file object directly
        company.save()
        return Response({"message": "Logo uploaded successfully!"}, status=status.HTTP_200_OK)

    except models.Companytable.DoesNotExist:
        return Response({"error": "Companytable entry not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_today_storage(request):
    try:
        # Fetch records from StorageTransactionsTable where transaction_date is today
        today = now().date()
        items = models.StorageTransactionsTable.objects.filter(transaction_date=today)

        # Serialize data
        serializer = serializers.StorageTransactionSerializer(items, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_all_storage(request):
    try:
        # Fetch records from StorageTransactionsTable where transaction_date is today
        today = now().date()
        items = models.StorageTransactionsTable.objects.all()

        # Serialize data
        serializer = serializers.StorageTransactionSerializer(items, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def filter_all_storage(request):
    try:
        filters = request.data  # Decode JSON payload
        query = Q()

        # Apply filters dynamically
        if filters.get("id"):
            query &= Q(storageid__icontains=filters["id"])
        if filters.get("client"):
            query &= Q(person__icontains=filters["client"])
        if filters.get("account_detail"):
            query &= Q(issued_for__icontains=filters["account_detail"])
        if filters.get("section"):
            query &= Q(section__icontains=filters["section"])
        if filters.get("subsection"):
            query &= Q(subsection__icontains=filters["subsection"])
        if filters.get("type"):
            query &= Q(account_type__icontains=filters["type"])
        if filters.get("transaction"):
            query &= Q(transaction__icontains=filters["transaction"])
        if filters.get("payment"):
            query &= Q(payment__icontains=filters["payment"])
        if filters.get("place"):
            query &= Q(place__icontains=filters["place"])

        # Date range filter
        fromdate = filters.get('fromdate', '').strip()
        todate = filters.get('todate', '').strip()
        if fromdate and todate:
            try:
                from_date_obj = make_aware(datetime.strptime(fromdate, "%Y-%m-%d"))
                to_date_obj = make_aware(datetime.strptime(todate, "%Y-%m-%d")) + timedelta(days=1) - timedelta(seconds=1)
                query &= Q(transaction_date__range=[from_date_obj, to_date_obj])
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch filtered results
        queryset = models.StorageTransactionsTable.objects.filter(query)

        # Serialize data
        serializer = serializers.StorageTransactionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
