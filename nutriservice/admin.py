from django.contrib import admin

from .models import Client, Meal, Meeting, Plan


class MealsInline(admin.TabularInline):
    model = Meal
    extra = 0

class MeetingsInline(admin.TabularInline):
    model = Meeting
    extra = 0

class PlansInline(admin.TabularInline):
    model = Plan
    extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nutritionist', 'name', 'born',)
    inlines = [MealsInline, PlansInline, MeetingsInline]

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'time', 'place')

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date')

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'meeting', 'date', 'daily_energy')
