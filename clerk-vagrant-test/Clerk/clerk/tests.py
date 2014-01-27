import datetime
from django.test import TestCase
from django.utils import timezone
import time

from clerk.models import Region, Service, Service_Type


def create_date(days=0, hours=0, minutes=0):
    return (timezone.now()
            + datetime.timedelta(days=days)
            + datetime.timedelta(hours=hours)
            + datetime.timedelta(minutes=minutes)
            )


class RegionFunctionTests(TestCase):

    def test_set_new_service_1(self):
        """This checks to make sure that you can set new services."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        serv2 = Service_Type.objects.create(name="morethings",
                                            pretty_name="More Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        loc.set_new_service(serv1, start_rate=0.5)
        loc.set_new_service(serv2, start_rate=0.5)
        self.assertEquals(loc.get_service_by_type_name("things").service_type,
                          serv1)

    def test_set_new_service_2(self):
        """Checks to make sure that the service added and the rate given,
        to it are the same as the ones returned."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        # starting rate given for the service is: 0.5
        loc.set_new_service(serv1, start_rate=0.5)
        self.assertEquals(loc.get_service_by_type_name("things").service_type,
                          serv1)
        # returned starting rate ought to be: 0.5
        rate = loc.get_service_by_type_name("things").get_current_rate()
        self.assertEquals(rate.rate, 0.5)

    def test_set_new_service_fail(self):
        """Checks that the function fail if given
           parameters of the wrong types."""
        loc = Region.objects.create(name="place")

        # wrong type:  service_type as number
        with self.assertRaises(TypeError):
            loc.set_new_service(service_type=5, start_rate=0.5)
        # wrong type:  start_rate as string
        with self.assertRaises(TypeError):
            loc.set_new_service(name="things", description="stuff",
                                start_rate="not a number")
        # wrong type:  start_rate as negative number
        with self.assertRaises(TypeError):
            loc.set_new_service(name="things", description="stuff",
                                start_rate=(-5))

    def test_get_service_by_type_name(self):
        """Checks that the services being added are the same
           as the ones being returned."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        serv2 = Service_Type.objects.create(name="things2",
                                            pretty_name="things 2",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        loc.set_new_service(serv1, start_rate=0.5)
        loc.set_new_service(serv2, start_rate=0.5)
        self.assertEquals(loc.get_service_by_type_name("things").service_type,
                          serv1)
        self.assertEquals(loc.get_service_by_type_name("things2").service_type,
                          serv2)

    def test_get_service_by_type_name_fail(self):
        """Checks that the function fails if given
           parameters of the wrong types."""
        loc = Region.objects.create(name="place")

        # wrong type: name as number
        with self.assertRaises(TypeError):
            loc.get_service_by_type_name(name=2)
        # invalid input:  name with disallowed characters
        with self.assertRaises(TypeError):
            loc.get_service_by_type_name(name="s p a c e ! ! ! !")


class ServiceFunctionTests(TestCase):

    def test_set_new_rate_default(self):
        """Tests that the default date value is indeed set to now,
           and that the newly created rate is now the current one."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        service = Service.objects.create(service_type=serv1, region=loc)
        service.set_new_rate(new_rate=0.3, start_date=create_date(-3))
        service.set_new_rate(new_rate=0.5)
        service.set_new_rate(new_rate=0.6, start_date=create_date(3))
        self.assertEquals(service.get_current_rate().rate, 0.5)

    def test_set_new_rate_fail(self):
        """Checks that set new rate fails on wrong types."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        service = Service.objects.create(service_type=serv1, region=loc)
        # wrong type: new_rate as negative
        with self.assertRaises(TypeError):
            service.set_new_rate(new_rate=(-3))
        # wrong type: start_date as string
        with self.assertRaises(TypeError):
            service.set_new_rate(new_rate=0.3, start_date="tomorrow")

    def test_get_current_rate(self):
        """Most recently set rate at default
           should always be the current rate."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        service = Service.objects.create(service_type=serv1, region=loc)
        for i in range(6):
            service.set_new_rate(new_rate=(float(i) / 10))
            time.sleep(1)
        self.assertEquals(service.get_current_rate().rate, 0.5)

    def test_get_current_rate_None(self):
        """Checks that none is being returned."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        service = Service.objects.create(service_type=serv1, region=loc)

        # None should be returned if no rate.
        rate = service.get_current_rate()
        self.assertEquals(rate, None)

    def test_get_rate_nearest_to(self):
        """Should always return the most recent rate that
           is less than or equal to the given date."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        service = Service.objects.create(service_type=serv1, region=loc)
        for i in range(-9, 0, 1):
            service.set_new_rate(new_rate=(float(-i) / 10),
                                 start_date=create_date(days=(i)))
        near_rate = service.get_rate_nearest_to(date=create_date(days=(-4),
                                                                 hours=(-1)))
        self.assertEquals(near_rate.rate, 0.5)
        near_rate = service.get_rate_nearest_to(date=create_date(days=(-7),
                                                                 hours=(-1)))
        self.assertEquals(near_rate.rate, 0.8)

    def test_get_rate_nearest_to_fail(self):
        """Checks that correct errors are being thrown."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        service = Service.objects.create(service_type=serv1, region=loc)

        # wrong type:  data as string
        with self.assertRaises(TypeError):
            service.get_rate_nearest_to(date="string")

    def test_get_rate_nearest_to_None(self):
        """Checks that none is being returned."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        service = Service.objects.create(service_type=serv1, region=loc)

        # None should be returned if no rate.
        rate = service.get_rate_nearest_to(date=timezone.now())
        self.assertEquals(rate, None)

    def test_get_next_future_rate(self):
        """Tests that the value returned is the nearest rate
           greater than now."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        service = Service.objects.create(service_type=serv1, region=loc)
        service.set_new_rate(new_rate=(1.1),
                             start_date=create_date(days=(11)))
        self.assertEquals(service.get_next_future_rate().rate, 1.1)
        for i in range(10, 3, -1):
            service.set_new_rate(new_rate=(float(i) / 10),
                                 start_date=create_date(days=(i)))
        self.assertEquals(service.get_next_future_rate().rate, 0.4)
        service.set_new_rate(new_rate=(0.25),
                             start_date=create_date(days=(2)))
        self.assertEquals(service.get_next_future_rate().rate, 0.25)

    def test_get_next_future_rate2(self):
        """Tests that the current rate is returned
        if there is no future rate."""
        serv1 = Service_Type.objects.create(name="things",
                                            pretty_name="Things",
                                            description="stuff")
        loc = Region.objects.create(name="place")
        service = Service.objects.create(service_type=serv1, region=loc)
        service.set_new_rate(new_rate=1.1)
        self.assertEquals(service.get_next_future_rate().rate, 1.1)
