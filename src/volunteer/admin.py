from django.contrib import admin
from .models import Task, Entry

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('desc', 'active')

    fields = ['desc', 'active', ('created_by', 'created_date'),
              ('modified_by', 'modified_date')]
    readonly_fields = ['created_by', 'created_date', 'modified_by', 'modified_date']


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'volunteer_date', 'volunteer_task', 'hours', 'mileage', 'active')

    fields = ['volunteer', 'volunteer_date', 'volunteer_task', 'hours', 'mileage', 'notes', 'active',
              ('created_by', 'created_date'),
              ('modified_by', 'modified_date')]

    readonly_fields = ['created_by', 'created_date', 'modified_by', 'modified_date']

