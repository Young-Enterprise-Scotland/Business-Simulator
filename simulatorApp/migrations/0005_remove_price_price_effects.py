# Generated by Django 3.1.2 on 2021-01-27 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simulatorApp', '0004_auto_20210127_1325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='price',
            name='price_effects',
        ),
    ]
