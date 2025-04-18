from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from almogOil import models
import json
from django.utils.timezone import now
from django.utils import timezone


class TestViews(TestCase):

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_post(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)  # Redirect expected
        #self.assertRedirects(response, reverse('home'))

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
        self.assertEqual(response.status_code, 302)

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
    def test_add_country(self):
        data = {
            'action': 'add',
            'name': 'Test Country'
        }
        response = self.client.post(reverse('manage_countries'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(models.Manufaccountrytable.objects.filter(countryname='Test Country').exists())

    def test_edit_country(self):
        country = models.Manufaccountrytable.objects.create(countryname='Old Country')
        data = {
            'action': 'edit',
            'id': country.fileid,
            'name': 'Updated Country'
        }
        response = self.client.post(reverse('manage_countries'), data)
        country.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(country.countryname, 'Updated Country')

    def test_delete_country(self):
        country = models.Manufaccountrytable.objects.create(countryname='Test Country')
        data = {
            'action': 'delete',
            'id': country.fileid
        }
        response = self.client.post(reverse('manage_countries'), data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Manufaccountrytable.objects.filter(fileid=country.fileid).exists())

    # # Test for Measurements view (Add, Edit, Delete)
    def test_add_measurement(self):
        data = {
            'action': 'add',
            'name': 'Test Measurement'
        }
        response = self.client.post(reverse('measurements'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(models.MeasurementsTable.objects.filter(name='Test Measurement').exists())

    def test_edit_measurement(self):
        measurement = models.MeasurementsTable.objects.create(name='Old Measurement')
        data = {
            'action': 'edit',
            'id': measurement.id,
            'name': 'Updated Measurement'
        }
        response = self.client.post(reverse('measurements'), data)
        measurement.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(measurement.name, 'Updated Measurement')

    def test_delete_measurement(self):
        measurement = models.MeasurementsTable.objects.create(name='Test Measurement')
        data = {
            'action': 'delete',
            'id': measurement.id
        }
        response = self.client.post(reverse('measurements'), data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.MeasurementsTable.objects.filter(id=measurement.id).exists())



class ClientFilterTests(TestCase):
    def setUp(self):
        models.Mainitem.objects.create(
            fileid='1', replaceno='C1', oem_numbers='OEM1;OEM2', pno=36
        )
        item = models.Mainitem.objects.get(pno=36)
        # Create some sample client records
        models.Clientstable.objects.create(
            pno=1, itemno='I1', maintype='Type1', itemname='Item 1',
            currentbalance=100, date='2023-01-01', clientname='Client A',
            billno='B1', description='Description 1', clientbalance=50, pno_instance=item
        )
        models.Clientstable.objects.create(
            pno=2, itemno='I002', maintype='Type2', itemname='Item 2',
            currentbalance=200, date='2023-01-02', clientname='Client B',
            billno='B002', description='Description 2', clientbalance=150, pno_instance=item
        )

    def test_filter_clients_with_valid_pno(self):
        response = self.client.get(reverse('filter-clients'), {'pno': '1'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['pno'], '1')

    def test_filter_clients_missing_pno(self):
        response = self.client.get(reverse('filter-clients'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Missing pno parameter')
class OemNumbersTests(TestCase):
    def setUp(self):
        # Add a Mainitem instance
        self.mainitem = models.Mainitem.objects.create(
            fileid='1', replaceno='C1', oem_numbers='OEM1;OEM2', pno=3
        )
        self.client.session['oem_company_name'] = 'Company A'
        self.client.session['oem_company_no'] = 'C1'
        self.client.session['oem_file_id'] = '1'
        self.client.session.save()  # Ensure session is saved

    # def test_get_oem_numbers(self):
    #     response = self.client.get(reverse('oem'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('OEM1', response.content.decode())
    #     self.assertIn('OEM2', response.content.decode())

    def test_post_oem_numbers_add(self):
        data = {
            'action': 'add', 'company-name': 'Company A', 'company-no': 'C1', 'oem-no': 'OEM3', 'id': '1'
        }
        response = self.client.post(reverse('oem'), data)
        self.mainitem.refresh_from_db()
        self.assertIn('OEM3', self.mainitem.oem_numbers)

    def test_post_oem_numbers_edit(self):
        data = {
            'action': 'edit', 'company-name': 'Company A', 'company-no': 'C1', 'oem-no': 'OEM1', 'id': '1'
        }
        response = self.client.post(reverse('oem'), data)
        self.mainitem.refresh_from_db()
        self.assertEqual(self.mainitem.oem_numbers, 'OEM1;OEM2')

    def test_post_oem_numbers_delete(self):
        data = {
            'action': 'delete', 'company-name': 'Company A', 'company-no': 'C1', 'oem-no': 'OEM2', 'id': '1'
        }
        response = self.client.post(reverse('oem'), data)
        self.mainitem.refresh_from_db()
        self.assertEqual(self.mainitem.oem_numbers, 'OEM1')

class DeleteRecordTests(TestCase):
    def setUp(self):
        # Add a sample Mainitem
        self.mainitem = models.Mainitem.objects.create(fileid=1, itemno='I1', itemname='Item 1', pno=8)

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
            itemno='I1', itemname='Item 1', itemmain='Main 1', companyproduct='Company A', pno=2
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
        response = self.client.post(reverse('filter_items'), '{"itemno": "I1"', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid JSON format')
class FilterClientsInputTests(TestCase):
    def setUp(self):
        models.Mainitem.objects.create(
            fileid='1', replaceno='C1', oem_numbers='OEM1;OEM2', pno=46
        )
        item = models.Mainitem.objects.get(pno=46)
        # Add some sample Clientstable records
        models.Clientstable.objects.create(
            itemno='I1', maintype='Type1', itemname='Item 1', clientname='Client A', pno=1, date='2023-01-01', pno_instance=item
        )
        models.Clientstable.objects.create(
            itemno='I002', maintype='Type2', itemname='Item 2', clientname='Client B', pno=2, date='2023-01-02', pno_instance=item
        )

    def test_filter_clients_input_valid(self):
        data = {
            'itemname': 'Item 1'
        }
        response = self.client.post(reverse('filter-client-input'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['itemname'], 'Item 1')

    def test_filter_clients_input_invalid_json(self):
        response = self.client.post(reverse('filter-client-input'), '{"itemname": "Item 1"', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid JSON format')

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
from io import BytesIO
from .models import Mainitem
import json

class ProcessExcelAndImportTests(TestCase):

    def setUp(self):
        # Prepare initial data or setup
        self.url = reverse('import_tabulator_data')

    # def test_process_excel_upload(self):
    #     # Create an Excel file to upload
    #     data = {
    #         "ItemNo": [1, 2],
    #         "ItemMain": ["Main1", "Main2"],
    #         "ItemName": ["Item1", "Item2"],
    #         "ItemValue": [100, 200],
    #         "Pno": [100, 200]  # Ensure Pno has valid values
    #     }
    #     df = pd.DataFrame(data)
    #     excel_file = BytesIO()
    #     with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    #         df.to_excel(writer, index=False)
    #     excel_file.seek(0)

    #     # Create a SimpleUploadedFile object to simulate file upload
    #     file = SimpleUploadedFile("test_file.xlsx", excel_file.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    #     # Send a POST request with the Excel file
    #     response = self.client.post(self.url, {'fileInput': file})

    #     # Check the response status and content
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('Excel data imported successfully', response.content.decode())

    #     # Verify records are created in the database
    #     self.assertEqual(Mainitem.objects.count(), 2)
    #     self.assertEqual(Mainitem.objects.first().itemno, 1)
    #     self.assertEqual(Mainitem.objects.last().itemname, "Item2")

    def test_process_tabulator_data(self):
        # Prepare the data to be sent via Tabulator
        data = [
            {
                "ItemNo": 1,
                "ItemMain": "Main1",
                "ItemName": "Item1",
                "ItemValue": 100,
                "PNo": "99"  # Ensure PNo has valid value
            },
            {
                "ItemNo": 2,
                "ItemMain": "Main2",
                "ItemName": "Item2",
                "ItemValue": 200,
                "PNo": "88"  # Ensure PNo has valid value
            }
        ]
        json_data = json.dumps(data)

        # Send a POST request with the Tabulator data
        response = self.client.post(self.url, {'data': json_data})

        # Check the response status and content
        self.assertEqual(response.status_code, 200)
        self.assertIn('Tabulator data imported successfully', response.content.decode())

        # Verify records are created in the database
        self.assertEqual(Mainitem.objects.count(), 2)  # Now we should have 4 items in the database

    def test_missing_file_or_data(self):
        # Send a POST request with no file or data
        response = self.client.post(self.url, {})

        # Check the response status and content
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid request or missing file', response.content.decode())

    def test_invalid_excel_file(self):
        # Create an invalid file type (not an Excel file)
        file = SimpleUploadedFile("invalid_file.txt", b"Invalid content", content_type="text/plain")

        # Send a POST request with the invalid file
        response = self.client.post(self.url, {'fileInput': file})

        # Check the response status and content
        self.assertEqual(response.status_code, 200)
        #self.assertIn('Excel file format cannot be determined', response.content.decode())  # Check the actual error message

from django.test import TestCase, Client
from django.urls import reverse
import json

class GeneratePDFTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('generate_pdf')  # Replace with your URL name

    def test_generate_pdf_success(self):
        # Prepare the data for the POST request
        data = {
            'data': [
                {
                    'fileid': '1',
                    'itemno': '123',
                    'itemmain': 'Main Item',
                    'itemsubmain': 'Sub Item',
                    'itemname': 'Item Name',
                    'companyproduct': 'Company Product',
                    'itemvalue': '100',
                    'memo': 'Description',
                    'replaceno': '1',
                    'barcodeno': '123456789',
                    'pno': '11',
                }
            ]
        }

        response = self.client.post(self.url, json.dumps(data), content_type="application/json")

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert that the response is a PDF
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('inline; filename="tabulator_data.pdf"'))

    def test_generate_pdf_no_data(self):
        # Test with empty data
        data = {'data': []}

        response = self.client.post(self.url, json.dumps(data), content_type="application/json")

        # Assert that the response is still a PDF, even with no data
        self.assertEqual(response.status_code, 400)

    def test_generate_pdf_invalid_method(self):
        # Test invalid method (GET instead of POST)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)  # Method Not Allowed


from django.test import TestCase, Client
from django.urls import reverse
import json
from almogOil.models import Mainitem  # Replace with the actual model import path

class EditMainItemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.item = Mainitem.objects.create(
            fileid='1',
            itemno='123',
            itemmain='Main Item',
            itemsubmain='Sub Item',
            itemname='Item Name',
            companyproduct='Company Product',
            itemvalue='100',
            memo='Description',
            pno=99
        )
        self.url = reverse('edit_main_item')  # Replace with your URL name

    def test_edit_main_item_success(self):
        # Prepare the data for the PATCH request
        data = {
            'fileid': '1',
            'originalno': '456',
            'itemmain': 'Updated Main Item',
            'itemsub': 'Updated Sub Item',
            'pnamearabic': 'اسم العنصر',
            'company': 'Updated Company',
            'sellprice': '200'
        }

        response = self.client.patch(self.url, json.dumps(data), content_type="application/json")

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the item was updated
        updated_item = Mainitem.objects.get(fileid='1')
        self.assertEqual(updated_item.itemno, '456')
        self.assertEqual(updated_item.itemmain, 'Updated Main Item')
        self.assertEqual(updated_item.companyproduct, 'Updated Company')
        self.assertEqual(updated_item.buyprice, 200)

    def test_edit_main_item_not_found(self):
        # Test for a fileid that does not exist
        data = {
            'fileid': '999',
            'originalno': '456',
            'itemmain': 'Updated Main Item',
        }

        response = self.client.patch(self.url, json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 404)  # Not Found

    def test_edit_main_item_invalid_method(self):
        # Test invalid method (POST instead of PATCH)
        data = {
            'fileid': '1',
            'originalno': '456',
            'itemmain': 'Updated Main Item',
        }

        response = self.client.post(self.url, json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 400)  # Bad Request (Invalid method)

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

class GetItemDataTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.item = Mainitem.objects.create(
            fileid='1',
            itemno='123',
            itemmain='Main Item',
            itemsubmain='Sub Item',
            itemname='Item Name',
            companyproduct='Company Product',
            itemvalue='100',
            memo='Description',
            pno=100
        )
        self.url = reverse('get_item_data', args=[self.item.fileid])  # Replace with your URL name

    def test_get_item_data_success(self):
        response = self.client.get(self.url)

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains the correct data
        self.assertEqual(response.data['fileid'], 1)
        self.assertEqual(response.data['itemno'], '123')
        self.assertEqual(response.data['itemmain'], 'Main Item')

    def test_get_item_data_not_found(self):
        # Test for a fileid that does not exist
        url = reverse('get_item_data', args=['999'])  # Non-existing fileid
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_data_invalid_method(self):
        # Test invalid method (POST instead of GET)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse
from .models import Mainitem

class CreateMainItemTest(TestCase):
    def test_create_main_item(self):
        data = {
            "originalno": "12345",
            "itemmain": "Main Category",
            "itemsub": "Sub Category",
            "pnamearabic": "اسم العنصر",
            "pnameenglish": "Item Name",
            "shortname": "ShortName",
            "company": "Company A",
            "companyno": "54321",
            "engine": "Engine123",
            "barcode": "1234567890",
            "description": "Product description",
            "location": "Warehouse A",
            "country": "Country A",
            "pieces4box": 10,
            "model": "Model A",
            "storage": 100,
            "backup": 20,
            "temp": 30,
            "reserved": 50,
            "originprice": 200.0,
            "buyprice": 180.0,
            "expensesprice": 150.0,
            "sellprice": 250.0,
            "lessprice": 10.0,
        }

        # Simulate the POST request to create an item
        response = self.client.post(reverse('create_main_item'), data, content_type="application/json")

        # Assert successful creation
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(response.json()['message'], 'Record created successfully!')

        # Verify the item was saved in the database
        self.assertTrue(Mainitem.objects.filter(itemno=data['originalno']).exists())

    def test_create_main_item_invalid_method(self):
        response = self.client.get(reverse('create_main_item'))  # Using GET instead of POST
        self.assertEqual(response.status_code, 405)  # Method not allowed
        self.assertEqual(response.json()['status'], 'error')
        self.assertEqual(response.json()['message'], 'Invalid request method.')


# class ProductsReportsTest(TestCase):
#     def test_products_reports(self):
#         response = self.client.get(reverse('products-reports'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'products-reports.html')
#         self.assertIn('company', response.context)
#         self.assertIn('columns', response.context)
#         self.assertIn('models', response.context)

#     def test_products_reports_with_invalid_method(self):
#         response = self.client.post(reverse('products-reports'))  # Using POST instead of GET
#         self.assertEqual(response.status_code, 405)
#         self.assertEqual(response.json()['message'], 'Invalid request method.')



class GetDataTest(TestCase):
    def test_get_data(self):
        response = self.client.get(reverse('get_data'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.json())
        self.assertIn('last_page', response.json())
        self.assertIn('total_rows', response.json())

    def test_get_data_with_full_table(self):
        response = self.client.get(reverse('get_data'), {'fullTable': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('fullTable', response.json())
        self.assertIn('total_itemvalue', response.json())


class UpdateItemValueTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.item = Mainitem.objects.create(
            fileid='1234',
            itemno='123',
            itemmain='Main Item',
            itemsubmain='Sub Item',
            itemname='Item Name',
            companyproduct='Company Product',
            itemvalue='100',
            memo='Description',
            pno=1234
        )

    def test_update_item_value(self):
        data = {
            'fileid': '1234',
            'newItemValue': 200
        }

        response = self.client.post(reverse('update-itemvalue'), data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(response.json()['message'], 'Item value updated successfully.')

    def test_update_item_value_item_not_found(self):
        data = {
            'fileid': '9999',  # Assuming item does not exist
            'newItemValue': 200
        }

        response = self.client.post(reverse('update-itemvalue'), data, content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'Item not found.')

    def test_update_item_value_invalid_method(self):
        response = self.client.get(reverse('update-itemvalue'))  # Using GET instead of POST
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['message'], 'Invalid request method.')

from django.test import TestCase
from django.urls import reverse
from .models import Mainitem
import json

class UpdateStorageTestCase(TestCase):
    def setUp(self):
        # Create a test Mainitem object
        self.item = Mainitem.objects.create(fileid="12345", itemplace="Old Storage",pno=22)

    def test_update_storage_success(self):
        url = reverse('update-storage')  # Replace with the actual URL name
        data = {
            "fileid": "12345",
            "storage": "New Storage"
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': True, 'message': 'storage updated successfully.'})

        # Check if the data was updated in the database
        self.item.refresh_from_db()
        self.assertEqual(self.item.itemplace, "New Storage")

    def test_update_storage_item_not_found(self):
        url = reverse('update-storage')  # Replace with the actual URL name
        data = {
            "fileid": "99999",  # This fileid doesn't exist
            "storage": "New Storage"
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': False, 'message': 'Item not found.'})


class DeleteLostDamagedTestCase(TestCase):
    def setUp(self):
        Mainitem.objects.create(fileid="12345", itemplace="Old Storage",pno=22)
        # Create a test LostAndDamagedTable record
        self.lost_damaged_item = models.LostAndDamagedTable.objects.create(
            fileid="12345", itemname="Test Item", quantity=10, costprice=100,pno_id=12345
        )

    def test_delete_lost_damaged_success(self):
        url = reverse('delete_lost_damaged')  # Replace with actual URL name
        data = {"fileid": "12345"}

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': True, 'message': 'Record deleted successfully.'})

        # Ensure that the record was deleted
        with self.assertRaises(models.LostAndDamagedTable.DoesNotExist):
            models.LostAndDamagedTable.objects.get(fileid="12345")

    def test_delete_lost_damaged_item_not_found(self):
        url = reverse('delete_lost_damaged')  # Replace with actual URL name
        data = {"fileid": "99999"}  # This fileid doesn't exist

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': False, 'message': 'Record with fileid 99999 does not exist.'})

class AddLostDamagedTestCase(TestCase):
    def setUp(self):
        # Create a test Mainitem object
        self.main_item = Mainitem.objects.create(fileid="12345", itemplace="Storage", itemvalue=100,pno=22)

    def test_add_lost_damaged_success(self):
        url = reverse('add_lost_damaged')  # Replace with actual URL name
        data = {
            "fileid": "12345",
            "itemno": "12345",
            "companyno": "98765",
            "company": "Test Company",
            "itemname": "Test Item",
            "costprice": 100,
            "quantity": 5,
            "pno": "22",  # This should correspond to a valid Mainitem
            "status": "Lost",
            "date": "2025-03-07",
            "itemmain": "Main Type"
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Record added successfully.',str(response.content, encoding='utf8'))

        # Ensure the LostAndDamagedTable record was created
        self.assertTrue(models.LostAndDamagedTable.objects.filter(itemno="12345").exists())

    def test_add_lost_damaged_missing_field(self):
        url = reverse('add_lost_damaged')  # Replace with actual URL name
        data = {
            "itemno": "12345",
            "companyno": "98765",
            "company": "Test Company",
            "itemname": "Test Item",
            "costprice": 100,
            #"quantity": 5,
            "pno": "22",  # This should correspond to a valid Mainitem
            "status": "Lost",
            # "date" is missing in this case
            "itemmain": "Main Type"
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': False, 'message': 'Missing required fields.'})

class FilterLostDamagedTestCase(TestCase):
    def setUp(self):
        Mainitem.objects.create(fileid="12345", itemplace="Old Storage",pno=22)
        # Create a test LostAndDamagedTable record
        self.lost_damaged_item = models.LostAndDamagedTable.objects.create(
            fileid="12345", itemname="Test Item", quantity=10, costprice=100, date="2025-03-07",pno_id=12345
        )

    def test_filter_lost_damaged_by_date(self):
        url = reverse('filter_lost_damaged')  # Replace with actual URL name
        filters = {
            "fromdate": "2025-03-01",
            "todate": "2025-03-31"
        }

        response = self.client.post(url, json.dumps(filters), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreater(len(data), 0)  # Check if there are results

    def test_filter_lost_damaged_invalid_date(self):
        url = reverse('filter_lost_damaged')  # Replace with actual URL name
        filters = {
            "fromdate": "invalid-date",
            "todate": "2025-03-31"
        }

        response = self.client.post(url, json.dumps(filters), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'error': 'Invalid date format'})

class GetAllClientsTestCase(TestCase):
    def setUp(self):
        # Create a test client record
        self.client_record = models.AllClientsTable.objects.create(
            clientid="12345", name="Test Client", address="Test Address", email="test@example.com"
        )

    def test_get_all_clients_success(self):
        url = reverse('get-all-clients')  # Replace with actual URL name
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreater(len(data['data']), 0)  # Ensure there are records
        self.assertEqual(data['data'][0]['clientid'], 12345)


    def test_get_all_clients_pagination(self):
        url = reverse('get-all-clients')  # Replace with actual URL name
        response = self.client.get(url, {'page': 1, 'size': 1})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 1)  # Pagination ensures only 1 record is returned

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
import json

class CreateClientRecordTestCase(TestCase):
    def setUp(self):
        # Set up any required data or users before the test
        self.url = reverse('create-client')  # Replace with the actual URL name

    def test_create_client_record_success(self):
        # Simulate the POST request with valid data
        data = {
            'client_name': 'Test Client',
            'address': 'Test Address',
            'email': 'test@example.com',
            'website': 'http://test.com',
            'phone': '1234567890',
            'mobile': '0987654321',
            'last_transaction': '100',
            'currency': 'USD',
            'account_type': 'Business',
            'sub_category': 'Retail',
            'limit': '12',
            'limit_value': '5000.0',
            'installments': '12',
            'types': 'Type A',
            'client_stop': '1',
            'curr_flag': '1',
            'permissions': 'Read, Write',
            'other': 'None',
            'username': 'client',
            'password':'12345'
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')

        # Assert the response status and message
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['message'], 'Record created successfully!')

        # Check if the user and client record were created
        user = User.objects.get(username='1234567890')
        self.assertEqual(user.email, 'test@example.com')

        # Check the client record
        client = models.AllClientsTable.objects.get(name='Test Client')
        self.assertEqual(client.email, 'test@example.com')
        self.assertEqual(client.address, 'Test Address')

    def test_create_client_record_missing_fields(self):
        # Simulate the POST request with missing required fields
        data = {
            'client_name': 'Test Client',
            'address': 'Test Address'
            # Missing other fields intentionally
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')

        # Assert the response status and message
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')




class UpdateClientRecordTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_instance = models.AllClientsTable.objects.create(
            clientid=1,
            name="Test Client",
            address="Test Address",
            email="test@example.com",
            phone="123456789",
            mobile="987654321",
            last_transaction=now(),
            accountcurr="USD",
            type="Regular",
            category="General",
            loan_period=12,
            loan_limit=5000.0,
            loan_day=30,
            subtype="Type A",
            client_stop=False,
            curr_flag=False,
            permissions="Read",
            other="Notes",
            geo_location="Test Location"
        )

    def test_update_client_success(self):
        response = self.client.post(
            "/api/update-client",
            json.dumps({"client_id": 1, "client_name": "Updated Client", "email": "updated@example.com"}),
            content_type="application/json",
        )
        self.client_instance.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client_instance.name, "Updated Client")
        self.assertEqual(self.client_instance.email, "updated@example.com")

    def test_update_client_not_found(self):
        response = self.client.post(
            "/api/update-client",
            json.dumps({"clientid": 999}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")

class DeleteClientRecordTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_instance = models.AllClientsTable.objects.create(clientid=2, name="To Delete")

    def test_delete_client_success(self):
        response = self.client.post(
            "/api/delete-client",
            json.dumps({"client_id": 2}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(models.AllClientsTable.objects.filter(clientid=2).exists())

    def test_delete_client_not_found(self):
        response = self.client.post(
            "/api/delete-client",
            json.dumps({"client_id": 999}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")

from django.utils.timezone import make_aware
from datetime import datetime

class FilterAllClientsTest(TestCase):
    def setUp(self):
        self.client = Client()
        models.AllClientsTable.objects.create(clientid=3, name="John Doe", email="john@example.com")

    def test_filter_client_by_name(self):
        response = self.client.post(
            "/api/filter-all-clients",
            json.dumps({"name": "John"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("John Doe" in str(response.content))

    def test_filter_client_by_email(self):
        response = self.client.post(
            "/api/filter-all-clients",
            json.dumps({"email": "john@example.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("john@example.com" in str(response.content))

    def test_invalid_date_format(self):
        response = self.client.post(
            "/api/filter-all-clients",
            json.dumps({"fromdate": "2024/01/01", "todate": "2024-12-31"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid date format")


class CreateStorageRecordTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_instance = models.AllClientsTable.objects.create(clientid=4, name="Storage Client")

    def test_create_storage_record_success(self):
        response = self.client.post(
            "/api/create-storage-record",
            json.dumps({
                "transaction_date": "2025-03-16",
                "reciept_no": "REC123",
                "amount": 1000.0,
                "for_what": "Office Supplies",
                "note": "Monthly Purchase",
                "type": "Expense",
                "transaction": "Purchase",
                "place": "Store A",
                "section": "Electronics",
                "subsection": "Laptops",
                "for_who": "Storage Client",
                "pay_method": "Cash",
                "daily": False,
                "bank": "XYZ Bank",
                "checkno": "CHK123"
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(models.StorageTransactionsTable.objects.exists())
        self.assertTrue(models.TransactionsHistoryTable.objects.exists())

    def test_create_storage_record_invalid_client(self):
        response = self.client.post(
            "/api/create-storage-record",
            json.dumps({
                "transaction_date": "2025-03-16",
                "for_who": "Unknown Client",
                "amount": 500.0,
                "daily": False,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Client 'Unknown Client' not found")


from django.test import TestCase, Client
from django.urls import reverse
from django.http import JsonResponse
from .models import StorageTransactionsTable
import json

class StorageTransactionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.storage_record = StorageTransactionsTable.objects.create(storageid="123",daily_status=False)

    def test_delete_storage_record_success(self):
        """Test deleting an existing storage record"""
        response = self.client.post(reverse('delete_storage_record'), json.dumps({"storage_id": "123"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Record deleted successfully!"})
        self.assertFalse(StorageTransactionsTable.objects.filter(storageid="123").exists())

    def test_delete_storage_record_not_found(self):
        """Test deleting a non-existent storage record"""
        response = self.client.post(reverse('delete_storage_record'), json.dumps({"storage_id": "999"}), content_type="application/json")
        self.assertEqual(response.status_code, 404)


    def test_delete_storage_record_invalid_method(self):
        """Test calling the delete function with GET method"""
        response = self.client.get(reverse('delete_storage_record'))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {"error": "Invalid request method."})

class GetAllStorageTests(TestCase):
    def setUp(self):
        self.client = Client()
        StorageTransactionsTable.objects.create(storageid="1", account_type="Type1",daily_status=False)
        StorageTransactionsTable.objects.create(storageid="2", account_type="Type2",daily_status=False)

    def test_get_all_storage_success(self):
        """Test fetching all storage records"""
        response = self.client.get(reverse('get-all-storage'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 2)

class FilterAllStorageTests(TestCase):
    def setUp(self):
        self.client = Client()
        StorageTransactionsTable.objects.create(storageid="1", person="Client1",daily_status=False, section="Finance", transaction_date="2024-01-01")

    def test_filter_all_storage_by_id(self):
        """Test filtering storage records by ID"""
        response = self.client.post(reverse('filter-all-storage'), json.dumps({"id": "1"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_filter_all_storage_invalid_json(self):
        """Test handling invalid JSON"""
        response = self.client.post(reverse('filter-all-storage'), "invalid json", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid JSON format"})

class GetLastRecieptNoTests(TestCase):
    def setUp(self):
        self.client = Client()
        models.StorageTransactionsTable.objects.create(storageid="1",daily_status=False , reciept_no="100", transaction="ايداع")
        models.StorageTransactionsTable.objects.create(storageid="2",daily_status=False , reciept_no="200", transaction="صرف")

    def test_get_last_reciept_no_valid(self):
        """Test fetching last receipt number"""
        response = self.client.get(reverse('last-reciept-no') + "?transactionType=ايداع")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"lastRecieptNo": 100})

    def test_get_last_reciept_no_invalid_type(self):
        """Test with an invalid transaction type"""
        response = self.client.get(reverse('last-reciept-no') + "?transactionType=Unknown")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid transaction type"})

class FetchInvoiceItemsTests(TestCase):
    def setUp(self):
        self.client = Client()
        invoice = models.Buyinvoicetable.objects.create(invoice_no=6562)
        item = models.BuyInvoiceItemsTable.objects.create(invoice_no=invoice , invoice_no2="6562", item_no="ITEM1")
        #item.refresh_from_db()

    # def test_fetch_invoice_items_success(self):
    #     """Test fetching invoice items"""
    #     response = self.client.get(reverse('fetch-buy-invoice-items') + "?id=6562")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.json()), 1)

    def test_fetch_invoice_items_not_found(self):
        """Test fetching invoice items for non-existent invoice"""
        response = self.client.get(reverse('fetch-buy-invoice-items') + "?id=999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_fetch_invoice_items_missing_id(self):
        """Test missing invoice number parameter"""
        response = self.client.get(reverse('fetch-buy-invoice-items'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invoice number is required."})

class CreateCostRecordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.invoice = models.Buyinvoicetable.objects.create(invoice_no="1", amount=1000, exchange_rate=5)

    def test_create_cost_record_success(self):
        """Test creating a cost record successfully"""
        data = {
            "invoice": "1",
            "type": "Shipping",
            "cost": "500",
            "rate": "5",
            "dinar": "2500"
        }
        response = self.client.post(reverse('create-cost-record'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["success"], True)

    def test_create_cost_record_missing_fields(self):
        """Test missing fields in request"""
        data = {
            "invoice": "1",
            "type": "Shipping"
        }
        response = self.client.post(reverse('create-cost-record'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)

    def test_create_cost_record_invalid_json(self):
        """Test invalid JSON input"""
        response = self.client.post(reverse('create-cost-record'), "invalid json", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"success": False, "message": "Invalid JSON format"})

class FetchCostsTests(TestCase):
    def setUp(self):
        self.invoice = models.Buyinvoicetable.objects.create(invoice_no="1", amount=1000, exchange_rate=5)

        self.cost = models.BuyinvoiceCosts.objects.create(
                invoice=self.invoice,
                cost_for=type,
                cost_price=100,
                exchange_rate=21.1,
                dinar_cost_price=100,
                invoice_no=self.invoice.invoice_no
            )

    def test_fetch_costs_valid_invoice_no(self):
        # Add your setup data here (create BuyinvoiceCosts with invoice_no)
        response = self.client.get(reverse('fetch-costs'), {'id': f"{self.invoice.invoice_no}"})
        self.assertEqual(response.status_code, 200)

    def test_fetch_costs_missing_invoice_no(self):
        response = self.client.get(reverse('fetch-costs'))
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invoice number is required", response.json().get('error'))

    def test_fetch_costs_invalid_method(self):
        response = self.client.post(reverse('fetch-costs'))
        self.assertEqual(response.status_code, 405)
        self.assertIn("Invalid HTTP method",response.json().get('error'))

class DeleteBuyInvoiceCostTests(TestCase):
    def setUp(self):
        self.invoice = models.Buyinvoicetable.objects.create(invoice_no="1", amount=1000, exchange_rate=5)

    def test_delete_buyinvoice_cost_valid_autoid(self):
        # Setup: Create a BuyinvoiceCosts instance
        cost = models.BuyinvoiceCosts.objects.create(invoice=self.invoice ,invoice_no='1', cost_for='Test', cost_price=100)
        response = self.client.delete(reverse('delete_buyinvoice_cost', args=[cost.autoid]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Record deleted successfully!', response.json().get('message'))

    def test_delete_buyinvoice_cost_invalid_autoid(self):
        response = self.client.delete(reverse('delete_buyinvoice_cost', args=[999]))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Record not found', response.json().get('message'))

    def test_delete_buyinvoice_cost_invalid_method(self):
        response = self.client.get(reverse('delete_buyinvoice_cost', args=[999]))
        self.assertEqual(response.status_code, 405)
        self.assertIn('Invalid request method', response.json().get('message'))

class CalculateCostTests(TestCase):
    def setUp(self):
        self.invoice = models.Buyinvoicetable.objects.create(invoice_no="1", amount=1000, exchange_rate=5)

    def test_calculate_cost_valid(self):
        data = {
            "cost_total": "1000",
            "invoice_total": "5000",
            "invoice": "1"
        }
        response = self.client.post(reverse('calculate-cost'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cost updated successfully.', response.json().get('message'))

    def test_calculate_cost_missing_fields(self):
        data = {
            "cost_total": "1000",
            "invoice_total": "5000"
        }
        response = self.client.post(reverse('calculate-cost'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required fields', response.json().get('message'))

    def test_calculate_cost_invalid_json(self):
        response = self.client.post(reverse('calculate-cost'), data="invalid_json", content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid JSON format.', response.json().get('message'))


class ProcessDataTests(TestCase):
    def test_process_data_valid(self):
        invoice = models.Buyinvoicetable.objects.create(invoice_no=123)
        models.BuyInvoiceItemsTable.objects.create(autoid=123,invoice_no=invoice)
        data = {
            "id": "123",
            "currency": "USD",
            "rate": "1.2"
        }
        response = self.client.post(reverse('process-edit-invoice'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, '/manage-buy-invoice/')

    def test_process_data_missing_fields(self):
        data = {
            "id": "123",
            "currency": "USD"
        }
        response = self.client.post(reverse('process-edit-invoice'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required fields', response.json().get('message'))

    def test_process_data_invalid_json(self):
        response = self.client.post(reverse('process-edit-invoice'), data="invalid_json", content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid JSON format', response.json().get('message'))



class UpdateBuyInvoiceItemTests(TestCase):

    def setUp(self):
        # Create an invoice
        self.invoice = models.Buyinvoicetable.objects.create(invoice_no=321,amount=0)

    def test_update_buyinvoice_item_valid(self):
        # Create an item
        item = models.BuyInvoiceItemsTable.objects.create(
            invoice_no=self.invoice,
            org_unit_price=Decimal(100),
            dinar_unit_price=Decimal(120),
            dinar_total_price=10*120,
            quantity=10
        )

        # Data for updating
        data = {
            'id': item.autoid,
            'invoice_no': str(self.invoice.invoice_no),  # Use actual invoice_no
            'org': '100',
            'order': '110',
            'quantity': 5
        }
        # Make the POST request to update
        response = self.client.post(
            reverse('update-buy-invoice-item'),
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn('Item updated successfully', response.json().get('message'))

    def test_update_buyinvoice_item_invalid_data(self):
        # Data with invalid quantity
        data = {
            'id': '0000',  # Non-existent ID
            'invoice_no': str(self.invoice.invoice_no),
            'org': '100',
            'order': '110',
            'quantity': 'five'  # Invalid quantity type (string instead of int)
        }

        # Make the POST request
        response = self.client.post(
            reverse('update-buy-invoice-item'),
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assertions
        self.assertEqual(response.status_code, 400)

    def test_update_buyinvoice_item_invalid_method(self):
        # Test with GET method (should return 405)
        response = self.client.get(reverse('update-buy-invoice-item'))
        self.assertEqual(response.status_code, 405)
        self.assertIn('Invalid request method', response.json().get('message'))

class BuyInvoiceExcellTests(TestCase):
    def setUp(self):
        # Create an invoice
        self.invoice = models.Buyinvoicetable.objects.create(invoice_no=11,amount=0)

    def test_buy_invoice_excell_post_valid(self):
        data = {
            "invoice": "1",
            "org": "org_value"
        }
        response = self.client.post(reverse('invoice_excell'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 302)  # Redirect


    def test_buy_invoice_excell_get_valid(self):
        self.client.post(reverse('invoice_excell'), data=json.dumps({"invoice": "11", "org": "org_value"}), content_type='application/json')
        response = self.client.get(reverse('invoice_excell'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'buy-invoice-excell.html')


    def test_buy_invoice_excell_get_no_invoice_in_session(self):
        response = self.client.get(reverse('invoice_excell'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('No invoice found in session', response.json().get('message'))


from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse
from unittest.mock import patch
from .models import Buyinvoicetable, BuyInvoiceItemsTable, Mainitem

# class ProcessBuyInvoiceExcelTest(TestCase):
#     def setUp(self):
#         # Set up necessary test data
#         self.invoice = Buyinvoicetable.objects.create(autoid=123,invoice_no="123")

#     # @patch('almogOil.views.BuyInvoiceItemsTable.objects.bulk_create')
#     # def test_process_buyInvoice_excel_success(self, mock_bulk_create):
#     #     url = reverse('process_buyInvoice_excel')  # Replace with actual URL name
#     #     data = {
#     #         "invoice_no": "123",
#     #         "data": [
#     #             {
#     #                 "الرقم الاصلي": "12345",
#     #                 "اسم الصنف": "Test Item",
#     #                 "الكمية": 10,
#     #                 "سعر التوريد": 100,
#     #                 "سعر الشراء": 90,
#     #                 "سعر التكلفة": 80,
#     #                 "سعر البيع": 120,
#     #                 "رقم الشركة": "1",
#     #                 "رقم الباركود": "123456",
#     #                 "العملة": "USD",
#     #                 "التاريخ": "2025-01-01"
#     #             }
#     #         ]
#     #     }

#     #     response = self.client.post(url, json.dumps(data), content_type='application/json')
#     #     ##print(f"success res: {response.content}")
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertEqual(response.json()['status'], 'success')

#     def test_process_buyInvoice_excel_invoice_not_found(self):
#         url = reverse('process_buyInvoice_excel')
#         data = {
#             "invoice_no": "INV999221",  # Non-existent invoice number
#             "data": [
#                 {
#                     "الرقم الاصلي": "12345",
#                     "اسم الصنف": "Test Item",
#                     "الكمية": 10,
#                     "سعر التوريد": 100
#                 }
#             ]
#         }

#         response = self.client.post(url, data, content_type='application/json')
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(response.json()['status'], 'error')

class CheckItemsTest(TestCase):
    def setUp(self):
        self.main_item = Mainitem.objects.create(replaceno="1", itemname="Test Item",pno=22)

    def test_check_items_success(self):
        url = reverse('check_items')
        data = [
            {"رقم الشركة": "1"},
            {"رقم الشركة": "002"}  # Non-existent company
        ]
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(len(response.json()['results']), 2)
        self.assertEqual(response.json()['results'][0]['exists'], 1)
        self.assertEqual(response.json()['results'][1]['exists'], 0)

    # def test_check_items_invalid_format(self):
    #     url = reverse('check_items')
    #     data = "invalid_data"  # Invalid data format
    #     response = self.client.post(url, data, content_type='application/json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json()['status'], 'error')

class ProcessTempConfirmTest(TestCase):
    def setUp(self):
        self.invoice = Buyinvoicetable.objects.create(autoid=123,invoice_no="123", temp_flag=1)

    def test_process_temp_confirm_success(self):
        url = reverse('process_temp_confirm')
        data = {
            "invoice_no": "123"
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    # def test_process_temp_confirm_invoice_not_found(self):
    #     url = reverse('process_temp_confirm')
    #     data = {
    #         "invoice_no": "999"  # Non-existent invoice
    #     }
    #     response = self.client.post(url, data, content_type='application/json')
    #     ##print(f"temp res: {response.content}")
    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(response.json()['status'], 'error')

class ConfirmTempInvoiceTest(TestCase):
    def setUp(self):
        self.invoice = Buyinvoicetable.objects.create(invoice_no="123", temp_flag=1)
        self.main_item = Mainitem.objects.create(replaceno="1",pno=22, itemname="Test Item", itemvalue=10)

    # def test_confirm_temp_invoice_success(self):
    #     url = reverse('confirm_temp_invoice')
    #     data = {
    #         "invoice_no": "123",
    #         "table": [
    #             {
    #                 "company_no": "1",
    #                 "name": "Updated Item",
    #                 "quantity": 5,
    #                 "dinar_unit_price": 100,
    #                 "cost_unit_price": 80,
    #                 "org_unit_price": 120,
    #                 "item_no": "12345"
    #             }
    #         ]
    #     }

    #     response = self.client.post(url, data, content_type='application/json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json()['status'], 'success')

    # def test_confirm_temp_invoice_invoice_not_found(self):
    #     url = reverse('confirm_temp_invoice')
    #     data = {
    #         "invoice_no": "INV999",  # Non-existent invoice
    #         "table": [
    #             {
    #                 "company_no": "1",
    #                 "name": "Updated Item",
    #                 "quantity": 5
    #             }
    #         ]
    #     }

    #     response = self.client.post(url, data, content_type='application/json')
    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(response.json()['status'], 'error')

# class BuyInvoiceItemCreateViewTest(TestCase):
#     def setUp(self):
#         self.invoice = Buyinvoicetable.objects.create(invoice_no="123",temp_flag=1,amount=0)
#         self.main_item = Mainitem.objects.create(replaceno="1", pno="1", itemname="Test Item",itemtemp=0,itemvalue=0)

#     def test_buy_invoice_item_create_success(self):
#         url = reverse('create-invoice-item')
#         data = {
#             "invoice_id": "123",
#             "itemno": "12345",
#             "pno": "1",
#             "itemname": "New Item",
#             "companyproduct": "Test Company",
#             "replaceno": "1",
#             "itemvalue": 10,
#             "currency": "USD",
#             "itemplace": "Storage",
#             "source": "Supplier",
#             "orgprice": 100,
#             "buyprice": 90,
#             "orderprice": 120,
#             "lessprice": 110
#         }

#         # Option 1: Use json.dumps to serialize the data to JSON
#         response = self.client.post(url, data, content_type='application/json')

#         # Option 2: Use format='json' (this will automatically serialize the data)
#         # response = self.client.post(url, data, format='json')

#         ##print(f"create success res: {response.content}")
#         self.assertEqual(response.status_code, 200)

#     def test_buy_invoice_item_create_missing_fields(self):
#         url = reverse('create-invoice-item')
#         data = {
#             "invoice_id": "123",
#             "itemno": "12345",
#             "pno": "1"
#         }

#         response = self.client.post(url, data, content_type='application/json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()['error'], "Missing required fields: itemname, companyproduct, replaceno, itemvalue, currency, itemplace, source, orgprice, buyprice, orderprice, lessprice")


class BuyInvoiceManagementTestCase(TestCase):

    def setUp(self):
        # Setup any data needed
        models.AllSourcesTable.objects.create(clientid="123", name="Test Source")
        self.url = reverse('b_invoice_management')  # Replace with actual URL pattern name

    def test_buyinvoice_management_view(self):
        response = self.client.get(self.url)

        # Assert that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert that the context contains the expected data
        self.assertIn("sources", response.context)
        self.assertEqual(len(response.context['sources']), 1)
        self.assertEqual(response.context['sources'][0]['name'], "Test Source")

class FetchBuyInvoicesTestCase(TestCase):

    def setUp(self):
        # Setup any data needed
        Buyinvoicetable.objects.create(invoice_no="1", amount=100)
        self.url = reverse('fetch_buyinvoices')  # Replace with actual URL pattern name

    def test_fetch_buyinvoices_view(self):
        response = self.client.get(self.url, {'page': 1, 'size': 1})

        # Assert that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert that the returned data is in the expected structure
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('last_page', data)
        self.assertIn('total_rows', data)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['invoice_no'], 1)
        self.assertEqual(data['total_amount'], '100.00')  # assuming format_number() outputs '100.00'
class FilterBuyInvoicesTestCase(TestCase):

    def setUp(self):
        # Setup any data needed
        Buyinvoicetable.objects.create(invoice_no="1", amount=100, source="Supplier")
        self.url = reverse('filter_buyinvoices')  # Replace with actual URL pattern name

    def test_filter_buyinvoices_view(self):
        filters = {
            'invoice_no': '1',
            'source': 'Supplier',
            'page': 1,
            'size': 1
        }
        response = self.client.post(self.url, json.dumps(filters), content_type='application/json')

        # Assert that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert that the returned data is in the expected structure
        data = response.json()
        self.assertIn('data', data)
        self.assertEqual(data['data'][0]['invoice_no'], 1)
class BuyInvoiceAddItemsTestCase(TestCase):

    def setUp(self):
        # Setup any data needed
        self.invoice = Buyinvoicetable.objects.create(invoice_no="1", amount=100)
        self.url = reverse('buy_invoice_add_items')  # Replace with actual URL pattern name

    def test_buy_invoice_add_items_view(self):
        # First, set the session data for the test
        self.client.post(
            reverse('buy_invoice_add_items'),
            json.dumps({'id': str(self.invoice.autoid)}),
            content_type='application/json'  # Ensure the content type is application/json
        )

        # Now test fetching the view with the session set
        response = self.client.get(self.url)

        # Assert that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert that the context contains the invoice data
        self.assertIn("invoice", response.context)
        self.assertEqual(response.context["invoice"].invoice_no, 1)
class SellInvoiceSearchStorageTestCase(TestCase):

    def setUp(self):
        # Setup any data needed
        self.url = reverse('sell_invoice_search_storage')  # Replace with actual URL pattern name

    def test_sell_invoice_search_storage_view(self):
        response = self.client.get(self.url)

        # Assert that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert that the context contains the expected data
        self.assertIn("company", response.context)
        self.assertIn("mainType", response.context)
        self.assertIn("subType", response.context)
        self.assertIn("countries", response.context)
class SellInvoiceAddInvoiceTestCase(TestCase):

    def setUp(self):
        # Setup any data needed
        models.AllClientsTable.objects.create(clientid="1", name="Test Client")
        self.url = reverse('sell_invoice_add_invoice')  # Replace with actual URL pattern name

    def test_sell_invoice_add_invoice_view(self):
        response = self.client.get(self.url)

        # Assert that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert that the context contains the expected data
        self.assertIn("clients", response.context)
        self.assertEqual(len(response.context['clients']), 1)
        self.assertEqual(response.context['clients'][0]['name'], "Test Client")

class SellInvoiceManagementTestCase(TestCase):

    def setUp(self):
        # Setup any data needed
        models.AllClientsTable.objects.create(clientid="1", name="Test Client")
        models.Clienttypestable.objects.create(fileid="1", tname="Regular")
        self.url = reverse('sell_invoice_management')  # Replace with actual URL pattern name

    def test_sell_invoice_management_view(self):
        response = self.client.get(self.url)

        # Assert that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert that the context contains the expected data
        self.assertIn("clients", response.context)
        self.assertIn("types", response.context)
        self.assertEqual(len(response.context['clients']), 1)
        self.assertEqual(len(response.context['types']), 1)

class SellInvoiceTests(TestCase):

    def setUp(self):
        # Setup test data (clients, products, etc.)
        self.client1 = models.AllClientsTable.objects.create(
            name="Test Client",
            clientid=1,
            category="Gold",
            subtype="Retail",
            loan_limit=5000
        )

        self.product = Mainitem.objects.create(
            pno="1",
            fileid="1",
            itemname="Test Product",
            itemmain="Category1",
            itemsubmain="Subcategory1",
            companyproduct="Test Company",
            itemvalue=100,
            buyprice=Decimal("50.00")
        )

        # Create a sell invoice for testing
        self.sell_invoice = models.SellinvoiceTable.objects.create(
            invoice_no=1,
            client_obj=self.client1,
            client_id=self.client1.clientid,
            client_name=self.client1.name,
            client_rate=self.client1.category,
            client_category=self.client1.subtype,
            client_limit=self.client1.loan_limit,
            client_balance=Decimal("1000.00"),
            invoice_date=timezone.now(),
            invoice_status="لم تحضر",
            payment_status="نقدي",
            for_who="application",
            date_time=timezone.now(),
            price_status="",
            mobile=False,
        )
        self.sell_invoice_item = models.SellInvoiceItemsTable.objects.create(invoice_instance=self.sell_invoice,invoice_no=1,pno=21)

    def test_create_sell_invoice(self):
        url = reverse('create_sell_invoice')  # Make sure this matches the URL name in your urls.py
        data = {
            "client": self.client1.clientid,
            "invoice_date": "2025-03-24",
            "payment_status": "نقدي",
            "for_who": "application",
            "mobile": False
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn("invoice_no", response.json())
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["invoice_no"], 2)  # Assuming the next invoice number is 2.

    def test_sell_invoice_add_items(self):
        url = reverse('sell_invoice_add_items')  # Ensure this URL name is correct
        data = {
            "invoice": self.sell_invoice.invoice_no
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 302)  # Should redirect to the target page

    def test_get_sell_invoice_items(self):
        url = reverse('fetch-sell-invoice-items')  # Ensure this URL name is correct
        response = self.client.get(url, {'id': self.sell_invoice.invoice_no})
        #print(f"response fetch: {response.content}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("invoice_no", response.json()[0])  # Check if the response contains invoice items

    def test_filter_sellinvoices(self):
        url = reverse('filter_sellinvoices')  # Ensure this URL name is correct
        filter_data = {
            "client": "Test Client",
            "payment_status": "نقدي"
        }
        response = self.client.post(url, json.dumps(filter_data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue("data" in response.json())
        self.assertGreater(len(response.json()["data"]), 0)  # Ensure we have data in the response

    def test_sell_invoice_create_item(self):
        url = reverse('sell_invoice_create_item')  # Ensure this URL name is correct
        ##print(f"reverse for si create: {reverse('sell_invoice_create_item')}")
        data = {
            "pno": self.product.pno,
            "fileid": self.product.fileid,
            "invoice_id": self.sell_invoice.invoice_no,
            "itemvalue": 5,
            "sellprice": "50.00"
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertIn("item_id", response.json())
        self.assertTrue(response.json()["confirm_status"] == "confirmed")

    def test_sell_invoice_create_item_missing_fields(self):
        url = reverse('sell_invoice_create_item')
        data = {
            "pno": self.product.pno,
            "invoice_id": self.sell_invoice.invoice_no,
            "itemvalue": 5,
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.json()["error"])

    def test_sell_invoice_create_item_insufficient_quantity(self):
        url = reverse('sell_invoice_create_item')
        data = {
            "pno": self.product.pno,
            "fileid": self.product.fileid,
            "invoice_id": self.sell_invoice.invoice_no,
            "itemvalue": 200,  # Greater than the available quantity (100)
            "sellprice": "50.00"
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn("Insufficient product quantity", response.json()["error"])