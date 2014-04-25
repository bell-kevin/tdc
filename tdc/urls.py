from django.conf.urls import patterns, include, url

from django.contrib import admin
from counter.api import router

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tdc.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include(admin.site.urls)),
    url(r'^', include("massadmin.urls")),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
