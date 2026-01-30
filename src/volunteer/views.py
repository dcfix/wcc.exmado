from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.db.models.functions import TruncDate
from collections import OrderedDict
from django.shortcuts import render
from collections import OrderedDict

from .forms import LogVolunteerHours, ReportVolunteerTimeframe, ReportCategoryHours
from .models import Entry

import datetime

# Create your views here.


# add a new volunteer
# update a volunteer (name, email, password, active)
# timesheet
# summary


def list_entries(request):
    # is the user a staff member? If so, then list all users
    # we will get the entries for a given time frame (since last monday)
    entries = Entry.objects.filter(volunteer=request.user)

    context = {
        'entries': entries,
    }

    return render(request, 'volunteer/list_entries.html', context=context)


def dashboard(request):

    context = {}
    return render(request, 'volunteer/dashboard.html', context)




@login_required
def rpt_timeframe(request):
    # must be staff to view the report

    if not request.user.is_staff:
        raise PermissionDenied

    start_date = datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today() + datetime.timedelta(days=2)

    form = ReportVolunteerTimeframe()

    # given a time frame, give the cumulative hours/miles per volunteer
    if request.method == "POST":
        # we need to grab the start and end dates for this report

        form = ReportVolunteerTimeframe(request.POST)

        # Check to see if the form is valid:
        if form.is_valid():
            # we need to save the new data
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"] + datetime.timedelta(days=1)
    else:
        form.start_date = start_date
        form.end_date = end_date

    qs = Entry.objects.filter(volunteer_date__range=[start_date, end_date])

    # aggregate totals per volunteer
    entries = qs.values('volunteer__id', 'volunteer__username')\
        .order_by('volunteer__username')\
        .annotate(total_hours=Sum('hours'))\
        .annotate(total_mileage=Sum('mileage'))\
        .annotate(total_meals=Sum('meal'))

    # group by date -> volunteer -> task (date -> volunteer -> tasks + totals)
    grouped_qs = qs.annotate(date=TruncDate('volunteer_date'))\
        .values('date', 'volunteer__username', 'volunteer_task__desc')\
        .order_by('date', 'volunteer__username', 'volunteer_task__desc')\
        .annotate(total_hours=Sum('hours'), total_mileage=Sum('mileage'), total_meals=Sum('meal'))

    grouped = OrderedDict()
    for row in grouped_qs:
        date = row['date']
        volunteer = row.get('volunteer__username') or 'Unknown'
        task = row['volunteer_task__desc'] or 'Unspecified'
        hours = row.get('total_hours') or 0
        mileage = row.get('total_mileage') or 0
        meals = row.get('total_meals') or 0

        if date not in grouped:
            grouped[date] = OrderedDict()

        if volunteer not in grouped[date]:
            grouped[date][volunteer] = {
                'totals': {'hours': 0.0, 'mileage': 0.0, 'meals': 0},
                'tasks': OrderedDict()
            }

        if task not in grouped[date][volunteer]['tasks']:
            grouped[date][volunteer]['tasks'][task] = {'hours': 0.0, 'mileage': 0.0, 'meals': 0}

        # set task-level totals (this row is already aggregated per volunteer/task/day)
        grouped[date][volunteer]['tasks'][task]['hours'] = float(hours)
        grouped[date][volunteer]['tasks'][task]['mileage'] = float(mileage)
        grouped[date][volunteer]['tasks'][task]['meals'] = int(meals)

        # accumulate volunteer-level totals
        grouped[date][volunteer]['totals']['hours'] += float(hours)
        grouped[date][volunteer]['totals']['mileage'] += float(mileage)
        grouped[date][volunteer]['totals']['meals'] += int(meals)

    # overall totals for the period
    overall = qs.aggregate(total_hours=Sum('hours'), total_mileage=Sum('mileage'), total_meals=Sum('meal'))

    context = {"form": form,
               "entries": entries,
               "grouped": grouped,
               "overall": overall}
    return render(request, 'volunteer/rpt_timeframe.html', context)


@login_required
def rpt_cat_hours(request):
    # must be staff to view the report
    if not request.user.is_staff:
        raise PermissionDenied

    start_date = datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today() + datetime.timedelta(days=2)

    form = ReportVolunteerTimeframe()
    form = ReportCategoryHours()

    if request.method == "POST":

        form = ReportCategoryHours(request.POST)

        if form.is_valid():
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"] + datetime.timedelta(days=1)
    else:
        form.start_date = start_date
        form.end_date = end_date

    qs = Entry.objects.filter(volunteer_date__range=[start_date, end_date])

    # sum hours per activity (task description)
    categories = qs.values('volunteer_task__desc')\
        .order_by('volunteer_task__desc')\
        .annotate(total_hours=Sum('hours'))

    overall = qs.aggregate(total_hours=Sum('hours'))

    context = {"form": form,
               "categories": categories,
               "overall": overall}
    return render(request, 'volunteer/rpt_cat_hours.html', context)



@login_required
def log_hours(request):
    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding):
        form = LogVolunteerHours(request.POST)

        # Check to see if the form is valid:
        if form.is_valid():
            # we need to save the new data

            entry = Entry()
            entry.volunteer = request.user
            entry.volunteer_task = form.cleaned_data["volunteer_task"]
            entry.volunteer_date = form.cleaned_data["volunteer_date"]
            entry.hours = form.cleaned_data["hours"]
            entry.mileage = form.cleaned_data["mileage"]
            entry.meal = form.cleaned_data.get("meal", 0)
            entry.notes = form.cleaned_data["notes"]

            entry.save()

    # grab the entries for this user for the last week.

    entries = Entry.objects.filter(volunteer=request.user, volunteer_date__gte = (datetime.date.today() - datetime.timedelta(days=7)))

    form = LogVolunteerHours(initial={'volunteer_date': datetime.date.today()})

    context = {
        'form': form,
        'entries': entries,
    }

    return render(request, 'volunteer/log_hours.html', context)

