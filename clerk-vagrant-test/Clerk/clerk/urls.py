from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from clerk import views

# API endpoints
urlpatterns = format_suffix_patterns(patterns('',
    url(r'^regions/(?P<name>\w+)/services/(?P<serv_type>\w+)/rates/current/$',
        views.RateCurrent.as_view()),
    url(r'^regions/(?P<name>\w+)/services/(?P<serv_type>\w+)/rates/future/$',
        views.RateFuture.as_view()),
    url(r'^regions/(?P<name>\w+)/services/(?P<serv_type>\w+)/rates/$',
        views.RateList.as_view()),
    url(r'^regions/(?P<name>\w+)/services/(?P<serv_type>\w+)/$',
        views.ServiceDetail.as_view()),
    url(r'^regions/(?P<name>\w+)/services/$',
        views.ServiceList.as_view()),
    url(r'^regions/(?P<name>\w+)/$',
        views.RegionDetail.as_view()),
    url(r'^regions/$', views.RegionList.as_view()),
    url(r'^service_types/(?P<name>\w+)/$', views.ServiceTypeDetail.as_view()),
    url(r'^service_types/$', views.ServiceTypeList.as_view())
))

# Login and logout views for the browsable API
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)
