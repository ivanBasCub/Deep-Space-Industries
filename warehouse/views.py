from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Tag, CorpItem
from sso.models import CharacterEve

# USER VIEW
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

# ADMIN VIEW

## EDIT TAGS OF ITEMS
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
    
## DEL ITEMS CORP ITEMS
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