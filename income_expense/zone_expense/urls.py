from django.urls import path
from . views import zone_expense, zone_transactions


urlpatterns = [
    path("", zone_expense, name="zone_expense"),
    path("<str:zone>/transactions/", zone_transactions, name="zone_transactions"),
]