from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from . import views

# Router for API endpoints
api_router = routers.DefaultRouter()
api_router.register(r'crawlers', views.CrawlerViewSet)
api_router.register(r'instances', views.CrawlerInstanceViewSet)
api_router.register(r'crawler_queue', views.CrawlerQueueViewSet)
api_router.register(r'tasks', views.TaskViewSet)

urlpatterns = [
    path("", views.list_crawlers, name="list_crawlers"),
    path("crawlers/", views.list_crawlers, name="list_crawlers"),
    path('grouped_crawlers', views.list_grouped_crawlers, name="list_grouped_crawlers"),
    path("new/", views.create_crawler, name="create_crawler"),
    path("new_group/", views.create_grouped_crawlers, name="create_grouped_crawlers"),
    path("edit/<int:crawler_id>/", views.edit_crawler, name="edit_crawler"),
    path("edit_group/<int:id>/", views.edit_grouped_crawlers, name="edit_grouped_crawlers"),
    path("delete/<int:crawler_id>/", views.delete_crawler, name="delete_crawler"),
    path("detail/<int:crawler_id>/", views.detail_crawler, name="detail_crawler"),
    path("crawlers/steps/", views.create_steps, name="create_steps"),
    path("monitoring/", views.monitoring, name="monitoring"),
    path("detail/run_crawl/<int:crawler_id>", views.run_crawl, name="run_crawl"),
    path("detail/stop_crawl/<int:crawler_id>", views.stop_crawl, name="stop_crawl"),
    path("tail_log_file/<str:instance_id>", views.tail_log_file, name="tail_log_file"),
    path("raw_log/<str:instance_id>", views.raw_log, name="raw_log"),
    
    path("download/files/found/<str:instance_id>/<int:num_files>", views.files_found, name="files_found"),
    path("download/file/success/<str:instance_id>", views.success_download_file, name="success_download_file"),
    path("download/file/previously_crawled/<str:instance_id>", views.previously_crawled_file, name="previously_crawled_file"),
    path("download/file/error/<str:instance_id>", views.error_download_file, name="error_download_file"),
    
    path("download/pages/found/<str:instance_id>/<int:num_pages>", views.pages_found, name="pages_found"),
    path("download/page/success/<str:instance_id>", views.success_download_page, name="success_download_page"),
    path("download/page/previously_crawled/<str:instance_id>", views.previously_crawled_page, name="previously_crawled_page"),
    path("download/page/error/<str:instance_id>", views.error_download_page, name="error_download_page"),
    path("download/page/duplicated/<str:instance_id>", views.duplicated_download_page, name="duplicated_download_page"),
    
    path("export_config/<str:instance_id>", views.export_config, name="export_config"),


    path("info/screenshots/<str:instance_id>/<int:page>", views.view_screenshots, name="view_screenshots"),

    path("iframe/load", views.load_iframe, name="load_iframe"),

    path('list_process', views.list_process, name="list_process"),
    path('get_crawlers_from_same_group/<int:crawler_id>', views.get_crawlers_from_same_group, name="get_crawlers_from_same_group"),

    path("crawler_queue/", views.crawler_queue, name="crawler_queue"),
    path("crawler_queue/remove/<int:crawler_id>", views.remove_crawl_request_view, name="remove_crawl_request"),

    path("scheduler/", views.scheduler, name="scheduler"),

    # Includes the API endpoints in the URLs
    url(r'^api/', include(api_router.urls)),
]
