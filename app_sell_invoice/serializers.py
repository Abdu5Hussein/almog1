# serializers.py
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
        return obj.invoice_date.strftime("%Y-%m-%d")  # Ensure "YYYY-MM-DD" format

class SellInvoiceItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SellInvoiceItemsTable
        fields = "__all__"