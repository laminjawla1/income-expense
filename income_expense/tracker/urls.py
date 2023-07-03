from django.urls import path
from .views import (dashboard, transactions, Transact, UpdateTransact, summary, company_leaderboard, admin_expense,
                    render_pv, all_transactions, new_transactions, company_dashboard, hold_transactions, company_transactions)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("summary/", summary, name="summary"),
    path("company_dashboard/", company_dashboard, name="company_dashboard"),
    path("transactions/", transactions, name="transactions"),
    path("admin_expense/", admin_expense, name="admin_expense"),
    path("all_transactions/", all_transactions, name="all_transactions"),
    path("<str:company>/transactions/", company_transactions, name="company_transactions"),
    path("company_leaderboard/", company_leaderboard, name="company_leaderboard"),
    path("hold_transactions/", hold_transactions, name="hold_transactions"),
    path("new_transactions/", new_transactions, name="new_transactions"),
    path("transact/", Transact.as_view(), name="transact"),
    path("transaction/<int:pk>/update", UpdateTransact.as_view(), name="update_transaction"),
    path("pv/<int:pv_id>/view", render_pv, name='render_pv'),
]