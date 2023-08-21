# Generated by Django 4.2.1 on 2023-08-18 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_profile_company"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
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
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name="profile",
            name="role",
            field=models.ManyToManyField(
                blank=True, related_name="roles", to="accounts.role"
            ),
        ),
    ]