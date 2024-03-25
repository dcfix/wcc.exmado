from django import forms


class CheckInForm(forms.Form):
    number_in_group = forms.IntegerField(help_text="How many people are in your party?")
    event_id = forms.IntegerField()
