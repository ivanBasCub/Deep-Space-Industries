from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_projects, name="projects"),
    path('admin/', views.admin_projects, name="admin_projects"),
    path('add/', views.add_project, name="add_project"),
    path('<int:project_id>/finish/', views.finish_project, name="finsih_project"),
    path('<int:project_id>/edit/', views.edit_project, name="edit_project"),
    path('<int:project_id>/del/', views.del_project, name="del_project"),
    path('<int:project_id>/view/', views.view_project, name="view_project"),
    path('<int:project_id>/material/add/', views.add_material_project, name="add_material_to_project"),
    path('<int:project_id>/material/<int:material_id>/edit/', views.edit_material_project, name="edit_material_of_project"),
    path('<int:project_id>/material/<int:material_id>/del/', views.del_material_project, name="del_material_of_project"),
]