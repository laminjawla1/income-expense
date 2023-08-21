import csv
from datetime import datetime

from accounts.models import Zone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from tracker.models import PaymentVoucher, Company


@login_required
def zone_expense(request):
    zones = Zone.objects.all().order_by('name')
    domain = "Yonna Zones"
    transactions = PaymentVoucher.objects.filter(
        date__year=timezone.now().year, date__month=timezone.now().month,
        zone__in=zones,
    ).order_by("-date", "prepared_by").all()
    if request.method == 'POST':
        if request.POST.get('from_date') and request.POST.get('to_date'):
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            from_zone = request.POST.get('from_zone')
            filename = f"yonna_zones_transactions_{from_date}_to_{to_date}.csv"
            if from_zone:
                items = PaymentVoucher.objects.filter(
                    prepared_by__profile__zone__in=zones.filter(name=from_zone),
                    date__gte=datetime.strptime(from_date, '%Y-%m-%d'),
                    date__lte=datetime.strptime(to_date, '%Y-%m-%d'),
                ).order_by('date')
                filename = f"{from_zone}_transactions_{from_date}_to_{to_date}.csv"
            else:
                items = PaymentVoucher.objects.filter(
                    date__gte=datetime.strptime(from_date, '%Y-%m-%d'),
                    date__lte=datetime.strptime(to_date, '%Y-%m-%d'),
                    prepared_by__profile__zone__in=zones,
                ).order_by('date')
            if not items:
                messages.error(request, "No transaction is available for download")
                return HttpResponseRedirect(reverse("zone_expense"))
            headers = ["ZONE", "TRANSACTION NUMBER", "TRANSACTION TYPE", "RECEIVED BY", "PREPARED BY", "REVIEWED BY", "VERIFIED BY",
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
                    writer.writerow([w.prepared_by.profile.zone.name, w.pv_id, w.transaction_type, w.received_by,
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

        if request.POST.get('zone'):
            return HttpResponseRedirect(reverse('zone_transactions', args=(request.POST.get('zone'),)))
        date = request.POST.get('date')
        if date:
            try:
                _date = datetime.strptime(date, '%Y-%m-%d')
                transactions = PaymentVoucher.objects.filter(
                    date__year=_date.year, date__month=_date.month,
                    zone__in=zones,
                )
            except ValueError:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('zone_expense'))
            transactions = transactions.filter(
                pv_id__icontains=request.POST['pv_id'],
                # received_by__icontains=request.POST.get('received_by', ''),
                status__icontains=request.POST['status'],
                category__name__icontains=request.POST['category'],
                transaction_type__icontains=request.POST['transaction_type'],
            ).order_by("-date")
        else:
            if request.POST.get('zone'):
                transactions = PaymentVoucher.objects.filter(
                    prepared_by__profile__zone__name__icontains=request.POST.get('zone'),
                    pv_id__icontains=request.POST['pv_id'],
                    # received_by__icontains=request.POST.get('received_by'),
                    status__icontains=request.POST['status'],
                    category__name__icontains=request.POST['category'],
                    transaction_type__icontains=request.POST['transaction_type']
                ).order_by("-date")
            else:
                print("Are you here?")
                transactions = PaymentVoucher.objects.filter(
                    zone__in=zones,
                    pv_id__icontains=request.POST.get('pv_id', ""),
                    # received_by__icontains=request.POST.get('received_by', ""),
                    status__icontains=request.POST.get('status', ""),
                    category__name__icontains=request.POST.get('category', ""),
                    transaction_type__icontains=request.POST.get('transaction_type', ""),
                ).order_by("-date")
            if transactions and request.POST.get('zone'):
                domain = request.POST.get('zone')
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

    return render(request, "zone_expense/all_transactions.html", {
        'transactions': paginator, 'total_amount_total': total_amount_total, 'zones': zones, 'current_page': 'zone_expense',
        'income_amount': income_amount, 'expense_amount': expense_amount, 'profit': profit, 'domain': domain,
        'company_balance': request.user.profile.company.first().limit
    })

@login_required
def zone_transactions(request, zone):
    zones = Zone.objects.all()
    domain = zone
    zone_balance = zones.filter(name=zone).first().limit
    transactions = PaymentVoucher.objects.filter(
            prepared_by__profile__zone__in=zones.filter(name=zone),
            date__year=timezone.now().year, date__month=timezone.now().month,
            zone__name__icontains=zone
    ).order_by("-date", "prepared_by").all()
    if request.method == 'POST':
        date = request.POST.get('date')
        if date:
            try:
                _date = datetime.strptime(date, '%Y-%m-%d')
                transactions = transactions.filter(date__year=_date.year, date__month=_date.month)
            except ValueError:
                messages.error(request, 'Invalid date format')
                return HttpResponseRedirect(reverse('zone_expense'))
            transactions = transactions.filter(
                prepared_by__profile__company__in=Company.objects.filter(
                                    name=request.POST.get('company', f"{request.user.profile.company.first().name}")),
                pv_id__icontains=request.POST['pv_id'],
                status__icontains=request.POST['status'],
                category__name__icontains=request.POST['category'],
                transaction_type__icontains=request.POST['transaction_type'], 
            ).order_by("-date")
        else:
            if request.POST.get('zone'):
                zone_balance = Zone.objects.filter(name=request.POST.get('zone')).first().limit
                transactions = PaymentVoucher.objects.filter(
                    prepared_by__profile__zone__name__icontains=request.POST.get('zone'),
                    pv_id__icontains=request.POST.get('pv_id', ""),
                    status__icontains=request.POST.get('status', ""),
                    category__name__icontains=request.POST.get('category', ""),
                    transaction_type__icontains=request.POST.get('transaction_type', "")
                ).order_by("-date")
            else:
                transactions = PaymentVoucher.objects.filter(
                    prepared_by__profile__zone__name__icontains=zone,
                    pv_id__icontains=request.POST['pv_id'],
                    status__icontains=request.POST['status'],
                    category__name__icontains=request.POST['category'],
                    transaction_type__icontains=request.POST['transaction_type']
                ).order_by("-date")
        if not transactions:
            messages.error(request, "No Entries Available")
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

    return render(request, "zone_expense/zone_transactions.html", {
        'transactions': paginator, 'total_amount_total': total_amount_total, 'zones': zones, 'current_page': 'zone_expense',
        'income_amount': income_amount, 'expense_amount': expense_amount, 'profit': profit, 'domain': domain, 'company_balance': zone_balance,
    })
