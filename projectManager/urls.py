from django.conf.urls import url
from . import views

app_name = "projectManager"

urlpatterns = [
    url(r'alerttab/$', views.alerttab_View, name='alertTab'),
    url(r'profile/$', views.profile_View, name='profile'),
    url(r'currentProjects/(?P<staff_id>[0-9]+)/$', views.currentprojectsget_View, name='currentprojectsget'),
    url(r'upcomingProjects/(?P<staff_id>[0-9]+)/$', views.upcomingprojectsget_View, name='upcomingprojectsget'),
    url(r'completedProjects/(?P<staff_id>[0-9]+)/$', views.completedprojectsget_View, name='completedprojectsget'),
    url(r'projectlist/$', views.projectlist_View, name='projectlist'),
    url(r'project/(?P<project_id>[0-9]+)/$', views.projectprofile_View, name='projectprofile'),
    url(r'myprojects/$', views.myprojects_View, name='myprojects'),
    url(r'staff/(?P<staff_id>[0-9]+)/$',views.staffprofile_View, name='staffprofile'),
    url(r'alerts/$', views.alert_View, name='alerts'),
    url(r'requestProject/$', views.requestproject_View, name='requestproject'),
    url(r'addSkill/(?P<project_id>[0-9]+)/$', views.addpskill_View, name='addskill'),
    url(r'addStaff/(?P<project_id>[0-9]+)/$', views.addpstaff_View, name='addstaff'),
    url(r'requestholiday/$', views.holiday_View, name='holidayrequest'),
    url(r'myrequests/$', views.requests_View, name='myrequests'),
    url(r'matchmaking/$', views.matchmakingSelect_View, name='matchmaking'),
    url(r'matchmaking/(?P<project_id>[0-9]+)/$', views.matchmaking_View, name='matchmakingProject'),
    url(r'messageBoard/$', views.messageBoard_View, name='message'),
    url(r'comments/(?P<board_id>[0-9]+)/$', views.comments_View, name='comments'),
    url(r'commentBox/(?P<board_id>[0-9]+)/$', views.comments_Box, name='commentsBox'),
    url(r'refresh/$', views.refresh_View, name='refresh'),
    url(r'report/(?P<project_id>[0-9]+)/$', views.report_View, name='report'),

]
