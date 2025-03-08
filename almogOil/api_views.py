from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
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
from .models import Mainitem,OrderQueue,EmployeeQueue,SupportChatConversation,SellinvoiceTable,SupportChatMessageSys, AllClientsTable,Feedback,EmployeesTable
from .serializers import MainitemSerializer,EmployeeSerializer,OrderSerializer,SupportChatConversationSerializer1,SellInvoiceSerializer, SupportChatMessageSysSerializer1, AllClientsTableSerializer,FeedbackSerializer
from rest_framework.exceptions import NotFound
from django.utils.timezone import now
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.dispatch import receiver
from rest_framework.decorators import action
from django.db import transaction


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

class CustomPagination(PageNumberPagination):
    page_size = 10  # Limit the results to 10 per page
    page_size_query_param = 'page_size'
    max_page_size = 100

def filter_Items(request):
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
    items = Mainitem.objects.filter(**filters)

    # Check if any items are found
    if not items.exists():
        return Response({"message": "No items found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)

    # Apply pagination
    paginator = CustomPagination()
    paginated_items = paginator.paginate_queryset(items, request)

    # Serialize the filtered and paginated items
    serializer = MainitemSerializer(paginated_items, many=True)

    # Return the paginated data as the response
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def support_conversations(request):
    if request.method == 'GET':
        conversations = SupportChatConversation.objects.all()
        serializer = SupportChatConversationSerializer1(conversations, many=True)
        return Response({'conversations': serializer.data})

# Get Messages in a Conversation
@api_view(['GET'])
def get_conversation_messages(request, conversation_id):
    if request.method == 'GET':
        try:
            conversation = SupportChatConversation.objects.get(conversation_id=conversation_id)
            messages = SupportChatMessageSys.objects.filter(conversation=conversation)
            serializer = SupportChatMessageSysSerializer1(messages, many=True)
            return Response({'messages': serializer.data})
        except SupportChatConversation.DoesNotExist:
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
                conversation = SupportChatConversation.objects.get(conversation_id=conversation_id)
            except SupportChatConversation.DoesNotExist:
                return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If no conversation_id, create a new conversation (assuming client sends message)
            client_id = request.data.get('client_id')  # Expect client_id in the request if no conversation_id
            try:
                client = AllClientsTable.objects.get(clientid=client_id)
                # Create a new conversation without support agent
                conversation = SupportChatConversation.objects.create(
                    client=client,
                    support_agent=None  # No support agent in this conversation
                )
            except AllClientsTable.DoesNotExist:
                return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create the message
        message = SupportChatMessageSys.objects.create(
            conversation=conversation,
            sender=conversation.client,  # Only the client is sending the message
            sender_type='client',  # 'client' is the sender type
            message=message_text,
            timestamp=timezone.now(),
            is_read=False
        )

        message_serializer = SupportChatMessageSysSerializer1(message)

        return Response({
            'message': 'Message sent successfully',
            'message_data': message_serializer.data
        }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_all_clients1(request,id=None):
    if request.method == 'GET':
        clients = AllClientsTable.objects.all().filter(clientid=id)
        serializer = AllClientsTableSerializer(clients, many=True)
        return Response({'clients': serializer.data})

@api_view(['POST'])
def start_conversation(request, client_id):
    if request.method == 'POST':
        try:
            # Get the client
            client = AllClientsTable.objects.get(clientid=client_id)

            # Check if there's already an existing conversation with the client
            existing_conversation = SupportChatConversation.objects.filter(client=client)
            if existing_conversation.exists():
                return Response({'error': 'Conversation already exists with this client'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new conversation with the support agent (request.user)
            conversation = SupportChatConversation.objects.create(
                client=client,
                support_agent=request.user
            )

            # Now, send the first message to start the conversation
            first_message = request.data.get('message')
            if not first_message:
                return Response({'error': 'Message is required to start a conversation'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the first message in the conversation
            message = SupportChatMessageSys.objects.create(
                conversation=conversation,
                sender=request.user,  # Assuming the support agent is the sender
                sender_type='support',  # Type 'support' for the agent
                message=first_message,
                timestamp=timezone.now(),
                is_read=False
            )

            message_serializer = SupportChatMessageSysSerializer1(message)

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
    feedback = Feedback(sender=client, feedback_text=feedback_text)
    feedback.save()

    # Return the created feedback data in response
    return Response(FeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def respond_to_feedback(request, client_id):
    if request.method == 'POST':
        try:
            client = AllClientsTable.objects.get(id=client_id)
            feedback = Feedback.objects.filter(sender=client).last()  # Get latest feedback
        except (AllClientsTable.DoesNotExist, Feedback.DoesNotExist):
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
    serializer = SellInvoiceSerializer(invoices, many=True)
    return Response(serializer.data)


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
        order_queue = OrderQueue.objects.create(employee=employee, order=assigned_order, is_accepted=True)

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
        order_queue = OrderQueue.objects.get(id=queue_id)

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

    except OrderQueue.DoesNotExist:
        return Response({"error": "Order queue entry not found."}, status=404)


@api_view(['POST'])
def decline_order(request, queue_id):
    try:
        # Fetch the order queue entry by ID
        order_queue = OrderQueue.objects.get(id=queue_id)

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
            OrderQueue.objects.create(employee=next_available_employee, order=order)

        # Mark the employee as available again and reset the active order flag
        employee = order_queue.employee
        employee.is_available = True
        employee.has_active_order = False  # Reset the active order flag
        employee.save()

        return Response({
            "message": "Order declined. The next available employee will take it."
        })

    except OrderQueue.DoesNotExist:
        return Response({"error": "Order queue entry not found."}, status=404)

@api_view(['POST'])
def deliver_order(request, queue_id):
    try:
        # Fetch the order queue entry by ID
        order_queue = OrderQueue.objects.get(id=queue_id)

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

    except OrderQueue.DoesNotExist:
        return Response({"error": "Order queue entry not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def skip_order(request, queue_id):
    try:
        # Fetch the order queue entry by ID
        order_queue = OrderQueue.objects.get(id=queue_id)

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
        OrderQueue.objects.create(employee=next_available_employee, order=order_queue.order)

        return Response({
            "message": "Order skipped. The next available employee will take it."
        })

    except OrderQueue.DoesNotExist:
        return Response({"error": "Order queue entry not found."}, status=404)


@api_view(['GET', 'POST'])
def UpdateItemsItemmainApiView(request, item_id):
    try:
        # Retrieve the item by its ID
        item = models.Mainitem.objects.get(pno=item_id)
    except models.Mainitem.DoesNotExist:
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
                return Response(serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        elif action == "remove":
            # Remove value from list
            if value in itemmain_list:
                itemmain_list.remove(value)
                item.itemmain = ";".join(itemmain_list)
                item.save()
                return Response(serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    # Default GET method to show current itemmain value
    elif request.method == 'GET':
        s_data = serializers.MainitemSerializer(item).data
        itemmain = s_data['itemmain']
        return Response({'itemmain': itemmain}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def UpdateItemsSubmainApiView(request, item_id):
    try:
        # Retrieve the item by its ID
        item = models.Mainitem.objects.get(pno=item_id)
    except models.Mainitem.DoesNotExist:
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
                return Response(serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        elif action == "remove":
            # Remove value from list
            if value in itemsub_list:
                itemsub_list.remove(value)
                item.itemsubmain = ";".join(itemsub_list)
                item.save()
                return Response(serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    # Default GET method to show current itemmain value
    elif request.method == 'GET':
        s_data = serializers.MainitemSerializer(item).data
        itemsubmain = s_data['itemsubmain']
        return Response({'itemsub': itemsubmain}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def UpdateItemsModelApiView(request, item_id):
    try:
        # Retrieve the item by its ID
        item = models.Mainitem.objects.get(pno=item_id)
    except models.Mainitem.DoesNotExist:
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
                return Response(serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        elif action == "remove":
            # Remove value from list
            if value in model_list:
                model_list.remove(value)
                item.itemthird = ";".join(model_list)
                item.save()
                return Response(serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    # Default GET method to show current itemmain value
    elif request.method == 'GET':
        s_data = serializers.MainitemSerializer(item).data
        itemthird = s_data['itemthird']
        return Response({'models': itemthird}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def UpdateItemsEngineApiView(request, item_id):
    try:
        # Retrieve the item by its ID
        item = models.Mainitem.objects.get(pno=item_id)
    except models.Mainitem.DoesNotExist:
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
                return Response(serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        elif action == "remove":
            # Remove value from list
            if value in engine_list:
                engine_list.remove(value)
                item.engine_no = ";".join(engine_list)
                item.save()
                return Response(serializers.MainitemSerializer(item).data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    # Default GET method to show current itemmain value
    elif request.method == 'GET':
        s_data = serializers.MainitemSerializer(item).data
        engines = s_data['engine_no']
        return Response({'engines': engines}, status=status.HTTP_200_OK)


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


from rest_framework import generics, mixins,viewsets


from rest_framework import viewsets, status
from rest_framework.response import Response
from decimal import Decimal
from . import models, serializers
from .models import AllClientsTable, SellinvoiceTable

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
            models.TransactionsHistoryTable.objects.filter(client_id_id=invoice.client)
            .order_by("-registration_date")
            .first()
        )
        last_balance_amount = last_balance.current_balance if last_balance else 0
        if invoice.payment_status == "نقدي":
            try:
                models.TransactionsHistoryTable.objects.create(
                    credit=Decimal(returned_item_instance.total),
                    debt=0.0,
                    transaction=f"ترجيع بضائع - ر.خ : {invoice_item.pno}",
                    details=f"ترجيع بضاتع - فاتورة رقم {invoice_item.invoice_no}",
                    registration_date=timezone.now(),
                    current_balance=round(last_balance_amount, 2) + Decimal(returned_item_instance.total),  # Updated balance
                    client_id_id=invoice.client,  # Client ID
                    )
            except:
                return Response({"error": "error in transaction saving!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client_object = AllClientsTable.objects.get(clientid=invoice.client)
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
                payment= "نقدا" if invoice.payment_status == "نقدي" else "اجل",
                daily_status =False,
            )
        except:
            return Response({"error": "error in storage saving!"}, status=status.HTTP_400_BAD_REQUEST)
        # Serialize and return the created object
        serializer = self.get_serializer(returned_item_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnginesTableViewSet(viewsets.ModelViewSet):
    queryset = models.enginesTable.objects.all()
    serializer_class = serializers.EnginesTableSerializer

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
        if not EmployeeQueue.objects.filter(employee=employee).exists():
            # Get the number of available employees in the queue to set the position
            queue_position = EmployeeQueue.objects.filter(is_available=True).count() + 1
            # Add to queue
            EmployeeQueue.objects.create(employee=employee, position=queue_position, is_assigned=False, is_available=True)
            message = f"Employee {employee.employee_id} is now available and added to the queue as position {queue_position}."
        else:
            message = f"Employee {employee.employee_id} is already in the queue."
    else:
        # If the employee is unavailable, remove them from the queue
        queue_entry = EmployeeQueue.objects.filter(employee=employee, is_available=True).first()
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
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=200)


# 📌 View all available employees
@api_view(['GET'])
def available_employees(request):
    employees = EmployeesTable.objects.filter(is_available=True)
    serializer = EmployeeSerializer(employees, many=True)
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

    # Add to queue if not already present
    if not EmployeeQueue.objects.filter(employee=employee).exists():
        queue_position = EmployeeQueue.objects.filter(is_available=True).count() + 1
        EmployeeQueue.objects.create(employee=employee, position=queue_position, is_assigned=False, is_available=True)
        message = f"Employee {employee.employee_id} is now available and added to the queue at position {queue_position}."
    else:
        message = f"Employee {employee.employee_id} is already in the queue."

    return Response({
        "message": message,
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
    queue_entry = EmployeeQueue.objects.filter(employee=employee, is_available=True).first()
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
    """Clear all employees from the queue and set all employees as unavailable"""

    # Clear the queue
    deleted_count, _ = EmployeeQueue.objects.all().delete()

    # Set all employees' is_available to False
    updated_count = EmployeesTable.objects.filter(is_available=True).update(is_available=False)
    updated_count = EmployeesTable.objects.filter( has_active_order=True).update( has_active_order=False)

    return Response({
        "message": "Employee queue has been cleared and all employees are now unavailable.",
        "deleted_queue_entries": deleted_count,
        "updated_employees": updated_count
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
def mainitem_add_json_desc(request, id):
    """Add JSON description to a Mainitem product"""
    try:
        data = request.data
        json_data = data.get('json')

        # Parse the JSON data
        parsed_json = json.loads(json_data) if isinstance(json_data, str) else json_data

        # Retrieve the product
        product = models.Mainitem.objects.get(pno=id)
        product.json_description = parsed_json  # Assuming this field is a JSONField
        product.save()

        return Response({"message": "JSON description updated successfully"}, status=status.HTTP_200_OK)

    except models.Mainitem.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
