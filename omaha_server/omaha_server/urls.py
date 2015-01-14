from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from rest_framework import routers

import omaha.api
import sparkle.api


router = routers.DefaultRouter()
router.register(r'app', omaha.api.AppViewSet)
router.register(r'platform', omaha.api.PlatformViewSet)
router.register(r'channel', omaha.api.ChannelViewSet)
router.register(r'omaha/version', omaha.api.VersionViewSet)
router.register(r'sparkle/version', sparkle.api.SparkleVersionViewSet)


urlpatterns = patterns('',
    url(r'', include('omaha.urls')),
    url(r'', include('crash.urls')),
    url(r'^sparkle/', include('sparkle.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )
    except ImportError:
        pass
