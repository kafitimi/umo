from django.conf.urls import url

from disciplines import views
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    url(r'^add/$', views.DisciplineCreate.as_view(), name='disciplines_add'),
    url(r'(?P<pk>[0-9]+)/update/$', staff_member_required(views.DisciplineUpdate.as_view()), name='update'),
    url(r'^delete/$', staff_member_required(views.discipline_delete), name='delete'),
    url(r'(?P<pk>[0-9]+)/$', views.discipline_detail, name='detail'),
    url(r'^details_list/$', views.DisciplineDetailsList.as_view(), name='details_list'),
    url(r'^add_details/$', views.DetailsCreate.as_view(), name='details_add'),
    url(r'(?P<pk>[0-9]+)/update_details/$', views.DisciplineDetailsUpdate.as_view(), name='update_details'),
    url(r'^export/$', views.export_to_excel, name='export'),
    url(r'^excel/$', views.excel, name='excel'),
    url(r'(?P<pk>[0-9]+)/disciplines_list/$', views.list_disc, name='disciplines'),
    url(r'^all_disciplines/$', views.DisciplineList.as_view(), name='disciplines_list'),
    url(r'^dataforekran/$', views.get_data_for_ekran, name='dataforekran'),
    url(r'^subjects/$', views.subjects, name='subjects'),
    url(r'^$', views.list_teachers, name='disc_teachers'),
]
