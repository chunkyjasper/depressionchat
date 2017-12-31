"""depressionchatrestapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from rest_framework import routers
from apiauth import views
from django.contrib import admin
from django.urls import path


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^users/authenticate', views.login),
    url(r'^users/register', views.register),
    url(r'^api-apiauth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^users/(?P<user_id>\d+)/friends$', views.friends),
    url(r'^users/(?P<user1_id>\d+)/(?P<user2_id>\d+)/messages$', views.messages),
    ]

urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]