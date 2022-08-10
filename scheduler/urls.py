from django.urls import include, path
from django.urls import path

from django.conf.urls import url
from rest_framework import routers
from scheduler.views import TaskViewSet

api_router = routers.DefaultRouter()
api_router.register(r'', TaskViewSet)

urlpatterns = [    
    url(r'^tasks/', include(api_router.urls)),
]
