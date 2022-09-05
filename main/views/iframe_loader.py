from django.shortcuts import render

from scrapy_puppeteer import iframe_loader

def load_iframe(request):
    url = request.GET['url'].replace('"', '')
    xpath = request.GET['xpath'].replace('"', '')

    try:
        content = iframe_loader(url, xpath)
        return render(request, 'main/iframe_loader.html', {'content': content})

    except Exception as e:
        ctx = {
            'url': url,
            'xpath': xpath,
            'error': str(e)
        }
        return render(request, 'main/error_iframe_loader.html', ctx)