from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sso.models import CharacterEve
from buyback.models import BuyBackProgram, ProgramSpecialTax, Location, BuyBackServices, Manager
from esi.views import structure_data, item_data_id

def index(request ):
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

# BUY BACK PROGRAMS 
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

## Add program
@login_required(login_url="/")
def add_buyback_program(request):
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

#TODO: Hacer la función edit_buyback_programs
# Edit Program
@login_required(login_url="/")
def edit_buyback_program(request, program_id):
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

# Del program
@login_required(login_url="/")
def del_buyback_program(request, program_id):
    try:
        program = BuyBackProgram.objects.get(id = program_id)
        special_taxes = ProgramSpecialTax.objects.filter(program = program).all()
        special_taxes.delete()
        program.delete()
    except BuyBackProgram.DoesNotExist:
        pass
    
    return redirect("/buybackprogram/")

# SPECIAL TAXES
## Index
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

## Add
@login_required(login_url="/")
def add_special_taxes(request, program_id):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    program = BuyBackProgram.objects.get(id = program_id)
    program.max_tax = 100 - program.tax
    
    if request.method == "POST":
        items = request.POST.get("items_name")
        special_tax = int(request.POST.get("special_tax") or 0)
        allowed = request.POST.get("allowed")
        item_list = [line.strip() for line in items.split("\n")]
        is_allowed = allowed == "true"
        
        for item in item_list:
            data = item_data_id(item)
            
            ProgramSpecialTax.objects.get_or_create( 
                item_id=item, 
                program=program, 
                defaults={ 
                    "item_name": data["name"], 
                    "special_tax": special_tax, 
                    "is_allowed": is_allowed, 
                }
            )
    
    return render(request, 'buyback/special_taxes/add.html',{
        'main':main,
        'program':program
    })

# LOCATIONS
## Index
@login_required(login_url='/')
def locations(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_locations = Location.objects.all()
    
    return render(request, "buyback/locations/index.html",{
        "main": main,
        "locations": list_locations
    })

## Add location to the database
@login_required(login_url="/")
def add_location(request):
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

@login_required(login_url="/")
def del_special_tax(request, program_id, special_tax_id):
    try:
        special_tax = ProgramSpecialTax.objects.get(id=special_tax_id)
        special_tax.delete()
    except ProgramSpecialTax.DoesNotExist:
        pass
    
    return redirect(f"/buybackprogram/{program_id}/special_taxes/")
    
## Remove location to the database    
@login_required(login_url="/")
def del_location(request, structure_id):
    try:
        location = Location.objects.get(station_id=structure_id)
        location.delete()
    except Location.DoesNotExist:
        pass
    
    return redirect("/locations/")
    