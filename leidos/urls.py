from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^adminSite/', admin.site.urls),
    url(r'^', include('accounts.urls')),
    url(r'^admin/', include('adminUser.urls')),
    url(r'^pm/', include('projectManager.urls')),
    url(r'^employee/', include('employee.urls')),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
]

