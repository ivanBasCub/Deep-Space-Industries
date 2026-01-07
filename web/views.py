from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sso.models import CharacterEve
from buyback.models import BuyBackProgram, ProgramSpecialTax, Location
from esi.views import structure_data

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
    
@login_required(login_url='/') 
def buyback_program(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    programs = BuyBackProgram.objects.all()
    
    for program in programs:
        program.special_taxes = ProgramSpecialTax.filter(program = program).count() 
    
    return render(request, 'buyback/index.html',{
        'main': main,
        'programs': programs
    })

#TODO Configure Add and Remove Locations

@login_required(login_url='/')
def locations(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_locations = Location.objects.all()
    
    return render(request, "buyback/locations/index.html",{
        "main": main,
        "locations": list_locations
    })

@login_required(login_url="/")
def add_location(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    
    if request.method == "POST":
        structure_id = int(request.POST.get("station_id"))
        if structure_id > 0:
            data = structure_data(character=main, structure_id=structure_id)
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
def del_location(request, structure_id):
    try:
        location = Location.objects.get(station_id=structure_id)
        location.delete()
    except Location.DoesNotExist:
        pass
    
    return redirect("/locations/")
    