from django.core.management.base import BaseCommand
from django.utils import timezone

from checkin.models import CheckIn


class Command(BaseCommand):
    help = (
        "Populate CheckIn.activity_date from created_date's local day.\n"
        "By default only rows missing a value are touched (a no-op once the "
        "0005 migration has run). Use --recompute to reset EVERY row from its "
        "created_date, which overwrites any manually-entered activity_date."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--recompute",
            action="store_true",
            help="Reset every row from created_date, overwriting manual dates.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing.",
        )

    def handle(self, *args, **options):
        recompute = options["recompute"]
        dry_run = options["dry_run"]

        rows = CheckIn.objects.all()
        if not recompute:
            rows = rows.filter(activity_date__isnull=True)

        changed = 0
        for checkin in rows.iterator():
            # created_date is non-null and timezone-aware.
            new_date = timezone.localtime(checkin.created_date).date()
            if checkin.activity_date == new_date:
                continue
            if not dry_run:
                checkin.activity_date = new_date
                checkin.save(update_fields=["activity_date"])
            changed += 1

        scope = "all rows" if recompute else "rows missing activity_date"
        verb = "Would update" if dry_run else "Updated"
        self.stdout.write(
            self.style.SUCCESS(f"{verb} {changed} of {scope}.")
        )
