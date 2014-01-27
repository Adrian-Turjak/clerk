from django.contrib import admin
from clerk.models import Rate, Service, Region, Service_Type
from clerk.forms import (CreateServiceForm, EditServiceForm,
                         CreateRateForm, create_region_form,
                         EditRateForm)


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created')
    readonly_fields = ('created',)
    search_fields = ['name', 'description']

    def get_actions(self, request):
        actions = super(RegionAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            del actions['delete_selected']
        return actions

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            # calls a function that dynamically creates a new form based on
            # the service_types in the database.
            return create_region_form()
        else:
            # returns the default autocreated form.
            return super(RegionAdmin, self).get_form(request, obj, **kwargs)


class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'pretty_name', 'description', 'created')
    search_fields = ['name', 'description', 'pretty_name']


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'region',
                    'get_current_rate', 'get_next_future_rate', 'created')
    readonly_fields = ('created',)
    list_filter = ['region']
    search_fields = ['service_type', 'region']

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return CreateServiceForm
        else:
            return EditServiceForm

    def get_actions(self, request):
        actions = super(ServiceAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            del actions['delete_selected']
        return actions

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('region', 'service_type', 'created',)
        else:
            return self.readonly_fields


class RateAdmin(admin.ModelAdmin):
    list_display = ('rate', 'date_effective', 'service',
                    'is_current', 'region', 'created')
    readonly_fields = ('created',)
    search_fields = ['region', 'service', 'service_type']
    list_filter = ['region', 'service_type']

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return CreateRateForm
        else:
            return EditRateForm

    def get_actions(self, request):
        actions = super(RateAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            del actions['delete_selected']
        return actions

    def has_change_permission(self, request, obj=None):
        # the readonly fields make this unnecessary but this stops
        # non-superusers from creating logs where nothing changes.
        if request.user.is_superuser:
            return True
        else:
            return request.method != 'POST'

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('rate', 'date_effective', 'service',
                    'service_type', 'region', 'created')
        else:
            return self.readonly_fields


class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    readonly_fields = admin.models.LogEntry._meta.get_all_field_names()
    list_filter = ['user', 'content_type', 'action_flag']
    search_fields = ['object_repr', 'change_message']
    list_display = ['action_time', 'user', 'content_type', 'action_flag',
                    'change_message']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # this statement ensures the user can VIEW, but not edit.
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Rate, RateAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Service_Type, ServiceTypeAdmin)
admin.site.register(admin.models.LogEntry, LogEntryAdmin)
