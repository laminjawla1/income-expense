from django.urls import path
from .views import dashboard, index, incomes, AddIncome, UpdateIncome, AddExpense, UpdateExpense, expenses, summary

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("index/", index, name="index"),
    path("summary/", summary, name="summary"),
    path("incomes/", incomes, name="incomes"),
    path("expenses/", expenses, name="expenses"),
    path("add_income/", AddIncome.as_view(), name="add_income"),
    path("incomes/<int:pk>/update", UpdateIncome.as_view(), name="update_income"),
    path("add_expense/", AddExpense.as_view(), name="add_expense"),
    path("expenses/<int:pk>/update", UpdateExpense.as_view(), name="update_expense"),
]