
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
#from almog1 import wholesale_app,products
from django.contrib import admin
from django.urls import path
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls
import rest_framework
from almogOil import consumers
from almogOil import api_views,views,api_temp
from products import views as products_views
from products import api_views as products_api_views
from app_sell_invoice import api_views as sell_invoice_api_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.urls import path, reverse
from django.shortcuts import redirect

router = DefaultRouter()
router.register(r'permissions', api_views.ReturnPermissionViewSet, basename='return-permission')
router.register(r'permission-items', api_views.ReturnPermissionItemsViewSet, basename='return-permission-items')
router.register(r'engines', api_views.EnginesTableViewSet)
router.register(r'api/employees-api', api_views.EmployeesTableViewSet)
router.register(r'api/balance-editions-api', api_views.BalanceEditionsTableViewSet)
router.register(r'api/attendance-api', api_views.AttendanceTableViewSet)

urlpatterns = [
    path('hozma/', include('wholesale_app.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # ReDoc UI
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path('', lambda request: redirect(reverse('home'))),
    path('login', views.LogInView, name='login'),
    path('process-login', api_views.sign_in, name='login-process'),
    path('mobile/login', api_views.mobile_sign_in, name='mobile-login'),
    path('api/user/logout', api_views.logout_view, name='logout'),

    path('home', views.HomeView, name='home'),
    path('products-details', views.ProductsDetails, name='products-details'),
    path('products-reports', views.ProductsReports, name='products-reports'),
    path('edit-prices', views.EditPrices, name='edit-prices'),
    path('partial-products-reports', views.PartialProductsReports, name='partial-products-reports'),
    path('products-movement', views.ProductsMovementReport, name='products-movement'),
    path('products-balance', views.ProductsBalance, name='products-balance'),
    path('data-inventory', views.DataInventory, name='data-inventory'),
    path('api/get-data/', products_api_views.get_data, name='get_data'),
    path('lost-and-damaged', views.LostDamaged, name='lost-and-damaged'),
    path('main-catalog', views.MainCat, name='main-catalog'),
    path('measurements', views.Measurements, name='measurements'),
    path('create_main_item/', products_api_views.create_main_item, name='create_main_item'),
    path('delete-record/',products_api_views.delete_record, name='delete_record'),
    path('edit_main_item/', products_api_views.edit_main_item, name='edit_main_item'),
    path('get_item_data/<int:fileid>/', products_api_views.get_item_data, name='get_item_data'),
    path('maintype', views.MainCat, name='maintype'),
    path('subtype', views.SubCat, name='subtype'),
    path('manage_companies', views.manage_companies, name='manage_companies'),
    path('countries/', views.manage_countries, name='manage_countries'),
    path('api/filter-items', products_api_views.web_filter_items, name='filter_items'),
    path('more-details', views.MoreDetails, name='more-details'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('oem/', views.OemNumbers, name='oem'),
    path('images/', views.ImageView, name='images'),
    path('models/', views.ModelView, name='models'),
    path('import-excel/', views.ImportExcel, name='import-excel'),
    path('import-tabulator-data/', views.process_excel_and_import, name='import_tabulator_data'),
    path('api/filter-clients/', api_temp.filter_clients, name='filter-clients'),
    path('api/filter-client-input/', api_temp.filter_clients_input, name='filter-client-input'),
    path('update-itemvalue', products_api_views.update_itemvalue, name='update-itemvalue'),
    path('fetch-lost-damaged-data/', api_temp.fetch_lost_damaged_data, name='fetch_lost_damaged_data'),
    path('add-lost-damaged', api_temp.add_lost_damaged, name='add_lost_damaged'),
    path('filter-lost-damaged', api_temp.filter_lost_damaged, name='filter_lost_damaged'),
    path('api/delete-lost-damaged', api_temp.delete_lost_damaged, name='delete_lost_damaged'),
    path('storage', views.StoragePlaces, name='storage'),
    path('update-storage', products_api_views.update_storage, name='update-storage'),
    path('clients-management', views.ClientsManagement, name='clients-management'),
    path('api/create-client', api_temp.create_client_record, name='create-client'),
    path('api/update-client', api_temp.update_client_record, name='update-client'),
    path('api/delete-client', api_temp.delete_client_record, name='delete-client'),
    path('api/get-all-clients', api_temp.get_all_clients, name='get-all-clients'),
    path('api/filter-all-clients', api_temp.filter_all_clients, name='filter-all-clients'),
    path('clients-reports', views.ClientsReports, name='clients-reports'),
    path('storage-records', views.StorageManagement, name='storage-records'),
    path("api/create-storage-record", api_temp.create_storage_record, name="create_storage_record"),
    path("api/delete-storage-record", api_temp.delete_storage_record, name="delete_storage_record"),
    path('api/get-all-storage', api_views.get_all_storage, name='get-all-storage'),
    path('api/get-today-storage', api_views.get_today_storage, name='get-today-storage'),
    path('api/filter-all-storage', api_views.filter_all_storage, name='filter-all-storage'),
    path('get-subsections/', api_temp.get_subsections, name='get_subsections'),
    path('account-statements', views.account_statement, name='account-statements'),
    path('get-account-statement', api_temp.get_account_statement, name='get_account_statement'),
    path('storage-reports', views.StorageReports, name='storage-reports'),
    path('api/get-last-reciept-no', api_temp.get_last_reciept_no, name='last-reciept-no'),
    path('sections-and-subsections', views.SectionAndSubSection, name='sections-and-subsections'),
    path('add-buy-invoice',views.BuyInvoicesAdd, name='add-buy-invoice'),
    path('get-last-buyinvoice-id',api_temp.get_buyinvoice_no,name='get-last-buy-invoice'),
    path('api/create-buy-invoice-record',api_temp.create_buy_invoice,name='create-buy-invoice'),
    path('add-invoice-items',views.BuyInvoiceItemsView,name='add-invoice-items'),
    path('api/create-invoice-item/', api_temp.BuyInvoiceItemCreateView, name='create-invoice-item'),
    path("api/get-invoice-items",api_temp.get_invoice_items,name="get_invoice_items"),
    path("manage-buy-invoice/",views.manage_buy_invoice,name="manage-buy-invoice"),
    path("fetch-buy-invoice-items",api_temp.fetch_invoice_items,name="fetch-buy-invoice-items"),
    path("update-buyinvoiceitem",api_temp.update_buyinvoiceitem,name="update-buy-invoice-item"),
    path("delete-buyinvoiceitem",api_temp.delete_buy_invoice_item,name="delete-buy-invoice-item"),
    path("process-edit-invoice",views.process_data,name="process-edit-invoice"),
    path("process-add-invoice",views.process_add_data,name="process-add-invoice"),
    path('cost-management',views.cost_management,name='cost-management'),
    path("fetch-costs",api_temp.fetch_costs,name="fetch-costs"),
    path('create-cost-record', api_temp.create_cost_record, name='create-cost-record'),
    path('calculate-cost', api_temp.calculate_cost, name='calculate-cost'),
    path('payment-installments', views.payment_installments, name='payment-installments'),
    path('invoice_excell', views.buyInvoice_excell, name='invoice_excell'),
    path('process_buyInvoice_excel',views.process_buyInvoice_excel, name='process_buyInvoice_excel'),
    path("temp_confirm",views.temp_confirm,name="temp_confirm"),
    path("process_temp_confirm",views.process_temp_confirm,name="process_temp_confirm"),
    path("confirm_temp_invoice",api_temp.confirm_temp_invoice,name="confirm_temp_invoice"),
    path("buy-invoice_edit-prices",views.buyInvoice_edit_prices,name="buyInvoice_edit_prices"),
    path("check_items",products_api_views.check_items,name="check_items"),
    path('delete-buyinvoice-cost/<int:autoid>/', api_temp.delete_buyinvoice_cost, name='delete_buyinvoice_cost'),
    path("b_invoice_management",views.Buyinvoice_management,name="b_invoice_management"),
    path('fetch-buyinvoices', api_temp.fetch_buyinvoices, name='fetch_buyinvoices'),
    path('filter_buyinvoices', api_temp.filter_buyinvoices, name='filter_buyinvoices'),
    path('buy_invoice_add_items', views.buy_invoice_add_items, name='buy_invoice_add_items'),
    path('sell_invoice_search_storage', views.sell_invoice_search_storage, name='sell_invoice_search_storage'),
    path('sell_invoice_add_invoice', views.sell_invoice_add_invoice, name='sell_invoice_add_invoice'),
    path('sell_invoice_management', views.sell_invoice_management, name='sell_invoice_management'),
    path('sell-invoice-profile/<int:id>/', views.sell_invoice_profile, name='sell_invoice_profile'),
    path('api/create-sell-invoice-record', sell_invoice_api_views.create_sell_invoice, name='create_sell_invoice'),
    path('get-last-sellinvoice-id',sell_invoice_api_views.get_sellinvoice_no,name='get-last-sell-invoice'),
    path('sell_invoice_add_items',views.sell_invoice_add_items,name='sell_invoice_add_items'),
    path('sell_invoice_create_item',sell_invoice_api_views.Sell_invoice_create_item,name='sell_invoice_create_item'),
    path("fetch-sell-invoice-items",sell_invoice_api_views.fetch_sell_invoice_items,name="fetch-sell-invoice-items"),
    path('fetch-sellinvoices', sell_invoice_api_views.fetch_sellinvoices, name='fetch_sellinvoices'),
    path('filter-sellinvoices', sell_invoice_api_views.filter_sellinvoices, name='filter_sellinvoices'),
    path('sell_invoice_storage_report', views.sell_invoice_prepare_report, name='sell_invoice_prepare_report'),
    path('sell_invoice_storage_manage', views.sell_invoice_storage_management, name='sell_invoice_storage_management'),
    path('prepare_sell_invoice', sell_invoice_api_views.prepare_sell_invoice, name='prepare_sell_invoice'),
    path('validate_sell_invoice', sell_invoice_api_views.validate_sell_invoice, name='validate_sell_invoice'),
    path('deliver_sell_invoice', sell_invoice_api_views.deliver_sell_invoice, name='deliver_sell_invoice'),
    path('cancel_sell_invoice', sell_invoice_api_views.cancel_sell_invoice, name='cancel_sell_invoice'),
    path('api/mainitems/get_last_pno', products_api_views.get_mainItem_last_pno, name='get_last_pno'),
    path('accept-order/<int:queue_id>/', api_views.accept_order, name='accept-order'),
    path('skip-order/<int:queue_id>/', api_views.skip_order, name='skip-order'),
    path('decline-order/<int:queue_id>/', api_views.decline_order, name='decline-order'),
    path('api/models/', api_views.get_models, name='get_models'),
    path('api/engines/', api_views.get_engines, name='get_engines'),
    path('api/main-types/', api_views.get_main_types, name='get_main_types'),
    path('api/sub-types/', api_views.get_sub_types, name='get_sub_types'),
    path('api/filter-itemsapp/', products_api_views.app_filter_Items, name='filter-items-for-app'),

    path('api/get-drop-lists', api_views.get_dropboxes, name='get-drop-lists'),
    path('fetch_messages/<int:feedback_id>/', views.fetch_feedback_messages, name='fetch_feedback_messages'),
    path("add_message_to_feedback/<int:feedback_id>/", views.add_message_to_feedback, name="add_message_to_feedback"),

    path('api/get/tokken', TokenObtainPairView.as_view(), name='get_tokken'),
    path('api/get/tokken/refresh', TokenRefreshView.as_view(), name='refresh_tokken'),

    path('send-message/', views.SendMessageView.as_view(), name='send-message'),
    path('get-messages/', views.GetChatMessagesView.as_view(), name='get-messages'),
    path('api/create-conversation/', views.create_conversation, name='create_conversation'),
    path('api/send-message/', views.SupportChatMessageView.as_view(), name='send_message'),
    path('api/get-messages/', views.SupportChatMessageView.as_view(), name='get_messages'),
    path('mark-read/<int:pk>/', views.MarkMessageAsReadView.as_view(), name='mark-message-as-read'),
    path('history/<int:id>/invoices/', sell_invoice_api_views.GetClientInvoices, name='get-client-invoices'),
    path('history/invoices/<int:id>/', sell_invoice_api_views.GetClientInvoicesByInvoiceNo, name='get-invoice-no-invoices'),
    path('api/support_conversations/', api_views.support_conversations, name='support_conversations'),
    path('api/conversations/<int:conversation_id>/messages/', api_views.get_conversation_messages, name='get_conversation_messages'),
    path('api/conversations/<int:conversation_id>/send_message/', api_views.send_message, name='send_message'),
    path('api/conversations/start/<int:client_id>/', api_views.start_conversation, name='start_conversation'),
    path('api/clients/<int:id>/', api_views.get_all_clients1, name='get_all_clients1'),
    path('api/conversations/send_message/', api_views.send_message, name='send_message_without_conversation'),
    path('respond_to_feedback/<int:feedback_id>/', api_views.respond_to_feedback, name='respond_to_feedback'),
    path('send_feedback/', api_views.send_feedback, name='send_feedback'),
    path('respond_to_feedback/<int:feedback_id>/', api_views.respond_to_feedback, name='respond_to_feedback'),
    path('support_dashboard/', views.support_dashboard, name='support_dashboard'),
    path("fetch_all_feedback/", views.fetch_all_feedback, name="fetch_all_feedback"),
    path('close_feedback/<int:feedback_id>/', views.close_feedback, name='close_feedback'),
    path('delete_feedback/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
    path('feedbacks/', views.feedback_by_user_id, name='feedback-by-user-id'),
    path('invoice/delivery/', api_views.get_delivery_invoices, name='get_delivery_invoices'),
    path('invoice/<str:invoice_no>/update_status/', api_views.update_invoice_status, name='update_invoice_status'),
    path('item/<int:id>/add-more-categories',views.addMoreCatView,name='add-more-categories'),
    path('item/<int:item_id>/update-main/',products_api_views.UpdateItemsItemmainApiView,name='update-main'),
    path('item/<int:item_id>/update-sub/',products_api_views.UpdateItemsSubmainApiView,name='update-sub'),
    path('item/<int:item_id>/update-model/',products_api_views.UpdateItemsModelApiView,name='update-model'),
    path('item/<int:item_id>/update-engine/',products_api_views.UpdateItemsEngineApiView,name='update-engine'),
    path('assign-order-manual/', views.assign_order_manual, name='assign-order'),
    path('feedback_details/<int:feedback_id>/', views.feedback_details, name='feedback_details'),
    path('get-employee-orders/<int:employee_id>/', api_views.get_employee_order, name='get-employee-order'),
    path('send-notification/', views.notify_user, name='send_firebase_notification'),
    path('notifications/', views.notifications_page, name='notifications_page'),
    path('sell-invoice/return-items-page/', views.return_items_view, name='return-items-view'),
    path('sell-invoice/<int:id>/<int:permission>/return-items/', views.return_items_add_items, name='return-items'),
    path('update-delivery-availability/', api_views.update_delivery_availability, name='update-delivery-availability'),
    path('sell-invoice/return-items-report/', views.return_items_report_view, name='return-report'),
    path('',include(router.urls)),
    path('engines-page/', views.engines_view, name='engines-view'),  # Render the engine management page
    path('sell-invoice/<int:id>/returned-items',api_views.get_invoice_returned_items,name="get-invoice-returned-items"),
    path('clients/payment-requests',views.request_payment_view,name="request_payment"),
    path('assign-orders/', api_views.assign_orders, name='assign_orders'),
    path('complete-delivery/<int:invoice_id>/', api_views.complete_delivery, name='complete_delivery'),
    path('pending-orders/', api_views.pending_orders, name='pending_orders'),
    path('employee/set_available/', api_views.set_available, name='set_available'),
    path('employee/set_unavailable/', api_views.set_unavailable, name='set_unavailable'),
    path('available-employees/', api_views.available_employees, name='available_employees'),
    path('employee/clear_queue/', api_views.clear_queue, name='clear_queue'),
    path('check-assign-status/', api_views.check_assign_status, name='check_assign_status'),
     path('api/available-employees/', api_views.get_available_employees, name='available_employees'),
    path('get-employee-orders/<int:employee_id>/', api_views.get_employee_orders, name='get_employee_orders'),
    path('deliver-order/<int:queue_id>/', api_views.deliver_order, name='deliver-order'),
    path('products/add-description',views.main_item_add_json_description,name="add-description"),
    path('confirm_order/<int:order_id>/', api_views.confirm_order, name='confirm_order'),
    path('decline_order/<int:order_id>/', api_views.decline_order, name='decline_order'),
    path('monitor-order-assignments/', api_views.monitor_order_assignments, name='monitor_order_assignments'),
    path("check-assign-statusss/<int:employee_id>/", api_views.check_assign_statusss, name="check_assign_status"),
    path('employee_order_info/<int:employee_id>/', api_views.employee_order_info, name='employee_order_info'),
    path('confirm_order_arrival/<int:order_id>/', api_views.confirm_order_arrival, name='confirm_order_arrival'),
    path('confirmed_orders/', api_views.get_all_confirmed_orders, name='get_all_confirmed_orders'),
    path('complete_order/<int:autoid>/', api_views.complete_order, name='complete_order'),
    path('WStest/', views.invoice_notifications, name='WStest'),
    path('invoice/<int:autoid>/', sell_invoice_api_views.get_invoice_data, name='get_invoice_data'),
    path('api/employees/', views.get_available_employees, name='get-employees'),
    path('api/orders/', views.get_unassigned_orders, name='get-orders'),
    path('assign-order/', views.assign_order_page, name='assign-order-page'),
    path('api/orders/', views.get_unassigned_orders, name='get-orders'),
    path('api/add-to-cart/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('api/store-token/', api_views.store_fcm_token, name='store_fcm_token'),  # Define the API URL
    path('archived-orders/<int:employee_id>/', api_views.get_archived_orders, name='get_archived_orders'),
    path('api/employee_current_order_info/<int:employee_id>/', api_views.employee_current_order_info, name='employee_current_order_info'),
    path('api/products/<int:id>/add-json-description',products_api_views.mainitem_add_json_desc,name="add-json-description"),
    path('api/payment-requests/<int:id>/accept',api_views.accept_payment_req,name="accept_payment_request"),
    path('api/filter-return-requests/', api_views.filter_return_reqs, name='filter_return_reqs'),
    path('sources/management',views.sources_management_View,name='sources_management_View'),
    path('register_fcm/', api_views.register_fcm_token, name='register_fcm_token'),
    path('send_notifications/', api_views.send_notification, name='send_notification'),
    path('api/create_source',api_views.create_source_record,name="create_source_record"),
    path('return-permissions/<int:id>/profile/',views.return_permission_profile,name="return_permission-profile"),
    path('api/products/<int:id>/get-images',products_api_views.get_product_images,name="product-get-images"),
    path('users/management', views.users_management,name="users_management"),
    path('maintypes/<int:id>/logo',views.maintype_logo_view,name="maintype_logo_view"),
    path('assign-orders-page/<str:invoice_id>/', views.assign_orders_page, name='assign_orders_page'),
    path('assign-order-employee/<str:invoice_id>/', views.assign_order_to_employee, name='assign_order_to_employee'),
    path('maintypes/<int:id>/upload/logo',products_api_views.upload_maintype_logo,name="upload_maintype_logo_api"),
    path('employee-detail/<int:employee_id>/', api_views.employee_detail_get, name='employee-detail-get'),
    path('companies/<int:id>/logo',views.company_logo_view,name="company_logo_view"),
    path('companies/<int:id>/upload/logo',api_views.upload_company_logo,name="upload_company_logo_api"),
    path('api/token/validate-token/', api_views.validate_token),
    path('products/<int:id>/company/logo',products_api_views.get_logo_by_pno,name="get_company_logo_by_pno_api"),
    path('employees/management/reports',views.employees_report_view,name="employees_report_view"),
    path('employees/management/salaries',views.employees_salary_view,name="employees_salaries_view"),
    path('employees/management/salaries/edit',views.employees_salary_edit_view,name="employees_salaries_edit_view"),
    path('employees/management/salaries/history',views.employees_cash_reports_view,name="employees_salaries_history"),
    path('employees/management/attendance',views.EmployeesAttendanceView,name="employees_attendance_view"),
    path('api/attendance/employees/<int:id>/',api_views.fetch_attendance_per_employee,name="fetch_attendance_per_employee"),
    path('employees/management',views.EmployeesDetailsView,name="employees_management_view"),
    path('api/get/employees-details-with-balance',api_views.get_all_employees_with_balance,name='employees-details-with-balance'),
    path('api/employees-api/<int:id>/edit-balance',api_views.Edit_employee_balance,name="employee-edit-balance"),
    path('lib/two_way/',api_views.two_way,name="two_way"),
    path('api/employees/<int:employee_id>/', api_views.get_employee_details, name='get_employee_details'),

    path('api/balance-editions/user/<int:id>',api_views.Get_balance_editions_by_employee, name='balance-editions-for-user'),
    path('api/filter/balance-editions-api/',api_views.filterBalanceEditions, name='filter-balance-editions'),
    path('api/filter/employees-api/',api_views.filter_employees, name='filter-employees'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + debug_toolbar_urls()

# Ensure static files are served in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)






websocket_urlpatterns = [
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]
