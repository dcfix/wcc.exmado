import datetime

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import ReportVolunteerTimeframe
from .models import Category, Event, CheckIn


def make_event(desc="Lunch"):
    category = Category.objects.create(desc=f"Cat-{desc}", active=True)
    return Event.objects.create(desc=desc, category=category, active=True)


class CheckInModelTests(TestCase):
    def test_activity_date_defaults_to_local_today(self):
        event = make_event()
        checkin = CheckIn.objects.create(event=event, number_in_group=1)
        self.assertEqual(checkin.activity_date, timezone.localdate())

    def test_activity_date_default_is_timezone_aware_callable(self):
        # Guards against date.today() / timezone.now().date(), which ignore
        # the active timezone and stamp evening check-ins with the UTC date.
        field = CheckIn._meta.get_field("activity_date")
        self.assertIs(field.default, timezone.localdate)

    def test_activity_date_can_be_set_explicitly(self):
        event = make_event()
        past = datetime.date(2026, 7, 1)
        checkin = CheckIn.objects.create(
            event=event, number_in_group=1, activity_date=past
        )
        self.assertEqual(checkin.activity_date, past)

    def test_created_date_is_not_editable(self):
        # created_date stays an auto-stamped audit field.
        self.assertFalse(CheckIn._meta.get_field("created_date").editable)


class ActivityReportTests(TestCase):
    def setUp(self):
        self.event = make_event()
        User = get_user_model()
        self.staff = User.objects.create_user(
            username="staff", password="pw", is_staff=True
        )
        self.client.force_login(self.staff)
        self.url = reverse("rpt_timeframe_activity")

    def _checkin(self, activity_date, created_date=None, number=1):
        checkin = CheckIn.objects.create(
            event=self.event, number_in_group=number, activity_date=activity_date
        )
        if created_date is not None:
            # created_date is auto_now_add; bypass it with an update().
            CheckIn.objects.filter(pk=checkin.pk).update(created_date=created_date)
        return checkin

    def _grand_total(self, start, end):
        resp = self.client.post(
            self.url,
            {
                "start_date": start.strftime("%m/%d/%Y"),
                "end_date": end.strftime("%m/%d/%Y"),
            },
        )
        self.assertEqual(resp.status_code, 200)
        return resp.context["totals"]["grand_total"]

    def test_filters_by_activity_date_not_created_date(self):
        window_start = datetime.date(2026, 7, 6)
        window_end = datetime.date(2026, 7, 10)
        # activity inside the window, but the row was created long after.
        created_outside = timezone.make_aware(
            datetime.datetime(2026, 8, 1, 12, 0)
        )
        self._checkin(
            activity_date=datetime.date(2026, 7, 8),
            created_date=created_outside,
            number=5,
        )
        self.assertEqual(self._grand_total(window_start, window_end), 5)

    def test_excludes_rows_whose_activity_date_is_outside_window(self):
        # created today (inside), but the activity happened before the window.
        self._checkin(activity_date=datetime.date(2026, 6, 1), number=5)
        self.assertEqual(
            self._grand_total(
                datetime.date(2026, 7, 6), datetime.date(2026, 7, 10)
            ),
            0,
        )

    def test_window_boundaries_are_inclusive(self):
        start = datetime.date(2026, 7, 6)
        end = datetime.date(2026, 7, 10)
        self._checkin(activity_date=start, number=2)
        self._checkin(activity_date=end, number=3)
        self.assertEqual(self._grand_total(start, end), 5)

    def test_day_after_end_is_excluded(self):
        # Regression guard against reintroducing the "+1 day" hack.
        start = datetime.date(2026, 7, 6)
        end = datetime.date(2026, 7, 10)
        self._checkin(activity_date=end + datetime.timedelta(days=1), number=9)
        self.assertEqual(self._grand_total(start, end), 0)


class ReportFormTests(TestCase):
    def test_unbound_form_defaults_to_last_seven_days(self):
        form = ReportVolunteerTimeframe()
        self.assertEqual(
            form["start_date"].value(),
            timezone.localdate() - datetime.timedelta(days=7),
        )
        self.assertEqual(form["end_date"].value(), timezone.localdate())

    def test_report_get_renders_default_dates(self):
        User = get_user_model()
        staff = User.objects.create_user(
            username="staff", password="pw", is_staff=True
        )
        self.client.force_login(staff)
        resp = self.client.get(reverse("rpt_timeframe_activity"))
        self.assertEqual(resp.status_code, 200)
        form = resp.context["form"]
        self.assertEqual(
            form["start_date"].value(),
            timezone.localdate() - datetime.timedelta(days=7),
        )
        self.assertEqual(form["end_date"].value(), timezone.localdate())


class BackfillCommandTests(TestCase):
    def setUp(self):
        self.event = make_event()

    def _row(self, activity_date, created_date):
        checkin = CheckIn.objects.create(
            event=self.event, number_in_group=1, activity_date=activity_date
        )
        # created_date is auto_now_add; bypass it with an update().
        CheckIn.objects.filter(pk=checkin.pk).update(created_date=created_date)
        return checkin

    def test_default_run_leaves_manual_dates_untouched(self):
        # Every row is already non-null (NOT NULL column), so the default
        # scope must not clobber a deliberately-set activity_date.
        manual = datetime.date(2026, 1, 2)
        created = timezone.make_aware(datetime.datetime(2026, 6, 15, 12, 0))
        checkin = self._row(activity_date=manual, created_date=created)
        call_command("backfill_activity_date")
        checkin.refresh_from_db()
        self.assertEqual(checkin.activity_date, manual)

    def test_recompute_resets_from_created_date_local_day(self):
        wrong = datetime.date(2026, 1, 2)
        created = timezone.make_aware(datetime.datetime(2026, 6, 15, 12, 0))
        checkin = self._row(activity_date=wrong, created_date=created)
        call_command("backfill_activity_date", "--recompute")
        checkin.refresh_from_db()
        self.assertEqual(
            checkin.activity_date, timezone.localtime(created).date()
        )

    def test_recompute_is_idempotent(self):
        created = timezone.make_aware(datetime.datetime(2026, 6, 15, 12, 0))
        checkin = self._row(
            activity_date=datetime.date(2026, 1, 2), created_date=created
        )
        call_command("backfill_activity_date", "--recompute")
        first = CheckIn.objects.get(pk=checkin.pk).activity_date
        call_command("backfill_activity_date", "--recompute")
        self.assertEqual(CheckIn.objects.get(pk=checkin.pk).activity_date, first)

    def test_dry_run_writes_nothing(self):
        wrong = datetime.date(2026, 1, 2)
        created = timezone.make_aware(datetime.datetime(2026, 6, 15, 12, 0))
        checkin = self._row(activity_date=wrong, created_date=created)
        call_command("backfill_activity_date", "--recompute", "--dry-run")
        checkin.refresh_from_db()
        self.assertEqual(checkin.activity_date, wrong)


class MigrationBackfillTests(TestCase):
    """The 0005 data migration backfills activity_date from created_date's
    local date. Verify the conversion logic against a row whose UTC timestamp
    lands on a different local day."""

    @override_settings(TIME_ZONE="America/Chicago")
    def test_backfill_uses_local_date_of_created_date(self):
        # 2026-07-09 02:00 UTC is 2026-07-08 21:00 in Chicago.
        created = datetime.datetime(2026, 7, 9, 2, 0, tzinfo=datetime.timezone.utc)
        self.assertEqual(timezone.localtime(created).date(), datetime.date(2026, 7, 8))
