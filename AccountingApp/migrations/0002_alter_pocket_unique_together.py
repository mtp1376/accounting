# Generated by Django 4.2.8 on 2024-02-21 20:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("AccountingApp", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="pocket", unique_together={("owner", "purpose")},
        ),
    ]
