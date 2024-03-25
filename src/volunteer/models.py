from django.db import models
from django.conf import settings
from django.urls import reverse

# Create your models here.
# we want to be able to track time and mileage for our volunteers.
# We need a table to store volunteer opportunities (driver, cook, board member, etc.)


class Task(models.Model):
    """What kind of task is this, lunch, delivering meals, board member, stuffing envelopes? """
    desc = models.CharField(
        max_length=50,
        unique=True,
        help_text="Enter a task description (e.g. meal prep, delivering meals, clerical, etc.)")
    active=models.BooleanField()
    created_date=models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.RESTRICT,
                                   related_name="task_created_by",
                                   blank=True,
                                   null=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.RESTRICT,
                                    related_name='task_modified_by',
                                    blank=True,
                                    null=True)

    def __str__(self):
        """String for representing the model object"""
        return self.desc

    def __get_absolute_url(self):
        """Returns the URL to access a detail record for this Task"""
        return reverse('task-detail', args=[str(self.id)])


class Entry(models.Model):
    """ This is where we track hours, mileage, task type, and notes"""
    volunteer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.RESTRICT,
                                  related_name="volunteer",
                                  blank=False,
                                  null=False)
    volunteer_task = models.ForeignKey(Task,
                                       on_delete=models.RESTRICT,
                                       related_name="volunteer_task",
                                       blank=True,
                                       null=True)
    volunteer_date = models.DateTimeField(blank=True, null=True)
    hours = models.DecimalField(decimal_places=2, max_digits=4)
    mileage = models.DecimalField(decimal_places=2, max_digits=4)
    notes = models.CharField(
        max_length=255,
        unique=False,
        null=True,
        blank=True,
        help_text="Did something noteworthy happen?")

    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.RESTRICT,
                                   related_name="entry_created_by",
                                   blank=True,
                                   null=True)

    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.RESTRICT,
                                    related_name='entry_modified_by',
                                    blank=True,
                                    null=True)

    def __str__(self):
        """String for representing the model object"""
        return f"{self.volunteer}, {self.volunteer_task}, {self.hours}, {self.mileage}"

    def __get_absolute_url(self):
        """Returns the URL to access a detail record for this Task"""
        return reverse('entry-detail', args=[str(self.id)])


