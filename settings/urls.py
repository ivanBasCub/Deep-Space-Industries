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
from django.urls import path
from django.conf import settings
import web.views as web_views
import sso.views as sso_views

urlpatterns = [
    path('', web_views.index, name='index'),
    path('dashboard/', web_views.dashboard, name='dashboard'),
    # SSO URLs
    path('sso/login/', sso_views.eve_login_user, name='eve_login'),
    path('sso/callback/', sso_views.eve_callback, name='eve_callback'),
    path('sso/logout/', sso_views.eve_logout, name='logout'),
    # Buyback program
    path('buybackprogram/', web_views.buyback_program, name="index_buybackprogram"),
    path('buybackprogram/add/', web_views.add_buyback_program, name="add_program"),
    path('buybackprogram/<int:program_id>/edit/', web_views.edit_buyback_program, name="edit_program"),
    path('buybackprogram/<int:program_id>/del/', web_views.del_buyback_program, name="del_program"),    
    path('buybackprogram/<int:program_id>/calculate/', web_views.program_calculator, name="program_calculator"),
    # Manager
    path('manager/login/', sso_views.eve_login_manager, name="manager_login"),
    # Special Taxes
    path('buybackprogram/<int:program_id>/special_taxes/', web_views.special_taxes, name="program_special_taxes"),
    path('buybackprogram/<int:program_id>/special_taxes/add/', web_views.add_special_taxes, name="program_special_taxes"),
    path('buybackprogram/<int:program_id>/special_taxes/<int:special_tax_id>/del/',web_views.del_special_tax, name="del_special_tax"),
    # Locations
    path('locations/', web_views.locations, name="locations_index"),
    path('locations/add/', web_views.add_location, name="add_location"),
    path('locations/<int:structure_id>/del/', web_views.del_location, name="del_location"),
    # Shop
    path('shop/', web_views.shop, name="shop"),
    path('shop/order/confirm/', web_views.confirm_order, name="confirm_order"),
    path('shop/orders/', web_views.pending_orders, name="pending_orders"),
    path('shop/orders/history/', web_views.order_history, name="order_history"),
    path('shop/orders/history/admin/', web_views.order_history, name="order_history_admin"),
    path('shop/items/', web_views.shop_items, name="shop_items"),
    path('shop/items/add/', web_views.add_shop_items, name="add_shop_items"),
    path('shop/items/<int:item_id>/edit/', web_views.edit_shop_items, name="edit_shop_items"),
    path('shop/items/<int:item_id>/del/',web_views.remove_item_shop, name="del_item"),
    path('cart/<int:item_id>/del/', web_views.remove_from_cart, name="del_cart_item"),
    path('shop/orders/<int:order_id>/status/<int:status>/', web_views.update_order_status, name="update_status_orders"),
    # Projects
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