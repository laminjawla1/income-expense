from django.shortcuts import render
from .models import PaymentVoucher
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.mail import send_mail
from .utils import gmd
import os

@login_required
def dashboard(request):
    total_cfs = len(PaymentVoucher.objects.filter(prepared_by__profile__company=request.user.profile.company))
    audit_level = len(PaymentVoucher.objects.filter(
            prepared_by__profile__company=request.user.profile.company, status="Audit Level"))
    approved_cfs = len(PaymentVoucher.objects.filter(
            prepared_by__profile__company=request.user.profile.company, status="Approved"))
    management = len(PaymentVoucher.objects.filter(
            prepared_by__profile__company=request.user.profile.company, status="Management Level"))
    final_review = len(PaymentVoucher.objects.filter(
            prepared_by__profile__company=request.user.profile.company, status="Final Review"))
    on_hold = len(PaymentVoucher.objects.filter(
            prepared_by__profile__company=request.user.profile.company, status="On Hold"))

    return render(request, "tracker/dashboard.html",{
        'total_cfs': total_cfs, 'audit_level': audit_level, 'approved_cfs': approved_cfs, 'management': management,
        'final_review': final_review, 'on_hold': on_hold
    })

@login_required
def index(request):

    return render(request, "tracker/dashboard.html",{
    })


@login_required
def incomes(request):
    incomes = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Income"
    ).all()
    page = request.GET.get('page', 1)
    paginator = Paginator(incomes, 10)

    # quantity_total = PaymentVoucher.objects.filter(
    #     date__year=timezone.now().year, date__month=timezone.now().month,
    #     prepared_by__profile__company=request.user.profile.company,
    #     transaction_type = "Income"
    # ).aggregate(Sum('quantity')).get('quantity__sum')
    # amount_total = PaymentVoucher.objects.filter(
    #     date__year=timezone.now().year, date__month=timezone.now().month,
    #     prepared_by__profile__company=request.user.profile.company,
    #     transaction_type = "Income"
    # ).aggregate(Sum('amount')).get('amount__sum')
    total_amount_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Income"
    ).aggregate(Sum('total_amount')).get('total_amount__sum')
    quantity_total = 0
    amount_total = 0
    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "tracker/income.html", {
        'incomes': paginator, 'quantity_total': quantity_total, 'amount_total': amount_total, 'total_amount_total': total_amount_total
    })

class AddIncome(LoginRequiredMixin, CreateView):
    model = PaymentVoucher
    template_name = "tracker/income_form.html"
    fields = ['request_by',
	                'item_one', 'item_one_quantity', 'item_one_unit_price', 'item_one_total_price',
	                'item_two', 'item_two_quantity', 'item_two_unit_price', 'item_two_total_price',
	                'item_three', 'item_three_quantity', 'item_three_unit_price', 'item_three_total_price',
	                'item_four', 'item_four_quantity', 'item_four_unit_price', 'item_four_total_price',
	                'item_five', 'item_five_quantity', 'item_five_unit_price', 'item_five_total_price',
	                'item_six', 'item_six_quantity', 'item_six_unit_price', 'item_six_total_price',
	                'item_seven', 'item_seven_quantity', 'item_seven_unit_price', 'item_seven_total_price',
	                'item_eight', 'item_eight_quantity', 'item_eight_unit_price', 'item_eight_total_price',
	                'item_nine', 'item_nine_quantity', 'item_nine_unit_price', 'item_nine_total_price',
	                'item_ten', 'item_ten_quantity', 'item_ten_unit_price', 'item_ten_total_price',
	                'total_amount', 'category', 'payment_method', 'status', 'description']

    def form_valid(self, form):
        form.instance.prepared_by = self.request.user
        form.instance.transaction_type = "Income"
        form.instance.status = "Audit Level"
        form.instance.total_amount = form.instance.amount * form.instance.quantity
        send_mail(
            'New Income',
            f'{self.request.user.first_name} {self.request.user.last_name} added {form.instance.quantity} item(s) worth {gmd(form.instance.total_amount)}.', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        messages.success(self.request, "New income added successfully 😊")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(AddIncome, self).get_context_data(*args, **kwargs)
        context['button'] = 'Add'
        context['legend'] = 'Add Income'
        context['recent'] = 'Recent Incomes'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        print(form)
        # form.fields['agent'].queryset = User.objects.filter(profile__is_supervisor=True).exclude(id=self.request.user.id)
        return form

class UpdateIncome(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PaymentVoucher
    template_name = "tracker/income_form.html"
    fields = ['request_by', 'item', 'quantity', 'amount', 'total_amount', 'category', 'payment_method', 'description']

    def form_valid(self, form):
        form.instance.prepared_by = self.request.user
        form.instance.transaction_type = "Income"
        form.instance.status = "Audit Level"
        form.instance.total_amount = form.instance.amount * form.instance.quantity
        messages.success(self.request, "Income updated successfully.")
        return super().form_valid(form)
    
    
    def test_func(self):
        income = self.get_object()
        return not income.status == "Approved"
    
    def get_context_data(self, *args, **kwargs):
        context = super(UpdateIncome, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        context['recent'] = 'Recent Incomes'
        return context

@login_required
def expenses(request):
    expenses = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
    ).all()
    page = request.GET.get('page', 1)
    paginator = Paginator(expenses, 10)

    quantity_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
    ).aggregate(Sum('quantity')).get('quantity__sum')
    amount_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
    ).aggregate(Sum('amount')).get('amount__sum')
    total_amount_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
    ).aggregate(Sum('total_amount')).get('total_amount__sum')

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "tracker/expense.html", {
        'expenses': paginator, 'quantity_total': quantity_total, 'amount_total': amount_total, 'total_amount_total': total_amount_total
    })

@login_required
def summary(request):
    expenses = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
    ).all()
    page = request.GET.get('page', 1)
    paginator = Paginator(expenses, 2)

    expense_quantity_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
    )#.aggregate(Sum('quantity')).get('quantity__sum')
    expense_amount_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
    )#.aggregate(Sum('amount')).get('amount__sum')
    expense_total_amount_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
    ).aggregate(Sum('total_amount')).get('total_amount__sum')

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    incomes = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Income"
        ).all()

    incomes_t = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Income"
        ).all()
    expenses_t = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
        ).all()
        
    page = request.GET.get('page', 1)
    paginator1 = Paginator(incomes, 2)

    income_quantity_total = len(PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Income"
    ))#.aggregate(Sum('quantity')).get('quantity__sum')
    income_amount_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Income"
    )#.aggregate(Sum('amount')).get('amount__sum')
    income_total_amount_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Income"
    ).aggregate(Sum('total_amount')).get('total_amount__sum')

    try:
        paginator1 = paginator1.page(page)
    except:
        paginator1 = paginator1.page(1)

    return render(request, "tracker/summary.html", {
        'expenses': paginator, 'expense_quantity_total': expense_quantity_total, 'expense_amount_total': expense_amount_total, 'expense_total_amount_total': expense_total_amount_total, 'incomes': paginator1, 'income_quantity_total': income_quantity_total,
        'income_amount_total': income_amount_total, 'income_total_amount_total': income_total_amount_total, 'incomes_t': incomes_t,
        'expenses_t': expenses_t, 'date': timezone.now()
    })


class AddExpense(LoginRequiredMixin, CreateView):
    model = PaymentVoucher
    template_name = "tracker/income_form.html"
    fields = ['request_by', 'item', 'quantity', 'amount', 'total_amount', 'category', 'payment_method', 'description']

    def form_valid(self, form):
        form.instance.prepared_by = self.request.user
        form.instance.transaction_type = "Expense"
        form.instance.status = "Audit Level"
        form.instance.total_amount = form.instance.amount * form.instance.quantity
        send_mail(
            'New Expense',
            f'{self.request.user.first_name} {self.request.user.last_name} added {form.instance.quantity} item(s) worth {gmd(form.instance.total_amount)}.', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        messages.success(self.request, "New expense added successfully 😊")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(AddExpense, self).get_context_data(*args, **kwargs)
        context['button'] = 'Add'
        context['legend'] = 'Add Expense'
        context['recent'] = 'Recent Expenses'
        return context

class UpdateExpense(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PaymentVoucher
    template_name = "tracker/income_form.html"
    fields = ['request_by', 'item', 'quantity', 'amount', 'total_amount', 'category', 'payment_method', 'description']

    def form_valid(self, form):
        form.instance.prepared_by = self.request.user
        form.instance.transaction_type = "Expense"
        form.instance.status = "Audit Level"
        form.instance.total_amount = form.instance.amount * form.instance.quantity
        messages.success(self.request, "Expense updated successfully.")
        return super().form_valid(form)
    
    
    def test_func(self):
        expense = self.get_object()
        return not expense.status == "Approved"
    
    def get_context_data(self, *args, **kwargs):
        context = super(UpdateExpense, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        context['legend'] = 'Update Expense'
        context['recent'] = 'Recent Expenses'
        return context