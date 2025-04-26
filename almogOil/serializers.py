# serializers.py
from rest_framework import serializers
from . import models
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

class EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmployeesTable
        fields = "__all__"

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AllClientsTable
        fields = "__all__"

class SourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AllSourcesTable
        fields = "__all__"

class StorageTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StorageTransactionsTable
        fields = "__all__"


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = models.ChatMessage
        fields = ['id', 'sender', 'receiver', 'sender_username', 'receiver_username', 'message', 'timestamp', 'is_read']

class FeedbackMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FeedbackMessage
        fields = fields = "__all__"
        read_only_fields = ['id', 'sent_at']

class SupportChatMessageSysSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username')
    conversation_id = serializers.IntegerField(source='conversation.conversation_id')

    class Meta:
        model = models.SupportChatMessageSys
        fields = ['message_id', 'conversation_id', 'sender_username', 'sender_type', 'message', 'timestamp', 'is_read']


class SupportChatConversationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.username')
    support_agent_name = serializers.CharField(source='support_agent.username')
    messages = SupportChatMessageSysSerializer(many=True)

    class Meta:
        model = models.SupportChatConversation
        fields = ['conversation_id', 'client_name', 'support_agent_name', 'messages']



class SupportChatMessageSysSerializer1(serializers.ModelSerializer):
    class Meta:
        model = models.SupportChatMessageSys
        fields = ('message_id', 'sender', 'sender_type', 'message', 'timestamp')

class SupportChatConversationSerializer1(serializers.ModelSerializer):
    client = serializers.StringRelatedField()  # Display the username
    support_agent = serializers.StringRelatedField()  # Display the username
    messages = SupportChatMessageSysSerializer(many=True, read_only=True)

    class Meta:
        model = models.SupportChatConversation
        fields = ('conversation_id', 'client', 'support_agent', 'created_at', 'updated_at', 'messages')


class AllClientsTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AllClientsTable
        fields =  "__all__"


class FeedbackSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()  # Display client name
    employee_response = serializers.CharField(required=False)  # Employee response is optional initially

    class Meta:
        model = models.Feedback
        fields = ['id', 'sender', 'feedback_text', 'created_at', 'employee_response', 'is_resolved', 'response_at']


class ReturnPermissionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = models.return_permission
        fields = "__all__"  # Include all fields

class ReturnPermissionItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.return_permission_items
        fields = "__all__"  # Include all fields


class BuyInvoiceSerializer(serializers.ModelSerializer):
    invoice_date = serializers.SerializerMethodField()

    class Meta:
        model = models.Buyinvoicetable
        fields = "__all__"

    def get_invoice_date(self, obj):
        return obj.invoice_date.strftime("%Y-%m-%d")  # Ensure "YYYY-MM-DD" format



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SellinvoiceTable
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmployeesTable
        fields = '__all__'

class EmployeeWithOrderSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)  # Assuming there is a related field for orders

    class Meta:
        model = models.EmployeesTable
        fields = ['employee_id', 'name', 'is_available', 'orders']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Clientstable
        fields = '__all__'


class TransactionsHistoryTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransactionsHistoryTable
        fields = '__all__'

class BuyInvoiceItemsTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BuyInvoiceItemsTable
        fields = '__all__'


class CostTypesTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CostTypesTable
        fields = '__all__'

class BuyinvoiceCostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BuyinvoiceCosts
        fields = '__all__'



class BalanceEditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.balance_editions
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attendance_table
        fields = '__all__'

class BasicEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmployeesTable
        # List only the basic, non-sensitive fields.
        fields = [
            'employee_id',
            'name',
            'salary',
            'start_date',
            'end_date',
            'active',
            'category',
            'notes',
            'phone',
            'address',
            'is_available',
            'has_active_order'
        ]

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    role = serializers.CharField(required=False, allow_blank=True)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

class AddToCartSerializer(serializers.Serializer):
    clientid = serializers.CharField()
    fileid = serializers.CharField()
    itemname = serializers.CharField()
    buyprice = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(required=False, default=1)
    image = serializers.CharField(required=False, allow_blank=True)
    logo = serializers.CharField(required=False, allow_blank=True)
    pno = serializers.CharField(required=False, allow_blank=True)
    itemvalue = serializers.IntegerField(required=False, default=0)


#hozma application serlizers

class PreOrderSerializer(serializers.ModelSerializer):
    invoice_date = serializers.SerializerMethodField()

    class Meta:
        model = models.PreOrderTable
        fields = "__all__"

    def get_invoice_date(self, obj):
        return obj.invoice_date.strftime("%Y-%m-%d")  # Ensure "YYYY-MM-DD" format

class PreOrderItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PreOrderItemsTable
        fields = "__all__"