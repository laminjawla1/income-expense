from django.contrib import admin
from .models import PaymentVoucher, Category, Company


class PaymentVoucherAdmin(admin.ModelAdmin):
    list_display = ['prepared_by', 'request_by', 'transaction_type', 'category', 'item_one_quantity', 'item_two_unit_price', 'total_amount', 'status', 'date']
    search_fields = ['prepared_by__username', 'request_by', 'payee', 'transaction_type', 'cheque_number', 'bank_name', 'payment_method', 'total_amount', 'description', 'status', 'date']
    list_filter = ['prepared_by__profile__company__name', 'transaction_type', 'bank_name', 'payment_method', 'status', 'date']
admin.site.register(PaymentVoucher, PaymentVoucherAdmin)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'limit']
    search_fields = ['name']
admin.site.register(Company, CompanyAdmin)


admin.site.register(Category)