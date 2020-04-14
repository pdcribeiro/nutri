import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.urls import reverse


class Client(models.Model):
    """The Client model."""
    nutritionist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Nutricionista')
    name = models.CharField(max_length=200, help_text='Introduza o nome do cliente', verbose_name='Nome')
    born = models.DateField(null=True, blank=True, help_text='Introduza a data de nascimento do cliente', verbose_name='Data de nascimento')
    #TODO calculate age to display

    class Meta:
        ordering = ['name', 'born']  #TODO ordenar por data da primeira ou última consulta

    def get_absolute_url(self):
        """Returns the url to access Client details."""
        return reverse('client-detail', args=[str(self.id)])

    def __str__(self):
        """String to represent Client model."""
        return self.name


class Meal(models.Model):  #TODO change SET_NULL to CASCADE
    """The Meal model."""
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, help_text='Selecione o cliente', verbose_name='Cliente')
    time = models.TimeField(default=None, null=True, blank=True, verbose_name='Hora')
    place = models.CharField(default='', max_length=200, blank=True, verbose_name='Local')

    class Meta:
        ordering = ['id']

    def __str__(self):
        """String to represent Meal model."""
        return f'meal_id: {self.id} ({self.client})'


class Meeting(models.Model):
    """The Meeting model."""

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, help_text='Selecione o cliente', verbose_name='Cliente')
    date = models.DateField(default=now, help_text='Introduza a data da consulta', verbose_name='Data')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Introduza o peso do cliente em kg', verbose_name='Peso')

    class Meta:
        ordering = ['-date']  #TODO ordenar por data da primeira ou última consulta

    def get_absolute_url(self):
        """Returns the url to access Meeting details."""
        return reverse('meeting-detail', args=[str(self.id)])

    def __str__(self):
        """String to represent Meeting model."""
        return f'{self.client.name} ({self.date})'


class Plan(models.Model):
    """The Plan model."""

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, help_text='Selecione o cliente', verbose_name='Cliente')
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, blank=True, help_text='Selecione a consulta', verbose_name='Consulta')
    date = models.DateField(default=now, null=True, blank=True, help_text='Introduza a data do plano', verbose_name='Data')  #TODO use default value in form, not in model
    energy = models.IntegerField(null=True, blank=True, help_text='Introduza a energia do plano em kcal', verbose_name='Energia')

    class Meta:
        ordering = ['-date']  #TODO ordenar por data da primeira ou última consulta

    def get_absolute_url(self):
        """Returns the url to access Plan details."""
        return reverse('plan-detail', args=[str(self.id)])
    
    def __str__(self):
        """String to represent Plan model."""
        return f'{self.client.name} ({self.date})'
