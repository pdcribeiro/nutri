# Generated by Django 3.0.5 on 2020-04-13 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nutriservice', '0006_auto_20200412_2205'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField(blank=True, null=True, verbose_name='Hora')),
                ('place', models.CharField(blank=True, max_length=200, null=True, verbose_name='Local')),
                ('client', models.ForeignKey(help_text='Selecione o cliente', null=True, on_delete=django.db.models.deletion.SET_NULL, to='nutriservice.Client', verbose_name='Cliente')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.DeleteModel(
            name='Meals',
        ),
    ]
