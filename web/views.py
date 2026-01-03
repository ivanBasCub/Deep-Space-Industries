from django.shortcuts import render


def index(request ):
    return render(request, 'index.html')

def audit(request):
    return render(request, 'audit.html')