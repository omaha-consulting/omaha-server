from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

from rest_framework import routers

import omaha.views
import omaha.api
import sparkle.api
import crash.api
import feedback.api


router = routers.DefaultRouter()
router.register(r'app', omaha.api.AppViewSet)
router.register(r'data', omaha.api.DataViewSet)
router.register(r'platform', omaha.api.PlatformViewSet)
router.register(r'channel', omaha.api.ChannelViewSet)
router.register(r'omaha/version', omaha.api.VersionViewSet)
router.register(r'action', omaha.api.ActionViewSet)
router.register(r'sparkle/version', sparkle.api.SparkleVersionViewSet)
router.register(r'symbols', crash.api.SymbolsViewSet)
router.register(r'crash_report', crash.api.CrashViewSet)
router.register(r'feedback', feedback.api.FeedbackViewSet)
router.register(r'statistics/months', omaha.api.StatisticsMonthsListView, 'api-statistics-months')

urlpatterns = [
    url(r'', include('omaha.urls')),
    url(r'', include('crash.urls')),
    url(r'', include('feedback.urls')),
    url(r'^healthcheck/', include('healthcheck.urls')),
    url(r'^sparkle/', include('sparkle.urls')),
]

if settings.IS_PRIVATE:
    urlpatterns += [
        url(r'', include('downloads.urls')),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^api/statistics/channels/(?P<app_name>[a-zA-Z0-9_ ]+)/$', omaha.api.StatisticsChannelsView.as_view(),
            name="api-statistics-channels"),
        url(r'^api/statistics/versions/(?P<app_name>[a-zA-Z0-9_ ]+)/$', omaha.api.StatisticsVersionsView.as_view(),
            name="api-statistics-versions"),
        url(r'^api/statistics/months/(?P<app_name>[a-zA-Z0-9_ ]+)/$', omaha.api.StatisticsMonthsDetailView.as_view(),
            name="api-statistics-months-detail"),
        url(r'^api/statistics/months/$', omaha.api.StatisticsMonthsListView.as_view(), name="api-statistics-months-list"),
        url(r'^api/version', omaha.api.ServerVersionView.as_view(), name='api-version'),
        url(r'^api/', include(router.urls)),
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        url(r'select2_userid_filter/', omaha.views.FilterByUserIDResponseView.as_view(),
            name='select2_userid_filter'),
    ]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
