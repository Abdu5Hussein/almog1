from django.urls import path
from . import views
from . import HozmaApi_views
from . import api_views
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView



urlpatterns = [
    # Down here is for car parts
    path('preorder/create/', HozmaApi_views.create_pre_order, name='create_pre_order'),
    path('preorder/last-invoice/', HozmaApi_views.get_sellinvoice_no, name='get_sellinvoice_no'),
    path('preorder/add-item/', HozmaApi_views.Sell_invoice_create_item, name='sell_invoice_create_item'),
    path('hozmabrands/', views.CarParts_page, name='CarParts_page'),
    path('products/', views.item_filter_page, name='item_filter_page'),
    path('hozmaHome/', views.CarPartsHome_page, name='CarPartsHome_page'),
    path('hozmaDashbord/', views.Dashbord_page, name='dashbord'),
    path('brand/<str:brand>/', api_views.brand_items, name='brand_items'),
    path('hozmaCart/', views.Cart_page, name='Cart'),
    path('hozmatrack-order/', views.track_order, name='track_order'),
    path('hozmareturn-policy/', views.return_policy, name='return_policy'),
    path('hozmafaq/', views.faq, name='faq'),
    path('hozmalogin/', views.hozmalogin, name='hozmalogin'),
    path('hozmaterms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('products/<int:pno>/', api_views.item_detail_view, name='item_detail'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/products/<int:id>/get-images',api_views.get_product_images,name="product-get-images"),
    #path('api/preorders/', api_views.show_all_preorders, name='show_all_preorders'),
    path('api/confirm-or-update-preorder-items/', HozmaApi_views.confirm_or_update_preorder_items, name='confirm_or_update_preorder_items'),
    
    path('api/confirm-or-update-preorder-items-buy-source/', HozmaApi_views.confirm_or_update_preorderBuy_items, name='confirm_or_update_preorderBuy_items'),
    path('api/preorders/', api_views.show_preorders, name='show_all_preorders'),
    path('api/preorders-buy/', HozmaApi_views.show_preordersBuy, name='show_all_preorders'),
    path('preorder-dashboard/', views.dashboard, name='dashboard'),  # For displaying all PreOrders
    path('preorder-detail/<str:invoice_no>/', views.preorder_detail, name='preorder_detail'),  # For displaying a specific PreOrder
    path('api/test-send-whatsapp/', HozmaApi_views.send_test_whatsapp_message, name='test-send-whatsapp'),
    path('api/full_Sell_invoice_create_item/', HozmaApi_views.full_Sell_invoice_create_item, name='full_Sell_invoice_create_item'),
    path('preorders-buy/', views.preorders_buy_page, name='preorders_buy_page'),
    path('preorders-buy/<str:invoice_no>/', views.preorder_buy_detail, name='preorder-detail'),
    
]
