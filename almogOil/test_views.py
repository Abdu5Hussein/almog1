from django.test import TestCase
from django.urls import reverse
from almogOil.models import (
    AllClientsTable, Sectionstable, Subsectionstable, Mainitem,
    AllSourcesTable, CurrenciesTable, Buyinvoicetable, Modeltable, Subtypetable
)
import json

class TestViews(TestCase):

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_post(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)  # Redirect expected
        self.assertRedirects(response, reverse('home'))

    def test_storage_management_view(self):
        response = self.client.get(reverse('storage-management'))
        self.assertEqual(response.status_code, 200)

    def test_storage_reports_view(self):
        response = self.client.get(reverse('storage-reports'))
        self.assertEqual(response.status_code, 200)

    def test_get_subsections(self):
        section = Sectionstable.objects.create(section='Test Section')
        subsection = Subsectionstable.objects.create(subsection='Test Sub', sectionid=section)
        response = self.client.get(reverse('get-subsections'), {'section_id': section.autoid})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['subsection'], 'Test Sub')

    def test_more_details_view(self):
        item = Mainitem.objects.create(fileid=1, name='Test Item')
        response = self.client.get(reverse('more-details'), {'product_id': item.fileid})
        self.assertEqual(response.status_code, 200)
        self.assertIn('item', response.context)

    def test_buy_invoices_add(self):
        AllSourcesTable.objects.create(clientid=1, name='Test Source')
        CurrenciesTable.objects.create(name='USD')
        response = self.client.get(reverse('add-buy-invoice'))
        self.assertEqual(response.status_code, 200)

    def test_create_buy_invoice(self):
        source = AllSourcesTable.objects.create(clientid=1, name='Test Source')
        data = {
            "invoice_autoid": "INV123",
            "org_invoice_id": "ORG001",
            "source": source.clientid,
            "invoice_date": "2024-01-01",
            "arrive_date": "2024-01-10",
            "order_no": "ORD123",
            "currency": "USD",
            "currency_rate": "1.0",
            "ready_date": "2024-01-15",
            "reminder": "5",
            "temp_flag": False,
            "multi_source_flag": False
        }
        response = self.client.post(reverse('create-buy-invoice'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])

    def test_model_view(self):
        sub_type = Subtypetable.objects.create(name='SubType1')
        model = Modeltable.objects.create(model_name='Model1', subtype_fk=sub_type)
        response = self.client.get(reverse('models'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('models', response.context)

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_section_and_subsection_view(self):
        response = self.client.get(reverse('sections-and-subsections'))
        self.assertEqual(response.status_code, 200)
