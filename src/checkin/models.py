from django.db import models
from django.conf import settings
from django.urls import reverse

# We want to keep track of how many people are attending an avent at the WCC
# This could be lunch, a fitness class, a board meeting, etc.


class Category(models.Model):
    """What kind of event is this, lunch, meeting, games, etc?"""
    desc = models.CharField(
        max_length=50,
        unique=True,
        help_text="Enter a event category (e.g. Meeting, Game, Fitness, etc.)")
    active=models.BooleanField()
    created_date=models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.RESTRICT,
                                   related_name="category_created_by",
                                   blank=True,
                                   null=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.RESTRICT,
                                    related_name='category_modified_by',
                                    blank=True,
                                    null=True)

    def __str__(self):
        """String for representing the model object"""
        return self.desc

    def __get_absolute_url(self):
        """Returns the URL to access a detail record for this Category"""
        return reverse('category-detail', args=[str(self.id)])


class Event(models.Model):
    """ Events held at WCC (yoga, 4h meetings, lunch, etc.)"""
    desc = models.CharField(
        max_length=50,
        unique=True,
        help_text="Enter a event category (e.g. Meeting, Game, Fitness, etc.)")
    category = models.ForeignKey('Category',
                                 on_delete=models.RESTRICT,
                                 null=True)
    active = models.BooleanField()

    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.RESTRICT,
                                   related_name='event_created_by',
                                   blank=True,
                                   null=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.RESTRICT,
                                    related_name='event_modified_by',
                                    blank=True,
                                    null=True)

    def __str__(self):
        """String for representing the model object"""
        return self.desc

    def __get_absolute_url(self):
        """Returns the URL to access a detail record for this Category"""
        return reverse('category-detail', args=[str(self.id)])


class CheckIn(models.Model):
    """ This is where we count attendance. This is usually completed in kiosk mode, where a user is logged in to
     the kiosk and has limited options. We don't track the individual user, and one person can sign
     multiple people in at a time (for instance, a family of 5 attending a 4H meeting would checkin once for
     all five. """

    number_in_group = models.IntegerField()
    note = models.CharField(max_length=255,
                            blank=True,
                            null=True)

    event = models.ForeignKey('Event', on_delete=models.RESTRICT, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.RESTRICT,
                                   related_name='checkin_created_by',
                                   blank=True,
                                   null=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.RESTRICT,
                                    related_name='checkin_modified_by',
                                    blank=True,
                                    null=True)

    def __str__(self):
        """String for representing the model object"""
        return f"{self.event.desc}, {self.number_in_group}"

    def __get_absolute_url(self):
        """Returns the URL to access a detail record for this Category"""
        return reverse('category-detail', args=[str(self.id)])

