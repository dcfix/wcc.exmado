# Generated by Django 4.2.7 on 2023-12-02 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkin', '0002_event_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='checkin',
            old_name='event_id',
            new_name='event',
        ),
        migrations.AlterField(
            model_name='checkin',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]