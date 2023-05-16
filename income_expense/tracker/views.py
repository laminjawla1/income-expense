from django.shortcuts import render
from .models import PaymentVoucher, Category
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.mail import send_mail
from datetime import datetime
from .utils import gmd
import os
import inflect
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

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
        'final_review': final_review, 'on_hold': on_hold, 'current_page': 'dashboard'
    })

@login_required
def transactions(request):
    transactions = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
    ).all().order_by("-date")
    if request.method == 'POST':
        date = request.POST.get('date')
        if date:
            try:
                date = date.split('-')
            except:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('payrolls'))
            try:
                _date = datetime(int(date[0]), int(date[1]), int(date[2]))
            except:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('payrolls'))
            transactions = PaymentVoucher.objects.filter(
                pv_id__icontains=request.POST['pv_id'],
                prepared_by__username__icontains=request.POST['prepared_by'],
                request_by__icontains=request.POST['request_by'],
                status__icontains=request.POST['status'],
                category__name__icontains=request.POST['category'],
                prepared_by__profile__company=request.user.profile.company,
                transaction_type__icontains = request.POST['transaction_type'], 
                date__year=_date.year, date__month=_date.month, date__day=_date.day
            )
        else:
            transactions = PaymentVoucher.objects.filter(
                pv_id__icontains=request.POST['pv_id'],
                prepared_by__username__icontains=request.POST['prepared_by'],
                request_by__icontains=request.POST['request_by'],
                status__icontains=request.POST['status'],
                category__name__icontains=request.POST['category'],
                prepared_by__profile__company=request.user.profile.company,
                transaction_type__icontains = request.POST['transaction_type']
            )
        if not transactions:
            messages.error(request, "No Entries Available")
        else:
            messages.success(request, "Result generated")
    page = request.GET.get('page', 1)
    paginator = Paginator(transactions, 10)

    total_amount_total = transactions.aggregate(Sum('total_amount')).get('total_amount__sum')


    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    income_amount = 0
    expense_amount = 0

    income_amount = PaymentVoucher.objects.filter(
        prepared_by__profile__company=request.user.profile.company,
        transaction_type="Income", status="Approved",
    ).aggregate(Sum('total_amount')).get('total_amount__sum')
    expense_amount = PaymentVoucher.objects.filter(
        prepared_by__profile__company=request.user.profile.company,
        transaction_type="Expense", status="Approved",
    ).aggregate(Sum('total_amount')).get('total_amount__sum')

    if not income_amount:
        income_amount = 0
    if not expense_amount:
        expense_amount = 0

    profit = income_amount - expense_amount

    return render(request, "tracker/transactions.html", {
        'transactions': paginator, 'total_amount_total': total_amount_total, 'current_page': 'transactions',
        'income_amount': income_amount, 'expense_amount': expense_amount, 'profit': profit
    })

class Transact(LoginRequiredMixin, CreateView):
    model = PaymentVoucher
    template_name = "tracker/transact_form.html"
    fields = ['request_by', 'transaction_type',
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
        if form.instance.status != "Audit Level":
            messages.error(self.request, "Sorry: You can only change the status to Audit Level")
            form
            return HttpResponseRedirect(reverse("transact"))
        
        form.instance.prepared_by = self.request.user

        form.instance.total_amount = 0

        if form.instance.item_one and form.instance.item_one_quantity and form.instance.item_one_unit_price:
            form.instance.item_one_total_price = form.instance.item_one_quantity * form.instance.item_one_unit_price
            form.instance.total_amount += form.instance.item_one_total_price

        if form.instance.item_two and form.instance.item_two_quantity and form.instance.item_two_unit_price:
            form.instance.item_two_total_price = form.instance.item_two_quantity * form.instance.item_two_unit_price
            form.instance.total_amount += form.instance.item_two_total_price

        if form.instance.item_three and form.instance.item_three_quantity and form.instance.item_three_unit_price:
            form.instance.item_three_total_price = form.instance.item_three_quantity * form.instance.item_three_unit_price
            form.instance.total_amount += form.instance.item_three_total_price

        if form.instance.item_four and form.instance.item_four_quantity and form.instance.item_four_unit_price:
            form.instance.item_four_total_price = form.instance.item_four_quantity * form.instance.item_four_unit_price
            form.instance.total_amount += form.instance.item_four_total_price

        if form.instance.item_five and form.instance.item_five_quantity and form.instance.item_five_unit_price:
            form.instance.item_five_total_price = form.instance.item_five_quantity * form.instance.item_five_unit_price
            form.instance.total_amount += form.instance.item_five_total_price

        if form.instance.item_six and form.instance.item_six_quantity and form.instance.item_six_unit_price:
            form.instance.item_six_total_price = form.instance.item_six_quantity * form.instance.item_six_unit_price
            form.instance.total_amount += form.instance.item_six_total_price

        if form.instance.item_seven and form.instance.item_seven_quantity and form.instance.item_seven_unit_price:
            form.instance.item_seven_total_price = form.instance.item_seven_quantity * form.instance.item_seven_unit_price
            form.instance.total_amount += form.instance.item_seven_total_price

        if form.instance.item_eight and form.instance.item_eight_quantity and form.instance.item_eight_unit_price:
            form.instance.item_eight_total_price = form.instance.item_eight_quantity * form.instance.item_eight_unit_price
            form.instance.total_amount += form.instance.item_eight_total_price

        if form.instance.item_nine and form.instance.item_nine_quantity and form.instance.item_nine_unit_price:
            form.instance.item_nine_total_price = form.instance.item_nine_quantity * form.instance.item_nine_unit_price
            form.instance.total_amount += form.instance.item_nine_total_price

        if form.instance.item_ten and form.instance.item_ten_quantity and form.instance.item_ten_unit_price:
            form.instance.item_ten_total_price = form.instance.item_ten_quantity * form.instance.item_ten_unit_price
            form.instance.total_amount += form.instance.item_ten_total_price

        send_mail(
            f'New {form.instance.transaction_type}',
            f'{self.request.user.first_name} {self.request.user.last_name} added an item(s) worth {gmd(form.instance.total_amount)}.', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        messages.success(self.request, f"New {form.instance.transaction_type} added successfully 😊")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        total_transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__company=self.request.user.profile.company,
        ).count()
        transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__company=self.request.user.profile.company,
        ).order_by('-date')[:10]
        context = super(Transact, self).get_context_data(*args, **kwargs)
        context['button'] = 'Add'
        context['legend'] = 'Add Transaction'
        context['recent'] = 'Recent Transactions'
        context['total'] = total_transactions
        context['recents'] = transactions
        context['current_page'] = 'transactions'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.profile.title == "Accountant":
            form.fields['status'].choices = [("Accounts Desk", "Accounts Desk"), ("Audit Level", "Audit Level")]
        return form
    
class UpdateTransact(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PaymentVoucher
    template_name = "tracker/transact_form.html"
    fields = ['request_by', 'transaction_type',
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
        if form.instance.status != "Audit Level":
            messages.error(self.request, "Sorry: You can only change the status to Audit Level")
            return HttpResponseRedirect(reverse("transact"))
        
        form.instance.prepared_by = self.request.user

        form.instance.total_amount = 0

        if form.instance.item_one and form.instance.item_one_quantity and form.instance.item_one_unit_price:
            form.instance.item_one_total_price = form.instance.item_one_quantity * form.instance.item_one_unit_price
            form.instance.total_amount += form.instance.item_one_total_price

        if form.instance.item_two and form.instance.item_two_quantity and form.instance.item_two_unit_price:
            form.instance.item_two_total_price = form.instance.item_two_quantity * form.instance.item_two_unit_price
            form.instance.total_amount += form.instance.item_two_total_price

        if form.instance.item_three and form.instance.item_three_quantity and form.instance.item_three_unit_price:
            form.instance.item_three_total_price = form.instance.item_three_quantity * form.instance.item_three_unit_price
            form.instance.total_amount += form.instance.item_three_total_price

        if form.instance.item_four and form.instance.item_four_quantity and form.instance.item_four_unit_price:
            form.instance.item_four_total_price = form.instance.item_four_quantity * form.instance.item_four_unit_price
            form.instance.total_amount += form.instance.item_four_total_price

        if form.instance.item_five and form.instance.item_five_quantity and form.instance.item_five_unit_price:
            form.instance.item_five_total_price = form.instance.item_five_quantity * form.instance.item_five_unit_price
            form.instance.total_amount += form.instance.item_five_total_price

        if form.instance.item_six and form.instance.item_six_quantity and form.instance.item_six_unit_price:
            form.instance.item_six_total_price = form.instance.item_six_quantity * form.instance.item_six_unit_price
            form.instance.total_amount += form.instance.item_six_total_price

        if form.instance.item_seven and form.instance.item_seven_quantity and form.instance.item_seven_unit_price:
            form.instance.item_seven_total_price = form.instance.item_seven_quantity * form.instance.item_seven_unit_price
            form.instance.total_amount += form.instance.item_seven_total_price

        if form.instance.item_eight and form.instance.item_eight_quantity and form.instance.item_eight_unit_price:
            form.instance.item_eight_total_price = form.instance.item_eight_quantity * form.instance.item_eight_unit_price
            form.instance.total_amount += form.instance.item_eight_total_price

        if form.instance.item_nine and form.instance.item_nine_quantity and form.instance.item_nine_unit_price:
            form.instance.item_nine_total_price = form.instance.item_nine_quantity * form.instance.item_nine_unit_price
            form.instance.total_amount += form.instance.item_nine_total_price

        if form.instance.item_ten and form.instance.item_ten_quantity and form.instance.item_ten_unit_price:
            form.instance.item_ten_total_price = form.instance.item_ten_quantity * form.instance.item_ten_unit_price
            form.instance.total_amount += form.instance.item_ten_total_price

        messages.success(self.request, "Transaction updated successfully.")
        return super().form_valid(form)
    
    
    def test_func(self):
        transaction = self.get_object()
        return not transaction.status == "Approved"
    
    def get_context_data(self, *args, **kwargs):
        total_transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__company=self.request.user.profile.company,
        ).count()
        transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__company=self.request.user.profile.company,
        ).order_by('-date')[:5]
        context = super(UpdateTransact, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update Transaction'
        context['legend'] = 'Update Transaction'
        context['recent'] = 'Recent Transactions'
        context['total'] = total_transactions
        context['recents'] = transactions
        context['current_page'] = 'transactions'
        return context


@login_required
def summary(request):
    if request.method == 'POST':
        date = request.POST['date']
        if date:
            try:
                date = date.split('-')
            except:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('summary'))
            try:
                _date = datetime(int(date[0]), int(date[1]), int(date[2]))
            except:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('summary'))
            
            expenses = PaymentVoucher.objects.filter(
                prepared_by__profile__company=request.user.profile.company,
                transaction_type = "Expense",
                date__year=_date.year, date__month=_date.month, date__day=_date.day,
            ).all().order_by("-date")
            page = request.GET.get('page', 1)
            paginator = Paginator(expenses, 2)

            expense_total_amount_total = PaymentVoucher.objects.filter(
                prepared_by__profile__company=request.user.profile.company,
                transaction_type = "Expense",
                date__year=_date.year, date__month=_date.month, date__day=_date.day,
            ).aggregate(Sum('total_amount')).get('total_amount__sum')

            try:
                paginator = paginator.page(page)
            except:
                paginator = paginator.page(1)

            incomes = PaymentVoucher.objects.filter(
                prepared_by__profile__company=request.user.profile.company,
                transaction_type = "Income",
                date__year=_date.year, date__month=_date.month, date__day=_date.day,
                ).all().order_by("-date")

            incomes_t = PaymentVoucher.objects.filter(
                prepared_by__profile__company=request.user.profile.company,
                transaction_type = "Income",
                date__year=_date.year, date__month=_date.month, date__day=_date.day,
                ).all()
            expenses_t = PaymentVoucher.objects.filter(
                prepared_by__profile__company=request.user.profile.company,
                transaction_type = "Expense",
                date__year=_date.year, date__month=_date.month, date__day=_date.day,
                ).all()
                
            page = request.GET.get('page', 1)
            paginator1 = Paginator(incomes, 2)

            income_total_amount_total = PaymentVoucher.objects.filter(
                prepared_by__profile__company=request.user.profile.company,
                transaction_type = "Income",
                date__year=_date.year, date__month=_date.month, date__day=_date.day,
            ).aggregate(Sum('total_amount')).get('total_amount__sum')

            try:
                paginator1 = paginator1.page(page)
            except:
                paginator1 = paginator1.page(1)

            income_categories = Category.objects.filter(
                paymentvoucher__transaction_type = "Income",
                paymentvoucher__status = "Approved",
                paymentvoucher__prepared_by__profile__company=request.user.profile.company,
                paymentvoucher__date__year=_date.year, paymentvoucher__date__month=_date.month, paymentvoucher__date__day=_date.day,
            ).annotate(total_amount=Sum('paymentvoucher__total_amount'))
            expense_categories = Category.objects.filter(
                paymentvoucher__transaction_type = "Expense",
                paymentvoucher__status = "Approved",
                paymentvoucher__prepared_by__profile__company=request.user.profile.company,
                paymentvoucher__date__year=_date.year, paymentvoucher__date__month=_date.month, paymentvoucher__date__day=_date.day,
            ).annotate(total_amount=Sum('paymentvoucher__total_amount'))

            return render(request, "tracker/summary.html", {
            'expenses': paginator, 'expense_total_amount_total': expense_total_amount_total, 'incomes': paginator1,
            'income_total_amount_total': income_total_amount_total, 'incomes_t': incomes_t, 'income_categories': income_categories,
            'expenses_t': expenses_t, 'date': timezone.now(), 'current_page': 'summary', 'expense_categories': expense_categories,
    })
    expenses = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Expense"
    ).all().order_by("-date")
    page = request.GET.get('page', 1)
    paginator = Paginator(expenses, 2)

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
        ).all().order_by("-date")

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

    income_total_amount_total = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        prepared_by__profile__company=request.user.profile.company,
        transaction_type = "Income"
    ).aggregate(Sum('total_amount')).get('total_amount__sum')

    try:
        paginator1 = paginator1.page(page)
    except:
        paginator1 = paginator1.page(1)

    income_categories = Category.objects.filter(
        paymentvoucher__transaction_type = "Income",
        paymentvoucher__status = "Approved",
        paymentvoucher__prepared_by__profile__company=request.user.profile.company,
    ).annotate(total_amount=Sum('paymentvoucher__total_amount'))
    expense_categories = Category.objects.filter(
        paymentvoucher__transaction_type = "Expense",
        paymentvoucher__status = "Approved",
        paymentvoucher__prepared_by__profile__company=request.user.profile.company,
    ).annotate(total_amount=Sum('paymentvoucher__total_amount'))

    return render(request, "tracker/summary.html", {
        'expenses': paginator, 'expense_total_amount_total': expense_total_amount_total, 'incomes': paginator1,
        'income_total_amount_total': income_total_amount_total, 'incomes_t': incomes_t, 'income_categories': income_categories,
        'expenses_t': expenses_t, 'date': timezone.now(), 'current_page': 'summary', 'expense_categories': expense_categories,
    })

def render_pv(request, pv_id):
    pv = PaymentVoucher.objects.filter(id=pv_id).first()
    if not pv:
        messages.error(request, 'No such payment voucher')
        return HttpResponseRedirect(reverse('transactions'))
    total_amount_in_words = inflect.engine()
    total_amount_in_words = total_amount_in_words.number_to_words(int(pv.total_amount)).capitalize() + " dalasis"
    return render(request, 'tracker/pv.html', {
        'pv': pv, 'total_amount_in_words': total_amount_in_words, 'current_page': 'transactions'
        })