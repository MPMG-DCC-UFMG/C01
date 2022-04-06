from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from . import views

# Router for API endpoints
api_router = routers.DefaultRouter()
api_router.register(r'crawlers', views.CrawlerViewSet)
api_router.register(r'instances', views.CrawlerInstanceViewSet)
api_router.register(r'crawler_queue', views.CrawlerQueueViewSet)

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
    path("export_config/<str:instance_id>", views.export_config, name="export_config"),


    path("info/form_fields", views.load_form_fields, name="load_form_fields"),
    path("info/screenshots/<str:instance_id>/<int:page>", views.view_screenshots, name="view_screenshots"),

    path("iframe/load", views.load_iframe, name="load_iframe"),

    path('list_process', views.list_process, name="list_process"),

    path("crawler_queue/", views.crawler_queue, name="crawler_queue"),
    path("crawler_queue/remove/<int:crawler_id>", views.remove_crawl_request_view, name="remove_crawl_request"),
    path("crawler_queue/run_next", views.run_next_crawl_requests_view, name="run_next_crawl_request"),

    # Includes the API endpoints in the URLs
    url(r'^api/', include(api_router.urls)),
]
