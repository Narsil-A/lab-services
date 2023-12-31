# Generated by Django 5.0 on 2023-12-17 17:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0004_alter_diagnosticservice_duration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="diagnosticservice",
            name="cost",
            field=models.DecimalField(
                decimal_places=2, help_text="Cost in dollars", max_digits=10
            ),
        ),
    ]
