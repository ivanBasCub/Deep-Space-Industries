from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from sso.models import CharacterEve
from warehouse.models import CorpItem, Tag

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return render(request, 'index.html')

@login_required(login_url='/')
def dashboard(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_characters = CharacterEve.objects.filter(user=request.user)
    return render(request, 'dashboard.html',{
        'main': main,
        'list_characters': list_characters
    })

## ADMIN USER
### View users List
@login_required(login_url="/")
def list_users(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_users = User.objects.exclude(username = "root").all()
    
    for user in list_users:
        user.username = user.username.replace("_"," ")
        user.user_groups = user.groups.all()
    
    return render(request, "admin/list_user.html",{
        "main":main,
        "list_user": list_users
    })
    
@login_required(login_url="/")
def edit_user_permissions(request, user_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    user = User.objects.get(id=user_id)
    user.username = user.username.replace("_", " ")
    user.user_groups = user.groups.all()
    list_groups = Group.objects.all()
    
    if request.method == "POST":
        permissions = request.POST.getlist("groups")
        selected_groups = Group.objects.filter(id__in = permissions)
        user.groups.set(selected_groups)
            
        
        return redirect("/users/")
    
    return render(request, "admin/edit.html",{
        "main": main,
        "user": user,
        "list_groups": list_groups
    })