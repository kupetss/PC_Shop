from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', views.CategoryListView.as_view(), name='category_list'),
    path('brand/<slug:slug>/', views.BrandListView.as_view(), name='brand_list'),
]