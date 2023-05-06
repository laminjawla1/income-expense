# Generated by Django 4.2.1 on 2023-05-06 15:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        default="profile_pics/default.png", upload_to="profile_pics"
                    ),
                ),
                (
                    "company",
                    models.CharField(
                        choices=[
                            (
                                "Yonna Foreign Exchange Bureau",
                                "Yonna Foreign Exchange Bureau",
                            ),
                            (
                                "Yonna Islamic Microfinance",
                                "Yonna Islamic Microfinance",
                            ),
                            ("Yonna Enterpriseprise", "Yonna Enterpriseprise"),
                            ("Yonna Insurance", "Yonna Insurance"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        choices=[
                            ("IT", "IT"),
                            ("Accountant", "Accountant"),
                            ("Auditor", "Auditor"),
                            ("Manager", "Manager"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
