from django.db import models
from django.utils import timezone
from datetime import datetime
from django.core import validators
from django.contrib.contenttypes.models import ContentType as ct
import re
from django.contrib.admin.models import LogEntry, ADDITION

noSpaces = validators.RegexValidator(regex='^[A-Za-z0-9_]+$',
                                     message="Must contain only " +
                                     "alphanumeric characters or '_'")


class Region(models.Model):
    """Representation of a server region
       and all the services available at the
       region with given rates."""
    name = models.CharField(max_length=200, validators=[noSpaces],
                            unique=True)
    description = models.TextField()
    created = models.DateTimeField(default=timezone.now, editable=False)

    def set_new_service(self, service_type, start_rate):
        """Adds a new service.
           - name = string
           - description = string
           - start_rate = any positive number or zero """

        # check input types, throw typeError if incorrect:
        if not isinstance(service_type, Service_Type):
            raise TypeError("service_type must be a Service_Type object")
        elif (not isinstance(start_rate, (int, long, float, complex))
              or start_rate < 0):
            raise TypeError("start_rate must be a positive number, or zero")

        if (len(self.service_set.filter(service_type=service_type)) == 0):
            new_service = Service(service_type=service_type, region=self)
            new_service.save()
            new_service.set_new_rate(start_rate)
            LogEntry.objects.log_action(
                user_id=1,  # somewhat unsafe assumption, that admin is user 1.
                content_type_id=ct.objects.get_for_model(Service).pk,
                object_id=new_service.pk,
                object_repr=new_service.__unicode__(),
                action_flag=ADDITION,
                change_message="New service created @ " + self.__unicode__() +
                               ", automatically.")
            return new_service
        else:
            raise AttributeError("service with this name already exists.")

    def get_service_by_type_name(self, type):
        """Return the service of with given type at this region.
           - name = string """
        # check input types, throw typeError if incorrect:
        if not isinstance(type, str) or not re.match(r'^[A-Za-z0-9_]+$', type):
            raise TypeError("type must be a string")
        service_type = Service_Type.objects.get(name=type)
        return self.service_set.get(service_type=service_type)

    def __unicode__(self):
        return self.name


class Service_Type(models.Model):
    name = models.CharField(max_length=200, validators=[noSpaces],
                            unique=True)
    pretty_name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    created = models.DateTimeField(default=timezone.now, editable=False)

    def __unicode__(self):
        return self.pretty_name


class Service(models.Model):
    """Service representation.
       Connects to all rates, past and future.
       """
    service_type = models.ForeignKey(Service_Type)
    created = models.DateTimeField(default=timezone.now, editable=False)
    region = models.ForeignKey(Region)

    def get_current_rate(self):
        """Returns the most recent rate that was effective from a date
           that is less than or equal to now."""
        now = timezone.now()
        rates = self.rate_set.filter(date_effective__lte=
                                     now).order_by('-date_effective')
        if len(rates) > 0:
            return rates[0]
        else:
            return None
    get_current_rate.short_description = "Current rate"

    def set_new_rate(self, new_rate, start_date=None):
        """Sets a new rate. If no start_date is given
           now will be used. Default value will mean given rate is now current.
           - new_rate = none negative number, can be zero
           - start_date = datetime object, can be in the future"""

        # Set start_date default if one is not given:
        if start_date is None:
            start_date = timezone.now()

        # check input types, throw typeError if incorrect:
        if type(start_date) != datetime:
            raise TypeError("start_date must be a datetime object " +
                            "unless using default.")
        elif (not isinstance(new_rate, (int, long, float, complex))
              or new_rate < 0):
            raise TypeError("new_rate must a positive number or zero")

        new_rate_object = Rate(rate=new_rate, date_effective=start_date,
                               service=self, service_type=self.service_type,
                               region=self.region)
        new_rate_object.save()
        LogEntry.objects.log_action(
            user_id=1,  # somewhat unsafe assumption, that admin is user 1.
            content_type_id=ct.objects.get_for_model(Rate).pk,
            object_id=new_rate_object.pk,
            object_repr=new_rate_object.__unicode__(),
            action_flag=ADDITION,
            change_message="New rate created for " + self.__unicode__() +
                           ", automatically.")
        return new_rate_object

    # this function is currently unused, but should be bound to the rest API
    def get_rate_nearest_to(self, date):
        """Returns the most recent rate that is less than or equal to
           the given date.
           - data = datetime object, can be in the future"""
        # check input types, throw typeError if incorrect:
        if type(date) != datetime:
            raise TypeError("date must be a datetime object.")

        rates = self.rate_set.filter(date_effective__lte=
                                     date).order_by('-date_effective')
        for i in range(len(rates)):
            if rates[i].date_effective <= date:
                return rates[i]
        return None

    def get_next_future_rate(self):
        """Returns the next rate after the current one.
           Returns current rate if no future ones."""
        now = timezone.now()
        rates = self.rate_set.filter(date_effective__gt=
                                     now).order_by('date_effective')
        if len(rates) > 0:
            return rates[0]
        else:
            return self.get_current_rate()
    get_next_future_rate.short_description = "Next future rate"

    def __unicode__(self):
        return (self.service_type.name + " @ "
                + self.region.name)


class Rate(models.Model):
    rate = models.FloatField()
    date_effective = models.DateTimeField('date_effective',
                                          default=timezone.now)
    created = models.DateTimeField(default=timezone.now, editable=False)

    service = models.ForeignKey(Service)
    service_type = models.ForeignKey(Service_Type)
    region = models.ForeignKey(Region)

    def is_current(self):
        return self.service.get_current_rate().pk == self.pk
    is_current.boolean = True

    def __unicode__(self):
        return str(self.rate)
