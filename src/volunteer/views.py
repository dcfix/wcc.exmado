from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.shortcuts import render

from .forms import LogVolunteerHours, ReportVolunteerTimeframe
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
    # given a time frame, give the cumulative hours/miles per volunteer
    form = ReportVolunteerTimeframe(request.POST)
    if request.method == "POST":
        # we need to grab the start and end dates for this report

        form = ReportVolunteerTimeframe(request.POST)

        # Check to see if the form is valid:
        if form.is_valid():
            # we need to save the new data
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"] + datetime.timedelta(days=1)
    else:
        start_date = datetime.date.today() - datetime.timedelta(days=7)
        end_date = datetime.date.today() + datetime.timedelta(days=1)
        form.start_date = start_date
        form.end_date = end_date

    entries = Entry.objects.filter(volunteer_date__range=[start_date, end_date])\
        .values('volunteer_date', 'volunteer__username', 'volunteer_task__desc')\
        .order_by('volunteer_date', 'volunteer_task__desc')\
        .annotate(total_hours=Sum('hours'))\
        .annotate(total_mileage=Sum('mileage'))

    context = {"form": form,
               "entries": entries}
    return render(request, 'volunteer/rpt_timeframe.html', context)



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

