# serializers.py
from rest_framework import serializers
from . import models
from .models import SupportMessage

class MainitemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mainitem
        fields = [
            'fileid', 'itemno', 'itemmain', 'itemsubmain', 'itemname', 'eitemname', 'companyproduct',
            'replaceno', 'pno', 'barcodeno', 'memo', 'itemsize', 'itemperbox', 'itemthird', 'itemvalue',
            'itemtemp', 'itemvalueb', 'resvalue', 'itemplace', 'orgprice', 'orderprice', 'costprice',
            'buyprice', 'lessprice'
        ]

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

class SubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subtypetable
        fields = "__all__"


class MainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Maintypetable
        fields = "__all__"

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Modeltable
        fields = "__all__"

class EngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.enginesTable
        fields = "__all__"

        class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllClientsTable
        fields = ['id', 'username', 'email']

class SupportMessageSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)  # Display client details in response
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=AllClientsTable.objects.all(), write_only=True, source='client'
    )

    class Meta:
        model = SupportMessage
        fields = ['id', 'client', 'client_id', 'message', 'timestamp', 'support_response', 'responded_at']