import csv
from datetime import datetime

import inflect
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView

from .models import Category, Company, PaymentVoucher
from .utils import gmd


@login_required
def dashboard(request):
    if request.user.is_staff:
        total_cfs = len(PaymentVoucher.objects.all())
        audit_level = len(PaymentVoucher.objects.filter(status="Audit Level"))
        approved_cfs = len(PaymentVoucher.objects.filter(approved=True))
        management = len(PaymentVoucher.objects.filter(status="Management Level"))
        final_review = len(PaymentVoucher.objects.filter(status="Final Review"))
        on_hold = len(PaymentVoucher.objects.filter(status="On Hold"))
        transactions = PaymentVoucher.objects.order_by('-total_amount').all()[:5]
        total_transactions = PaymentVoucher.objects.count()
    else:
        total_cfs = len(PaymentVoucher.objects.filter(prepared_by__profile__company__in=request.user.profile.company.all()))
        audit_level = len(PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(), status="Audit Level"))
        approved_cfs = len(PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(), approved=True))
        management = len(PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(), status="Management Level"))
        final_review = len(PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(), status="Final Review"))
        on_hold = len(PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(), status="On Hold"))
        transactions = PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(),
            ).order_by('-total_amount')[:5]
        total_transactions = PaymentVoucher.objects.filter(prepared_by__profile__company__in=request.user.profile.company.all()).count()

    return render(request, "tracker/dashboard.html",{
        'total_cfs': total_cfs, 'audit_level': audit_level, 'approved_cfs': approved_cfs, 'management': management,
        'final_review': final_review, 'on_hold': on_hold, 'current_page': 'dashboard', 'recents': transactions,
        'total_transactions': total_transactions, 'company_balance': request.user.profile.company.first().limit
    })

@login_required
def transactions(request):
    transactions = PaymentVoucher.objects.filter(
        prepared_by__profile__company__in=request.user.profile.company.all(),
        date__year=timezone.now().year, date__month=timezone.now().month,
    ).order_by("-pv_id")

    if request.method == 'POST':
        if request.POST.get('from_date') and request.POST.get('to_date'):
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            items = PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(),
                date__gte=datetime.strptime(from_date, '%Y-%m-%d'),
                date__lte=datetime.strptime(to_date, '%Y-%m-%d'),
            ).order_by('date')
            if not items:
                messages.error(request, "No transaction is available for download")
                return HttpResponseRedirect(reverse("transactions"))
            headers = ["TRANSACTION NUMBER", "TRANSACTION TYPE", "REQUEST BY", "PREPARED BY", "REVIEWED BY", "VERIFIED BY", "APPROVED BY",
                        "PAYEE", "CHEQUE NUMBER", "ACCOUNT NUMBER", "BANK", "ENTRIES", "QUANTITIES", "UNIT PRICES", "TOTAL",
                        "CATEGORY", "STATUS", "PAYMENT METHOD", "DATE", "DESCRIPTION"]
            
            response = HttpResponse(
                content_type='text/csv',
                headers = {'Content-Disposition': f'attachment; filename="{request.user.profile.company.first()}_transactions_{from_date}_to_{to_date}.csv"'},
            )
            writer = csv.writer(response)
            writer.writerow(["PAYMENT VOUCHERS"])
            writer.writerow(headers)
            for w in items:
                n_items = 0
                if w.item_one:
                    n_items += 1
                if w.item_two:
                    n_items += 1
                if w.item_three:
                    n_items += 1
                if w.item_four:
                    n_items += 1
                if w.item_five:
                    n_items += 1
                if w.item_six:
                    n_items += 1
                if w.item_seven:
                    n_items += 1
                if w.item_eight:
                    n_items += 1
                if w.item_nine:
                    n_items += 1
                if w.item_ten:
                    n_items += 1
                # try:
                writer.writerow([w.pv_id, w.transaction_type, w.request_by, f'{w.prepared_by.first_name} {w.prepared_by.last_name}', 
                                f'{w.reviewed_by.first_name} {w.reviewed_by.last_name}',
                                f'{w.verified_by.first_name} {w.verified_by.last_name}', 
                                f'{w.approved_by.first_name} {w.approved_by.last_name}', w.payee, w.cheque_number,
                                w.account_number, w.bank_name, n_items,

                                (w.item_one_quantity + w.item_two_quantity + w.item_three_quantity + w.item_four_quantity +
                                w.item_five_quantity + w.item_six_quantity + w.item_seven_quantity + w.item_eight_quantity + w.item_nine_quantity + w.item_ten_quantity),

                                (w.item_one_unit_price + w.item_two_unit_price + w.item_three_unit_price + w.item_four_unit_price +
                                w.item_five_unit_price + w.item_six_unit_price + w.item_seven_unit_price + w.item_eight_unit_price + w.item_nine_unit_price + w.item_ten_unit_price),

                                (w.item_one_total_price + w.item_two_total_price + w.item_three_total_price + w.item_four_total_price +
                                w.item_five_total_price + w.item_six_total_price + w.item_seven_total_price + w.item_eight_total_price + w.item_nine_total_price + w.item_ten_total_price),

                                w.category.name, w.status, w.payment_method, w.date, w.description])
                # except:
                #     messages.warning(request, "An error occured while processing the request. \
                #                     It seems like the selected transactions has not been reviewed,\
                #                     verified or approved. If that's so, please inform the right people responsible for that")
                #     return HttpResponseRedirect(reverse("transactions"))
            return response
        date = request.POST.get('date')
        if date:
            try:
                _date = datetime.strptime(date, '%Y-%m-%d')
                transactions = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__in=request.user.profile.company.all(),
                    date__year=_date.year, date__month=_date.month)
            except ValueError:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('transactions'))

        transactions = transactions.filter(
            pv_id__icontains=request.POST.get('pv_id', ""),
            prepared_by__first_name__icontains=request.POST.get('prepared_by', ""),
            request_by__icontains=request.POST.get('request_by', ""),
            status__icontains=request.POST.get('status', ""),
            category__name__icontains=request.POST.get('category', ""),
            transaction_type__icontains=request.POST.get('transaction_type', "")
        )

        if not transactions:
            messages.error(request, "No Entries Available")

    if request.method == "GET":
        paginator = Paginator(transactions, 6)
        page = request.GET.get('page', 1)

        try:
            paginator_page = paginator.page(page)
        except:
            paginator_page = paginator.page(1)
    else:
        paginator_page = transactions

    income_amount = transactions.filter(
        transaction_type="Income",
        approved=True
    ).aggregate(total_amount_sum=Sum('total_amount'))['total_amount_sum'] or 0

    expense_amount = transactions.filter(
        transaction_type="Expense",
        approved=True
    ).aggregate(total_amount_sum=Sum('total_amount'))['total_amount_sum'] or 0

    profit = income_amount - expense_amount

    return render(request, "tracker/transactions.html", {
        'transactions': paginator_page, 'current_page': 'transactions',
        'income_amount': income_amount, 'expense_amount': expense_amount,
        'profit': profit, 'company_balance': request.user.profile.company.first().limit
    })

class Transact(LoginRequiredMixin, CreateView):
    model = PaymentVoucher
    template_name = "tracker/transact_form.html"
    fields = ['date', 'request_by', 'transaction_type',
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
        if form.instance.status != "Audit Level": # and form.instance.status != "Accounts Desk":
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
        
        if form.instance.transaction_type == 'Expense':
            if not self.request.user.profile.company.first().limit - form.instance.total_amount >= 0:
                messages.error(self.request, f"The balance of {self.request.user.profile.company.first()} is \
                               {gmd(self.request.user.profile.company.first().limit)}. Not sufficient to make this expense")
                return HttpResponseRedirect(reverse("transact"))

        auditor = User.objects.filter(profile__company__in=self.request.user.profile.company.all(), profile__title="Auditor").first()
        send_mail(
            f' New Transaction Recorded - [{form.instance.transaction_type}]',

            
            f"""Dear {auditor.first_name} {auditor.last_name},

I hope this email finds you well. I would like to inform you that a new transaction has been recorded in our financial system. The details of the transaction are as follows:

Type: {form.instance.transaction_type}
Request By: {form.instance.request_by}
Date: {form.instance.date.strftime('%Y-%m-%d')}
Amount: {gmd(form.instance.total_amount)}
Category: {form.instance.category}

Description: {form.instance.description}

Please review the transaction at your earliest convenience and ensure its accuracy. If you have any questions or require additional information, please don't hesitate to reach out to me.

Thank you for your attention to this matter.

Best regards,
{form.instance.prepared_by.first_name} {form.instance.prepared_by.last_name}
{form.instance.prepared_by.profile.title} - {form.instance.prepared_by.profile.company.first}""", 
            'yonnatech.g@gmail.com',
            [ auditor.email],
            fail_silently=False,
        )
        messages.success(self.request, f"New {form.instance.transaction_type} added successfully 😊")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        total_transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__company__in=self.request.user.profile.company.all(),
        ).count()
        transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__company__in=self.request.user.profile.company.all(),
        ).order_by('-date')[:10]
        context = super(Transact, self).get_context_data(*args, **kwargs)
        context['button'] = 'Add'
        context['legend'] = 'Add Transaction'
        context['recent'] = 'Recent Transactions'
        context['total'] = total_transactions
        context['recents'] = transactions
        context['current_page'] = 'transactions'
        context['company_balance'] = self.request.user.profile.company.first().limit
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['status'].choices = [("Audit Level", "Audit Level")]
        form.fields['date'].widget=forms.DateInput(attrs={'type': 'date'})
        return form

class UpdateTransact(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PaymentVoucher
    template_name = "tracker/transact_update_form.html"
    fields = ['date', 'request_by', 'transaction_type', 'payee', 
                'payment_method', 'cheque_number', 'account_number', 'bank_name',
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
                'total_amount', 'category', 'payment_method', 'description']

    def form_valid(self, form):
        if form.instance.status == "Approved":
            form.instance.approved = True
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
        return not transaction.approved and not transaction.prepared_by.profile.company in self.request.user.profile.company.all()
    
    def get_context_data(self, *args, **kwargs):
        total_transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__company__in=self.request.user.profile.company.all(),
        ).count()
        transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__company__in=self.request.user.profile.company.all(),
        ).order_by('-date')[:15]
        context = super(UpdateTransact, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update Transaction'
        context['legend'] = 'Update Transaction'
        context['recent'] = 'Recent Transactions'
        context['total'] = total_transactions
        context['recents'] = transactions
        context['current_page'] = 'transactions'
        context['company_balance'] = self.request.user.profile.company.first().limit
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget=forms.DateInput(attrs={'type': 'date'})
        return form

@login_required
def summary(request):
    transactions = PaymentVoucher.objects.filter(
        prepared_by__profile__company__in=request.user.profile.company.all(),
    )
    if request.method == 'POST':
        date = request.POST['date']
        if date:
            try:
                _date = datetime.strptime(date, '%Y-%m-%d')
                transactions = transactions.filter(date__year=_date.year, date__month=_date.month)
            except ValueError:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('transactions'))
            
            expenses = transactions.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(),
                transaction_type = "Expense",
            ).all().order_by("-date")
            page = request.GET.get('page', 1)
            paginator = Paginator(expenses, 2)

            expense_total_amount_total = transactions.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(),
                transaction_type = "Expense",
            ).aggregate(Sum('total_amount')).get('total_amount__sum')

            try:
                paginator = paginator.page(page)
            except:
                paginator = paginator.page(1)

            incomes = transactions.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(),
                transaction_type = "Income",
                ).all().order_by("-date")

            incomes_t = transactions.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(),
                transaction_type = "Income",
                ).all()
            expenses_t = transactions.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(),
                transaction_type = "Expense",
                ).all()
                
            page = request.GET.get('page', 1)
            paginator1 = Paginator(incomes, 2)

            income_total_amount_total = transactions.filter(
                prepared_by__profile__company__in=request.user.profile.company.all(),
                transaction_type = "Income",
            ).aggregate(Sum('total_amount')).get('total_amount__sum')

            try:
                paginator1 = paginator1.page(page)
            except:
                paginator1 = paginator1.page(1)

            income_categories = Category.objects.filter(
                paymentvoucher__transaction_type = "Income",
                paymentvoucher__approved=True,
                paymentvoucher__prepared_by__profile__company__in=request.user.profile.company.all(),
                paymentvoucher__date__year=_date.year, paymentvoucher__date__month=_date.month,
            ).annotate(total_amount=Sum('paymentvoucher__total_amount'))
            expense_categories = Category.objects.filter(
                paymentvoucher__transaction_type = "Expense",
                paymentvoucher__approved=True,
                paymentvoucher__prepared_by__profile__company__in=request.user.profile.company.all(),
                paymentvoucher__date__year=_date.year, paymentvoucher__date__month=_date.month,
            ).annotate(total_amount=Sum('paymentvoucher__total_amount'))

            return render(request, "tracker/summary.html", {
            'expenses': paginator, 'expense_total_amount_total': expense_total_amount_total, 'incomes': paginator1,
            'income_total_amount_total': income_total_amount_total, 'incomes_t': incomes_t, 'income_categories': income_categories,
            'expenses_t': expenses_t, 'date': timezone.now(), 'current_page': 'summary', 'expense_categories': expense_categories,
            'company_balance': request.user.profile.company.first().limit
    })
    expenses = transactions.filter(
        prepared_by__profile__company__in=request.user.profile.company.all(),
        transaction_type = "Expense"
    ).all().order_by("-date")
    page = request.GET.get('page', 1)
    paginator = Paginator(expenses, 2)

    expense_total_amount_total = transactions.filter(
        prepared_by__profile__company__in=request.user.profile.company.all(),
        transaction_type = "Expense"
    ).aggregate(Sum('total_amount')).get('total_amount__sum')

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    incomes = transactions.filter(
        prepared_by__profile__company__in=request.user.profile.company.all(),
        transaction_type = "Income"
        ).all().order_by("-date")

    incomes_t = transactions.filter(
        prepared_by__profile__company__in=request.user.profile.company.all(),
        transaction_type = "Income"
        ).all()
    expenses_t = transactions.filter(
        prepared_by__profile__company__in=request.user.profile.company.all(),
        transaction_type = "Expense"
        ).all()
        
    page = request.GET.get('page', 1)
    paginator1 = Paginator(incomes, 2)

    income_total_amount_total = transactions.filter(
        prepared_by__profile__company__in=request.user.profile.company.all(),
        transaction_type = "Income"
    ).aggregate(Sum('total_amount')).get('total_amount__sum')

    try:
        paginator1 = paginator1.page(page)
    except:
        paginator1 = paginator1.page(1)

    income_categories = Category.objects.filter(
        paymentvoucher__transaction_type = "Income",
        paymentvoucher__approved=True,
        paymentvoucher__prepared_by__profile__company__in=request.user.profile.company.all(),
    ).annotate(total_amount=Sum('paymentvoucher__total_amount'))
    expense_categories = Category.objects.filter(
        paymentvoucher__transaction_type = "Expense",
        paymentvoucher__approved=True,
        paymentvoucher__prepared_by__profile__company__in=request.user.profile.company.all(),
    ).annotate(total_amount=Sum('paymentvoucher__total_amount'))

    return render(request, "tracker/summary.html", {
        'expenses': paginator, 'expense_total_amount_total': expense_total_amount_total, 'incomes': paginator1,
        'income_total_amount_total': income_total_amount_total, 'incomes_t': incomes_t, 'income_categories': income_categories,
        'expenses_t': expenses_t, 'date': timezone.now(), 'current_page': 'summary', 'expense_categories': expense_categories,
        'company_balance': request.user.profile.company.first().limit
    })

@login_required
def render_pv(request, pv_id):
    # get current page url
    page_url = request.build_absolute_uri()
    # Lists of statuses that are used as the status of the pv
    statuses = [
        "Accounts Desk",
        "Audit Level",
        "Management Level",
        "Final Review",
        "Approved",
        "On Hold"
    ]
    pv = PaymentVoucher.objects.filter(id=pv_id).first()
    if not pv:
        messages.error(request, 'No such payment voucher')
        return HttpResponseRedirect(reverse('transactions'))
    
    # Security check
    if not request.user.is_staff:
        if not pv.prepared_by.profile.company.first() in request.user.profile.company.all():
            raise PermissionDenied()
        
    if request.method == 'POST':                                                                 
        pv = PaymentVoucher.objects.filter(id=request.POST.get('pv_id')).first()
        if not pv:
            messages.error(request, 'No such payment voucher')
            return HttpResponseRedirect(reverse('transactions'))
        status = request.POST.get('status')
        email_message = request.POST.get('email_message')
        if not (status in statuses):
            messages.error(request, 'Invalid status')
            return HttpResponseRedirect(reverse('render_pv', args=[pv_id]))

        if status == "Management Level" and not request.user.is_staff:
            manager = User.objects.filter(profile__company__in=request.user.profile.company.all(), profile__title="Manager").first()
            send_mail(
                f'Transaction Endorsed - [{pv.transaction_type}]',
                f"""Dear {manager.first_name} {manager.last_name},

I hope this email finds you well. I would like to inform you that the recent transaction in our financial system has been reviewed and endorsed by the auditor. The details of the transaction are as follows:

Type: {pv.transaction_type}
Request By: {pv.request_by}
Date: {pv.date.strftime('%Y-%m-%d')}
Amount: {gmd(pv.total_amount)}
Category: {pv.category}

Description: {pv.description}

The auditor has carefully examined the transaction and confirmed its accuracy. We can proceed with incorporating this transaction into our financial records.

If you have any further questions or require additional information, please feel free to reach out to the auditor directly.

Here is a link to the transaction - {page_url}

Thank you for your attention to this matter.

Best regards,
{request.user.first_name} {request.user.last_name}
{request.user.profile.title} - {request.user.profile.company.first()}""", 
                'yonnatech.g@gmail.com',
                [manager.email],
                fail_silently=False,
            )
            pv.reviewed_by = request.user
        elif status == "Final Review":
            ceo = User.objects.filter(profile__title="CEO").first()
            manager = User.objects.filter(is_staff=True, profile__title="Manager").first()
            if not ceo or not manager:
                messages.error(request, "Contact IT for this exception")
                return HttpResponseRedirect(reverse('render_pv', args=[pv_id]))
            send_mail(
                f'Endorsed Transaction Notification - [{pv.transaction_type}]',
                
                f"""Dear {ceo.first_name} {ceo.last_name} / {manager.first_name} {manager.last_name},

I hope this email finds you well. I would like to bring to your attention a recently endorsed transaction that has been reviewed and approved by the auditor. The details of the transaction are as follows:

Type: {pv.transaction_type}
Request By: {pv.request_by}
Date: {pv.date.strftime('%Y-%m-%d')}
Total Amount: {gmd(pv.total_amount)}
Category: {pv.category}

Description: {pv.description}

The auditor has thoroughly examined the transaction and has confirmed its accuracy. We have obtained their endorsement, signifying the transaction's compliance with our financial policies and procedures.

I wanted to personally inform you about this transaction as it contributes to our overall financial picture. Should you require any additional information or have any concerns, please do not hesitate to reach out to me.

Here is a link to the transaction - {page_url}

Thank you for your attention to this matter.

Sincerely,
{request.user.first_name} {request.user.last_name}
{request.user.profile.title} - {request.user.profile.company.first()}""", 
                'yonnatech.g@gmail.com',
                [ceo.email, manager.email],
                fail_silently=False,
            )
            pv.verified_by = request.user
        elif status == "Accounts Desk":
            if email_message:
                send_mail(
                    f'Transaction Uendorsed - [{pv.transaction_type}]',
                    f'{email_message}', 
                    'yonnatech.g@gmail.com',
                    [pv.prepared_by.email],
                    fail_silently=False,
                )
            else:
                messages.error(request, 'Please leave a message to inform your subordinate')
                return HttpResponseRedirect(reverse('render_pv', args=[pv_id]))
        elif status == "Audit Level" and request.user.profile.title != "Accountant":
            if email_message:
                send_mail(
                    f'Transaction Uendorsed - [{pv.transaction_type}]',
                    
                    f'{email_message}', 
                    'yonnatech.g@gmail.com',
                    [pv.reviewed_by.email],
                    fail_silently=False,
                )
            else:
                messages.error(request, 'Please leave a message')
                return HttpResponseRedirect(reverse('render_pv', args=[pv_id]))
        elif status == "Audit Level" and request.user.profile.title == "Accountant":
            auditor = User.objects.filter(profile__company__in=request.user.profile.company.all(), profile__title="Auditor").first()
            send_mail(
            f'Request for Transaction Update - [{pv.pv_id}]',
            
            f"""Dear {auditor.first_name} {auditor.last_name},

{email_message}

Details:

Transaction ID: [{pv.pv_id}]
Type: {pv.transaction_type}
Request By: {pv.request_by}
Date: {pv.date.strftime('%Y-%m-%d')}
Amount: {gmd(pv.total_amount)}
Category: {pv.category}

Description: {pv.description}

Best regards,
{pv.prepared_by.first_name} {pv.prepared_by.last_name}
{pv.prepared_by.profile.title} - {pv.prepared_by.profile.company.first()}""", 
            'yonnatech.g@gmail.com',
            [auditor.email],
            fail_silently=False,
        )
        if request.user.is_staff:
            if status == "Management Level":
                if email_message:
                    send_mail(
                        f'Transaction Uendorsed - [{pv.transaction_type}]',
                        
                        f'{email_message}', 
                        'yonnatech.g@gmail.com',
                        [ pv.verified_by.email],
                        fail_silently=False,
                    )
                else:
                    messages.error(request, 'Please leave a message to inform your subordinate')
                    return HttpResponseRedirect(reverse('render_pv', args=[pv_id]))
        if request.user.is_staff:
            if status == "Approved":
                    if pv.transaction_type == 'Expense':
                        company = pv.prepared_by.profile.company.first()
                        print(f"Company: {company}")
                        if company.limit - pv.total_amount >= 0:
                            company.limit -= pv.total_amount
                            company.save()
                        else:
                            messages.error(request, f"The balance of {company} is {gmd(company.limit)}. Not sufficient to make this expense")
                            return HttpResponseRedirect(reverse("transactions"))
                    send_mail(
                        f'RE: Endorsed Transaction Notification - [{pv.transaction_type}]',
                        f"""Dear {pv.verified_by.first_name} {pv.verified_by.last_name},

Thank you for notifying me about the endorsed transaction. I appreciate your diligence in ensuring that our financial records are accurate and compliant with our policies.

Based on the auditor's endorsement and your recommendation, I hereby approve the transaction. Please proceed with incorporating it into our financial records accordingly.

If there are any further updates or significant transactions that require my attention, please keep me informed.

Thank you for your continued commitment to maintaining the financial integrity of our organization.

Here is a link to the transaction - {page_url}

Best regards,

Sheriffo Touray
CEO, Yonna Group
                        """, 
                        'yonnatech.g@gmail.com',
                        [pv.verified_by.email, pv.reviewed_by, pv.prepared_by.email],
                        fail_silently=False,
                    )
                    pv.approved_by = request.user
        pv.status = status
        pv.save()
        messages.success(request, 'Transaction\'s status updated successfully')
        return HttpResponseRedirect(reverse('transactions'))
    total_amount_in_words = inflect.engine()
    total_amount_in_words = total_amount_in_words.number_to_words(int(pv.total_amount)).capitalize() + " dalasis"
    return render(request, 'tracker/pv.html', {
        'pv': pv, 'total_amount_in_words': total_amount_in_words, 'current_page': 'transactions',
        'company_balance': request.user.profile.company.first().limit
    })

@login_required
def all_transactions(request):
    comapanies = [
        "Yonna Foreign Exchange Bureau",
        "Yonna Islamic Microfinance",
        "Yonna Enterprise",
        "Yonna Insurance",
    ]
    domain = "Yonna Group"
    transactions = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
    ).order_by("-date", "prepared_by").all()
    if request.method == 'POST':
        if request.POST.get('from_date') and request.POST.get('to_date'):
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            from_company = request.POST.get('from_company')
            filename = f"yonna_group_transactions_{from_date}_to_{to_date}.csv"
            if from_company:
                items = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__in=Company.objects.filter(name=from_company),
                    date__gte=datetime.strptime(from_date, '%Y-%m-%d'),
                    date__lte=datetime.strptime(to_date, '%Y-%m-%d'),
                ).order_by('date')
                filename = f"{from_company}_transactions_{from_date}_to_{to_date}.csv"
            else:
                items = PaymentVoucher.objects.filter(
                    date__gte=datetime.strptime(from_date, '%Y-%m-%d'),
                    date__lte=datetime.strptime(to_date, '%Y-%m-%d'),
                ).order_by('date')
            if not items:
                messages.error(request, "No transaction is available for download")
                return HttpResponseRedirect(reverse("all_transactions"))
            headers = ["COMPANY", "TRANSACTION NUMBER", "TRANSACTION TYPE", "REQUEST BY", "PREPARED BY", "REVIEWED BY", "VERIFIED BY",
                       "APPROVED BY", "PAYEE", "CHEQUE NUMBER", "ACCOUNT NUMBER", "BANK", "ENTRIES", "QUANTITIES", "UNIT PRICES",
                       "TOTAL", "CATEGORY", "STATUS", "PAYMENT METHOD", "DATE", "DESCRIPTION"]
            
            response = HttpResponse(
                content_type='text/csv',
                headers = {'Content-Disposition': f'attachment; filename="{filename}"'},
            )
            writer = csv.writer(response)
            writer.writerow(["PAYMENT VOUCHERS"])
            writer.writerow(headers)
            for w in items:
                n_items = 0
                if w.item_one:
                    n_items += 1
                if w.item_two:
                    n_items += 1
                if w.item_three:
                    n_items += 1
                if w.item_four:
                    n_items += 1
                if w.item_five:
                    n_items += 1
                if w.item_six:
                    n_items += 1
                if w.item_seven:
                    n_items += 1
                if w.item_eight:
                    n_items += 1
                if w.item_nine:
                    n_items += 1
                if w.item_ten:
                    n_items += 1
                try:
                    writer.writerow([w.prepared_by.profile.company.first().name, w.pv_id, w.transaction_type, w.request_by,
                                    f'{w.prepared_by.first_name} {w.prepared_by.last_name}', 
                                    f'{w.reviewed_by.first_name} {w.reviewed_by.last_name}',
                                    f'{w.verified_by.first_name} {w.verified_by.last_name}', 
                                    f'{w.approved_by.first_name} {w.approved_by.last_name}', w.payee, w.cheque_number,
                                    w.account_number, w.bank_name, n_items,

                                    (w.item_one_quantity + w.item_two_quantity + w.item_three_quantity + w.item_four_quantity +
                                    w.item_five_quantity + w.item_six_quantity + w.item_seven_quantity + w.item_eight_quantity + w.item_nine_quantity + w.item_ten_quantity),

                                    (w.item_one_unit_price + w.item_two_unit_price + w.item_three_unit_price + w.item_four_unit_price +
                                    w.item_five_unit_price + w.item_six_unit_price + w.item_seven_unit_price + w.item_eight_unit_price + w.item_nine_unit_price + w.item_ten_unit_price),

                                    (w.item_one_total_price + w.item_two_total_price + w.item_three_total_price + w.item_four_total_price +
                                    w.item_five_total_price + w.item_six_total_price + w.item_seven_total_price + w.item_eight_total_price + w.item_nine_total_price + w.item_ten_total_price),

                                    w.category.name, w.status, w.payment_method, w.date, w.description])
                except:
                    messages.warning(request, "An error occured while processing the request. \
                                    It seems like the selected transactions has not been reviewed,\
                                    verified or approved. If that's so, please inform the right people responsible for that")
                    return HttpResponseRedirect(reverse("transactions"))
            return response

        if request.POST.get('company'):
            return HttpResponseRedirect(reverse('company_transactions', args=(request.POST.get('company'),)))
        date = request.POST.get('date')
        if date:
            try:
                _date = datetime.strptime(date, '%Y-%m-%d')
                transactions = PaymentVoucher.objects.filter(date__year=_date.year, date__month=_date.month)
            except ValueError:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('all_transactions'))
            transactions = transactions.filter(
                pv_id__icontains=request.POST['pv_id'],
                request_by__icontains=request.POST['request_by'],
                status__icontains=request.POST['status'],
                category__name__icontains=request.POST['category'],
                transaction_type__icontains=request.POST['transaction_type'], 
            ).order_by("-date")
            if transactions:
                domain = transactions[0].prepared_by.profile.company.first().name
        else:
            if request.POST.get('company'):
                transactions = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__name__icontains=request.POST.get('company'),
                    pv_id__icontains=request.POST['pv_id'],
                    request_by__icontains=request.POST['request_by'],
                    status__icontains=request.POST['status'],
                    category__name__icontains=request.POST['category'],
                    transaction_type__icontains=request.POST['transaction_type']
                ).order_by("-date")
            else:
                transactions = PaymentVoucher.objects.filter(
                    pv_id__icontains=request.POST.get('pv_id', ""),
                    request_by__icontains=request.POST.get('request_by', ""),
                    status__icontains=request.POST.get('status', ""),
                    category__name__icontains=request.POST.get('category', ""),
                    transaction_type__icontains=request.POST.get('transaction_type', "")
                ).order_by("-date")
            if transactions and request.POST.get('company'):
                domain = request.POST.get('company')
    if request.method == "GET":
        page = request.GET.get('page', 1)
        paginator = Paginator(transactions, 8)
        paginator = paginator.page(page)
    else:
        paginator = transactions

    total_amount_total = transactions.filter(approved=True).aggregate(Sum('total_amount')).get('total_amount__sum') or 0

    income_amount = transactions.filter(
        transaction_type="Income"
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    expense_amount = transactions.filter(
        transaction_type="Expense"
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0

    profit = income_amount - expense_amount

    return render(request, "tracker/all_transactions.html", {
        'transactions': paginator, 'total_amount_total': total_amount_total, 'comapanies': comapanies, 'current_page': 'all_transactions',
        'income_amount': income_amount, 'expense_amount': expense_amount, 'profit': profit, 'domain': domain,
        'company_balance': request.user.profile.company.first().limit
    })

@login_required
def company_transactions(request, company):
    comapanies = [
        "Yonna Foreign Exchange Bureau",
        "Yonna Islamic Microfinance",
        "Yonna Enterprise",
        "Yonna Insurance",
    ]
    domain = company
    company_balance = Company.objects.filter(name=company).first().limit
    transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__company__in=Company.objects.filter(name=company),
    ).order_by("-date", "prepared_by").all()
    if request.method == 'POST':
        date = request.POST.get('date')
        if date:
            try:
                _date = datetime.strptime(date, '%Y-%m-%d')
                transactions = transactions.filter(date__year=_date.year, date__month=_date.month)
            except ValueError:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('all_transactions'))
            transactions = transactions.filter(
                prepared_by__profile__company__in=Company.objects.filter(
                                    name=request.POST.get('company', f"{request.user.profile.company.first().name}")),
                pv_id__icontains=request.POST['pv_id'],
                request_by__icontains=request.POST['request_by'],
                status__icontains=request.POST['status'],
                category__name__icontains=request.POST['category'],
                transaction_type__icontains=request.POST['transaction_type'], 
            ).order_by("-date")
            if transactions:
                domain = transactions[0].prepared_by.profile.company.first().name
        else:
            if request.POST.get('company'):
                company_balance = Company.objects.filter(name=request.POST.get('company')).first().limit
                transactions = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__name__icontains=request.POST.get('company'),
                    pv_id__icontains=request.POST['pv_id'],
                    request_by__icontains=request.POST['request_by'],
                    status__icontains=request.POST['status'],
                    category__name__icontains=request.POST['category'],
                    transaction_type__icontains=request.POST['transaction_type']
                ).order_by("-date")
            else:
                transactions = PaymentVoucher.objects.filter(
                    pv_id__icontains=request.POST['pv_id'],
                    request_by__icontains=request.POST['request_by'],
                    status__icontains=request.POST['status'],
                    category__name__icontains=request.POST['category'],
                    transaction_type__icontains=request.POST['transaction_type']
                ).order_by("-date")
        if not transactions:
            messages.error(request, "No Entries Available")
        else:
            domain = transactions[0].prepared_by.profile.company.first().name
    page = request.GET.get('page', 1)
    paginator = Paginator(transactions, 8)
    paginator = paginator.page(page)

    total_amount_total = transactions.filter(approved=True).aggregate(Sum('total_amount')).get('total_amount__sum')
    income_amount = transactions.filter(
        transaction_type="Income"
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    expense_amount = transactions.filter(
        transaction_type="Expense"
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0


    profit = income_amount - expense_amount

    return render(request, "tracker/company_transactions.html", {
        'transactions': paginator, 'total_amount_total': total_amount_total, 'comapanies': comapanies, 'current_page': 'all_transactions',
        'income_amount': income_amount, 'expense_amount': expense_amount, 'profit': profit, 'domain': domain, 'company_balance': company_balance,
        'company_balance': company_balance
    })

@login_required
def new_transactions(request):
    transactions = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        status="Final Review",
    ).all().order_by("-date", "prepared_by")
    page = request.GET.get('page', 1)
    paginator = Paginator(transactions, 10)

    if not transactions:
        messages.error(request, "You have not been notified of any new transaction yet.")
    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)
    return render(request, "tracker/new_transactions.html", {
        'transactions': paginator, 'current_page': 'new_transactions',
        'company_balance': request.user.profile.company.first().limit
    })

@login_required
def hold_transactions(request):
    hold_transactions = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
         status="On Hold",
    ).all().order_by("-date", "prepared_by")
    page = request.GET.get('page', 1)
    paginator = Paginator(hold_transactions, 10)

    if not hold_transactions:
        messages.error(request, "No transaction on hold.")
    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)
    return render(request, "tracker/hold_transactions.html", {
        'transactions': hold_transactions, 'current_page': 'hold_transactions',
        'company_balance': request.user.profile.company.first().limit
    })



@login_required
def company_dashboard(request):
    company = "Yonna Group"
    companies = [
        "Yonna Foreign Exchange Bureau",
        "Yonna Islamic Microfinance",
        "Yonna Enterprise",
        "Yonna Insurance",
    ]
    if request.method == 'POST':
        if not request.POST.get('company') and not request.POST.get('date'):
            return HttpResponseRedirect(reverse("company_dashboard"))
        if request.POST.get('company'):
            company = request.POST['company']
        date = request.POST['date']
        domains = Company.objects.filter(name=company).all()
        if date:
            if request.POST.get('company'):
                try:
                    _date = datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    messages.error(request, 'Invalid date format')
                    return HttpResponseRedirect(reverse('company_dashboard'))
                expenses = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__in=domains,
                    transaction_type = "Expense", approved = True,
                    date__year=_date.year, date__month=_date.month,
                ).all().order_by("-date")
                page = request.GET.get('page', 1)
                paginator = Paginator(expenses, 2)

                expense_total_amount_total = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__name__in=domains,
                    transaction_type = "Expense", approved = True,
                    date__year=_date.year, date__month=_date.month,
                ).aggregate(Sum('total_amount')).get('total_amount__sum')

                try:
                    paginator = paginator.page(page)
                except:
                    paginator = paginator.page(1)
                
                incomes = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__in=domains,
                    transaction_type = "Income", approved = True,
                    date__year=_date.year, date__month=_date.month,
                    ).all().order_by("-date")

                incomes_t = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__in=domains,
                    transaction_type = "Income",
                    approved = True,
                    date__year=_date.year, date__month=_date.month,
                    ).all()
                expenses_t = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__in=domains,
                    approved = True,
                    transaction_type = "Expense",
                    date__year=_date.year, date__month=_date.month,
                    ).all()
                    
                page = request.GET.get('page', 1)
                paginator1 = Paginator(incomes, 2)

                income_total_amount_total = PaymentVoucher.objects.filter(
                    prepared_by__profile__company__in=domains,
                    approved = True,
                    transaction_type = "Income",
                    date__year=_date.year, date__month=_date.month,
                ).aggregate(Sum('total_amount')).get('total_amount__sum')

                try:
                    paginator1 = paginator1.page(page)
                except:
                    paginator1 = paginator1.page(1)

                income_categories = Category.objects.filter(
                    paymentvoucher__prepared_by__profile__company__in=domains,
                    paymentvoucher__transaction_type = "Income",
                    paymentvoucher__approved = True,
                    paymentvoucher__date__year=_date.year, paymentvoucher__date__month=_date.month,
                ).annotate(total_amount=Sum('paymentvoucher__total_amount'))
                expense_categories = Category.objects.filter(
                    paymentvoucher__prepared_by__profile__company__name__icontains=company,
                    paymentvoucher__transaction_type = "Expense",
                    paymentvoucher__approved = True,
                    paymentvoucher__date__year=_date.year, paymentvoucher__date__month=_date.month,
                ).annotate(total_amount=Sum('paymentvoucher__total_amount'))

                return render(request, "tracker/company_dashboard.html", {
                    'expenses': paginator, 'expense_total_amount_total': expense_total_amount_total, 'incomes': paginator1, 'companies': companies,
                    'income_total_amount_total': income_total_amount_total, 'incomes_t': incomes_t, 'income_categories': income_categories,
                    'expenses_t': expenses_t, 'expense_categories': expense_categories,
                    'company': company, 'current_page': 'company_dashboard', 'company_balance': request.user.profile.company.first().limit
                })
            else:
                try:
                    _date = datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    messages.error(request, 'Invalid date format')
                    return HttpResponseRedirect(reverse('company_dashboard'))
                expenses = PaymentVoucher.objects.filter(
                    transaction_type="Expense", approved = True,
                    date__year=_date.year, date__month=_date.month,
                ).all().order_by("-date")
                page = request.GET.get('page', 1)
                paginator = Paginator(expenses, 2)

                expense_total_amount_total = PaymentVoucher.objects.filter(
                    transaction_type = "Expense", approved = True,
                    date__year=_date.year, date__month=_date.month,
                ).aggregate(Sum('total_amount')).get('total_amount__sum')

                try:
                    paginator = paginator.page(page)
                except:
                    paginator = paginator.page(1)
                
                incomes = PaymentVoucher.objects.filter(
                    transaction_type="Income", approved = True,
                    date__year=_date.year, date__month=_date.month
                    ).all().order_by("-date")

                incomes_t = PaymentVoucher.objects.filter(
                    transaction_type = "Income",
                    approved = True,
                    date__year=_date.year, date__month=_date.month
                    ).all()
                expenses_t = PaymentVoucher.objects.filter(
                    approved = True,
                    transaction_type = "Expense",
                    date__year=_date.year, date__month=_date.month
                    ).all()
                    
                page = request.GET.get('page', 1)
                paginator1 = Paginator(incomes, 2)

                income_total_amount_total = PaymentVoucher.objects.filter(
                    approved = True,
                    transaction_type = "Income",
                    date__year=_date.year, date__month=_date.month
                ).aggregate(Sum('total_amount')).get('total_amount__sum')

                try:
                    paginator1 = paginator1.page(page)
                except:
                    paginator1 = paginator1.page(1)

                income_categories = Category.objects.filter(
                    paymentvoucher__transaction_type = "Income",
                    paymentvoucher__approved = True,
                    paymentvoucher__date__year=_date.year, paymentvoucher__date__month=_date.month
                ).annotate(total_amount=Sum('paymentvoucher__total_amount'))
                expense_categories = Category.objects.filter(
                    paymentvoucher__transaction_type = "Expense",
                    paymentvoucher__approved = True,
                    paymentvoucher__date__year=_date.year, paymentvoucher__date__month=_date.month
                ).annotate(total_amount=Sum('paymentvoucher__total_amount'))

                return render(request, "tracker/company_dashboard.html", {
                    'expenses': paginator, 'expense_total_amount_total': expense_total_amount_total, 'incomes': paginator1, 'companies': companies,
                    'income_total_amount_total': income_total_amount_total, 'incomes_t': incomes_t, 'income_categories': income_categories,
                    'expenses_t': expenses_t, 'expense_categories': expense_categories,
                    'company': company, 'current_page': 'company_dashboard', 'company_balance': request.user.profile.company.first().limit
                })
        else:
            expenses = PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=domains,
                transaction_type="Expense", approved = True,
            ).all().order_by("-date")
            page = request.GET.get('page', 1)
            paginator = Paginator(expenses, 2)

            expense_total_amount_total = PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=domains,
                transaction_type="Expense", approved = True,
            ).aggregate(Sum('total_amount')).get('total_amount__sum')

            try:
                paginator = paginator.page(page)
            except:
                paginator = paginator.page(1)

            incomes = PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=domains,
                transaction_type="Income", approved = True,
                ).all().order_by("-date")

            incomes_t = PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=domains,
                transaction_type="Income",
                approved=True,
            ).all()
            expenses_t = PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=domains,
                approved=True,
                transaction_type = "Expense",
            ).all()
            page = request.GET.get('page', 1)
            paginator1 = Paginator(incomes, 2)

            income_total_amount_total = PaymentVoucher.objects.filter(
                prepared_by__profile__company__in=domains,
                approved = True,
                transaction_type = "Income",
            ).aggregate(Sum('total_amount')).get('total_amount__sum')

            try:
                paginator1 = paginator1.page(page)
            except:
                paginator1 = paginator1.page(1)

            income_categories = Category.objects.filter(
                paymentvoucher__prepared_by__profile__company__in=domains,
                paymentvoucher__transaction_type = "Income",
                paymentvoucher__approved = True,
            ).annotate(total_amount=Sum('paymentvoucher__total_amount'))
            expense_categories = Category.objects.filter(
                paymentvoucher__prepared_by__profile__company__in=domains,
                paymentvoucher__transaction_type = "Expense",
                paymentvoucher__approved = True,
            ).annotate(total_amount=Sum('paymentvoucher__total_amount'))

            return render(request, "tracker/company_dashboard.html", {
                'expenses': paginator, 'expense_total_amount_total': expense_total_amount_total, 'incomes': paginator1, 'companies': companies,
                'income_total_amount_total': income_total_amount_total, 'incomes_t': incomes_t, 'income_categories': income_categories,
                'expenses_t': expenses_t, 'expense_categories': expense_categories,
                'company': company, 'current_page': 'company_dashboard', 'company_balance': request.user.profile.company.first().limit
            })
    expenses = PaymentVoucher.objects.filter(
        transaction_type="Expense", approved=True,
    ).all().order_by("-date")
    page = request.GET.get('page', 1)
    paginator = Paginator(expenses, 2)

    expense_total_amount_total = PaymentVoucher.objects.filter(
        transaction_type="Expense", approved=True,
    ).aggregate(Sum('total_amount')).get('total_amount__sum')

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    incomes = PaymentVoucher.objects.filter(
        transaction_type="Income", approved=True,
        ).all().order_by("-date")

    incomes_t = PaymentVoucher.objects.filter(
        transaction_type="Income", approved=True,
    ).all()
    expenses_t = PaymentVoucher.objects.filter(
        transaction_type="Expense", approved=True,
    ).all()
        
    page = request.GET.get('page', 1)
    paginator1 = Paginator(incomes, 2)

    income_total_amount_total = PaymentVoucher.objects.filter(
        transaction_type="Income", approved=True,
    ).aggregate(Sum('total_amount')).get('total_amount__sum')

    try:
        paginator1 = paginator1.page(page)
    except:
        paginator1 = paginator1.page(1)

    income_categories = Category.objects.filter(
        paymentvoucher__transaction_type = "Income",
        paymentvoucher__status = "Approved",
        paymentvoucher__approved=True,
    ).annotate(total_amount=Sum('paymentvoucher__total_amount'))
    expense_categories = Category.objects.filter(
        paymentvoucher__transaction_type = "Expense",
        paymentvoucher__status = "Approved",
        paymentvoucher__approved=True,
    ).annotate(total_amount=Sum('paymentvoucher__total_amount'))

    return render(request, "tracker/company_dashboard.html", {
        'expenses': paginator, 'expense_total_amount_total': expense_total_amount_total, 'incomes': paginator1, 'companies': companies,
        'income_total_amount_total': income_total_amount_total, 'incomes_t': incomes_t, 'income_categories': income_categories,
        'expenses_t': expenses_t, 'expense_categories': expense_categories,
        'company': company, 'current_page': 'company_dashboard', 'company_balance': request.user.profile.company.first().limit
    })

@login_required
def company_leaderboard(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    # Forex
    yfeb_total_income_amounts = PaymentVoucher.objects.filter(
        prepared_by__profile__company__name__icontains="Yonna Foreign Exchange Bureau",
        transaction_type="Income", approved=True
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    yfeb_total_expense_amounts = PaymentVoucher.objects.filter(
        prepared_by__profile__company__name="Yonna Foreign Exchange Bureau",
        transaction_type="Expense", approved=True
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    yfeb_difference = yfeb_total_income_amounts - yfeb_total_expense_amounts

    # Microfinance
    yimf_total_income_amounts = PaymentVoucher.objects.filter(
        prepared_by__profile__company__name="Yonna Islamic Microfinance",
        transaction_type="Income", approved=True
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    yimf_total_expense_amounts = PaymentVoucher.objects.filter(
        prepared_by__profile__company__name="Yonna Islamic Microfinance",
        transaction_type="Expense", approved=True
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    yimf_difference = yimf_total_income_amounts - yimf_total_expense_amounts

    # Enterprise
    ent_total_income_amounts = PaymentVoucher.objects.filter(
        prepared_by__profile__company__name="Yonna Enterprise",
        transaction_type="Income", approved=True
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    ent_total_expense_amounts = PaymentVoucher.objects.filter(
        prepared_by__profile__company__name="Yonna Enterprise",
        transaction_type="Expense", approved=True
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    ent_difference = ent_total_income_amounts - ent_total_expense_amounts

    # Insurance
    insurance_total_income_amounts = PaymentVoucher.objects.filter(
        prepared_by__profile__company__name="Yonna Insurance",
        transaction_type="Income", approved=True
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    insurance_total_expense_amounts = PaymentVoucher.objects.filter(
        prepared_by__profile__company__name="Yonna Insurance",
        transaction_type="Expense", approved=True
    ).aggregate(Sum('total_amount')).get('total_amount__sum') or 0
    insurance_difference = insurance_total_income_amounts - insurance_total_expense_amounts

    context = [
        {"name": "Yonna Foreign Exchange Bureau", "difference": yfeb_difference,
         "total_income_amounts": yfeb_total_income_amounts, "total_expense_amounts": yfeb_total_expense_amounts,
         'limit': Company.objects.filter(name="Yonna Foreign Exchange Bureau").first().limit},

        {"name": "Yonna Islamic Microfinance", "difference": yimf_difference,
         "total_income_amounts": yimf_total_income_amounts, "total_expense_amounts": yimf_total_expense_amounts,
         'limit': Company.objects.filter(name="Yonna Islamic Microfinance").first().limit},

        {"name": "Yonna Enterprise", "difference": ent_difference,
         "total_income_amounts": ent_total_income_amounts, "total_expense_amounts": ent_total_expense_amounts,
         'limit': Company.objects.filter(name="Yonna Enterprise").first().limit},

        {"name": "Yonna Insurance", "difference": insurance_difference,
         "total_income_amounts": insurance_total_income_amounts, "total_expense_amounts": insurance_total_expense_amounts,
         'limit': Company.objects.filter(name="Yonna Insurance").first().limit},
    ]

    context = sorted(context, key=lambda c: c["difference"], reverse=True)
    return render(request, "tracker/company_leaderboard.html", {
        "context": context, "current_page": "company_leaderboard", 'company_balance': request.user.profile.company.first().limit
    })