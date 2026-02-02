from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from sso.models import CharacterEve
from buyback.models import BuyBackProgram, ProgramSpecialTax, Location, BuyBackServices, Manager
from project.models import Project, Item as ProjectItem, Product, MaterialProject, Contract
from shop.models import Item, ItemsOrder, Order
from esi.views import structure_data, item_data_id, apprisal_data
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

# BUYBACK FEATURES VIEWS

## User View

### List buyback programs
@login_required(login_url='/') 
def buyback_program(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    programs = BuyBackProgram.objects.all()
    
    for program in programs:
        program.jita_buy = program.settings.filter(name="Jita Buy").exists()
        program.jita_sell = program.settings.filter(name="Jita Sell").exists()
        program.all_items = program.settings.filter(name="All Items").exists()
        program.freighter = program.settings.filter(name="Freight").exists()
        program.unpacked_items = program.settings.filter(name="Unpacked Items").exists()
        program.special_taxes = ProgramSpecialTax.objects.filter(program = program).count()

    return render(request, 'buyback/index.html',{
        'main': main,
        'programs': programs
    })

### View Buyback program Special Taxes
@login_required(login_url="/")
def special_taxes(request, program_id):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    program = BuyBackProgram.objects.get(id = program_id)
    list_special_taxes = ProgramSpecialTax.objects.filter(program=program).all()
    
    for item in list_special_taxes:
        item.total_tax = program.tax + item.special_tax
    
    return render(request, 'buyback/special_taxes/index.html',{
        'main':main,
        "program" : program,
        "special_taxes": list_special_taxes
    })

# View Contract Calculator
@login_required(login_url="/")
def program_calculator(request, program_id):
    # View Classes
    class Item():
        def __init__(self,item_id, item_name, amount, buy_price, sell_price, item_tax, is_allowed, final_price, total, tax_difference):
            self.item_id = item_id
            self.item_name = item_name
            self.amount = amount
            self.buy_price = buy_price
            self.sell_price = sell_price
            self.item_tax = item_tax
            self.is_allowed = is_allowed
            self.final_price = final_price
            self.total = total
            self.tax_difference = tax_difference
    
    class Contract():
        def __init__(self, contract_id, raw_price, total_volume, general_tax, freigther_tax, donation_tax, net_price):
            self.contract_id = contract_id
            self.raw_price = raw_price
            self.total_volume = total_volume
            self.general_tax = general_tax
            self.freigther_tax = freigther_tax
            self.donation_tax = donation_tax
            self.net_price = net_price
            
    # Obtain data for the database
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    program = BuyBackProgram.objects.get(id = program_id)
    program.jita_buy = program.settings.filter(name="Jita Buy").exists()
    program.all_items = program.settings.filter(name="All Items").exists()
    program.freighter = program.settings.filter(name="Freight").exists()
    
    if request.method == "POST":
        items = request.POST.get("items")
        donation = int(request.POST.get("donation"))
        
        data = apprisal_data(items, program)

        characters = string.ascii_letters + string.digits 
        contract_id = f"{program.id}-{''.join(random.choices(characters, k=8))}-{''.join(random.choices(characters, k=8))}"

        total_volume = data["totalPackagedVolume"]
        raw_price=0

        list_items = []
        for janice_item in data["items"]:
            special_item = ProgramSpecialTax.objects.filter(item_id=janice_item["itemType"]["eid"]).first()

            buy = janice_item["effectivePrices"]["buyPrice"] / 100
            sell = janice_item["effectivePrices"]["sellPrice"] / 100
            tax = program.tax
            allowed = True
            tax_difference = 0
            if special_item:
                allowed = special_item.is_allowed
                if allowed:
                    tax_difference = special_item.special_tax
                tax += special_item.special_tax
            elif not program.all_items:
                buy = 0
                sell = 0
                tax = 0
                allowed = False

            if allowed:
                if program.jita_buy:
                    raw_price += buy * janice_item["amount"]
                else:
                    raw_price += sell * janice_item["amount"]

            final_price = buy if program.jita_buy else sell
            final_price -= final_price * (tax / 100)

            item = Item(
                item_id=janice_item["itemType"]["eid"],
                item_name=janice_item["itemType"]["name"],
                amount=janice_item["amount"],
                buy_price=buy,
                sell_price=sell,
                item_tax=tax,
                is_allowed=allowed,
                final_price=final_price,
                total=final_price * janice_item["amount"],
                tax_difference=tax_difference
            )

            list_items.append(item)
    
        total_price = 0
        freighter_tax = 0
        donation_tax = 0
        
        for item in list_items:
            total_price = total_price + item.total
            
        if program.freighter_tax != 0:
            freighter_tax = total_volume * program.freighter_tax
            
        if donation != 0:
            donation_tax = total_price * (donation / 100)
            
        net_price = (total_price - donation_tax) + freighter_tax
        
        contract = Contract(
            contract_id=contract_id,
            raw_price= raw_price,
            total_volume= total_volume,
            general_tax= raw_price - total_price,
            freigther_tax=freighter_tax,
            donation_tax=donation_tax,
            net_price=net_price
        )
        
        return render(request,"buyback/calculate.html",{
            "main":main,
            "program": program,
            "donation": donation,
            "list_items": list_items,
            "contract": contract
        })
        
    return render(request,"buyback/calculate.html",{
        "main":main,
        "program": program
    })

## Admin View

### Add buyback program
@login_required(login_url="/")
def add_buyback_program(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_locations = Location.objects.exclude(station_name="Anywhere").all()
    list_services = BuyBackServices.objects.exclude(name__in=["Jita Buy","Jita Sell"]).all()
    base_price = BuyBackServices.objects.filter(name__in=["Jita Buy","Jita Sell"]).all()
    
    if request.method == "POST":
        if Manager.objects.exists() == False:
            return render(request, 'buyback/programs/add.html',{
                'main': main,
                "locations":list_locations,
                "services": list_services,
                "base_prices" : base_price
            })
            
        program_name = request.POST.get("program_name")
        location_id = int(request.POST.get("program_location") or 0)
        tax = int(request.POST.get("program_tax") or 0)
        services = request.POST.getlist("program_services")
        freighter_tax = int(request.POST.get("freight_tax") or 0)
        program_base_price = int(request.POST.get("program_item_price") or 0)
        
        man = Manager.objects.first()
        prog_loc = Location.objects.get(station_id = location_id)
        selected_services = BuyBackServices.objects.filter(id__in=services)
        base_price = BuyBackServices.objects.get(id = program_base_price)
        
        program = BuyBackProgram.objects.create(
            name = program_name,
            location = prog_loc,
            tax = tax,
            manager = man,
            freighter_tax = freighter_tax
        )
        program.settings.set(list(selected_services) + [base_price])
        program.save()
        
        return redirect("/buybackprogram/")
    
    return render(request, 'buyback/programs/index.html',{
        'main': main,
        "locations":list_locations,
        "services": list_services,
        "base_prices" : base_price
    })

### Edit buyback program
@login_required(login_url="/")
def edit_buyback_program(request, program_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    program = BuyBackProgram.objects.get(id = program_id)
    list_locations = Location.objects.exclude(station_name="Anywhere").all()
    list_services = BuyBackServices.objects.exclude(name__in=["Jita Buy","Jita Sell"]).all()
    base_price = BuyBackServices.objects.filter(name__in=["Jita Buy","Jita Sell"]).all()
    
    if request.method == "POST":
        program_name = request.POST.get("program_name")
        location_id = int(request.POST.get("program_location") or 0)
        tax = int(request.POST.get("program_tax") or 0)
        services = request.POST.getlist("program_services")
        freighter_tax = int(request.POST.get("freight_tax") or 0)
        program_base_price = int(request.POST.get("program_item_price") or 0)

        prog_loc = Location.objects.get(station_id = location_id)
        selected_services = BuyBackServices.objects.filter(id__in=services)
        base_price = BuyBackServices.objects.get(id = program_base_price)
        
        program.name = program_name
        program.location = prog_loc
        program.tax = tax
        program.freighter_tax = freighter_tax
        program.settings.set(list(selected_services) + [base_price])
        program.save()
        
        return redirect("/buybackprogram/")
    
    return render(request, 'buyback/programs/index.html',{
        'main': main,
        'program':program,
        "locations":list_locations,
        "services": list_services,
        "base_prices" : base_price
    })

### Del buyback program
@login_required(login_url="/")
def del_buyback_program(request, program_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    try:
        program = BuyBackProgram.objects.get(id = program_id)
        special_taxes = ProgramSpecialTax.objects.filter(program = program).all()
        special_taxes.delete()
        program.delete()
    except BuyBackProgram.DoesNotExist:
        pass
    
    return redirect("/buybackprogram/")

### Configure Special taxes in a buyback program

#### Add Special Tax to a program
@login_required(login_url="/")
def add_special_taxes(request, program_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    program = BuyBackProgram.objects.get(id = program_id)
    program.max_tax = 100 - program.tax
    
    if request.method == "POST":
        items = request.POST.get("items_name")
        special_tax = int(request.POST.get("special_tax") or 0)
        allowed = request.POST.get("allowed")
        is_allowed = allowed == "true"
        
        data = apprisal_data(items, program)
        
        for item in data["items"]:
            
            ProgramSpecialTax.objects.get_or_create( 
                item_id=item["itemType"]["eid"], 
                program=program, 
                defaults={ 
                    "item_name": item["itemType"]["name"], 
                    "special_tax": special_tax, 
                    "is_allowed": is_allowed, 
                }
            )
            
        redirect(f"/buyback/{program_id}/special_taxes/")
    
    return render(request, 'buyback/special_taxes/add.html',{
        'main':main,
        'program':program
    })

#### Del special tax
@login_required(login_url="/")
def del_special_tax(request, program_id, special_tax_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    try:
        special_tax = ProgramSpecialTax.objects.get(id=special_tax_id)
        special_tax.delete()
    except ProgramSpecialTax.DoesNotExist:
        pass
    
    return redirect(f"/buybackprogram/{program_id}/special_taxes/")

### Configure locations

#### View list of locations
@login_required(login_url='/')
def locations(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_locations = Location.objects.all()
    
    return render(request, "buyback/locations/index.html",{
        "main": main,
        "locations": list_locations
    })

#### Add new locations
@login_required(login_url="/")
def add_location(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    
    if request.method == "POST":
        if Manager.objects.exists() == False:
            return render(request, "buyback/locations/add.html",{
                "main": main
            })
            
        manager = Manager.objects.first()
        structure_id = int(request.POST.get("station_id"))
        
        if structure_id > 0:
            data = structure_data(character=manager, structure_id=structure_id)
            print(data)
            if data != {}:
                Location.objects.get_or_create(
                    station_id = structure_id,
                    station_name = data["name"]
                )

                return redirect("..")
        
    return render(request, "buyback/locations/add.html",{
        "main": main
    })

#### Del location   
@login_required(login_url="/")
def del_location(request, structure_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    try:
        location = Location.objects.get(station_id=structure_id)
        location.delete()
    except Location.DoesNotExist:
        pass
    
    return redirect("/locations/")
 
# SHOP FEATURE VIEWS

## User views

### Shop view
@login_required(login_url="/")
def shop(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_items = Item.objects.all().exclude(quantity=0)
    cart = request.session.get("cart", {})

    if request.method == "POST":
        item_id = int(request.POST.get("product_id") or 0)
        quantity = int(request.POST.get("quantity") or 0)

        item = get_object_or_404(Item, item_id=item_id)
        nueva_cantidad = cart.get(str(item_id), 0) + quantity

        if nueva_cantidad > item.quantity:
            messages.warning(request, "There is not enough stock available")
            return redirect("/shop/")

        cart[str(item_id)] = nueva_cantidad
        request.session["cart"] = cart

        messages.success(request, "Item added to basket")
        return redirect("/shop/")

    cart_items = []
    total = 0

    for item_id, qty in cart.items():
        item = Item.objects.get(item_id=item_id)
        subtotal = item.price * qty
        total += subtotal

        cart_items.append({
            "item": item,
            "quantity": qty,
            "subtotal": subtotal,
        })

    return render(request, "shop/index.html", {
        "main": main,
        "list_items": list_items,
        "cart_items": cart_items,
        "total": total,
    })

### Remove item from the cart
@login_required(login_url="/")
def remove_from_cart(request, item_id):
    cart = request.session.get("cart", {})

    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session["cart"] = cart

    return redirect("/shop/")

### Confirm the order
@login_required(login_url="/")
def confirm_order(request):
    order = Order.objects.create(
        user=request.user,
        status=0
    )
    
    cart = request.session.get("cart", {})

    characters = string.ascii_letters + string.digits 
    order_id = f"{''.join(random.choices(characters, k=8))}-{''.join(random.choices(characters, k=8))}-{''.join(random.choices(characters, k=8))}"
    order.order_id = order_id
    order.save()
    
    for item_id, quantity in cart.items():
        item = Item.objects.get(item_id=item_id)

        ItemsOrder.objects.get_or_create(
            order=order,
            item=item,
            quantity=quantity
        )

        item.quantity -= quantity
        item.save()

    request.session["cart"] = {}

    messages.success(request, "Your order has been successfully created")
    return redirect("/shop/")

### View Order History User
@login_required(login_url="/")
def order_history(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_orders = Order.objects.filter(user=request.user).order_by('created_at').reverse()
    if request.user.groups.filter(name="Admin").exists() and request.path.endswith("/admin/"):
        list_orders = Order.objects.all().order_by('created_at').reverse()
    
    total_value = 0
    pending_orders = 0
    pending_orders_value = 0
    for order in list_orders:
        order.user.username = order.user.username.replace("_"," ")
        total_value += order.total_price()
        if order.status == 0:
            pending_orders += 1
            pending_orders_value += order.total_price()
    
    return render(request, "shop/order_history.html",{
        "main": main,
        "list_orders": list_orders,
        "total_value": total_value,
        "pending_orders": pending_orders,
        "pending_orders_value": pending_orders_value
    })

## Admin View

### View Item Sell Orders
@login_required(login_url="/")
def shop_items(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_items = Item.objects.all().exclude(quantity=0)
    
    return render(request, "shop/items/index.html",{
        "main": main,
        "list_items": list_items,
    })

### Add Item Sell Order
@login_required(login_url="/")
def add_shop_items(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    if request.method == "POST":
        item_name = request.POST.get("item_name")
        quantity = int(request.POST.get("quantity") or 0)
        price = int(request.POST.get("price") or 0)
        status = request.POST.get("status") == "true"
        
        data = apprisal_data(items=item_name)

        Item.objects.create(
            item_id = data["items"][0]["itemType"]["eid"],
            item_name=data["items"][0]["itemType"]["name"],
            quantity = quantity,
            price = price,
            status = status
        )
        
        return redirect("/shop/items/")
        
    
    return render(request, "shop/items/add.html",{
        "main": main,
        "status":0
    })

### Edit Item Sell Order
@login_required(login_url="/")
def edit_shop_items(request, item_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    item = Item.objects.get(item_id=item_id)
    
    if request.method == "POST":
        item_name = request.POST.get("item_name")
        quantity = int(request.POST.get("quantity") or 0)
        price = float(request.POST.get("price") or 0)
        status = request.POST.get("status") == "true"
        
        data = apprisal_data(items=item_name)

        item.item_id = data["items"][0]["itemType"]["eid"]
        item.item_name = data["items"][0]["itemType"]["name"]
        item.quantity = quantity
        item.price = price
        item.status = status
        item.save()
        
        return redirect("/shop/items/")
    
    return render(request, "shop/items/add.html",{
        "main": main,
        "item": item,
        "status": 1 
    })

### Remove Item Sell Order
@login_required(login_url="/")
def remove_item_shop(request, item_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    cart = request.session.get("cart", {})

    try:
        item = Item.objects.get(item_id=item_id)
        
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session["cart"] = cart
        
        item.delete()
    except Item.DoesNotExist:
        pass
    
    return redirect("/shop/items/")

### View Pending Orders
@login_required(login_url="/")
def pending_orders(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_orders = Order.objects.filter(status = 0)
    
    for order in list_orders:
        order.user.username = order.user.username.replace("_"," ")
    
    return render(request, "shop/orders.html",{
        "main": main,
        "list_orders": list_orders
    })

# Update Status Orders
@login_required(login_url="/")
def update_order_status(request, order_id, status):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")

    order = Order.objects.get(id = order_id)
    order.status = status
    order.save()
    
    if order.status == 3:
        list_items = order.order_items.all()
        for item_order in list_items:
            item = item_order.item
            item.quantity += item_order.quantity
            item.save()
    
    return redirect("/shop/")
    
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