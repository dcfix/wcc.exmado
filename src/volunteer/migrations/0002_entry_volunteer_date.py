# Generated by Django 4.2.7 on 2024-02-18 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='volunteer_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
