from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ['first_name',
                    'phone', 'email', 'order_total', 'status', 'is_ordered', 'created_at']


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
