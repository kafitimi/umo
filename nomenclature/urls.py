from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required

from nomenclature import views

admin.autodiscover()
urlpatterns = [
    url(r'^upload_file/$', views.upload_file, name='upload_file'),
    url(r'^select_semester/$', views.select_semester, name='select_semester'),
    url(r'^set_teachers/$', views.vuborka, name='set_teachers'),
    url(r'^set_teachers/done/$', views.subjects_save, name='set_teachers_done'),
    url(r'^rup/$', views.EduProgListView.as_view(), name='rup'),
    url(r'^nomenclature_disciplines/$', views.nomenclature_discipline, name='nomenclature_disciplines')
]