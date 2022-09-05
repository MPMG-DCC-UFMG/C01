from django.shortcuts import render

def create_steps(request):
    return render(request, 'main/steps_creation.html', {})