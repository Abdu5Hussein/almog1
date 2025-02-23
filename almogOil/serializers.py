# serializers.py
from rest_framework import serializers
from . import models

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