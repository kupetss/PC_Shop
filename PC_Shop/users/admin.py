from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from .models import User
from orders.models import Order

class PurchaseHistoryInline(admin.StackedInline):
    """Inline для отображения истории покупок"""
    model = Order
    fk_name = 'user'
    extra = 0
    max_num = 15
    can_delete = False
    readonly_fields = ['order_info', 'created', 'total_price', 'status', 'paid_status', 'view_link']
    fields = ['order_info', 'created', 'total_price', 'status', 'paid_status', 'view_link']
    verbose_name = "Заказ"
    verbose_name_plural = "История покупок"
    
    def order_info(self, obj):
        return f"Заказ #{obj.id}"
    order_info.short_description = "Номер заказа"
    
    def paid_status(self, obj):
        if obj.paid:
            return format_html('<span style="color: green;">✅ Оплачен</span>')
        return format_html('<span style="color: red;">❌ Не оплачен</span>')
    paid_status.short_description = "Статус оплаты"
    
    def view_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.id])
        return format_html('<a href="{}" class="button">📋 Детали заказа</a>', url)
    view_link.short_description = "Действия"
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'order_count', 'total_spent', 'is_staff', 'date_joined_short']
    list_display_links = ['username', 'email']
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email']
    readonly_fields = ['order_count', 'total_spent_display', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Информация', {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Статистика', {
            'fields': ('order_count', 'total_spent_display'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PurchaseHistoryInline]
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).prefetch_related('order_set')
    
    def order_count(self, obj):
        count = obj.get_order_count()
        if count > 0:
            url = reverse("admin:orders_order_changelist") + "?" + urlencode({"user__id": f"{obj.id}"})
            return format_html('<a href="{}">{} заказов</a>', url, count)
        return "0 заказов"
    order_count.short_description = "Заказы"
    
    def total_spent(self, obj):
        total = obj.get_total_spent()
        return format_html('<span style="font-weight: bold;">{:.2f} ₽</span>', total)
    total_spent.short_description = "Потрачено"
    
    def total_spent_display(self, obj):
        total = obj.get_total_spent()
        return format_html('<span style="font-size: 18px; font-weight: bold; color: green;">{:.2f} ₽</span>', total)
    total_spent_display.short_description = "Общая сумма покупок"
    
    def date_joined_short(self, obj):
        return obj.date_joined.strftime('%d.%m.%Y')
    date_joined_short.short_description = 'Регистрация'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions