from clerk.models import Service, Rate, Region, Service_Type
from django import forms
from django.contrib.admin import widgets


def create_region_form():
    """Takes the 'RegionFormTemplate' and builds a new form with a
       list of services for the new region."""
    fields = RegionFormTemplate().fields
    for service in Service_Type.objects.all():
        key = str(service.name) + "_rate"
        label = "Starting rate for " + service.pretty_name
        fields[key] = forms.FloatField(label=label, required=True, min_value=0)
    # Using the type function here to create a new form allows dynamic forms
    # based on data in the Service_Type table. It just adds extra fields to the
    # below template form based on what Service_Types exist.
    form = type('CreateRegionForm', (RegionFormTemplate,), fields)
    return form


class RegionFormTemplate(forms.ModelForm):
    """A basic template to be used with the 'create_region_form'
       function to populate a list of service starting rates fields."""
    class Meta:
        model = Region
        fields = ('name', 'description')

    def save(self, **kwargs):
        if self.is_valid():
            name = str(self.cleaned_data['name'])
            description = str(self.cleaned_data['description'])
            region = Region.objects.create(name=name,
                                           description=description)
            region.save()
            # Sets a new service for each type based on the Service_types
            # table data, and uses the rates given in this form.
            for service in Service_Type.objects.all():
                # Constructs the same key as used by 'create_region_form()'
                # and uses it to pull the correct rate out.
                key = str(service.name) + "_rate"
                rate = float(self.cleaned_data[key])
                region.set_new_service(service, rate)
            return region

    def save_m2m(self):
        pass


class CreateServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('service_type', 'region')

    service_type = forms.ModelChoiceField(queryset=Service_Type.objects,
                                          empty_label=None)
    region = forms.ModelChoiceField(queryset=Region.objects,
                                    empty_label=None)
    start_rate = forms.FloatField(label="Starting rate:", min_value=0)

    def clean(self):
        cleaned_data = super(CreateServiceForm, self).clean()
        # if these fields are empty, then it will throw
        # standard 'required' field errors
        if 'service_type' and 'region' in cleaned_data:
            servtype = self.cleaned_data['service_type']
            region = self.cleaned_data['region']

            if (len(region.service_set.filter(service_type=servtype)) != 0):
                raise forms.ValidationError("Region already has this" +
                                            " service_type.")
        return cleaned_data

    def save(self, **kwargs):
        if self.is_valid():
            region = self.cleaned_data['region']
            service_type = self.cleaned_data['service_type']
            rate = float(self.cleaned_data['start_rate'])
            # Once the form has been confirmed valid the data is passed to the
            # internal model function that also creates and sets a new rate.
            service = region.set_new_service(service_type, rate)
            service.save()
            return service

    def save_m2m(self):
        pass


class EditServiceForm(forms.ModelForm):
    """Form for adding new rates to services."""
    class Meta:
        model = Service
        fields = []

    new_rate = forms.FloatField(label="Set a new rate:", min_value=0)
    date = forms.DateTimeField(label="Effective start date for new rate:",
                               widget=widgets.AdminSplitDateTime())

    def save(self, **kwargs):
        instance = self.instance
        if self.is_valid() and instance is not None:
            instance.set_new_rate(float(self.cleaned_data['new_rate']),
                                  self.cleaned_data['date'])
            instance.save()
            return instance

    def save_m2m(self):
        pass


class CreateRateForm(forms.ModelForm):
    class Meta:
        model = Rate
        fields = ('service',)
    rate = forms.FloatField(min_value=0)

    date = forms.DateTimeField(label="Effective start date for new rate:",
                               widget=widgets.AdminSplitDateTime())

    def save(self, **kwargs):
        if self.is_valid():
            service = self.cleaned_data['service']
            rate = float(self.cleaned_data['rate'])
            date = self.cleaned_data['date']
            # Once cleaned sets a new rate via internal model functions
            return service.set_new_rate(rate, date)

    def save_m2m(self):
        pass


class EditRateForm(forms.ModelForm):
    class Meta:
        model = Rate
    rate = forms.FloatField(min_value=0)
