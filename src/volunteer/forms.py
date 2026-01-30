from datetime import datetime

from django import forms
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Entry, Task


class LogVolunteerHours(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy('log-hours')
        self.helper.form_method = "post"
        self.helper.add_input(Submit('submit', 'Submit'))

    volunteer_task = forms.ModelChoiceField(queryset=Task.objects.filter(active=True),
                                            widget=forms.RadioSelect(),
                                            label="Task type")
    volunteer_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y',
                                                            attrs={'type': 'date', 'max': datetime.now().date()}))
    hours = forms.DecimalField(label="Hours", required=True, initial=0)
    mileage = forms.DecimalField(label="Mileage", required=True, initial=0)
    meal = forms.TypedChoiceField(
        label="Took meal?",
        choices=((0, 'No'), (1, 'Yes')),
        coerce=int,
        widget=forms.RadioSelect(),
        initial=0,
        required=False,
        help_text='0 = no meal, 1 = meal')
    notes = forms.CharField(label="Additional notes or feedback", required=False)


class ReportVolunteerTimeframe(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy('rpt_timeframe')
        self.helper.form_method = "post"
        self.helper.add_input(Submit('submit', 'Submit'))

    start_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y',
                                                        attrs={'type': 'date',
                                                               'maxDate': datetime.now().date(),
                                                               'date': datetime.now().date(),
                                                               }))


    end_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y',
                                                      attrs={'type': 'date',
                                                             'maxDate': datetime.now().date()}))

class ReportCategoryHours(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy('rpt_cat_hours')
        self.helper.form_method = "post"
        self.helper.add_input(Submit('submit', 'Submit'))

    start_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y',
                                                        attrs={'type': 'date',
                                                               'maxDate': datetime.now().date(),
                                                               'date': datetime.now().date(),
                                                               }))


    end_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y',
                                                      attrs={'type': 'date',
                                                             'maxDate': datetime.now().date()}))