from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin


urlpatterns = patterns('',
    url(r'', include('omaha.urls')),
    url(r'', include('crash.urls')),
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
