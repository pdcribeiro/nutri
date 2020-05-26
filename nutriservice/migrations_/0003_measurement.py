# Generated by Django 3.0.5 on 2020-05-26 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nutriservice', '0002_auto_20200525_2315'),
    ]

    operations = [
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measure', models.CharField(choices=[('w', 'Peso'), ('h', 'Altura'), ('f', 'Gordura')], default='w', max_length=1, verbose_name='Medida')),
                ('value', models.IntegerField(verbose_name='Idade (anos)')),
                ('unit', models.CharField(blank=True, max_length=50, verbose_name='Unidade')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutriservice.Client', verbose_name='Cliente')),
            ],
        ),
    ]
