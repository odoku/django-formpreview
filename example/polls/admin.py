from django.contrib import admin

from models import Poll


class PollAdmin(admin.ModelAdmin):
    pass
admin.site.register(Poll, PollAdmin)
