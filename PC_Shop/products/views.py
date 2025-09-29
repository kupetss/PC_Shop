from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Product, Category, Brand

class ProductListView(ListView):
    """Список всех товаров с пагинацией"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12  # Количество товаров на странице
    
    def get_queryset(self):
        # Оптимизируем запросы к БД
        return Product.objects.filter(available=True).select_related('category', 'brand').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст все категории для фильтрации (в будущем)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context

class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        # Оптимизируем запросы к БД
        return Product.objects.filter(available=True).select_related('category', 'brand').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Получаем главное изображение
        context['main_image'] = product.images.filter(is_main=True).first()
        
        # Получаем все изображения кроме главного
        context['other_images'] = product.images.exclude(is_main=True)
        
        # Похожие товары (из той же категории)
        context['related_products'] = Product.objects.filter(
            category=product.category, 
            available=True
        ).exclude(id=product.id).select_related('brand').prefetch_related('images')[:4]
        
        return context

class CategoryListView(ListView):
    """Список товаров конкретной категории (с учетом вложенности)"""
    template_name = 'products/category_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        # Получаем категорию по slug
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        
        # Получаем все товары категории и всех её подкатегорий
        categories = self.category.get_descendants(include_self=True)
        
        return Product.objects.filter(
            category__in=categories, 
            available=True
        ).select_related('category', 'brand').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context

class BrandListView(ListView):
    """Список товаров конкретного бренда"""
    template_name = 'products/brand_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        # Получаем бренд по slug
        self.brand = get_object_or_404(Brand, slug=self.kwargs['slug'])
        
        return Product.objects.filter(
            brand=self.brand, 
            available=True
        ).select_related('category', 'brand').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Временно закомментируем работу с изображениями
        # context['main_image'] = product.images.filter(is_main=True).first()
        # context['other_images'] = product.images.exclude(is_main=True)
        
        context['related_products'] = Product.objects.filter(
            category=product.category, 
            available=True
        ).exclude(id=product.id)[:4]
        
        return context