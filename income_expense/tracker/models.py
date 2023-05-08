from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name

class PaymentVoucher(models.Model):
    transaction_type = models.CharField(max_length=50, choices=[
        ("Income", "Income"),
        ("Expense", "Expense"),
    ])
    prepared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    request_by = models.CharField(max_length=50, blank=True, null=True)
    payee = models.CharField(max_length=50, null=True, blank=True)
    cheque_number = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=100, choices=[
        ("Yonna Islamic Microfinance", "Yonna Islamic Microfinance"),
        ("Ecobank", "Ecobank"),
        ("GT-Bank", "GT-Bank"),
        ("Access Bank", "Access Bank"),
        ("Trust Bank", "Trust Bank"),
    ], null=True, blank=True)

    item_one = models.CharField('Item 1', max_length=120, default='', blank=True, null=True)
    item_one_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_one_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_one_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    item_two = models.CharField('Item 2', max_length=120, default='', blank=True, null=True)
    item_two_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_two_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_two_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    item_three = models.CharField('Item 3', max_length=120, default='', blank=True, null=True)
    item_three_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_three_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_three_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    item_four = models.CharField('Item 4', max_length=120, default='', blank=True, null=True)
    item_four_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_four_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_four_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    item_five = models.CharField('Item 5', max_length=120, default='', blank=True, null=True)
    item_five_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_five_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_five_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    item_six = models.CharField('Item 6', max_length=120, default='', blank=True, null=True)
    item_six_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_six_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_six_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    item_seven = models.CharField('Item 7', max_length=120, default='', blank=True, null=True)
    item_seven_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_seven_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_seven_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    item_eight = models.CharField('Item 8', max_length=120, default='', blank=True, null=True)
    item_eight_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_eight_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_eight_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    item_nine = models.CharField('Item 9', max_length=120, default='', blank=True, null=True)
    item_nine_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_nine_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_nine_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    item_ten = models.CharField('Item 10', max_length=120, default='', blank=True, null=True)
    item_ten_quantity = models.IntegerField('Quantity', default=0, blank=True, null=True)
    item_ten_unit_price = models.FloatField('Unit Price (D)', default=0, blank=True, null=True)
    item_ten_total_price = models.FloatField('Entry Total (D)', default=0, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    total_amount = models.FloatField(default=0)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=[
        ("Audit Level", "Audit Level"),
        ("Management Level", "Management Level"),
        ("Final Review", "Final Review"),
        ("Approved", "Approved"),
        ("On Hold", "On Hold"),
    ])
    payment_method = models.CharField(max_length=50, choices=[
        ("Cash", "Cash"),
        ("Bank Transfer", "Bank Transfer"),
        ("Cheque", "Cheque"),
    ], null=True, blank=True)
    date = models.DateField(default=timezone.now)
    pv_id = models.CharField(max_length=128, null=True, blank=True, unique=True)

    def __str__(self):
        return self.prepared_by.username
    
    def save(self, *args, **kwargs):
        id = 1
        if not self.pv_id:
            # Get the last invoice number from the database
            last_pv = PaymentVoucher.objects.last()
            if last_pv:
                id = last_pv.pk + 1
        if not self.pv_id:
            self.pv_id = timezone.now().strftime("%Y-%m-%d") + "-" + "%06d" % id
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.transaction_type == "Income":
            return reverse('incomes')
        return reverse('incomes')
