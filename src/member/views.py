from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def login_routing(request):
    """ After the user logs in, route them to the correct page
    * kiosk users should go to the kiosk page
    * volunteers should go to the volunteer dashboard
    * admins should go to the admin dashboard
    """

    # grab the categories and events for a checkin
    if request.user.has_perm("member.is_kiosk_user"):
        # A superuser will have all permissions by default,
        # but we don't want to the superuser to automatically go to quick checkin
        if not request.user.is_superuser:
            # redirect them to the kiosk page
            print("here we go, kiosk mode!")
            return redirect('/checkin/')
    else:
        # send them to the volunteer page
        return redirect('log-hours')

    return redirect('log-hours')
