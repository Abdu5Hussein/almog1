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
    path('item-for-inqury-page/<int:pno>/', api_views.item_detail_view, name='item_detail'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/products/<int:id>/get-images',api_views.get_product_images,name="product-get-images"),
]
