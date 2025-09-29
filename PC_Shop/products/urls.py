from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Главная страница каталога - все товары
    path('', views.ProductListView.as_view(), name='product_list'),
    
    # Детальная страница товара
    path('product/<int:pk>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Товары по категории
    path('category/<slug:slug>/', views.CategoryListView.as_view(), name='category_list'),
    
    # Товары по бренду
    path('brand/<slug:slug>/', views.BrandListView.as_view(), name='brand_list'),
]