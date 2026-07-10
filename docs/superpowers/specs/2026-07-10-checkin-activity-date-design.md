# CheckIn `activity_date` — Design

**Date:** 2026-07-10
**Status:** Approved, pending implementation

## Problem

Staff need to enter attendance data manually through the Django admin — for example,
recording last Tuesday's lunch that nobody checked in at the kiosk.

Today this is impossible. `CheckIn.created_date` uses `auto_now_add=True`, which sets
`editable=False` at the model level, so Django will not render it as a form input. It is
also listed in `CheckInAdmin.readonly_fields`. A row added through the admin is always
stamped with the moment it was saved.

The Activity Report (`checkin.views.rpt_timeframe_activity`) filters on `created_date`,
so a backfilled row lands in the report on the day it was *typed in*, not the day the
activity happened.

`created_date` conflates two distinct facts:

- **When the activity happened** — a business fact staff may need to set or correct.
- **When the row was created** — an audit fact that must never be editable.

## Decision

Add a separate, editable `activity_date` field. Leave `created_date` untouched as an
audit trail.

This mirrors the volunteer app, which already solved this exact problem:
`Entry.volunteer_date` is user-editable, `Entry.created_date` is auto-stamped and
readonly, and `volunteer.views.rpt_timeframe` filters on `volunteer_date`.

`activity_date` is a `DateField`, not a `DateTimeField`. The Activity Report only ever
filters and groups by calendar day, and a date has no timezone, which removes an entire
class of boundary bug (see Timezone below).

### Rejected alternatives

**Make `created_date` editable** (drop `auto_now_add`, use `default=timezone.now`).
No new field and no data migration, but it permanently destroys the audit trail: a
backfilled row becomes indistinguishable from a live kiosk check-in, and "when was this
row actually entered" becomes unanswerable. It also breaks the convention every other
model in the codebase follows, including `Category` and `Event` in the same file.

**Nullable `activity_date` with a `Coalesce` fallback to `created_date`.**
Avoids a data migration, but every read site must remember the fallback forever, and the
same fact gets two representations. The one-time backfill is cheaper than permanent
ambiguity.

## Changes

### 1. Model — `src/checkin/models.py`

Add the import (the module currently imports `models`, `settings`, `reverse` but not
`timezone`):

```python
from django.utils import timezone
```

Add to `CheckIn`, positioned with the business fields (above the audit block):

```python
activity_date = models.DateField(
    default=timezone.localdate,
    help_text="The date the activity actually took place.")
```

Non-null with a default, so the kiosk flow in `checkin_final` needs no change — a live
check-in gets today's local date automatically.

Pass the callable `timezone.localdate`, not `timezone.localdate()`. The latter would
evaluate once at import and freeze the date.

### 2. Timezone — `src/config/settings.py`

`TIME_ZONE` is currently `'UTC'`. Change to `'America/Chicago'`.

`USE_TZ` stays `True`, so `DateTimeField` values remain stored as UTC; only their
interpretation shifts. Without this, `timezone.localdate` returns the UTC date and a 7pm
Central check-in defaults to *tomorrow*.

This must land before the data migration runs, so the backfill converts to the correct
local day.

### 3. Migrations — `src/checkin/migrations/`

A single `0005_checkin_activity_date.py` with three operations in order. A bare
`AddField` with `default=timezone.localdate` would stamp every existing row with the
migration-run date, which is wrong.

1. `AddField` — `activity_date`, `null=True`, no default.
2. `RunPython` — backfill `activity_date = timezone.localtime(created_date).date()`
   for every row. `created_date` is non-null and timezone-aware, so this is total.
   Provide `reverse_code=migrations.RunPython.noop`.
3. `AlterField` — `null=False`, `default=timezone.localdate`.

Use `apps.get_model('checkin', 'CheckIn')` in the backfill, not a direct import.

### 4. Admin — `src/checkin/admin.py`

In `CheckInAdmin`:

- Add `activity_date` to `fields`, grouped with the business fields.
- Add `activity_date` to `list_display`.
- Add `list_filter = ('activity_date', 'event', 'isMember')` so staff can find rows to
  correct.
- Leave `created_date` in `readonly_fields`. It stays an audit field.

### 5. Report — `src/checkin/views.py`

In `rpt_timeframe_activity`:

- Change the filter to `activity_date__range=[start_date, end_date]`.
- **Remove** `+ datetime.timedelta(days=1)` from the submitted `end_date`. That existed
  to make a datetime range cover the end day. A date range is naturally inclusive on
  both ends; leaving it in would silently include one extra day.
- Change the GET defaults to `timezone.localdate() - timedelta(days=7)` through
  `timezone.localdate()`. The old `+ timedelta(days=2)` future window was compensating
  for the datetime/midnight problem and is no longer meaningful.
- Delete the `print(context["form"]["start_date"])` debug line.

Out of scope, noted for later: on a GET, lines 116-117 do `form.start_date = start_date`,
which sets an attribute on the form object and does not populate the field. The date
inputs render empty while the table shows the last-week window. Fixing that means passing
`initial=` to the form fields.

## Data Flow

**Kiosk check-in** — `checkin_final` saves a `CheckIn`. `activity_date` defaults to the
local day; `created_date` auto-stamps the instant. Both agree.

**Manual admin entry** — staff pick `activity_date` for the day the activity happened.
`created_date` auto-stamps now. They disagree, and that difference is the audit record.

**Report** — filters on `activity_date` alone. `created_date` never affects report
output.

## Testing

`src/checkin/tests.py` is an empty stub. These are the first real tests for the app.

**Model**
- A `CheckIn` saved with no `activity_date` defaults to today's *local* date.
- A `CheckIn` saved at 7pm Central has `activity_date` equal to that day, not the next
  (regression test for the UTC bug).
- `created_date` cannot be set explicitly — it always reflects save time.

**Migration**
- Backfill sets `activity_date` to the local date of each existing row's `created_date`.
  Exercise with a row whose UTC timestamp falls on a different local day.

**Report**
- A row whose `activity_date` is inside the window but whose `created_date` is outside it
  **is** included. This is the whole point of the change.
- A row whose `created_date` is inside the window but whose `activity_date` is outside it
  is **excluded**.
- Rows on the exact `start_date` and exact `end_date` are both included (inclusive range).
- A row one day past `end_date` is excluded (guards against reintroducing the `+1 day`).

**Admin**
- `activity_date` is editable on the add form.
- `created_date` is not editable.

Run with `python manage.py test checkin` from `src/`.

## Risks

`TIME_ZONE` affects how every existing `DateTimeField` renders across the whole site, not
just this app. Admin columns and the volunteer report will shift by the UTC offset. This
is a correction, not a regression — the values were always UTC and were always being
displayed as UTC — but it is a visible change and worth mentioning to users.

The migration is not reversible in a data-preserving way. `reverse_code` is a noop, so
rolling back drops the column. Back up `db.sqlite3` before migrating in production.
