from clerk.models import Region, Service, Service_Type
from clerk.serializers import (RegionSerializer, ServiceSerializer,
                               RateSerializer, ServiceTypeSerializer)
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework import permissions
import re


# Helper Methods:

def get_service_type(name):
    try:
        return Service_Type.objects.get(name__exact=name)
    except Service_Type.DoesNotExist:
        raise Http404


def get_region(name):
    try:
        return Region.objects.get(name__exact=name)
    except Region.DoesNotExist:
        raise Http404


def get_service(name, serv_type):
    try:
        loc = get_region(name)
        return loc.get_service_by_type_name(type=str(serv_type))
    except Service.DoesNotExist:
        raise Http404


class ServiceTypeList(APIView):
    """List all Service Types, or create a new one."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        servTypes = Service_Type.objects.all()
        serializer = ServiceTypeSerializer(servTypes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        if request.user.is_superuser:
            serializer = ServiceTypeSerializer(data=request.DATA)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ServiceTypeDetail(APIView):
    """Retrieve or update a Service Type instance."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, name, format=None):
        servType = get_service_type(name)
        serializer = ServiceTypeSerializer(servType)
        return Response(serializer.data)

    def put(self, request, name, format=None):
        if request.user.is_superuser:
            servType = get_service_type(name)
            serializer = ServiceTypeSerializer(servType, data=request.DATA)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, name, format=None):
        if request.user.is_superuser:
            servType = get_service_type(name)
            serializer = ServiceTypeSerializer(servType, data=request.DATA,
                                               partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class RegionList(APIView):
    """List all Regions, or create a new Region."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        regions = Region.objects.all()
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # This builds a list of additional data that is needed based
        # on service types
        required = dict()
        for service in Service_Type.objects.all():
            keyword = str(service.name) + "_rate"
            required[keyword] = service

        errors = dict()
        rates = dict()

        for keyword in required.keys():
            # ensure the required parameters are there:
            if keyword in request.DATA:
                # ensure it is valid number:
                if re.match(r'^\d+(\.\d)?\d*$', str(request.DATA[keyword])):
                    rates[keyword] = float(request.DATA[keyword])
                else:
                    errors[keyword] = ["Must be a valid decimal number."]
            else:
                errors[keyword] = ["Is a required parameter."]

        # We then build the region and check that it's data is correct.
        serializer = RegionSerializer(data=request.DATA)
        # also check we don't have additonal errors
        if serializer.is_valid() and not len(errors) > 0:
            region = serializer.save()

            # once we know all the data is there and valid, we begin creating
            # all given service types at the new region:
            for keyword in required.keys():
                rate = rates[keyword]
                region.set_new_service(required[keyword], rate)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        errors = dict(errors.items() + serializer.errors.items())
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class RegionDetail(APIView):
    """Retrieve or update a region instance."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, name, format=None):
        region = get_region(name)
        serializer = RegionSerializer(region)
        return Response(serializer.data)

    def put(self, request, name, format=None):
        region = get_region(name)
        serializer = RegionSerializer(region, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, name, format=None):
        region = get_region(name)
        serializer = RegionSerializer(region, data=request.DATA,
                                        partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceList(APIView):
    """List all services, or create a new services."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, name, format=None):
        services = get_region(name).service_set.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)


class ServiceDetail(APIView):
    """Retrieve or update a service instance."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, name, serv_type, format=None):
        service = get_service(name, serv_type)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)


class RateList(APIView):
    """List all Rates, or create a new rate."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, name, serv_type, format=None):
        rates = get_service(name, serv_type).rate_set.all()
        serializer = RateSerializer(rates, many=True)
        return Response(serializer.data)

    def post(self, request, name, serv_type, format=None):
        service = get_service(name, serv_type)
        data = request.DATA
        date = None

        if 'date' in data:
            try:
                date = datetime.strptime(data['date'], "%d/%m/%Y")
            except ValueError:
                return Response({'date': [u'Must be a valid date' +
                                          'in the format: dd/mm/yyyy']},
                                status=status.HTTP_400_BAD_REQUEST)

        if 'rate' in data:
            rate = data['rate']
            if not re.match(r'^\d+(\.\d)?\d*$', rate):
                return Response({'rate': [u'Must be a valid number >= zero']},
                                status=status.HTTP_400_BAD_REQUEST)

            if date is None:
                service.set_new_rate(float(rate))
                return Response({'rate': rate, 'date': datetime.now()},
                                status=status.HTTP_201_CREATED)
            else:
                service.set_new_rate(float(rate), date)
                return Response({'rate': rate, 'date': date},
                                status=status.HTTP_201_CREATED)

        else:
            return Response({'rate': [u'is a required parameter']},
                            status=status.HTTP_400_BAD_REQUEST)


class RateCurrent(APIView):
    """Retrieve the 'current' rate instance."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, name, serv_type, format=None):
        rate = get_service(name, serv_type).get_current_rate()
        serializer = RateSerializer(rate)
        return Response(serializer.data)


class RateFuture(APIView):
    """Retrieve the next up coming rate instance."""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, name, serv_type, format=None):
        rate = get_service(name, serv_type).get_next_future_rate()
        serializer = RateSerializer(rate)
        return Response(serializer.data)
