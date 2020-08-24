from django.urls import path
from . import views

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
    path("detail/stop_crawl/<int:crawler_id>/<int:instance_id>", views.stop_crawl, name="stop_crawl"),
    path("tail_log_file/<str:crawler_id>/<str:instance_id>", views.tail_log_file, name="tail_log_file"),
]
