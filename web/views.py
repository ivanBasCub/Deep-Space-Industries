from django.shortcuts import render, redirect
from sso.models import CharacterEve


def index(request ):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return render(request, 'index.html')

def dashboard(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_characters = CharacterEve.objects.filter(user=request.user)
    return render(request, 'dashboard.html',{
        'main': main,
        'list_characters': list_characters
    })