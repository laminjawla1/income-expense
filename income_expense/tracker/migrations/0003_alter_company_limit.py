# Generated by Django 4.2.1 on 2023-05-31 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0002_company_limit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="limit",
            field=models.FloatField(default=0),
        ),
    ]
