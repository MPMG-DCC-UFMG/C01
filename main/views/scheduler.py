from django.shortcuts import render

from main.models import CrawlRequest

def scheduler(request):
    crawl_requests = CrawlRequest.objects.all()
    context = {
        'crawl_requests': crawl_requests
    }
    return render(request, 'main/scheduler.html', context)
