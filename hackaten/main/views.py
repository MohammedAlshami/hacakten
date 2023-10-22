from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'landing/index.html')

def register_option(request):
    return render(request, 'signup/options.html')