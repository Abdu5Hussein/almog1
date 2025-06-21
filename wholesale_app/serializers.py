from rest_framework import serializers
from almogOil import models as almogOil_models
from django.db import models


class PreOrderTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.PreOrderTable
        fields = '__all__'

class PreOrderItemsTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.PreOrderItemsTable
        fields = '__all__'


class OrderBuyInvoiceItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.OrderBuyInvoiceItemsTable
        fields = '__all__'

class OrderBuyinvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.OrderBuyinvoicetable
        fields = '__all__'        

class PreorderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", default="Unknown")

    class Meta:
        model = almogOil_models.PreOrderTable
        fields = '__all__'  # Or list specific fields        

class OemTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.Oemtable
        fields = ['fileid', 'cname', 'cno', 'oemno']       



class AllClientsTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.AllClientsTable
        fields = '__all__'



class PreOrderTableSerializerCart(serializers.ModelSerializer):
    client = AllClientsTableSerializer()
    preorderitems = serializers.SerializerMethodField()

    class Meta:
        model = almogOil_models.PreOrderTable
        fields = '__all__'

    def get_preorderitems(self, obj):
        items = almogOil_models.PreOrderItemsTable.objects.filter(invoice_instance=obj)
        return PreOrderItemsTableSerializer(items, many=True).data  
          
class SimplePreOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.PreOrderTable
        fields = ['invoice_no',   'net_amount', 'date_time', 'invoice_status','shop_confrim', 'autoid'] 
        
         # customize this list
class ItemCategoryWithCountSerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = almogOil_models.ItemCategory
        fields = ("id", "name", "item_count")

class WhatsAppMessageSerializer(serializers.Serializer):
    clientid = serializers.IntegerField()
    message = serializers.CharField(max_length=2000)       

class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.TermsAndConditions
        fields = [
            'title',
            'last_updated',
            'introduction',
            'acceptance_text',
            'contact_info',
            'is_active',
            'sections'
        ]
class ReturnPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.ReturnPolicy
        fields = '__all__'


        

class MainitemSerializerHozma(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.Mainitem
        fields = [
            'fileid',
            'itemno',
            'itemmain',
            'itemsubmain',
            'itemname',
            'short_name',
            'itemthird',
            'itemsize',
            'companyproduct',
            'itemvalue',
            'itemtemp',
            'buyprice',
            'memo',
            'itemtype',
            'eitemname',
            'pno',
            'oem_numbers',
            'engine_no',
            'json_description',
            'showed',
            'category_type',
            'item_category',
            'discount',
        ]        





class ClientInfoSerializer(serializers.ModelSerializer):
    total_orders = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    client_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = almogOil_models.AllClientsTable
        fields = [
            'client_photo_url',
            'name',
            'email',
            'mobile',
            'type',
            'is_online',
            'total_orders',
            'total_amount',
            'last_activity'
        ]

    def get_total_orders(self, obj):
        return almogOil_models.PreOrderTable.objects.filter(client=obj).count()

    def get_total_amount(self, obj):
        return almogOil_models.PreOrderTable.objects.filter(client=obj).aggregate(total=models.Sum('amount'))['total'] or 0

    def get_client_photo_url(self, obj):
        request = self.context.get('request')
        if obj.client_photo and hasattr(obj.client_photo, 'url'):
            return request.build_absolute_uri(obj.client_photo.url)
        return None



class driverPreOrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_geo_location = serializers.CharField(source='client.geo_location', read_only=True)
    assigned_employee_name = serializers.CharField(source='assigned_employee.name', read_only=True)

    class Meta:
        model = almogOil_models.PreOrderTable
        fields = [
            'autoid', 'invoice_no', 'invoice_date', 'amount',
            'delivery_status', 'assigned_employee', 'assigned_employee_name',
            'client_name', 'client_geo_location', 
            'delivery_start_time', 'delivery_end_time','invoice_status','date_time','net_amount'
        ]


class AssignPreOrderSerializer(serializers.Serializer):
    invoice_no = serializers.IntegerField()
    employee_id = serializers.IntegerField()

    def validate(self, data):
        # Use invoice_no to get the preorder
        preorder = almogOil_models.PreOrderTable.objects.filter(invoice_no=data['invoice_no']).first()
        if not preorder:
            raise serializers.ValidationError("Invalid invoice number (PreOrder does not exist).")

        employee = almogOil_models.EmployeesTable.objects.filter(
            employee_id=data['employee_id'], 
            type='driver', 
            active=True
        ).first()
        if not employee:
            raise serializers.ValidationError("Invalid or inactive delivery employee.")

        data['preorder'] = preorder
        data['employee'] = employee
        return data

class DeleveryPreOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = almogOil_models.PreOrderItemsTable
        fields = ['name', 'confirm_quantity', 'item_no', 'pno', 'company', 'confirmed_delevery_quantity', 'dinar_unit_price']       