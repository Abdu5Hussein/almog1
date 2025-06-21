from django.test import TestCase

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
from decimal import Decimal
from django.utils import timezone

from almogOil import models as m
from django.contrib.auth.models import User


class SellInvoiceItemCreationTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

        self.source = m.AllSourcesTable.objects.create(name='TestSource')
        self.client_obj = m.AllClientsTable.objects.create(
            name="Test Client", mobile="218912345678", discount=Decimal("0.1"), delivery_price=Decimal("5.0")
        )
        self.product = m.Mainitem.objects.create(
            pno="P001", fileid="F001", itemno="I001",
            itemname="Test Item", showed=10,
            buyprice=Decimal("2.0"), costprice=Decimal("1.5"),
            itemmain="Main", itemsubmain="Sub",
            itemplace="Store", companyproduct="Company",
            eitemname="E001", source=self.source,
            source_pno="SP001", itemvalue=50
        )
        self.invoice = m.PreOrderTable.objects.create(
            invoice_no="INV001", client=self.client_obj, amount=Decimal("0.0"), net_amount=Decimal("0.0")
        )
        self.url = reverse('full_Sell_invoice_create_item')  # OR use the direct path if not named

    @patch('almogOil.views.send_whatsapp_message_via_green_api')
    def test_create_invoice_item_success(self, mock_whatsapp):
        mock_whatsapp.return_value = {"idMessage": "msg123"}

        payload = {
            "pno": self.product.pno,
            "fileid": self.product.fileid,
            "invoice_id": self.invoice.invoice_no,
            "itemvalue": 2,
            "sellprice": "5.0"
        }

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("item_id", response.data)
        self.assertTrue(response.data["whatsapp_sent"])
        self.assertEqual(response.data["left item"], 8)

    def test_missing_fields(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Missing required fields", response.data["error"])

    def test_invalid_product(self):
        payload = {
            "pno": "WrongPno",
            "fileid": "F001",
            "invoice_id": self.invoice.invoice_no,
            "itemvalue": 1,
            "sellprice": "5.0"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Product not found")

    def test_invalid_invoice(self):
        payload = {
            "pno": self.product.pno,
            "fileid": self.product.fileid,
            "invoice_id": "INVALID_ID",
            "itemvalue": 1,
            "sellprice": "5.0"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Invoice not found")

    def test_insufficient_quantity(self):
        payload = {
            "pno": self.product.pno,
            "fileid": self.product.fileid,
            "invoice_id": self.invoice.invoice_no,
            "itemvalue": 100,
            "sellprice": "5.0"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Insufficient quantity available")

    def test_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

