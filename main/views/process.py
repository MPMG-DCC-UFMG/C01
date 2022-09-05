import multiprocessing as mp 
from django.http import HttpResponse

def list_process(request):
    text = ''
    for p in mp.active_children():
        text += f'child {p.name} is PID {p.pid}<br>'

    return HttpResponse(text)