from django.urls import path
from .views import dashboard, transactions, Transact, UpdateTransact, summary, render_pv

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("summary/", summary, name="summary"),
    path("transactions/", transactions, name="transactions"),
    path("transact/", Transact.as_view(), name="transact"),
    path("transaction/<int:pk>/update", UpdateTransact.as_view(), name="update_transaction"),
    path("pv/<int:pv_id>/view", render_pv, name='render_pv'),
]