from datetime import datetime

from django import forms
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CheckInForm(forms.Form):
    number_in_group = forms.IntegerField(help_text="How many people are in your party?")
    event_id = forms.IntegerField()


class ReportVolunteerTimeframe(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy('rpt_timeframe_activity')
        self.helper.form_method = "post"
        self.helper.add_input(Submit('submit', 'Submit'))

    start_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y',
                                                            attrs={'type': 'date', 'max': datetime.now().date()}))

    end_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y',
                                                          attrs={'type': 'date', 'max': datetime.now().date()}))
