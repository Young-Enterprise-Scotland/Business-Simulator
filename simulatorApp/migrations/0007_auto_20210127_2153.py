# Generated by Django 3.1.2 on 2021-01-27 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('simulatorApp', '0006_acknowledgedevent_popupevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acknowledgedevent',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.popupevent'),
        ),
    ]
