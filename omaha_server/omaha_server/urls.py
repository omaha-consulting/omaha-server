from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from omaha.views import UpdateView


urlpatterns = patterns('',
    url(r'^api/update/$', UpdateView.as_view(), name='update'),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )
    except ImportError:
        pass
