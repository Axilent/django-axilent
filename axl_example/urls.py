from django.conf.urls.defaults import *

urlpatterns = patterns('axl_example.views',
    ('^$','index'),
    ('^article/(?P<article_id>\d+)/$','article'),
)

