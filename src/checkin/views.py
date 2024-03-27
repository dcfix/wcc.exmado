import datetime

from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.shortcuts import render

from .models import Category, Event, CheckIn
from .forms import CheckInForm, ReportVolunteerTimeframe
# Create your views here.


def pick_category(request):
    """ View function for checkin """

    # grab the categories and events for a checkin
    categories = Category.objects.filter(active=True).order_by('desc')
    context = {'categories': categories}

    return render(request, 'checkin-category.html', context=context)


def pick_event(request, category_id=1):
    """ View function to pick the event"""

    print(category_id)
    # grab the categories and events for a checkin
    events = Event.objects.filter(active=True, category_id=category_id).order_by('desc')

    context = {'events': events}
    print(events.count())
    return render(request, 'checkin-event.html', context=context)


def checkin_final(request, event_id=2):
    """ finish the checkin and save it to the database"""
    if request.method == "POST":
        form = CheckInForm(request.POST)
        if form.is_valid():
            new_checkin = CheckIn()
            new_checkin.event_id = form.cleaned_data["event_id"]
            new_checkin.number_in_group = form.cleaned_data["number_in_group"]

            new_checkin.save()
            if new_checkin.number_in_group == 1:
                phrase = "person has"
            else:
                phrase = "people have"
            msg = f" {new_checkin.number_in_group} {phrase} been checked in for { new_checkin.event.desc } "
            messages.add_message(request, messages.SUCCESS, msg)

        return HttpResponseRedirect("/checkin/")
    else:

        my_event = Event.objects.get(active=True, id=event_id)
        context = {'event_desc': my_event.desc,
                   'event_id': my_event.id}

        return render(request, 'checkin.html', context=context)


@login_required
def rpt_timeframe_activity(request):
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
            end_date = form.cleaned_data["end_date"]
    else:

        start_date = datetime.date.today() - datetime.timedelta(days=7)
        end_date = datetime.date.today() + datetime.timedelta(days=1)
        form.start_date = start_date
        form.end_date = end_date

    entries = CheckIn.objects.filter(created_date__range=[start_date, end_date])\
        .values('event__desc', )\
        .order_by('event__desc')\
        .annotate(total_attendance=Sum('number_in_group'))

    context = {"form": form,
               "entries": entries}
    return render(request, 'rpt_timeframe_activity.html', context)
