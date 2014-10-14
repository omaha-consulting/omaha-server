from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from omaha.views import UpdateView, SparkleView


urlpatterns = patterns('',
    url(r'^service/update2$', UpdateView.as_view(), name='update'),
    url(r'^sparkle/(?P<app_name>[\w-]+)/(?P<channel>[\w-]+)/appcast.xml$',
        SparkleView.as_view(), name='sparkle_appcast'),
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
