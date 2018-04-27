from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # login and regisration routes
    url(r'^$', views.index),
    url(r'^register/$', views.register),
    url(r'^login/$', views.login),
    url(r'^registeruser/$', views.registeruser),
    url(r'^dashboard/$', views.dashboard),
    url(r'^admin/$', views.login),
    # add and show routes
    url(r'^addrequest/$', views.addrequest),
    url(r'^request_add/$', views.request_add),
    url(r'^home/$', views.home),
    url(r'^search/$', views.search),
    url(r'^keywordsrch/$', views.keywordsrch),
    url(r'^logout/$', views.logout),
    url(r'^checkout$', views.checkout, name="checkout_page"),
    url(r'^adddoc/$', views.adddocument),
    # specific interaction routes
    url(r'^update/$', views.update),
    url(r'^userupdate/$', views.user_update),
    url(r'^request/(?P<req_id>\d+)$', views.show_request),
    url(r'^updatereq/(?P<req_id>\d+)$', views.update_request),
    url(r'^updateusr/(?P<usr_id>\d+)$', views.update_user),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)