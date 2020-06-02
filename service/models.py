import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import dateparse, timezone
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
    name = models.CharField(max_length=200, verbose_name='Nome')
    date = models.DateField(null=True, blank=True, verbose_name='Data de início da parceria')
    # active = models.BooleanField(...)
    calendar = models.CharField(max_length=200, verbose_name='Calendário Google')

    class Meta:
        ordering = ['-date', 'name']
        verbose_name = 'parceiro'

    def get_absolute_url(self):
        return reverse('partner-detail', args=[str(self.pk)])

    def __str__(self):
        return f'{self.name}'


class Client(models.Model):
    STATE = (
        ('p', 'Pendente'),
        ('a', 'Ativo'),
        ('f', 'Finalizado'),
    )

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Utilizador')
    nutritionist = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='nutritionist', null=True, verbose_name='Nutricionista')

    name = models.CharField(max_length=200, verbose_name='Nome')
    gender = models.CharField(max_length=1, choices=GENDER, default='f', verbose_name='Sexo')
    # born = models.DateField(verbose_name='Data de nascimento')
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)], verbose_name='Idade (anos)')
    pal = models.DecimalField(max_digits=3, decimal_places=2, choices=PAL, default=PAL[1][0], verbose_name='Atividade física atual')
    
    height = models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(300)], verbose_name='Altura (cm)')
    weight = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Peso (kg)')
    body_fat = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Gordura corporal (%)')
    
    state = models.CharField(max_length=1, choices=STATE, default='a', verbose_name='Estado')
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, verbose_name='Parceiro')

    class Meta:
        ordering = ['name', 'age']
        verbose_name = 'cliente'

    def get_absolute_url(self):
        return reverse('client-detail', args=[str(self.pk)])

    def __str__(self):
        return f'{self.name}'

    def get_bmi(self):
        return round(float(self.weight) / (self.height / 100) ** 2, 1)


class Meal(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    time = models.TimeField(null=True, blank=True, verbose_name='Hora')
    place = models.CharField(max_length=200, blank=True, verbose_name='Local')

    class Meta:
        ordering = ['id']
        verbose_name = 'refeição'
        verbose_name_plural = 'refeições'

    def __str__(self):
        return f'meal_id: {self.pk} ({self.client})'


class Meeting(models.Model):
    STATE = (
        ('s', 'Agendada'),
        ('o', 'A decorrer'),
        ('f', 'Terminada'),
        ('m', 'Falhada'),
    )
    PHASE = (
        ('', ''),
        ('s', 'Início'),
        ('m', 'Medições'),
        ('c', 'Cálculos'),
        ('p', 'Plano'),
        ('f', 'Final'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    date = models.DateField(verbose_name='Data')
    time = models.TimeField(verbose_name='Hora')
    duration = models.IntegerField(verbose_name='Duração (minutos)')
    summary = models.CharField(max_length=200, verbose_name='Resumo')
    event = models.CharField(max_length=200, verbose_name='ID do evento Google')
    
    state = models.CharField(max_length=1, choices=STATE, default='s', verbose_name='Estado')
    phase = models.CharField(max_length=1, choices=PHASE, blank=True, verbose_name='Fase')
    
    notes = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        ordering = ['-date', '-time']
        verbose_name = 'consulta'

    def get_absolute_url(self):
        return reverse('meeting-detail', args=[str(self.pk)])

    def __str__(self):
        return f'{self.date}'

    def get_previous(self):
        return self.client.meeting_set.filter(date__lt=self.date).first()

    def check_missed(self):
        if self.state != 's': return
        meeting_dtime = self.get_meeting_datetime()
        tdelta = datetime.timedelta(hours=2)
        if timezone.localtime() > meeting_dtime + tdelta:
            self.state = 'm'
            self.save()
    
    def get_color(self):
        # return {'s': '', 'o': 'warning', 'f': '', 'm': 'danger'}[self.state]
        if self.state == 'm': return 'danger'
        elif self.is_startable() or self.state == 'o': return 'warning'

    def get_meeting_datetime(self):
        unaware_dtime = datetime.datetime.combine(self.date, self.time)
        return timezone.make_aware(unaware_dtime)
    
    def is_startable(self):
        if self.state in ['f', 'm']: return False
        meeting_dtime = self.get_meeting_datetime()
        tdelta = datetime.timedelta(hours=2)
        return timezone.localtime() > meeting_dtime - tdelta


class Measure(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100, verbose_name='Nome')
    unit = models.CharField(max_length=50, blank=True, verbose_name='Unidade')

    class Meta:
        ordering = ['id']
        verbose_name = 'medida'

    def __str__(self):
        # return f'{self.display_name} ({self.unit})'
        return self.display_name


class Measurement(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Consulta')
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE, verbose_name='Medida')
    
    value = models.IntegerField(verbose_name='Valor')
    unit = models.CharField(max_length=50, blank=True, verbose_name='Unidade')
    date = models.DateField(default=datetime.date.today, verbose_name='Data')

    class Meta:
        ordering = ['-date', 'client__name', '-id']
        verbose_name = 'medição'
        verbose_name_plural = 'medições'

    def __str__(self):
        return f'{self.measure.display_name} of {self.client.name} in {self.date}'


class PrePlan(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Consulta')
    date = models.DateField(default=timezone.now, null=True, blank=True, verbose_name='Data')

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

    protein = models.IntegerField(default=25, null=True, blank=True, verbose_name='Proteína (%)')
    carbs = models.IntegerField(default=50, null=True, blank=True, verbose_name='Hidratos de carbono (%)')
    fats = models.IntegerField(default=25, null=True, blank=True, verbose_name='Lípidos (%)')
    
    regular_milk = models.IntegerField(default=0, null=True, blank=True, verbose_name='Leite meio-gordo (doses)')
    low_fat_milk = models.IntegerField(default=0, null=True, blank=True, verbose_name='Leite magro (doses)')
    solid_yoghurt = models.IntegerField(default=0, null=True, blank=True, verbose_name='Iogurte sólido (doses)')
    liquid_yoghurt = models.IntegerField(default=0, null=True, blank=True, verbose_name='Iogurte líquido (doses)')
    whey = models.IntegerField(default=0, null=True, blank=True, verbose_name='Whey (doses)')
    fruit = models.IntegerField(default=3, null=True, blank=True, verbose_name='Fruta (doses)')
    vegetables = models.IntegerField(default=4, null=True, blank=True, verbose_name='Vegetais (doses)')
    
    protein_dosage = models.IntegerField(null=True, blank=True, verbose_name='Carne e equiv. (doses)')
    carbs_dosage = models.IntegerField(null=True, blank=True, verbose_name='Pão e equiv. (doses)')
    fats_dosage = models.IntegerField(null=True, blank=True, verbose_name='Gordura (doses)')

    class Meta:
        ordering = ['-date', 'client__name', '-id']
        verbose_name = 'cálculos'
        verbose_name_plural = 'cálculos'

    def get_absolute_url(self):
        return reverse('preplan-detail', args=[str(self.pk)])
    
    def __str__(self):
        return f'{self.client.name} ({self.date})'


class MealPlan(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Consulta')
    date = models.DateField(default=timezone.now, null=True, blank=True, verbose_name='Data')

    todo = models.BooleanField(default=True, verbose_name='Bigan')
