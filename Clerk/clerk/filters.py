from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class IsCurrentListFilter(admin.SimpleListFilter):
    title = _('is current')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'decade'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('True', _('true')),
            ('False', _('false')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        print "words!! "

        if self.value() == 'False':
            return queryset.filter(current=False)
        else:
            return queryset.filter(current=True)