# Generated by Django 4.2.1 on 2023-05-31 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="limit",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
