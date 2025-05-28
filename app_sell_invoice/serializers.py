# serializers.py
from django.utils.timezone import localtime
from rest_framework import serializers
from almogOil import models
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

class SellInvoiceSerializer(serializers.ModelSerializer):
    invoice_date = serializers.SerializerMethodField()

    class Meta:
        model = models.SellinvoiceTable
        fields = "__all__"

    def get_invoice_date(self, obj):
        return obj.invoice_date.strftime("%Y-%m-%d") if obj.invoice_date else None   # Ensure "YYYY-MM-DD" format

    def get_delivered_date(self, obj):
        if obj.delivered_date:
            return localtime(obj.delivered_date).strftime('%Y-%m-%d %H:%M')
        return None

class SellInvoiceItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SellInvoiceItemsTable
        fields = "__all__"