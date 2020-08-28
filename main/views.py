from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .forms import CrawlRequestForm, RawCrawlRequestForm,\
                   ResponseHandlerFormSet, RequestConfigForm
from .models import CrawlRequest, CrawlerInstance, RequestConfiguration

import subprocess
from datetime import datetime
import time

import crawlers.crawler_manager as crawler_manager

def getAllData():
    return CrawlRequest.objects.all().order_by('-creation_date')

def list_crawlers(request):
    context = {'allcrawlers': getAllData()}
    return render(request, "main/list_crawlers.html", context)

def create_crawler(request):
    context = {}
    if request.method == "POST":
        my_form = RawCrawlRequestForm(request.POST)
        templated_url_form = RequestConfigForm(request.POST)
        response_formset = ResponseHandlerFormSet(request.POST)
        if my_form.is_valid() and templated_url_form.is_valid() and \
           response_formset.is_valid():
            request_inst = templated_url_form.save()
            response_formset.instance = request_inst
            response_formset.save()
            new_crawl = CrawlRequestForm(my_form.cleaned_data)
            new_crawl.instance.templated_url_config = request_inst
            instance = new_crawl.save()
            
            return HttpResponseRedirect('http://localhost:8000/crawlers/')
    else:
        my_form = RawCrawlRequestForm()
        templated_url_form = RequestConfigForm()
        response_formset = ResponseHandlerFormSet()
    context['form'] = my_form
    context['response_formset'] = response_formset
    context['templated_url_form'] = templated_url_form
    return render(request, "main/create_crawler.html", context)

def edit_crawler(request, id):
    crawler = get_object_or_404(CrawlRequest, pk=id)
    form = CrawlRequestForm(request.POST or None, instance=crawler)
    templated_url_form = RequestConfigForm(request.POST or None,
        instance=crawler.templated_url_config)
    response_formset = ResponseHandlerFormSet(request.POST or None,
        instance=crawler.templated_url_config)

    if request.method == 'POST' and form.is_valid() and \
       templated_url_form.is_valid() and response_formset.is_valid():
            form.save()
            templated_url_form.save()
            response_formset.save()
            return HttpResponseRedirect('http://localhost:8000/crawlers/')
    else:
        return render(request, 'main/create_crawler.html', {
            'form': form,
            'response_formset': response_formset,
            'templated_url_form': templated_url_form,
            'crawler' : crawler
        })
        
def delete_crawler(request, id):
    crawler = CrawlRequest.objects.get(id=id)
    
    if request.method == 'POST':
        crawler.delete()
        return HttpResponseRedirect('http://localhost:8000/crawlers/')
    
    return render(request, 'main/confirm_delete_modal.html', {'crawler': crawler})

def detail_crawler(request, id):
    crawler = CrawlRequest.objects.get(id=id)
    # order_by("-atribute") orders descending
    instances = CrawlerInstance.objects.filter(crawler_id=id).order_by("-last_modified")

    context = {
        'crawler': crawler,
        'instances': instances,
        'last_instance': instances[0] if len(instances) else None
    }

    return render(request, 'main/detail_crawler.html', context)

def monitoring(request):
    return HttpResponseRedirect("http://localhost:5000/")

def create_steps(request):
    return render(request, "main/steps_creation.html", {})

def stop_crawl(request, crawler_id, instance_id):
    crawler_manager.stop_crawler(instance_id)
    
    instance = CrawlerInstance.objects.get(instance_id=instance_id)
    instance.running = False
    instance.save()
    
    crawler = CrawlRequest.objects.filter(id=crawler_id)[0]
    crawler.running = False
    crawler.save()
    context = {'instance':instance, 'crawler':crawler}
    return redirect(f"/detail/{crawler_id}")
    # return render(request, "main/detail_crawler.html", context)

def run_crawl(request, crawler_id):
    crawler = CrawlRequest.objects.filter(id=crawler_id)[0]
    crawler.running = True
    crawler.save()

    data = CrawlRequest.objects.filter(id=crawler_id).values()[0]
    data = CrawlRequest.processConfigData(data)
    instance_id = crawler_manager.start_crawler(data)
    
    instance = create_instance(data['id'], instance_id)
    context = {'instance':instance, 'crawler':crawler}
    
    return redirect(f"/detail/{crawler_id}")
    # return render(request, "main/detail_crawler.html", context)

def create_instance(crawler_id, instance_id):
    mother = CrawlRequest.objects.filter(id=crawler_id)
    obj = CrawlerInstance.objects.create(crawler_id=mother[0], instance_id=instance_id, running=True)
    return obj

def tail_log_file(request, instance_id):
    out = subprocess.run(["tail", f"crawlers/log/{instance_id}.out", "-n", "10"], stdout=subprocess.PIPE).stdout
    err = subprocess.run(["tail", f"crawlers/log/{instance_id}.err", "-n", "10"], stdout=subprocess.PIPE).stdout
    return JsonResponse({
        "out": out.decode('utf-8'),
        "err": err.decode('utf-8'),
        "time": str(datetime.fromtimestamp(time.time())),
    })