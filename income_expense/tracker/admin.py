from django.contrib import admin
from .models import PaymentVoucher, Category


class PaymentVoucherAdmin(admin.ModelAdmin):
    list_display = ['prepared_by', 'request_by', 'payee', 'transaction_type', 'cheque_number', 'bank_name', 'payment_method', 'item', 'quantity', 'amount', 'total_amount', 'description', 'status', 'date']
    search_fields = ['prepared_by__username', 'request_by', 'payee', 'transaction_type', 'cheque_number', 'bank_name', 'payment_method', 'item', 'quantity', 'amount', 'total_amount', 'description', 'status', 'date']
    list_filter = ['prepared_by', 'request_by', 'payee', 'transaction_type', 'cheque_number', 'bank_name', 'payment_method', 'item', 'quantity', 'amount', 'total_amount', 'description', 'status', 'date']


admin.site.register(PaymentVoucher, PaymentVoucherAdmin)
admin.site.register(Category)