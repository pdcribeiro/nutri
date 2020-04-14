import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.urls import reverse


class Client(models.Model):
    """The Client model."""
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    nutritionist = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='nutritionist', null=True, verbose_name='Nutricionista')
    name = models.CharField(max_length=200, verbose_name='Nome')
    born = models.DateField(null=True, blank=True, verbose_name='Data de nascimento')

    class Meta:
        ordering = ['name', 'born']

    def get_absolute_url(self):
        """Returns the url to access Client details."""
        return reverse('client-detail', args=[str(self.id)])

    def __str__(self):
        """String to represent Client model."""
        return f'{self.name} ({self.id})'


class Meal(models.Model):
    """The Meal model."""
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    time = models.TimeField(null=True, blank=True, verbose_name='Hora')
    place = models.CharField(max_length=200, blank=True, verbose_name='Local')

    class Meta:
        ordering = ['id']

    def __str__(self):
        """String to represent Meal model."""
        return f'meal_id: {self.id} ({self.client})'


class Meeting(models.Model):
    """The Meeting model."""
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(default=now, null=True, blank=True, verbose_name='Data')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Peso')

    class Meta:
        ordering = ['-date']

    def get_absolute_url(self):
        """Returns the url to access Meeting details."""
        return reverse('meeting-detail', args=[str(self.id)])

    def __str__(self):
        """String to represent Meeting model."""
        return f'{self.client.name} ({self.date})'


class Plan(models.Model):
    """The Plan model."""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, verbose_name='Cliente')
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Consulta')
    date = models.DateField(default=now, null=True, blank=True, verbose_name='Data')
    energy = models.IntegerField(null=True, blank=True, verbose_name='Energia')

    class Meta:
        ordering = ['-date']

    def get_absolute_url(self):
        """Returns the url to access Plan details."""
        return reverse('plan-detail', args=[str(self.id)])
    
    def __str__(self):
        """String to represent Plan model."""
        return f'{self.client.name} ({self.date})'
