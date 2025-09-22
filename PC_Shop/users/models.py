from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def get_order_count(self):
        """Количество заказов пользователя"""
        return self.order_set.count()

    def get_total_spent(self):
        """Общая сумма покупок пользователя"""
        from django.db.models import Sum
        result = self.order_set.aggregate(total=Sum('total_price'))
        return result['total'] or 0