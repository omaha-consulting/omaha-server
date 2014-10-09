# coding: utf8

from django.contrib import admin
from models import Channel, Platform, Application, Version, Action


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'id',)


class ActionInline(admin.StackedInline):
    model = Action
    extra = 0


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    inlines = (ActionInline,)
    list_display = ('app', 'version', 'channel', 'platform',)
    list_filter = ('channel__name', 'platform__name', 'app__name',)
    readonly_fields = ('file_hash',)
