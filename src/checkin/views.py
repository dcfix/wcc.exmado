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

def pick_isMember(request):
    """ View function for is this is a checkin by a member or not """
    if request.method == "POST":
        # Store membership status in session
        is_member = request.POST.get('is_member') == 'true'
        request.session['is_member'] = is_member
        return HttpResponseRedirect('/checkin/category/')
    
    context = {}
    return render(request, 'check_membership.html', context=context)


def pick_category(request):
    """ View function for checkin """
    
    # Check if membership status is in session
    is_member = request.session.get('is_member')
    if is_member is None:
        # Redirect back to membership check if not set
        return HttpResponseRedirect("/checkin/")

    # grab the categories and events for a checkin
    categories = Category.objects.filter(active=True).order_by('desc')
    context = {'categories': categories, 'is_member': is_member}

    return render(request, 'checkin-category.html', context=context)


def pick_event(request, category_id=1):
    """ View function to pick the event"""
    
    # Check if membership status is in session
    is_member = request.session.get('is_member')
    if is_member is None:
        # Redirect back to membership check if not set
        return HttpResponseRedirect("/checkin/")

    print(category_id)
    # grab the categories and events for a checkin
    events = Event.objects.filter(active=True, category_id=category_id).order_by('desc')

    context = {'events': events, 'is_member': is_member}
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
            
            # Get membership status from session
            new_checkin.isMember = request.session.get('is_member', None)

            new_checkin.save()
            
            # Clear the session data after successful checkin
            request.session.pop('is_member', None)
            
            if new_checkin.number_in_group == 1:
                phrase = "person has"
            else:
                phrase = "people have"
            msg = f" {new_checkin.number_in_group} {phrase} been checked in for { new_checkin.event.desc } "
            messages.add_message(request, messages.SUCCESS, msg)

        return HttpResponseRedirect("/checkin/")
    else:
        # Check if membership status is in session
        is_member = request.session.get('is_member')
        if is_member is None:
            # Redirect back to membership check if not set
            return HttpResponseRedirect("/checkin/")

        my_event = Event.objects.get(active=True, id=event_id)
        context = {'event_desc': my_event.desc,
                   'event_id': my_event.id,
                   'is_member': is_member}

        return render(request, 'checkin.html', context=context)


@login_required
def rpt_timeframe_activity(request):
    # must be staff to view the report
    if not request.user.is_staff:
        raise PermissionDenied

    form = ReportVolunteerTimeframe()
    start_date = datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today() + datetime.timedelta(days=2)

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

    # Get raw data grouped by event and membership status
    raw_entries = CheckIn.objects.filter(created_date__range=[start_date, end_date])\
        .values('event__desc', 'isMember')\
        .order_by('event__desc', 'isMember')\
        .annotate(total_attendance=Sum('number_in_group'))

    # Process data to group by event with member/guest breakdown
    event_data = {}
    for entry in raw_entries:
        event_name = entry['event__desc']
        is_member = entry['isMember']
        attendance = entry['total_attendance']
        
        if event_name not in event_data:
            event_data[event_name] = {
                'event_name': event_name,
                'member_count': 0,
                'guest_count': 0,
                'unknown_count': 0,
                'total_count': 0
            }
        
        if is_member is True:
            event_data[event_name]['member_count'] = attendance
        elif is_member is False:
            event_data[event_name]['guest_count'] = attendance
        else:
            event_data[event_name]['unknown_count'] = attendance
        
        event_data[event_name]['total_count'] += attendance

    # Convert to list for template
    entries = list(event_data.values())
    
    # Calculate totals
    totals = {
        'total_members': sum(entry['member_count'] for entry in entries),
        'total_guests': sum(entry['guest_count'] for entry in entries),
        'total_unknown': sum(entry['unknown_count'] for entry in entries),
        'grand_total': sum(entry['total_count'] for entry in entries)
    }

    context = {"form": form,
               "entries": entries,
               "totals": totals}
    print(context["form"]["start_date"])
    return render(request, 'rpt_timeframe_activity.html', context)
