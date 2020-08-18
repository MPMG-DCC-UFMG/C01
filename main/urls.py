from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers

from . import views

# Router for API endpoints
api_router = routers.DefaultRouter()
api_router.register(r'crawlers', views.CrawlerViewSet)
api_router.register(r'instances', views.CrawlerInstanceViewSet)

urlpatterns = [
    path("", views.list_crawlers, name="list_crawlers"),
    path("crawlers/", views.list_crawlers, name="list_crawlers"),
    path("new/", views.create_crawler, name="create_crawler"),
    path("edit/<int:id>/", views.edit_crawler, name="edit_crawler"),
    path("delete/<int:id>/", views.delete_crawler, name="delete_crawler"),
    path("detail/<int:id>/", views.detail_crawler, name="detail_crawler"),
    path("crawlers/steps/", views.create_steps, name="create_steps"),
    path("monitoring/", views.monitoring, name="monitoring"),
    path("detail/run_crawl/<int:crawler_id>", views.run_crawl, name="run_crawl"),
    path("detail/stop_crawl/<int:crawler_id>", views.stop_crawl, name="stop_crawl"),
    path("tail_log_file/<str:instance_id>", views.tail_log_file, name="tail_log_file"),

    # Includes the API endpoints in the URLs
    url(r'^api/', include(api_router.urls)),
]
