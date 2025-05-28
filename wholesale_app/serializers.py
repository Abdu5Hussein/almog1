from rest_framework import serializers
from almogOil import models as almogOil_models

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

