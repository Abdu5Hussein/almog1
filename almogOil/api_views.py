from decimal import Decimal
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
from .models import SupportChatConversation,SellinvoiceTable,SupportChatMessageSys, AllClientsTable,Feedback,EmployeesTable
from .serializers import SupportChatConversationSerializer1,SellInvoiceSerializer, SupportChatMessageSysSerializer1, AllClientsTableSerializer,FeedbackSerializer
from rest_framework.exceptions import NotFound
from django.utils.timezone import now
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.dispatch import receiver
from rest_framework.decorators import action


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
    invoices = SellinvoiceTable.objects.filter(invoice_status="سلمت",mobile=True,delivery_status="جاري التوصيل")
    serializer = SellInvoiceSerializer(invoices, many=True)
    return Response(serializer.data)



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
            quantity=int(data.get("quantity")) if data.get("quantity") else None,
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
    lookup_field = 'pno'

    def create(self, request, *args, **kwargs):
        data = request.data

        # Convert and validate foreign keys
        invoice_id = data.get("invoice")
        pno = data.get("pno")
        autoid = data.get("autoid")

        if not SellinvoiceTable.objects.filter(invoice_no=invoice_id).exists():
            return Response({"error": "Invoice not found"}, status=status.HTTP_400_BAD_REQUEST)

        if not models.SellInvoiceItemsTable.objects.filter(autoid=autoid).exists():
            return Response({"error": "Client not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch related objects
        invoice = models.SellinvoiceTable.objects.get(invoice_no=invoice_id)
        invoice_item = models.SellInvoiceItemsTable.objects.get(autoid=autoid)

        # Create the return permission
        returned_item_instance = models.return_permission_items.objects.create(
            pno=invoice_item.pno,
            company_no=invoice_item.company_no,
            company=invoice_item.company,
            item_name=invoice_item.name,
            org_quantity=invoice.quantity,
            returned_quantity=data.get("quantity") if data.get("quantity") else invoice.quantity,
            price=invoice_item.dinar_unit_price,
            invoice_obj=invoice,
            invoice_no=invoice.invoice_no,
        )

        # Serialize and return the created object
        serializer = self.get_serializer(returned_item_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnginesTableViewSet(viewsets.ModelViewSet):
    queryset = models.enginesTable.objects.all()
    serializer_class = serializers.EnginesTableSerializer
