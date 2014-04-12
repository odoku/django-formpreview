from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'polls.views.index', name='index'),
    url(r'^poll/form$', 'polls.views.form', name='form'),
    url(r'^poll/create$', 'polls.views.create', name='create'),
    url(r'^poll/update/(?P<pk>\d+)$', 'polls.views.update', name='update'),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += patterns(
    '',
    url(
        r'^media/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}
    )
)
