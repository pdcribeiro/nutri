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
    list_display = ('name', 'born', 'nutritionist')  #TODO add last_meeting
    inlines = [MealsInline, PlansInline, MeetingsInline]

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('client', 'date')

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('client', 'meeting', 'date', 'energy')
