from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_crawlers, name='list_crawlers'),
    
    # crawlers
    path('new/', views.create_crawler, name='create_crawler'),
    path('crawlers/', views.list_crawlers, name='list_crawlers'),
    path('crawlers/steps/', views.create_steps, name='create_steps'),
    
    path('detail/<int:crawler_id>/', views.detail_crawler, name='detail_crawler'),
    path('detail/run_crawl/<int:crawler_id>', views.run_crawl, name='run_crawl'),
    path('detail/stop_crawl/<int:crawler_id>', views.stop_crawl, name='stop_crawl'),
    
    path('edit/<int:crawler_id>/', views.edit_crawler, name='edit_crawler'),
    path('edit_group/<int:id>/', views.edit_grouped_crawlers, name='edit_grouped_crawlers'),
    
    path('delete/<int:crawler_id>/', views.delete_crawler, name='delete_crawler'),
    
    # grouped crawlers
    path('new_group/', views.create_grouped_crawlers, name='create_grouped_crawlers'),
    path('grouped_crawlers', views.list_grouped_crawlers, name='list_grouped_crawlers'),
    
    # misc
    path('monitoring/', views.monitoring, name='monitoring'),
    path('iframe/load', views.load_iframe, name='load_iframe'),
    path('list_process', views.list_process, name='list_process'),

    # crawler queue
    path('crawler_queue/', views.crawler_queue, name='crawler_queue'),
    path('crawler_queue/remove/<int:crawler_id>', views.remove_crawl_request_view, name='remove_crawl_request'),

    # scheduler
    path('scheduler/', views.scheduler, name='scheduler'),
]