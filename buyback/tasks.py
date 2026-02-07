from celery import shared_task
from sso.models import CharacterEve
from .models import Contract, BuyBackProgram
from esi.views import corp_contracts
@shared_task
def check_buyback_contracts():
    contracts = corp_contracts()
    
    try:
        for contract in contracts:
            contract_id = contract["title"].split("-")
            character_id = contract["issuer_id"]
            if len(contract_id) != 3:
                continue
            
            try:
                program_id = int(contract_id[0])
            except ValueError:
                continue
            
            price = 0
            if "price" in contract:
                price = contract["price"]
                    
            program = BuyBackProgram.objects.get(id = program_id)
            character = CharacterEve.objects.get(character_id = character_id)
            status_map = {
                "outstanding": 1, 
                "finished": 2, 
                "cancelled": 3, 
                "deleted": 4,
            }
            new_status = status_map.get(contract["status"], 0)
            
            if Contract.objects.filter(contract_id = contract_id).exists():
                ct = Contract.objects.get(contract_id =contract_id)
                ct.status = new_status
                ct.save()
            else:
                Contract.objects.create(
                    contract_id=contract_id,
                    program = program,
                    character = character,
                    status = new_status,
                    price = price
                )
   
    except Exception as e:
        print(f"[ERROR] Ha ocurrido un error en el proceso {e}")