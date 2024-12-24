
"""
URL configuration for Almog1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
from almogOil.views import BuyInvoiceItemCreateView, BuyInvoiceItemsView, BuyInvoicesAdd, ClientsManagement, ClientsReports, ImageView, ImportExcel, ModelView, OemNumbers, SectionAndSubSection, StoragePlaces, StorageManagement, StorageReports, account_statement, add_lost_damaged, buyInvoice_edit_prices, buyInvoice_excell, calculate_cost, check_items, confirm_temp_invoice, cost_management, create_buy_invoice, create_client_record, create_cost_record, create_storage_record, delete_buy_invoice_item, delete_client_record, delete_lost_damaged, delete_storage_record, fetch_costs, fetch_invoice_items, fetch_lost_damaged_data, filter_all_clients, filter_all_storage, filter_clients, filter_clients_input, filter_lost_damaged, generate_pdf,MoreDetails,filter_items, get_account_statement, get_all_clients, get_all_storage, get_buyinvoice_no, get_clients, get_invoice_items, get_last_reciept_no, get_subsections, manage_buy_invoice, payment_installments, process_add_data, process_buyInvoice_excel, process_data, process_excel_and_import,manage_countries,manage_companies,SubCat,MainCat,get_item_data,edit_main_item,delete_record,create_main_item,Measurements ,MainCat,LostDamaged,get_data,DataInventory,TestView, UsersView,AddUserView , LogInView,HomeView,ProductsDetails,UpdateUserView,ProductsReports,EditPrices,ProductsMovementReport,PartialProductsReports, ProductsBalance, process_temp_confirm, temp_confirm, update_buyinvoiceitem, update_client_record, update_itemvalue, update_storage
import almogOil.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', TestView, name='test'),
    path('users',UsersView , name='users'),
    path('add-user/', AddUserView, name='add_user'),
    path('', LogInView, name='login'),
    path('home', HomeView, name='home'),  
    path('products-details', ProductsDetails, name='products-details'),  
    path('update-user/', UpdateUserView, name='update_user'),  # New URL for update
    path('products-reports', ProductsReports, name='products-reports'),  
    path('edit-prices', EditPrices, name='edit-prices'),  
    path('partial-products-reports', PartialProductsReports, name='partial-products-reports'),  
    path('products-movement', ProductsMovementReport, name='products-movement'),  
    path('products-balance', ProductsBalance, name='products-balance'),
    path('data-inventory', DataInventory, name='data-inventory'),
    path('api/get-data/', get_data, name='get_data'),
    path('lost-and-damaged', LostDamaged, name='lost-and-damaged'),
    path('main-catalog', MainCat, name='main-catalog'),
    path('measurements', Measurements, name='measurements'),
    path('create_main_item/', create_main_item, name='create_main_item'),
    path('delete-record/',delete_record, name='delete_record'),
    path('edit_main_item/', edit_main_item, name='edit_main_item'),
    path('get_item_data/<int:fileid>/', get_item_data, name='get_item_data'),
    path('maintype', MainCat, name='maintype'),
    path('subtype', SubCat, name='subtype'),
    path('manage_companies', manage_companies, name='manage_companies'),
    path('countries/', manage_countries, name='manage_countries'),    
    path('api/filter-items', filter_items, name='filter_items'),
    path('more-details', MoreDetails, name='more-details'),
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('oem/', OemNumbers, name='oem'),
    path('images/', ImageView, name='images'),
    path('models/', ModelView, name='models'),
    path('import-excel/', ImportExcel, name='import-excel'),
    path('import-tabulator-data/', process_excel_and_import, name='import_tabulator_data'),
    path('api/filter-clients/', filter_clients, name='filter-clients'),
    path('api/filter-client-input/', filter_clients_input, name='filter-client-input'),
    path('update-itemvalue', update_itemvalue, name='update-itemvalue'),
    path('fetch-lost-damaged-data/', fetch_lost_damaged_data, name='fetch_lost_damaged_data'),
    path('add-lost-damaged', add_lost_damaged, name='add_lost_damaged'),
    path('filter-lost-damaged', filter_lost_damaged, name='filter_lost_damaged'),
    path('api/delete-lost-damaged', delete_lost_damaged, name='delete_lost_damaged'),
    path('storage', StoragePlaces, name='storage'),
    path('update-storage', update_storage, name='update-storage'),
    path('clients-management', ClientsManagement, name='clients-management'),
    path('api/create-client', create_client_record, name='create-client'),
    path('api/update-client', update_client_record, name='update-client'),
    path('api/delete-client', delete_client_record, name='delete-client'),
    path('api/get-all-clients', get_all_clients, name='get-all-clients'),
    path('api/filter-all-clients', filter_all_clients, name='filter-all-clients'),
    path('clients-reports', ClientsReports, name='clients-reports'),
    path('storage-records', StorageManagement, name='storage-records'),
    path("api/create-storage-record", create_storage_record, name="create_storage_record"),
    path("api/delete-storage-record", delete_storage_record, name="delete_storage_record"),
    path('api/get-all-storage', get_all_storage, name='get-all-storage'),
    path('api/filter-all-storage', filter_all_storage, name='filter-all-storage'),
    path('get-subsections/', get_subsections, name='get_subsections'),
    path('account-statements', account_statement, name='account-statements'),
    path('get-account-statement', get_account_statement, name='get_account_statement'),
    path('storage-reports', StorageReports, name='storage-reports'),
    path('api/get-last-reciept-no', get_last_reciept_no, name='last-reciept-no'),
    path('sections-and-subsections', SectionAndSubSection, name='sections-and-subsections'),
    path('add-buy-invoice',BuyInvoicesAdd, name='add-buy-invoice'),
    path('get-last-buyinvoice-id',get_buyinvoice_no,name='get-last-buy-invoice'),
    path('api/create-buy-invoice-record',create_buy_invoice,name='create-buy-invoice'),
    path('add-invoice-items',BuyInvoiceItemsView,name='add-invoice-items'),
    path('api/create-invoice-item/', BuyInvoiceItemCreateView, name='create-invoice-item'),
    path("api/get-invoice-items",get_invoice_items,name="get_invoice_items"),
    path("manage-buy-invoice/",manage_buy_invoice,name="manage-buy-invoice"),
    path("fetch-buy-invoice-items",fetch_invoice_items,name="fetch-buy-invoice-items"),
    path("update-buyinvoiceitem",update_buyinvoiceitem,name="update-buy-invoice-item"),
    path("delete-buyinvoiceitem",delete_buy_invoice_item,name="delete-buy-invoice-item"),
    path("process-edit-invoice",process_data,name="process-edit-invoice"),
    path("process-add-invoice",process_add_data,name="process-add-invoice"),
    path('cost-management',cost_management,name='cost-management'),
    path("fetch-costs",fetch_costs,name="fetch-costs"),
    path('create-cost-record', create_cost_record, name='create-cost-record'),
    path('calculate-cost', calculate_cost, name='calculate-cost'),
    path('payment-installments', payment_installments, name='payment-installments'),
    path('invoice_excell', buyInvoice_excell, name='invoice_excell'),
    path('process_buyInvoice_excel',process_buyInvoice_excel, name='process_buyInvoice_excel'),
    path("temp_confirm",temp_confirm,name="temp_confirm"),
    path("process_temp_confirm",process_temp_confirm,name="process_temp_confirm"),
    path("confirm_temp_invoice",confirm_temp_invoice,name="confirm_temp_invoice"),
    path("buy-invoice_edit-prices",buyInvoice_edit_prices,name="buyInvoice_edit_prices"),
    path("check_items",check_items,name="check_items"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
