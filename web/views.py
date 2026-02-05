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
    
# WAREHOUSE

# List of the content of the warehouse
@login_required(login_url="/")
def warehouse(request):
    if not request.user.groups.filter(name__in=["Admin","Industry"]).exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_tags = Tag.objects.all()
    list_items = CorpItem.objects.all()
    list_location = ["Hangar Corporation 1","Hangar Corporation 2","Hangar Corporation 3","Hangar Corporation 4","Hangar Corporation 5","Hangar Corporation 6"] 
    list_stations = set()
    for item in list_items:
        item.container = "Hangar Corporation " + item.loc_flag[-1]
        list_stations.add(item.location)
        
    if request.method == "POST":
        ids = request.POST.getlist("selected_items")
        
        if not ids: 
            messages.error(request, "No seleccionaste ningún item.") 
            return redirect("warehouse")

        return redirect("edit_tags_bulk")
    
    return render(request, 'warehouse/index.html',{
        "main":main,
        "list_tags": list_tags,
        "list_items": list_items,
        "list_location": list_location,
        "list_stations": list_stations
    })

@login_required(login_url="/")
def edit_tags_bulk(request):
    if not request.user.groups.filter(name__in=["Admin","Industry"]).exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()

    ids = request.GET.getlist("selected_items", [])
    items = CorpItem.objects.filter(id__in=ids)
    list_tags = Tag.objects.all()

    if request.method == "POST":
        selected_tags = request.POST.getlist("tags")
        tags = Tag.objects.filter(id__in=selected_tags)
        
        for item in items:
            item.items.all().delete()
            for tag in tags:
                item.items.create(tag=tag)

        return redirect("warehouse")

    return render(request, "warehouse/edit.html", {
        "main": main,
        "tags": list_tags,
        "items": items,
    })
    
@login_required(login_url="/")
def del_corp_item(request, item_id):
    if not request.user.groups.filter(name__in=["Admin","Industry"]).exists():
        return redirect("/dashboard/")
    
    item = CorpItem.objects.get(id=item_id)
    try:
        item.items.all().delete()
        item.delete()
    except CorpItem.DoesNotExist:
        pass
    
    return redirect("warehouse")