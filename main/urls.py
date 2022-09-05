from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers

from main.views import (crawler_queue as crawler_queue_view,
                        crawler as crawler_view,
                        iframe_loader as iframe_loader_view,
                        process as process_view,
                        scheduler as scheduler_view,
                        steps as steps_view)

from main.api import (crawler_instance as crawler_instance_api,
                    crawler_queue as crawler_queue_api,
                    crawler as crawler_api,
                    crawling_status as crawling_status_api,
                    export_config as export_config_api,
                    log as log_api,
                    scheduler_task as scheduler_task_api,
                    screenshot as screenshot_api)

# Router for API endpoints
api_router = routers.DefaultRouter()
api_router.register(r'crawlers', crawler_api.CrawlerViewSet)
api_router.register(r'instances', crawler_instance_api.CrawlerInstanceViewSet)
api_router.register(r'crawler_queue', crawler_queue_api.CrawlerQueueViewSet)
api_router.register(r'tasks', scheduler_task_api.SchedulerTaskViewSet)

urlpatterns = [
    path('', crawler_view.list_crawlers, name='list_crawlers'),
    path('crawlers/', crawler_view.list_crawlers, name='list_crawlers'),
    path('new/', crawler_view.create_crawler, name='create_crawler'),
    path('edit/<int:crawler_id>/', crawler_view.edit_crawler, name='edit_crawler'),
    path('delete/<int:crawler_id>/', crawler_view.delete_crawler, name='delete_crawler'),
    path('detail/<int:crawler_id>/', crawler_view.detail_crawler, name='detail_crawler'),
    path('detail/run_crawl/<int:crawler_id>', crawler_view.run_crawl, name='run_crawl'),
    path('detail/stop_crawl/<int:crawler_id>', crawler_view.stop_crawl, name='stop_crawl'),

    path('crawlers/steps/', steps_view.create_steps, name='create_steps'),

    path('iframe/load', iframe_loader_view.load_iframe, name='load_iframe'),

    path('list_process', process_view.list_process, name='list_process'),

    path('crawler_queue/', crawler_queue_view.crawler_queue, name='crawler_queue'),
    path('crawler_queue/remove/<int:crawler_id>', crawler_queue_view.remove_crawl_request, name='remove_crawl_request'),

    path('scheduler/', scheduler_view.scheduler, name='scheduler'),

    path('tail_log_file/<str:instance_id>', log_api.tail_log_file, name='tail_log_file'),
    path('raw_log/<str:instance_id>', log_api.raw_log, name='raw_log'),

    path('download/files/found/<str:instance_id>/<int:num_files>', crawling_status_api.files_found, name='files_found'),
    path('download/file/success/<str:instance_id>', crawling_status_api.success_download_file, name='success_download_file'),
    path('download/file/error/<str:instance_id>', crawling_status_api.error_download_file, name='error_download_file'),
    path('download/pages/found/<str:instance_id>/<int:num_pages>', crawling_status_api.pages_found, name='pages_found'),
    path('download/page/success/<str:instance_id>', crawling_status_api.success_download_page, name='success_download_page'),
    path('download/page/error/<str:instance_id>', crawling_status_api.error_download_page, name='error_download_page'),
    path('download/page/duplicated/<str:instance_id>', crawling_status_api.duplicated_download_page, name='duplicated_download_page'),
    
    path('export_config/<str:instance_id>', export_config_api.export_config, name='export_config'),

    path('info/screenshots/<str:instance_id>/<int:page>', screenshot_api.view_screenshots, name='view_screenshots'),

    # Includes the API endpoints in the URLs
    url(r'^api/', include(api_router.urls)),
]
