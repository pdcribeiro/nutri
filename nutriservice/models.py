from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import now
from django.urls import reverse

GENDER = (
    ('m', 'Masculino'),
    ('f', 'Feminino'),
    ('o', 'Outro'),
)
PAL = (
    (Decimal('1.20'), 'Sedentário'),
    (Decimal('1.50'), 'Leve'),
    (Decimal('1.75'), 'Ativo'),
    (Decimal('2.20'), 'Muito ativo'),
)


class Partner(models.Model):
    """The Partner model."""
    name = models.CharField(max_length=200, verbose_name='Nome')
    date = models.DateField(null=True, blank=True, verbose_name='Data de início da parceria')
    # active = models.BooleanField(...)
    calendar = models.CharField(max_length=200, verbose_name='ID do calendário Google')

    class Meta:
        ordering = ['-date', 'name']

    def get_absolute_url(self):
        """Returns the url to access Partner details."""
        return reverse('partner-detail', args=[str(self.id)])

    def __str__(self):
        """String to represent Partner model."""
        return f'{self.name}'


class Client(models.Model):
    """The Client model."""
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Utilizador')
    nutritionist = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='nutritionist', null=True, verbose_name='Nutricionista')
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, verbose_name='Parceiro')

    name = models.CharField(max_length=200, verbose_name='Nome')
    gender = models.CharField(max_length=1, choices=GENDER, default='f', verbose_name='Sexo')
    # born = models.DateField(verbose_name='Data de nascimento')
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)], verbose_name='Idade (anos)')
    
    height = models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(300)], verbose_name='Altura (cm)')
    weight = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Peso (kg)')
    body_fat = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Gordura corporal (%)')
    pal = models.DecimalField(max_digits=3, decimal_places=2, choices=PAL, default=PAL[1][0], verbose_name='Atividade física atual')

    class Meta:
        ordering = ['name', 'age']

    def get_absolute_url(self):
        """Returns the url to access Client details."""
        return reverse('client-detail', args=[str(self.id)])

    def __str__(self):
        """String to represent Client model."""
        return f'{self.name}'

    def get_bmi(self):
        return round(float(self.weight) / (self.height / 100) ** 2, 1)


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
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    date = models.DateField(verbose_name='Data')
    time = models.TimeField(verbose_name='Hora')
    duration = models.IntegerField(verbose_name='Duração (minutos)')
    summary = models.CharField(max_length=200, verbose_name='Resumo')
    event = models.CharField(max_length=200, verbose_name='ID do evento Google')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Peso (kg)')

    class Meta:
        ordering = ['-date', '-time']

    def get_absolute_url(self):
        """Returns the url to access Meeting details."""
        return reverse('meeting-detail', args=[str(self.id)])

    def __str__(self):
        """String to represent Meeting model."""
        return f'{self.date}'


class Plan(models.Model):
    """The Plan model."""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Consulta')
    date = models.DateField(default=now, null=True, blank=True, verbose_name='Data')

    goal_weight = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name='Peso desejado (kg)')
    goal_body_fat = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Gordura corporal (%)')
    new_pal = models.DecimalField(max_digits=3, decimal_places=2, choices=PAL, default=PAL[2][0], null=True, blank=True, verbose_name='Atividade física atual')
    
    goal_time = models.DecimalField(
        max_digits=3, decimal_places=1, validators=[MinValueValidator(0.5), MaxValueValidator(12)],
        default=3, null=True, blank=True, verbose_name='Duração da dieta (meses)')
    pal_change = models.DecimalField(
        max_digits=4, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(300)],
        default=0, null=True, blank=True, verbose_name='Mudança no PAL (%)')

    daily_energy = models.IntegerField(validators=[MinValueValidator(500), MaxValueValidator(5000)], null=True, blank=True, verbose_name='Energia diária (kcal/dia)')

    proteins = models.IntegerField(default=25, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de proteínas (%)')
    carbs = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de hidratos de carbono (%)')
    fats = models.IntegerField(default=25, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de lípidos (%)')
    
    regular_milk = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de leite meio-gordo (doses)')
    low_fat_milk = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de leite magro (doses)')
    solid_yoghurt = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de iogurte sólido (doses)')
    liquid_yoghurt = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de iogurte líquido (doses)')
    whey = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de whey (doses)')
    fruit = models.IntegerField(default=3, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de fruta (doses)')
    vegetables = models.IntegerField(default=4, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Quantidade de vegetais (doses)')
    
    # proteins_dosage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Carne e equivalentes (doses)')
    # carbs_dosage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Pão e equivalentes (doses)')
    # fats_dosage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True, verbose_name='Gordura (doses)')

    class Meta:
        ordering = ['-date', 'client__name', '-id']

    def get_absolute_url(self):
        """Returns the url to access Plan details."""
        return reverse('plan-detail', args=[str(self.id)])
    
    def __str__(self):
        """String to represent Plan model."""
        return f'{self.client.name} ({self.date})'
