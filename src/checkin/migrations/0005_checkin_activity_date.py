import django.utils.timezone
from django.db import migrations, models


def backfill_activity_date(apps, schema_editor):
    CheckIn = apps.get_model("checkin", "CheckIn")
    for checkin in CheckIn.objects.all().iterator():
        # created_date is non-null and timezone-aware; use its local date.
        checkin.activity_date = django.utils.timezone.localtime(
            checkin.created_date
        ).date()
        checkin.save(update_fields=["activity_date"])


class Migration(migrations.Migration):

    dependencies = [
        ("checkin", "0004_checkin_ismember"),
    ]

    operations = [
        migrations.AddField(
            model_name="checkin",
            name="activity_date",
            field=models.DateField(null=True),
        ),
        migrations.RunPython(
            backfill_activity_date,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="checkin",
            name="activity_date",
            field=models.DateField(
                default=django.utils.timezone.localdate,
                help_text="The date the activity actually took place.",
            ),
        ),
    ]
