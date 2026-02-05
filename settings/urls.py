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
    # SSO urls
    path('sso/',include('sso.urls')),
    # Feature Buyback program urls
    path('buybackprogram/', include('buyback.urls')),
    # Feature Shop urls
    path("shop/", include('shop.urls')),
    # Feature Project urls
    path("projects/", include('project.urls')),

    
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