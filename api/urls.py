from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from django.shortcuts import redirect
from . import views

app_name = 'api'

# Router for API endpoints
# api_router = routers.DefaultRouter()
# api_router.register(r'crawlers', views.CrawlerViewSet)
# api_router.register(r'instances', views.CrawlerInstanceViewSet)
# api_router.register(r'crawler_queue', views.CrawlerQueueViewSet)
# api_router.register(r'tasks', views.TaskViewSet)

list_and_create_actions = {'get': 'list', 'post': 'create'}
retrieve_update_and_destroy_actions = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}
all_actions = {'get': 'list', 'post': 'create', 'put': 'update', 'delete': 'destroy'}
only_list_action = {'get': 'list'}
only_retrieve_action = {'get': 'retrieve'}

urlpatterns = [
    path('', lambda request: redirect('api:swagger-ui', permanent=True)),
    
    path('crawler/', views.CrawlerViewSet.as_view(list_and_create_actions), name='crawler'),
    path('crawler/<int:pk>', views.CrawlerViewSet.as_view(retrieve_update_and_destroy_actions), name='crawler-detail'),
    path('crawler/<int:pk>/run', views.CrawlerViewSet.as_view({'get': 'run'}), name='crawler-run'),
    path('crawler/<int:pk>/stop', views.CrawlerViewSet.as_view({'get': 'stop'}), name='crawler-run'),
    path('crawler/<int:pk>/group', views.CrawlerViewSet.as_view({'get': 'group'}), name='crawler-group'),

    path('instance/', views.CrawlerInstanceViewSet.as_view(only_list_action), name='instance'),
    path('instance/<int:pk>', views.CrawlerInstanceViewSet.as_view(only_retrieve_action), name='instance-detail'),
    path('instance/<int:pk>/export_config', views.CrawlerInstanceViewSet.as_view({'get': 'export_config'}), name='instance-export-config'),
    path('instance/<int:pk>/file/found/<int:num_files>', views.CrawlerInstanceViewSet.as_view({'get': 'files_found'}), name='instance-files-found'),
    path('instance/<int:pk>/file/success', views.CrawlerInstanceViewSet.as_view({'get': 'success_download_file'}), name='instance-success-download-file'),
    path('instance/<int:pk>/file/error', views.CrawlerInstanceViewSet.as_view({'get': 'error_download_file'}), name='instance-error-download-file'),
    path('instance/<int:pk>/file/duplicated', views.CrawlerInstanceViewSet.as_view({'get': 'previously_crawled_file'}), name='instance-duplicated-download-file'),

    path('task/', views.TaskViewSet.as_view(list_and_create_actions), name='task'),
    path('task/<int:pk>', views.TaskViewSet.as_view(retrieve_update_and_destroy_actions), name='task-detail'),
    path('task/<int:pk>/filter', views.TaskViewSet.as_view({'get': 'filter'}), name='task-filter'),

    path('queue/', views.CrawlerQueueViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='queue'),
    path('queue/switch_position/<int:a>/<int:b>', views.CrawlerQueueViewSet.as_view({'get': 'switch_position'}), name='queue-switch-position'),
    path('queue/force_execution/<int:item_id>', views.CrawlerQueueViewSet.as_view({'get': 'force_execution'}), name='queue-force-execution'),
    path('queue/remove_item/<int:item_id>', views.CrawlerQueueViewSet.as_view({'get': 'remove_item'}), name='queue-remove-item'),

    path('open-api/', get_schema_view(
        title='Plataforma de Coletas - API',
        description='API para as principais funcionalidades da plataforma de coletas.',
        version='1.0.0',
        public=True,
        url='/api/',
        urlconf='api.urls'
    ), name='open-api'),
    path('swagger-ui/',  TemplateView.as_view(
        template_name='api/swagger-ui.html', 
        extra_context={'schema_url':'api:open-api'}
    ), name='swagger-ui')
]

#     # Includes the API endpoints in the URLs
#     url(r'^api/', include(api_router.urls)),
#     path('openapi/', get_schema_view(
#         title='Áduna',
#         description='API para busca de dados não estruturados',
#         url='/services/',
#         version='1.0.0',
#         urlconf='services.urls',
#         public=True,
#     ), name='openapi'),
# ]
