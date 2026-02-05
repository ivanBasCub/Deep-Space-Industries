from django.urls import path
from . import views

urlpatterns = [
    path('', views.warehouse, name="warehouse"),
    path('bulk/',views.edit_tags_bulk, name="Edit bulk items tag"),
    path('<int:item_id>/del/', views.del_corp_item, name="Del corp item"),
]