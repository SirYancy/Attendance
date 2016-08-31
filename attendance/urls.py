from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ClassView.as_view(), name='choose_class'),
    url(r'^signin/$', views.SignInView.as_view(), name='signin'),
    url(r'^tabulate/$', views.TabulateView.as_view(), name='tabulate'),
    url(r'^verify/$', views.verify, name='verify'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
]
