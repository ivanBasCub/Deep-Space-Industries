from django.urls import path
from . import views

urlpatterns = [
    # Programs Index
    path('', views.buyback_program, name="index_buybackprogram"),
    path('add/', views.add_buyback_program, name="add_program"),
    path('<int:program_id>/edit/', views.edit_buyback_program, name="edit_program"),
    path('<int:program_id>/del/', views.del_buyback_program, name="del_program"),    
    path('<int:program_id>/calculate/', views.program_calculator, name="program_calculator"),
    path('contracts/', views.contract_history, name="contract_user_history"),
    path('contracts/admin/', views.admin_contract_history, name="contract_user_history"),
    # Special Taxes
    path('<int:program_id>/special_taxes/', views.special_taxes, name="program_special_taxes"),
    path('<int:program_id>/special_taxes/add/', views.add_special_taxes, name="program_special_taxes"),
    path('<int:program_id>/special_taxes/<int:special_tax_id>/del/',views.del_special_tax, name="del_special_tax"),
    # Locations
    path('locations/', views.locations, name="locations_index"),
    path('locations/add/', views.add_location, name="add_location"),
    path('locations/<int:structure_id>/del/', views.del_location, name="del_location")
]