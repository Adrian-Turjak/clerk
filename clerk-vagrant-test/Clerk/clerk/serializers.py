from rest_framework import serializers
from clerk.models import Region, Service, Rate, Service_Type
import re


class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ('name', 'description', 'created')

    def validate_name(self, attrs, source):

        if re.match(r'^[A-Za-z0-9_]+$', attrs[source]):
            size = len(Region.objects.filter(name__exact=attrs[source]))
            if size == 0:
                return attrs
            else:
                raise serializers.ValidationError("Region with that name " +
                                                  "already exists.")
        else:
            raise serializers.ValidationError("Must contain only " +
                                              "alphanumeric characters or '_'")


class ServiceTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service_Type
        fields = ('name', 'pretty_name', 'description', 'created')

    def validate_name(self, attrs, source):
        if re.match(r'^[A-Za-z0-9_]+$', attrs[source]):
            size = len(Region.objects.filter(name__exact=attrs[source]))
            if size == 0:
                return attrs
            else:
                raise serializers.ValidationError("Service type with " +
                                                  "that name already exists.")
        else:
            raise serializers.ValidationError("Must contain only " +
                                              "alphanumeric characters or '_'")

    def validate_pretty_name(self, attrs, source):
        size = len(Region.objects.filter(name__exact=attrs[source]))
        if size == 0:
            return attrs
        else:
            raise serializers.ValidationError("Service type with " +
                                              "that pretty_name " +
                                              "already exists.")


class ServiceSerializer(serializers.ModelSerializer):
    region = serializers.Field(source='region.name')
    service_type = serializers.Field(source='service_type.name')

    class Meta:
        model = Service
        fields = ('service_type', 'created', 'region')

    def validate_name(self, attrs, source):
        if re.match(r'^[A-Za-z0-9_]+$', attrs[source]):
            size = len(Service.objects.filter(name__exact=attrs[source]))
            if size == 0:
                return attrs
            else:
                raise serializers.ValidationError("Region with that name " +
                                                  "already exists.")
        else:
            raise serializers.ValidationError("Must be alphanumeric or '_' ")


class RateSerializer(serializers.ModelSerializer):
    service = serializers.Field(source='service.service_type')
    region = serializers.Field(source='region.name')

    class Meta:
        model = Rate
        fields = ('rate', 'date_effective', 'created', 'service', 'region')
