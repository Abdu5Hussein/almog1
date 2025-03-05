
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
from almogOil.views import addMoreCatView,notify_user,notifications_page,feedback_details, return_items_add_items, return_items_report_view, return_items_view, cancel_sell_invoice,Sell_invoice_create_item,fetch_feedback_messages,support_dashboard,fetch_all_feedback, close_feedback,delete_feedback,add_message_to_feedback,feedback_by_user_id, SendMessageView, GetChatMessagesView, MarkMessageAsReadView,SupportChatMessageView, create_conversation, create_sell_invoice, deliver_sell_invoice, fetch_sell_invoice_items, fetch_sellinvoices, filter_sellinvoices, get_mainItem_last_pno, get_sellinvoice_no, prepare_sell_invoice, sell_invoice_add_items, sell_invoice_management,sell_invoice_add_invoice, sell_invoice_prepare_report,sell_invoice_search_storage,buy_invoice_add_items,filter_buyinvoices,fetch_buyinvoices,Buyinvoice_management,delete_buyinvoice_cost, BuyInvoiceItemCreateView, BuyInvoiceItemsView, BuyInvoicesAdd, ClientsManagement, ClientsReports, ImageView, ImportExcel, ModelView, OemNumbers, SectionAndSubSection, StoragePlaces, StorageManagement, StorageReports, account_statement, add_lost_damaged, buyInvoice_edit_prices, buyInvoice_excell, calculate_cost, check_items, confirm_temp_invoice, cost_management, create_buy_invoice, create_client_record, create_cost_record, create_storage_record, delete_buy_invoice_item, delete_client_record, delete_lost_damaged, delete_storage_record, fetch_costs, fetch_invoice_items, fetch_lost_damaged_data, filter_all_clients, filter_all_storage, filter_clients, filter_clients_input, filter_lost_damaged, generate_pdf,MoreDetails,filter_items, get_account_statement, get_all_clients, get_all_storage, get_buyinvoice_no, get_clients, get_invoice_items, get_last_reciept_no, get_subsections, manage_buy_invoice, payment_installments, process_add_data, process_buyInvoice_excel, process_data, process_excel_and_import,manage_countries,manage_companies,SubCat,MainCat,get_item_data,edit_main_item,delete_record,create_main_item,Measurements ,MainCat,LostDamaged,get_data,DataInventory,TestView, UsersView,AddUserView , LogInView,HomeView,ProductsDetails,UpdateUserView,ProductsReports,EditPrices,ProductsMovementReport,PartialProductsReports, ProductsBalance, process_temp_confirm, sell_invoice_storage_management, temp_confirm, update_buyinvoiceitem, update_client_record, update_itemvalue, update_storage, validate_sell_invoice
from almogOil.api_views import filter_Items,support_conversations,get_models,get_engines,get_main_types,get_sub_types,get_delivery_invoices,update_invoice_status, get_conversation_messages, send_message,get_all_clients1,start_conversation,respond_to_feedback,send_feedback
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls
import rest_framework
from almogOil import api_views,views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'permissions', api_views.ReturnPermissionViewSet, basename='return-permission')
router.register(r'permission-items', api_views.ReturnPermissionItemsViewSet, basename='return-permission-items')
router.register(r'engines', api_views.EnginesTableViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
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
    path('delete-buyinvoice-cost/<int:autoid>/', delete_buyinvoice_cost, name='delete_buyinvoice_cost'),
    path("b_invoice_management",Buyinvoice_management,name="b_invoice_management"),
    path('fetch-buyinvoices', fetch_buyinvoices, name='fetch_buyinvoices'),
    path('filter_buyinvoices', filter_buyinvoices, name='filter_buyinvoices'),
    path('buy_invoice_add_items', buy_invoice_add_items, name='buy_invoice_add_items'),
    path('sell_invoice_search_storage', sell_invoice_search_storage, name='sell_invoice_search_storage'),
    path('sell_invoice_add_invoice', sell_invoice_add_invoice, name='sell_invoice_add_invoice'),
    path('sell_invoice_management', sell_invoice_management, name='sell_invoice_management'),
    path('sell-invoice-profile/<int:id>/', views.sell_invoice_profile, name='sell_invoice_profile'),
    path('api/create-sell-invoice-record', create_sell_invoice, name='create_sell_invoice'),
    path('get-last-sellinvoice-id',get_sellinvoice_no,name='get-last-sell-invoice'),
    path('sell_invoice_add_items',sell_invoice_add_items,name='sell_invoice_add_items'),
    path('sell_invoice_create_item',Sell_invoice_create_item,name='sell_invoice_create_item'),
    path("fetch-sell-invoice-items",fetch_sell_invoice_items,name="fetch-buy-invoice-items"),
    path('fetch-sellinvoices', fetch_sellinvoices, name='fetch_sellinvoices'),
    path('filter-sellinvoices', filter_sellinvoices, name='filter_sellinvoices'),
    path('sell_invoice_storage_report', sell_invoice_prepare_report, name='sell_invoice_prepare_report'),
    path('sell_invoice_storage_manage', sell_invoice_storage_management, name='sell_invoice_storage_management'),
    path('prepare_sell_invoice', prepare_sell_invoice, name='prepare_sell_invoice'),
    path('validate_sell_invoice', validate_sell_invoice, name='validate_sell_invoice'),
    path('deliver_sell_invoice', deliver_sell_invoice, name='deliver_sell_invoice'),
    path('cancel_sell_invoice', cancel_sell_invoice, name='cancel_sell_invoice'),
    path('api/mainitems/get_last_pno', get_mainItem_last_pno, name='get_last_pno'),

    path('api/models/', get_models, name='get_models'),
    path('api/engines/', get_engines, name='get_engines'),
    path('api/main-types/', get_main_types, name='get_main_types'),
    path('api/sub-types/', get_sub_types, name='get_sub_types'),
    path('api/filter-itemsapp/', api_views.filter_Items, name='filter-items'),
    path('process-login', api_views.sign_in, name='login-process'),
    path('api/get-drop-lists', api_views.get_dropboxes, name='get-drop-lists'),
    path('fetch_messages/<int:feedback_id>/', fetch_feedback_messages, name='fetch_feedback_messages'),
    path("add_message_to_feedback/<int:feedback_id>/", add_message_to_feedback, name="add_message_to_feedback"),
    path('api/get/tokken', TokenObtainPairView.as_view(), name='get_tokken'),
    path('api/get/tokken/refresh', TokenRefreshView.as_view(), name='refresh_tokken'),
    path('send-message/', SendMessageView.as_view(), name='send-message'),
    path('get-messages/', GetChatMessagesView.as_view(), name='get-messages'),
    path('api/create-conversation/', create_conversation, name='create_conversation'),
    path('api/send-message/', SupportChatMessageView.as_view(), name='send_message'),
    path('api/get-messages/', SupportChatMessageView.as_view(), name='get_messages'),
    path('mark-read/<int:pk>/', MarkMessageAsReadView.as_view(), name='mark-message-as-read'),
    path('history/<int:id>/invoices/', api_views.GetClientInvoices, name='get-client-invoices'),
     path('api/support_conversations/', support_conversations, name='support_conversations'),
    path('api/conversations/<int:conversation_id>/messages/', get_conversation_messages, name='get_conversation_messages'),
    path('api/conversations/<int:conversation_id>/send_message/', send_message, name='send_message'),
    path('api/conversations/start/<int:client_id>/', start_conversation, name='start_conversation'),
    path('api/clients/<int:id>/', get_all_clients1, name='get_all_clients1'),
    path('api/conversations/send_message/', send_message, name='send_message_without_conversation'),
    path('respond_to_feedback/<int:feedback_id>/', respond_to_feedback, name='respond_to_feedback'),
    path('send_feedback/', send_feedback, name='send_feedback'),
    path('respond_to_feedback/<int:feedback_id>/', respond_to_feedback, name='respond_to_feedback'),
    path('support_dashboard/', support_dashboard, name='support_dashboard'),
    path("fetch_all_feedback/", fetch_all_feedback, name="fetch_all_feedback"),
    path('close_feedback/<int:feedback_id>/', close_feedback, name='close_feedback'),
    path('delete_feedback/<int:feedback_id>/', delete_feedback, name='delete_feedback'),
    path('feedbacks/', feedback_by_user_id, name='feedback-by-user-id'),
    path('invoice/delivery/', get_delivery_invoices, name='get_delivery_invoices'),
    path('invoice/<str:invoice_no>/update_status/', update_invoice_status, name='update_invoice_status'),
    path('item/<int:id>/add-more-categories',addMoreCatView,name='add-more-categories'),
    path('item/<int:item_id>/update-main/',api_views.UpdateItemsItemmainApiView,name='update-main'),
    path('item/<int:item_id>/update-sub/',api_views.UpdateItemsSubmainApiView,name='update-sub'),
    path('item/<int:item_id>/update-model/',api_views.UpdateItemsModelApiView,name='update-model'),
    path('item/<int:item_id>/update-engine/',api_views.UpdateItemsEngineApiView,name='update-engine'),
    path('feedback_details/<int:feedback_id>/', feedback_details, name='feedback_details'),

    path('send-notification/', notify_user, name='send_firebase_notification'),
    path('notifications/', notifications_page, name='notifications_page'),
    path('sell-invoice/return-items-page/', return_items_view, name='return-items-view'),
    path('sell-invoice/<int:id>/return-items/', return_items_add_items, name='return-items'),

    path('sell-invoice/return-items-report/', return_items_report_view, name='return-report'),
    path('',include(router.urls)),
    path('engines-page/', views.engines_view, name='engines-view'),  # Render the engine management page
    path('sell-invoice/<int:id>/returned-items',api_views.get_invoice_returned_items,name="get-invoice-returned-items"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + debug_toolbar_urls()

# Ensure static files are served in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
