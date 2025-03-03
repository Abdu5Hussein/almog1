from django.test import TestCase
from django.urls import reverse
from almogOil import models
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
        response = self.client.get(reverse('storage-records'))
        self.assertEqual(response.status_code, 200)

    def test_storage_reports_view(self):
        response = self.client.get(reverse('storage-reports'))
        self.assertEqual(response.status_code, 200)

    def test_get_subsections(self):
        section = models.Sectionstable.objects.create(section='Test Section')
        subsection = models.Subsectionstable.objects.create(subsection='Test Sub', sectionid=section)
        response = self.client.get(reverse('get_subsections'), {'section_id': section.autoid})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['subsection'], 'Test Sub')

    def test_more_details_view(self):
        item = models.Mainitem.objects.create(fileid=1, itemname='Test Item',pno=5)
        response = self.client.get(reverse('more-details'), {'product_id': item.fileid})
        self.assertEqual(response.status_code, 200)
        self.assertIn('item', response.context)

    def test_buy_invoices_add(self):
        models.AllSourcesTable.objects.create(clientid=1, name='Test Source')
        models.CurrenciesTable.objects.create(currency='USD')
        response = self.client.get(reverse('add-buy-invoice'))
        self.assertEqual(response.status_code, 200)

    def test_create_buy_invoice(self):
        source = models.AllSourcesTable.objects.create(clientid=1, name='Test Source')
        data = {
            "original_no": "95",
            "invoice_date": "2025-03-03T00:00:00Z",
            "source": str(source.clientid),
            "currency": "جنيه استرليني (£)",
            "exchange_rate": "6.00",
            "invoice_no": "66564"
        }

        response = self.client.post(
            reverse('create-buy-invoice'),
            data,
            content_type='application/json'
        )
        print("Response Data:", response.json())
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])

    def test_model_view(self):
        main = models.Maintypetable.objects.create(typename='mainType1')
        sub_type = models.Subtypetable.objects.create(subtypename='SubType1',maintype_fk=main)
        model = models.Modeltable.objects.create(model_name='Model1', subtype_fk=sub_type)
        response = self.client.get(reverse('models'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('models', response.context)

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_section_and_subsection_view(self):
        response = self.client.get(reverse('sections-and-subsections'))
        self.assertEqual(response.status_code, 200)

#new
# Test for MainCat view (Add, Edit, Delete)
    def test_add_main_type(self):
        data = {
            'action': 'add',
            'name': 'Test Main Type'
        }
        response = self.client.post(reverse('maintype'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(models.Maintypetable.objects.filter(typename='Test Main Type').exists())

    def test_edit_main_type(self):
        maintypetable = models.Maintypetable.objects.create(typename='Old Main Type')
        data = {
            'action': 'edit',
            'id': maintypetable.fileid,
            'name': 'Updated Main Type'
        }
        response = self.client.post(reverse('maintype'), data)
        maintypetable.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(maintypetable.typename, 'Updated Main Type')

    def test_delete_main_type(self):
        maintypetable = models.Maintypetable.objects.create(typename='Test Main Type')
        data = {
            'action': 'delete',
            'id': maintypetable.fileid
        }
        response = self.client.post(reverse('maintype'), data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Maintypetable.objects.filter(fileid=maintypetable.fileid).exists())

    # Test for SubCat view (Add, Edit, Delete)
    def test_add_sub_type(self):
        maintypetable = models.Maintypetable.objects.create(typename='Main Type')
        data = {
            'action': 'add',
            'sub_type-name': 'Test Sub Type',
            'sub_type-main-type': maintypetable.fileid
        }
        response = self.client.post(reverse('subtype'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(models.Subtypetable.objects.filter(subtypename='Test Sub Type').exists())

    def test_edit_sub_type(self):
        maintypetable = models.Maintypetable.objects.create(typename='Main Type')
        subtypetable = models.Subtypetable.objects.create(subtypename='Old Sub Type', maintype_fk=maintypetable)
        data = {
            'action': 'edit',
            'id': subtypetable.fileid,
            'sub_type-name': 'Updated Sub Type'
        }
        response = self.client.post(reverse('subtype'), data)
        subtypetable.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(subtypetable.subtypename, 'Updated Sub Type')

    def test_delete_sub_type(self):
        maintypetable = models.Maintypetable.objects.create(typename='Main Type')
        subtypetable = models.Subtypetable.objects.create(subtypename='Test Sub Type', maintype_fk=maintypetable)
        data = {
            'action': 'delete',
            'id': subtypetable.fileid
        }
        response = self.client.post(reverse('subtype'), data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Subtypetable.objects.filter(fileid=subtypetable.fileid).exists())

    # Test for manage_companies view (Add, Edit, Delete)
    def test_add_company(self):
        data = {
            'action': 'add',
            'name': 'Test Company'
        }
        response = self.client.post(reverse('manage_companies'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(models.Companytable.objects.filter(companyname='Test Company').exists())

    def test_edit_company(self):
        company = models.Companytable.objects.create(companyname='Old Company')
        data = {
            'action': 'edit',
            'id': company.pk,
            'name': 'Updated Company'
        }
        response = self.client.post(reverse('manage_companies'), data)
        company.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(company.companyname, 'Updated Company')

    def test_delete_company(self):
        company = models.Companytable.objects.create(companyname='Test Company')
        data = {
            'action': 'delete',
            'id': company.pk
        }
        response = self.client.post(reverse('manage_companies'), data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Companytable.objects.filter(pk=company.pk).exists())

    # # Test for manage_countries view (Add, Edit, Delete)
    # def test_add_country(self):
    #     data = {
    #         'action': 'add',
    #         'name': 'Test Country'
    #     }
    #     response = self.client.post(reverse('manage_countries'), data)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(models.Manufaccountrytable.objects.filter(countryname='Test Country').exists())

    # def test_edit_country(self):
    #     country = models.Manufaccountrytable.objects.create(countryname='Old Country')
    #     data = {
    #         'action': 'edit',
    #         'id': country.fileid,
    #         'name': 'Updated Country'
    #     }
    #     response = self.client.post(reverse('manage_countries'), data)
    #     country.refresh_from_db()
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(country.countryname, 'Updated Country')

    # def test_delete_country(self):
    #     country = models.Manufaccountrytable.objects.create(countryname='Test Country')
    #     data = {
    #         'action': 'delete',
    #         'id': country.fileid
    #     }
    #     response = self.client.post(reverse('manage_countries'), data)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertFalse(models.Manufaccountrytable.objects.filter(fileid=country.fileid).exists())

    # # Test for Measurements view (Add, Edit, Delete)
    # def test_add_measurement(self):
    #     data = {
    #         'action': 'add',
    #         'name': 'Test Measurement'
    #     }
    #     response = self.client.post(reverse('measurements'), data)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(models.MeasurementsTable.objects.filter(name='Test Measurement').exists())

    # def test_edit_measurement(self):
    #     measurement = models.MeasurementsTable.objects.create(name='Old Measurement')
    #     data = {
    #         'action': 'edit',
    #         'id': measurement.id,
    #         'name': 'Updated Measurement'
    #     }
    #     response = self.client.post(reverse('measurements'), data)
    #     measurement.refresh_from_db()
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(measurement.name, 'Updated Measurement')

    # def test_delete_measurement(self):
    #     measurement = models.MeasurementsTable.objects.create(name='Test Measurement')
    #     data = {
    #         'action': 'delete',
    #         'id': measurement.id
    #     }
    #     response = self.client.post(reverse('measurements'), data)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertFalse(models.MeasurementsTable.objects.filter(id=measurement.id).exists())



class ClientFilterTests(TestCase):
    def setUp(self):
        item = models.Mainitem.objects.get(pno=2)
        # Create some sample client records
        models.Clientstable.objects.create(
            pno=1, itemno='I001', maintype='Type1', itemname='Item 1',
            currentbalance=100, date='2023-01-01', clientname='Client A',
            billno='B001', description='Description 1', clientbalance=50, pno_instance=item
        )
        models.Clientstable.objects.create(
            pno=2, itemno='I002', maintype='Type2', itemname='Item 2',
            currentbalance=200, date='2023-01-02', clientname='Client B',
            billno='B002', description='Description 2', clientbalance=150, pno_instance=item
        )

    def test_filter_clients_with_valid_pno(self):
        response = self.client.get(reverse('filter_clients'), {'pno': 'P001'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['pno'], 'P001')

    def test_filter_clients_missing_pno(self):
        response = self.client.get(reverse('filter_clients'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Missing pno parameter')
class OemNumbersTests(TestCase):
    def setUp(self):
        # Add a Mainitem instance
        self.mainitem = models.Mainitem.objects.create(
            fileid='1', replaceno='C001', oem_numbers='OEM1;OEM2', pno=3
        )
        self.client.session['oem_company_name'] = 'Company A'
        self.client.session['oem_company_no'] = 'C001'
        self.client.session['oem_file_id'] = '1'

    def test_get_oem_numbers(self):
        response = self.client.get(reverse('oem'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('OEM1', response.content.decode())
        self.assertIn('OEM2', response.content.decode())

    def test_post_oem_numbers_add(self):
        data = {
            'action': 'add', 'company-name': 'Company A', 'company-no': 'C001', 'oem-no': 'OEM3', 'id': '1'
        }
        response = self.client.post(reverse('oem'), data)
        self.mainitem.refresh_from_db()
        self.assertIn('OEM3', self.mainitem.oem_numbers)

    def test_post_oem_numbers_edit(self):
        data = {
            'action': 'edit', 'company-name': 'Company A', 'company-no': 'C001', 'oem-no': 'OEM1', 'id': '1'
        }
        response = self.client.post(reverse('oem'), data)
        self.mainitem.refresh_from_db()
        self.assertEqual(self.mainitem.oem_numbers, 'OEM1;OEM2')

    def test_post_oem_numbers_delete(self):
        data = {
            'action': 'delete', 'company-name': 'Company A', 'company-no': 'C001', 'oem-no': 'OEM2', 'id': '1'
        }
        response = self.client.post(reverse('oem'), data)
        self.mainitem.refresh_from_db()
        self.assertEqual(self.mainitem.oem_numbers, 'OEM1')
class DeleteRecordTests(TestCase):
    def setUp(self):
        # Add a sample Mainitem
        self.mainitem = models.Mainitem.objects.create(fileid=1, itemno='I001', itemname='Item 1', pno=8)

    def test_delete_record_success(self):
        data = {'fileid': 1}
        response = self.client.post(reverse('delete_record'), data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Record deleted successfully.')
        self.assertFalse(models.Mainitem.objects.filter(fileid=1).exists())

    def test_delete_record_not_found(self):
        data = {'fileid': '2'}
        response = self.client.post(reverse('delete_record'), data, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'Record not found.')

    def test_delete_record_missing_fileid(self):
        data = {}
        response = self.client.post(reverse('delete_record'), data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], "No 'fileid' provided.")
class FilterItemsTests(TestCase):
    def setUp(self):
        # Add some sample Mainitem records
        models.Mainitem.objects.create(
            itemno='I001', itemname='Item 1', itemmain='Main 1', companyproduct='Company A', pno=2
        )
        models.Mainitem.objects.create(
            itemno='I002', itemname='Item 2', itemmain='Main 2', companyproduct='Company B', pno=9
        )

    def test_filter_items_valid(self):
        data = {
            'itemname': 'Item 1'
        }
        response = self.client.post(reverse('filter_items'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data['data']), 1)
        self.assertEqual(response_data['data'][0]['itemname'], 'Item 1')

    def test_filter_items_invalid_json(self):
        response = self.client.post(reverse('filter_items'), '{"itemno": "I001"', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid JSON format')
class FilterClientsInputTests(TestCase):
    def setUp(self):
        item = models.Mainitem.objects.get(pno=2)
        # Add some sample Clientstable records
        models.Clientstable.objects.create(
            itemno='I001', maintype='Type1', itemname='Item 1', clientname='Client A', pno=1, date='2023-01-01', pno_instance=item
        )
        models.Clientstable.objects.create(
            itemno='I002', maintype='Type2', itemname='Item 2', clientname='Client B', pno=2, date='2023-01-02', pno_instance=item
        )

    def test_filter_clients_input_valid(self):
        data = {
            'itemname': 'Item 1'
        }
        response = self.client.post(reverse('filter_clients_input'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['itemname'], 'Item 1')

    def test_filter_clients_input_invalid_json(self):
        response = self.client.post(reverse('filter_clients_input'), '{"itemname": "Item 1"', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid JSON format')
