# Generated by Django 3.1.2 on 2021-01-18 06:16

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketAttributeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=56, unique=True)),
                ('low_label', models.CharField(default='Low', max_length=56)),
                ('low_cost', models.DecimalField(decimal_places=4, default=0.5, max_digits=12)),
                ('low_customer', models.DecimalField(decimal_places=4, default=1, max_digits=12)),
                ('low_sales', models.DecimalField(decimal_places=4, default=0.75, max_digits=12)),
                ('med_label', models.CharField(default='Medium', max_length=56)),
                ('med_cost', models.DecimalField(decimal_places=4, default=1.0, max_digits=12)),
                ('med_customer', models.DecimalField(decimal_places=4, default=3, max_digits=12)),
                ('med_sales', models.DecimalField(decimal_places=4, default=1.0, max_digits=12)),
                ('high_label', models.CharField(default='High', max_length=56)),
                ('high_cost', models.DecimalField(decimal_places=4, default=1.5, max_digits=12)),
                ('high_customer', models.DecimalField(decimal_places=4, default=2, max_digits=12)),
                ('high_sales', models.DecimalField(decimal_places=4, default=0.75, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='PolicyStrategy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chosen_option', models.PositiveSmallIntegerField()),
                ('policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.policy')),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_name', models.TextField(max_length=256)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('is_school', 'Is a school account'),),
            },
        ),
        migrations.CreateModel(
            name='Simulator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('lengthOfTradingDay', models.DurationField(default=datetime.timedelta(days=1))),
                ('productName', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, upload_to='')),
                ('maxPrice', models.DecimalField(decimal_places=4, max_digits=12)),
                ('minPrice', models.DecimalField(decimal_places=4, max_digits=12)),
                ('priceBoundary1', models.DecimalField(decimal_places=4, default=1.5, max_digits=12)),
                ('priceBoundary2', models.DecimalField(decimal_places=4, default=3.5, max_digits=12)),
                ('marketOpen', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Strategy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consistency', models.DecimalField(decimal_places=4, default=0, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='YES',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('is_yes_staff', 'Is a yes member of staff'),),
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.TextField(max_length=256)),
                ('leaderboard_position', models.IntegerField(default=-1)),
                ('school_position', models.IntegerField(default=-1)),
                ('schoolid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.school')),
                ('strategyid', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.strategy')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('is_team', 'Is a team account'),),
            },
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=4, default=1, max_digits=12)),
                ('efctOnSales', models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ('customers', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('qual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.policystrategy')),
                ('simulator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.simulator')),
                ('team', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.team')),
            ],
        ),
        migrations.AddField(
            model_name='policystrategy',
            name='strategy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.strategy'),
        ),
        migrations.CreateModel(
            name='MarketEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('simulator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.simulator')),
                ('strategyid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.strategy')),
            ],
        ),
        migrations.CreateModel(
            name='MarketAttributeTypeData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('parameterValue', models.DecimalField(decimal_places=4, max_digits=12)),
                ('marketAttributeType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.marketattributetype')),
                ('marketEntryId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='simulatorApp.marketentry')),
            ],
        ),
    ]
