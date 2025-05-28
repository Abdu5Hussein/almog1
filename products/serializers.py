# serializers.py
from rest_framework import serializers
from almogOil import models
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

class MainitemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mainitem
        fields = '__all__'
        # fields = [
        #     'fileid', 'itemno', 'itemmain', 'itemsubmain', 'itemname', 'eitemname', 'companyproduct',
        #     'replaceno', 'pno', 'barcodeno', 'memo', 'itemsize', 'itemperbox', 'itemthird', 'itemvalue',
        #     'itemtemp', 'itemvalueb', 'resvalue', 'itemplace', 'orgprice', 'orderprice', 'costprice',
        #     'buyprice', 'lessprice',#'shortname',
        # ]


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

class EnginesTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.enginesTable
        fields = ['fileid', 'engine_name', 'maintype_str', 'subtype_str']


class productImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Imagetable
        fields = '__all__'

class SubsectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subsectionstable
        fields = '__all__'


class LostAndDamagedTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LostAndDamagedTable
        fields = '__all__'

class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ItemCategory
        fields = ['id', 'name']        