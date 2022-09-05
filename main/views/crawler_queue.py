from django.shortcuts import render, redirect
from main.api import crawler_queue

def crawler_queue(request):
    return render(request, 'main/crawler_queue.html')

def remove_crawl_request(request, crawler_id):
    crawler_queue.remove_crawl_request(crawler_id)
    return redirect('/detail/' + str(crawler_id))