from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .forms import CrawlRequestForm, RawCrawlRequestForm
from .models import CrawlRequest, CrawlerInstance

from crawlers.constants import *

import subprocess
from datetime import datetime
import time

import crawlers.crawler_manager as crawler_manager


def getAllData():
    return CrawlRequest.objects.all().order_by('-creation_date')


def list_crawlers(response):
    context = {'allcrawlers': getAllData()}
    return render(response, "main/list_crawlers.html", context)


def create_crawler(response):
    context = {}
    if response.method == "POST":
        my_form = RawCrawlRequestForm(response.POST)
        if my_form.is_valid():
            new_crawl = CrawlRequestForm(my_form.cleaned_data)
            new_crawl.save()

            return HttpResponseRedirect('http://localhost:8000/crawlers/')
    else:
        my_form = RawCrawlRequestForm()
    context['form'] = my_form
    return render(response, "main/create_crawler.html", context)


def edit_crawler(request, id):
    crawler = get_object_or_404(CrawlRequest, pk=id)
    form = CrawlRequestForm(request.POST or None, instance=crawler)

    if(request.method == 'POST'):
        if(form.is_valid()):
            form.save()
            return HttpResponseRedirect('http://localhost:8000/crawlers/')
    else:
        return render(request, 'main/create_crawler.html', {'form': form, 'crawler': crawler})


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


def monitoring(response):
    return HttpResponseRedirect("http://localhost:5000/")


def create_steps(response):
    return render(response, "main/steps_creation.html", {})


def stop_crawl(response, crawler_id, instance_id):
    config = CrawlRequest.objects.filter(id=crawler_id).values()[0]
    crawler_manager.stop_crawler(instance_id, config)

    instance = CrawlerInstance.objects.get(instance_id=instance_id)
    instance.running = False
    instance.save()

    crawler = CrawlRequest.objects.filter(id=crawler_id)[0]
    crawler.running = False
    crawler.save()
    context = {'instance': instance, 'crawler': crawler}
    return redirect(f"/detail/{crawler_id}")
    # return render(response, "main/detail_crawler.html", context)


def run_crawl(response, crawler_id):
    crawler = CrawlRequest.objects.filter(id=crawler_id)[0]
    crawler.running = True
    crawler.save()

    data = CrawlRequest.objects.filter(id=crawler_id).values()[0]
    del data['creation_date']
    del data['last_modified']
    instance_id = crawler_manager.start_crawler(data)

    instance = create_instance(data['id'], instance_id)
    context = {'instance': instance, 'crawler': crawler}

    return redirect(f"/detail/{crawler_id}")
    # return render(response, "main/detail_crawler.html", context)


def create_instance(crawler_id, instance_id):
    mother = CrawlRequest.objects.filter(id=crawler_id)
    obj = CrawlerInstance.objects.create(crawler_id=mother[0], instance_id=instance_id, running=True)
    return obj


def tail_log_file(request, instance_id):


    crawler_id = CrawlerInstance.objects.filter(instance_id=instance_id).values()[0]["crawler_id_id"]

    config = CrawlRequest.objects.filter(id=int(crawler_id)).values()[0]
    if config["output_path"] is None:
        output_path = CURR_FOLDER_FROM_ROOT
    else:
        if config["output_path"][-1] == "/":
            output_path = config["output_path"][:-1]
        else:
            output_path = config["output_path"]


    out = subprocess.run(["tail", f"{output_path}/log/{instance_id}.out", "-n", "10"], stdout=subprocess.PIPE).stdout
    err = subprocess.run(["tail", f"{output_path}/log/{instance_id}.err", "-n", "10"], stdout=subprocess.PIPE).stdout
    return JsonResponse({
        "out": out.decode('utf-8'),
        "err": err.decode('utf-8'),
        "time": str(datetime.fromtimestamp(time.time())),
    })
