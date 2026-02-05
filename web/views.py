from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from sso.models import CharacterEve
from project.models import Project, Item as ProjectItem, Product, MaterialProject, Contract
from shop.models import Item, ItemsOrder, Order
from warehouse.models import CorpItem, Tag
from esi.views import apprisal_data
import random
import string

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

    
# PROJECTS Feature View

## User View

### View List of Projects
@login_required(login_url="/")
def list_projects(request):
    if not request.user.groups.filter(name__in=["Admin","Industry"]).exists():
        return redirect("/dashboard/")
        
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_projects = Project.objects.all().order_by('created_at').reverse()
    
    return render(request,"project/list.html",{
        "main": main,
        "list_projects": list_projects
    })

# View Project
@login_required(login_url="/")
def view_project(request, project_id):
    if not request.user.groups.filter(name__in=["Admin","Industry"]).exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    project = get_object_or_404(Project, id=project_id)
    list_materials = MaterialProject.objects.filter(project=project)
    list_contracts = Contract.objects.filter(project=project)
    characters = string.ascii_letters + string.digits
    
    materials_id = f"{''.join(random.choices(characters, k=9))}-{project.id}-1-{''.join(random.choices(characters, k=9))}"
    economic_id = f"{''.join(random.choices(characters, k=9))}-{project.id}-2-{''.join(random.choices(characters, k=9))}"
    
    material_total_cost = 0
    contract_total_cost = 0
    total_cost = 0
    for material in list_materials:
        material_total_cost += material.total_price_needed()
        
    for contract in list_contracts:
        if contract.status in [1, 2]:
            contract_total_cost += contract.value
    
    total_cost = material_total_cost + contract_total_cost
    
    return render(request,"project/view.html",{
        "main": main,
        "project": project,
        "list_materials": list_materials,
        "material_total_cost": material_total_cost,
        "contract_total_cost": contract_total_cost,
        "total_cost": total_cost,
        "materials_id": materials_id,
        "economic_id": economic_id
    })

## Admin View

### List Porjects Admin
@login_required(login_url="/")
def admin_projects(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_projects = Project.objects.all().order_by('created_at').reverse()
    
    return render(request,"project/admin/projects.html",{
        "main": main,
        "list_projects": list_projects
    })


### Add Project
@login_required(login_url="/")
def add_project(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    
    if request.method == "POST":
        project_name = request.POST.get("project_name")
        project_description = request.POST.get("project_description")
        item_name = request.POST.get("item_name")
        quantity = int(request.POST.get("item_quantity") or 0)
        
        data = apprisal_data(items=item_name)
        item, _ = ProjectItem.objects.get_or_create(
            eve_id = data["items"][0]["itemType"]["eid"],
            defaults={
                "name": item_name,
                "jita_price": data["items"][0]["effectivePrices"]["sellPrice"] / 100,
                "volume": data["items"][0]["totalVolume"]
            }
        )

        project = Project.objects.create(
            name = project_name,
            description = project_description,
            status = 0
        )
        
        Product.objects.create(
            project = project,
            item = item,
            quantity = quantity
        )
        
        return redirect("/projects/")
    
    return render(request,"project/admin/add.html",{
        "main": main
    })

### Edit Project
@login_required(login_url="/")
def edit_project(request, project_id):
    if not request.user.groups.filter(name__in=["Admin","Industry"]).exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    project = get_object_or_404(Project, id=project_id)
    product = Product.objects.get(project = project)
    
    if request.method == "POST":
        project_name = request.POST.get("project_name")
        project_description = request.POST.get("project_description")
        item_name = request.POST.get("item_name")
        quantity = int(request.POST.get("item_quantity") or 0)
        
        project.name = project_name
        project.description = project_description
        project.save()
        
        if product.item.name != item_name:
            item_data = apprisal_data(item_name)
            
            item, created = ProjectItem.objects.get_or_create(
                eve_id = item_data["items"][0]["itemType"]["eid"],
                defaults={
                    "name": item_name,
                    "jita_price": item_data["items"][0]["effectivePrices"]["buyPrice"] / 100,
                    "volume": item_data["items"][0]["totalVolume"]
                }
            )

            if not created:
                item.jita_price = item_data["items"][0]["effectivePrices"]["buyPrice"] / 100
                item.volume = item_data["items"][0]["totalVolume"]
                item.save()
                
            product.item = item
            
        product.quantity = quantity
        product.save()
        
        return redirect(f"/projects/{project_id}/view")

    
    return render(request,"project/admin/add.html",{
        "main": main,
        "project": project,
        "product" : product
    })
    
### Delete Project
@login_required(login_url="/")
def del_project(request, project_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")

    try:
        project = get_object_or_404(Project, id=project_id)
        list_materials = MaterialProject.objects.filter(project=project)
        list_contracts = Contract.objects.filter(project=project)
        product = Product.objects.get(project = project)
        product.delete()
        list_contracts.delete()
        list_materials.delete()
        project.delete()
    except Project.DoesNotExist:
        pass
    
    return redirect("/projects/")

### Finish Project
@login_required(login_url="/")
def finish_project(request, project_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    project = Project.objects.get(id = project_id)
    project.status = 1
    project.save()
    
    return redirect(f"/projects/{project_id}/view/")
     
### MATERIALS

#### Add new list of materials
@login_required(login_url="/")
def add_material_project(request, project_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == "POST":
        materials = request.POST.get("materials") 
        data = apprisal_data(items=materials)
        
        for item in data["items"]:
            pItem, created = ProjectItem.objects.get_or_create(
                eve_id = item["itemType"]["eid"],
                defaults={
                    "name": item["itemType"]["name"],
                    "jita_price": item["effectivePrices"]["buyPrice"] / 100,
                    "volume": item["totalVolume"]
                }
            )
            
            if not created:
                pItem.jita_price = item["effectivePrices"]["buyPrice"] / 100
                pItem.save()
            
            MaterialProject.objects.get_or_create(
                project = project,
                item = pItem,
                defaults={
                    "quantity": item["amount"]
                }
            )

        return redirect(f"/projects/{project_id}/view/")
    
    return render(request, "project/materials/add.html",{
        "main": main,
        "project": project
    })
    
#### Edit Material in Project
@login_required(login_url="/")
def edit_material_project(request, project_id, material_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    project = get_object_or_404(Project, id=project_id)
    material = get_object_or_404(MaterialProject, id=material_id)
    
    if request.method == "POST":
        quantity = int(request.POST.get("quantity") or 0)
        material.quantity = quantity
        material.save()
        
        return redirect(f"/projects/{project_id}/view/")
    
    return render(request, "project/materials/edit.html",{
        "main": main,
        "project": project,
        "material": material
    })
    
#### Remove Material from Project
@login_required(login_url="/")
def del_material_project(request, project_id, material_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    material = get_object_or_404(MaterialProject, id=material_id)

    try:
        material.delete()
    except MaterialProject.DoesNotExist:
        pass
    
    return redirect(f"/projects/{project_id}/view/")

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