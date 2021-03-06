from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required

from students import views

urlpatterns = [
    url(r'^$', views.StudentListView.as_view(), name='student_changelist'),
    url(r'^list$', views.StudentsList.as_view(), name='student_list'),
    url(r'^add$', views.StudentCreateView.as_view(), name='student_add'),
    url(r'^delete$', views.student_delete, name='student_delete'),
    url(r'^add$', views.StudentUpdateView.as_view(), name='student_edit'),
    url(r'^group_points$', views.group_points, name='group_points'),
    url(r'^profile$', views.student_profile, name='student_profile'),
    url(r'^my_scores$', views.ScoresView.as_view(), name='my_scores')
]
