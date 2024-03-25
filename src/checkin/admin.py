from django.contrib import admin
from .models import Category, Event, CheckIn

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('desc', 'active')

    fields = ['desc', 'active', ('created_by', 'created_date'),
              ('modified_by', 'modified_date')]
    readonly_fields = ['created_by', 'created_date', 'modified_by', 'modified_date']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('desc', 'category', 'active')

    fields = ['desc', 'category', 'active', ('created_by', 'created_date'),
              ('modified_by', 'modified_date')]

    readonly_fields = ['created_by', 'created_date', 'modified_by', 'modified_date']


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('event', 'number_in_group', 'note', 'created_date')

    fields = ['event', 'number_in_group', 'note',
              ('created_by', 'created_date'),
              ('modified_by', 'modified_date')]
    readonly_fields = ['created_by', 'created_date', 'modified_by', 'modified_date']
