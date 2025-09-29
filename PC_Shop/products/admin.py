# products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from .models import Category, Brand, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'is_main', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Предпросмотр"

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'product_count', 'has_image']
    list_display_links = ['name', 'slug']
    list_editable = ['parent']
    list_filter = ['parent']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    readonly_fields = ['product_count']
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'slug', 'parent', 'description']
        }),
        ('Изображение', {
            'fields': ['image'],
            'classes': ['collapse']
        }),
    ]
    
    def product_count(self, obj):
        count = obj.products.count()
        url = (
            reverse("admin:products_product_changelist")
            + "?"
            + urlencode({"category__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} товаров</a>', url, count)
    product_count.short_description = "Количество товаров"
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = "Есть изображение"

class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count']
    list_display_links = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    readonly_fields = ['product_count']
    
    def product_count(self, obj):
        count = obj.products.count()
        url = (
            reverse("admin:products_product_changelist")
            + "?"
            + urlencode({"brand__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} товаров</a>', url, count)
    product_count.short_description = "Количество товаров"

class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'price', 
        'category', 
        'brand', 
        'stock', 
        'available',
        'created_short',
        'image_preview'
    ]
    list_display_links = ['name', 'image_preview']
    list_editable = ['price', 'stock', 'available']
    list_filter = [
        'available', 
        'category', 
        'brand', 
        'created',
        'updated'
    ]
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description', 'category__name', 'brand__name']
    readonly_fields = ['created', 'updated', 'main_image_preview']
    date_hierarchy = 'created'
    inlines = [ProductImageInline]
    
    fieldsets = [
        ('Основная информация', {
            'fields': [
                'name', 
                'slug', 
                'description',
                'main_image_preview'
            ]
        }),
        ('Цена и наличие', {
            'fields': [
                'price',
                'stock',
                'available'
            ]
        }),
        ('Категория и бренд', {
            'fields': [
                'category',
                'brand'
            ]
        }),
        ('Даты', {
            'fields': [
                'created',
                'updated'
            ],
            'classes': ['collapse']
        }),
    ]
    
    def make_available(self, request, queryset):
        updated = queryset.update(available=True)
        self.message_user(request, f"{updated} товаров теперь доступны")
    make_available.short_description = "Сделать выбранные товары доступными"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(available=False)
        self.message_user(request, f"{updated} товаров теперь недоступны")
    make_unavailable.short_description = "Сделать выбранные товары недоступными"
    
    def increase_price_10_percent(self, request, queryset):
        for product in queryset:
            product.price *= 1.1
            product.save()
        self.message_user(request, f"Цены увеличены на 10% для {queryset.count()} товаров")
    increase_price_10_percent.short_description = "Увеличить цену на 10%"
    
    def created_short(self, obj):
        return obj.created.strftime('%d.%m.%Y')
    created_short.short_description = 'Создан'
    
    def image_preview(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />', 
                main_image.image.url
            )
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />', 
                first_image.image.url
            )
        return "—"
    image_preview.short_description = "Изображение"
    
    def main_image_preview(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return format_html(
                '<img src="{}" width="200" height="200" style="object-fit: cover; border: 1px solid #ccc;" />', 
                main_image.image.url
            )
        return "Главное изображение не установлено"
    main_image_preview.short_description = "Предпросмотр главного изображения"
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.images.filter(is_main=True).exists():
            first_image = obj.images.first()
            if first_image:
                first_image.is_main = True
                first_image.save()
    
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'brand').prefetch_related('images')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)