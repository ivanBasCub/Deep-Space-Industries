"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import web.views as web_views

urlpatterns = [
    path('', web_views.index, name='index'),
    path('dashboard/', web_views.dashboard, name='dashboard'),
    # Feature Buyback program urls
    path('buybackprogram/', include('buyback.urls')),
    # SSO urls
    path('sso/',include('sso.urls')),
    # Shop urls
    path("shop/", include('shop.urls')),

    path('projects/', web_views.list_projects, name="projects"),
    path('projects/admin/', web_views.admin_projects, name="admin_projects"),
    path('projects/add/', web_views.add_project, name="add_project"),
    path('projects/<int:project_id>/finish/', web_views.finish_project, name="finsih_project"),
    path('projects/<int:project_id>/edit/', web_views.edit_project, name="edit_project"),
    path('projects/<int:project_id>/del/', web_views.del_project, name="del_project"),
    path('projects/<int:project_id>/view/', web_views.view_project, name="view_project"),
    path('projects/<int:project_id>/material/add/', web_views.add_material_project, name="add_material_to_project"),
    path('projects/<int:project_id>/material/<int:material_id>/edit/', web_views.edit_material_project, name="edit_material_of_project"),
    path('projects/<int:project_id>/material/<int:material_id>/del/', web_views.del_material_project, name="del_material_of_project"),
    # Warehouse
    path('warehouse/', web_views.warehouse, name="warehouse"),
    path('warehouse/bulk/',web_views.edit_tags_bulk, name="Edit bulk items tag"),
    path('warehouse/<int:item_id>/del/', web_views.del_corp_item, name="Del corp item"),
    # Admin Users
    path('users/', web_views.list_users, name="user_list"),
    path('users/<int:user_id>/edit/permissions/', web_views.edit_user_permissions, name="user_permissions")
]

if settings.DEBUG:
    urlpatterns += [
            path('admin/', admin.site.urls),
    ]