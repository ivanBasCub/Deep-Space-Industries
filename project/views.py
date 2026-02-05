from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from sso.models import CharacterEve
from .models import Project, Product, MaterialProject, Contract, Item
from esi.views import apprisal_data
import string
import random

# USER VIEW

## LIST OF PROJECTS
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
    
## VIEW PROJECT INFO
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
    
# ADMIN VIEW

## LIST OF PROJECTS ADMIN
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
    
## ADD NEW PROJECT
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
        item, _ = Item.objects.get_or_create(
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

## EDIT PROJECT
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
            
            item, created = Item.objects.get_or_create(
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

## DELETE PROJECT
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

## FINISH PROJECT
@login_required(login_url="/")
def finish_project(request, project_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    project = Project.objects.get(id = project_id)
    project.status = 1
    project.save()
    
    return redirect(f"/projects/{project_id}/view/")

## MATERIALS

### ADD LIST OF MATERIALS TO THE PROJECT
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
            pItem, created = Item.objects.get_or_create(
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
    
### EDIT MATERIAL QUANTITY
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
    
### REMOVE MATERIAL FROM PROJECT
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
