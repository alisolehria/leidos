from django.conf.urls import include, url
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"
urlpatterns = [
    url(r'^$', views.login_user, name='login'),
    url(r'logout/$', views.logout_user, name='logoutUser'),




]
