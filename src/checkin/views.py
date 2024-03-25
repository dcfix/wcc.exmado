from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages

from .models import Category, Event, CheckIn
from .forms import CheckInForm

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
        print(request.POST)
        print("POSTED:w")
        if form.is_valid():
            print("it's valid!")
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
