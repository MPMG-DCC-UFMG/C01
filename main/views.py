from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .forms import CrawlRequestForm, RawCrawlRequestForm,\
                   ResponseHandlerFormSet, ParameterHandlerFormSet
from .models import CrawlRequest, CrawlerInstance

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
        parameter_formset = ParameterHandlerFormSet(request.POST,
            prefix='params')
        response_formset = ResponseHandlerFormSet(request.POST,
            prefix='responses')
        if my_form.is_valid() and parameter_formset.is_valid() and \
           response_formset.is_valid():
            new_crawl = CrawlRequestForm(my_form.cleaned_data)
            instance = new_crawl.save()

            # save sub-forms and attribute to this crawler instance
            parameter_formset.instance = instance
            parameter_formset.save()
            response_formset.instance = instance
            response_formset.save()

            return HttpResponseRedirect('http://localhost:8000/crawlers/')
    else:
        my_form = RawCrawlRequestForm()
        parameter_formset = ParameterHandlerFormSet(prefix='params')
        response_formset = ResponseHandlerFormSet(prefix='responses')
    context['form'] = my_form
    context['response_formset'] = response_formset
    context['parameter_formset'] = parameter_formset
    return render(request, "main/create_crawler.html", context)

def edit_crawler(request, id):
    crawler = get_object_or_404(CrawlRequest, pk=id)
    form = CrawlRequestForm(request.POST or None, instance=crawler)
    parameter_formset = ParameterHandlerFormSet(request.POST or None,
        instance=crawler, prefix='params')
    response_formset = ResponseHandlerFormSet(request.POST or None,
        instance=crawler, prefix='responses')

    if request.method == 'POST' and form.is_valid() and \
       parameter_formset.is_valid() and response_formset.is_valid():
            form.save()
            parameter_formset.save()
            response_formset.save()
            return HttpResponseRedirect('http://localhost:8000/crawlers/')
    else:
        return render(request, 'main/create_crawler.html', {
            'form': form,
            'response_formset': response_formset,
            'parameter_formset': parameter_formset,
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
    data = CrawlRequest.process_config_data(crawler, data)
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