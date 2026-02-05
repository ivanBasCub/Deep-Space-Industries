from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop, name="shop"),
    path('order/confirm/', views.confirm_order, name="confirm_order"),
    path('orders/', views.pending_orders, name="pending_orders"),
    path('orders/history/', views.order_history, name="order_history"),
    path('orders/history/admin/', views.order_history, name="order_history_admin"),
    path('items/', views.shop_items, name="shop_items"),
    path('items/add/', views.add_shop_items, name="add_shop_items"),
    path('items/<int:item_id>/edit/', views.edit_shop_items, name="edit_shop_items"),
    path('items/<int:item_id>/del/',views.remove_item_shop, name="del_item"),
    path('cart/<int:item_id>/del/', views.remove_from_cart, name="del_cart_item"),
    path('orders/<int:order_id>/status/<int:status>/', views.update_order_status, name="update_status_orders"),
]