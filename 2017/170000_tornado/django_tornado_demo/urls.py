from django.conf.urls import *
from views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = [
    url(r'^hello-django', hello),
]


# urlpatterns = patterns('',
#                        (r'^hello-django', 'hello'),
#     # Example:
#     # (r'^testsite/', include('testsite.foo.urls')),

#     # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
#     # to INSTALLED_APPS to enable admin documentation:
#     # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

#     # Uncomment the next line to enable the admin:
#     # (r'^admin/', include(admin.site.urls)),
# )
