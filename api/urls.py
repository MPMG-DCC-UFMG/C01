from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from django.shortcuts import redirect
from . import views

app_name = 'api'

list_and_create_actions = {'get': 'list', 'post': 'create'}
retrieve_update_and_destroy_actions = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}
all_actions = {'get': 'list', 'post': 'create', 'put': 'update', 'delete': 'destroy'}
only_list_action = {'get': 'list'}
only_retrieve_action = {'get': 'retrieve'}

urlpatterns = [
    path('', lambda request: redirect('api:swagger-ui', permanent=True)),
    
    # crawler info
    path('crawler/', views.CrawlerViewSet.as_view(list_and_create_actions), name='crawler'),
    path('crawler/<int:pk>', views.CrawlerViewSet.as_view(retrieve_update_and_destroy_actions), name='crawler-detail'),
    path('crawler/<int:pk>/run', views.CrawlerViewSet.as_view({'get': 'run'}), name='crawler-run'),
    path('crawler/<int:pk>/stop', views.CrawlerViewSet.as_view({'get': 'stop'}), name='crawler-run'),
    path('crawler/<int:pk>/group', views.CrawlerViewSet.as_view({'get': 'group'}), name='crawler-group'),

    # instance 
    path('instance/', views.CrawlerInstanceViewSet.as_view(only_list_action), name='instance'),
    path('instance/<int:pk>', views.CrawlerInstanceViewSet.as_view(only_retrieve_action), name='instance-detail'),
    
    # instance config export
    path('instance/<int:pk>/export/config', views.CrawlerInstanceViewSet.as_view({'get': 'export_config'}), name='instance-export-config'),
    
    # instance update file download status
    path('instance/<int:pk>/file/found/<int:num_files>', views.CrawlerInstanceViewSet.as_view({'get': 'files_found'}), name='instance-files-found'),
    path('instance/<int:pk>/file/success', views.CrawlerInstanceViewSet.as_view({'get': 'file_success'}), name='instance-success-download-file'),
    path('instance/<int:pk>/file/error', views.CrawlerInstanceViewSet.as_view({'get': 'file_error'}), name='instance-error-download-file'),
    path('instance/<int:pk>/file/previously', views.CrawlerInstanceViewSet.as_view({'get': 'file_previously'}), name='instance-previously-download-file'),
    
    # instance update page download status
    path('instance/<int:pk>/page/found/<int:num_files>', views.CrawlerInstanceViewSet.as_view({'get': 'pages_found'}), name='instance-pages-found'),
    path('instance/<int:pk>/page/success', views.CrawlerInstanceViewSet.as_view({'get': 'page_success'}), name='instance-success-download-page'),
    path('instance/<int:pk>/page/error', views.CrawlerInstanceViewSet.as_view({'get': 'page_error'}), name='instance-error-download-page'),
    path('instance/<int:pk>/page/previously', views.CrawlerInstanceViewSet.as_view({'get': 'page_previously'}), name='instance-previously-download-page'),
    path('instance/<int:pk>/page/duplicated', views.CrawlerInstanceViewSet.as_view({'get': 'page_duplicated'}), name='instance-duplicated-download-page'),

    # instance get logs
    path('instance/<int:pk>/log/tail', views.CrawlerInstanceViewSet.as_view({'get': 'tail_log'}), name='instance-log-tail'),
    path('instance/<int:pk>/log/raw/error', views.CrawlerInstanceViewSet.as_view({'get': 'raw_log_err'}), name='instance-log-raw-error'),
    path('instance/<int:pk>/log/raw/out', views.CrawlerInstanceViewSet.as_view({'get': 'raw_log_out'}), name='instance-log-raw-out'),

    # instance debug
    path('instance/<int:pk>/debug/trace', views.CrawlerInstanceViewSet.as_view({'get': 'export_trace'}), name='instance-debug-trace'),
    path('instance/<int:pk>/debug/screenshots', views.CrawlerInstanceViewSet.as_view({'get': 'screenshots'}), name='instance-debug-screenshots'),
    
    # task info
    path('task/', views.TaskViewSet.as_view(list_and_create_actions), name='task'),
    path('task/<int:pk>', views.TaskViewSet.as_view(retrieve_update_and_destroy_actions), name='task-detail'),
    path('task/<int:pk>/filter', views.TaskViewSet.as_view({'get': 'filter'}), name='task-filter'),

    # queue info
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
