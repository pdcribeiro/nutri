from django.contrib import admin

from .models import Client, Meal, Measure, Measurement, Meeting, PrePlan


class MealsInline(admin.TabularInline):
    model = Meal
    extra = 0

class MeasurementsInline(admin.TabularInline):
    model = Measurement
    extra = 0

class MeetingsInline(admin.TabularInline):
    model = Meeting
    extra = 0

class PrePlansInline(admin.TabularInline):
    model = PrePlan
    extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nutritionist', 'name', 'age',)
    inlines = [MealsInline, MeasurementsInline, MeetingsInline, PrePlansInline]

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'time', 'place')

@admin.register(Measure)
class MeasureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit')
    inlines = [MeasurementsInline]

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date', 'measure', 'value', 'unit')

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date')

@admin.register(PrePlan)
class PrePlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'meeting', 'date', 'daily_energy')