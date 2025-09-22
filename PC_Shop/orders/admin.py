# orders/admin.py
from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'paid', 'status', 'created_short']
    list_filter = ['paid', 'status', 'created']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created', 'updated']
    
    def created_short(self, obj):
        return obj.created.strftime('%d.%m.%Y %H:%M')
    created_short.short_description = 'Создан'