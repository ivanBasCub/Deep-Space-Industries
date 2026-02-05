from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from sso.views import CharacterEve
from esi.views import apprisal_data
from .models import Item, Order, ItemsOrder
import string
import random

# USER VIEW

## INDEX VIEW
@login_required(login_url="/")
def shop(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_items = Item.objects.all().exclude(quantity=0)
    cart = request.session.get("cart", {})

    if request.method == "POST":
        item_id = int(request.POST.get("product_id") or 0)
        quantity = int(request.POST.get("quantity") or 0)

        item = get_object_or_404(Item, item_id=item_id)
        nueva_cantidad = cart.get(str(item_id), 0) + quantity

        if nueva_cantidad > item.quantity:
            messages.warning(request, "There is not enough stock available")
            return redirect("/shop/")

        cart[str(item_id)] = nueva_cantidad
        request.session["cart"] = cart

        messages.success(request, "Item added to basket")
        return redirect("/shop/")

    cart_items = []
    total = 0

    for item_id, qty in cart.items():
        item = Item.objects.get(item_id=item_id)
        subtotal = item.price * qty
        total += subtotal

        cart_items.append({
            "item": item,
            "quantity": qty,
            "subtotal": subtotal,
        })

    return render(request, "shop/index.html", {
        "main": main,
        "list_items": list_items,
        "cart_items": cart_items,
        "total": total,
    })

## CART OPERATIONS

### REMOVE ITEM FROM CART
@login_required(login_url="/")
def remove_from_cart(request, item_id):
    cart = request.session.get("cart", {})

    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session["cart"] = cart

    return redirect("/shop/")

### CONFIRM THE ORDER
@login_required(login_url="/")
def confirm_order(request):
    order = Order.objects.create(
        user=request.user,
        status=0
    )
    
    cart = request.session.get("cart", {})

    characters = string.ascii_letters + string.digits 
    order_id = f"{''.join(random.choices(characters, k=8))}-{''.join(random.choices(characters, k=8))}-{''.join(random.choices(characters, k=8))}"
    order.order_id = order_id
    order.save()
    
    for item_id, quantity in cart.items():
        item = Item.objects.get(item_id=item_id)

        ItemsOrder.objects.get_or_create(
            order=order,
            item=item,
            quantity=quantity
        )

        item.quantity -= quantity
        item.save()

    request.session["cart"] = {}

    messages.success(request, "Your order has been successfully created")
    return redirect("/shop/")

## ORDER HISTORY
@login_required(login_url="/")
def order_history(request):
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_orders = Order.objects.filter(user=request.user).order_by('created_at').reverse()
    if request.user.groups.filter(name="Admin").exists() and request.path.endswith("/admin/"):
        list_orders = Order.objects.all().order_by('created_at').reverse()
    
    total_value = 0
    pending_orders = 0
    pending_orders_value = 0
    for order in list_orders:
        order.user.username = order.user.username.replace("_"," ")
        total_value += order.total_price()
        if order.status == 0:
            pending_orders += 1
            pending_orders_value += order.total_price()
    
    return render(request, "shop/order_history.html",{
        "main": main,
        "list_orders": list_orders,
        "total_value": total_value,
        "pending_orders": pending_orders,
        "pending_orders_value": pending_orders_value
    })

# ADMIN VIEW

## VIEW ITEM SELL ORDERS
@login_required(login_url="/")
def shop_items(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_items = Item.objects.all().exclude(quantity=0)
    
    return render(request, "shop/items/index.html",{
        "main": main,
        "list_items": list_items,
    })
    
## ADD NEW ITEM SELL ORDER
@login_required(login_url="/")
def add_shop_items(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    if request.method == "POST":
        item_name = request.POST.get("item_name")
        quantity = int(request.POST.get("quantity") or 0)
        price = int(request.POST.get("price") or 0)
        status = request.POST.get("status") == "true"
        
        data = apprisal_data(items=item_name)

        Item.objects.create(
            item_id = data["items"][0]["itemType"]["eid"],
            item_name=data["items"][0]["itemType"]["name"],
            quantity = quantity,
            price = price,
            status = status
        )
        
        return redirect("/shop/items/")
        
    
    return render(request, "shop/items/add.html",{
        "main": main,
        "status":0
    })
    
## EDIT ITEM SELL ORDER
@login_required(login_url="/")
def edit_shop_items(request, item_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    item = Item.objects.get(item_id=item_id)
    
    if request.method == "POST":
        item_name = request.POST.get("item_name")
        quantity = int(request.POST.get("quantity") or 0)
        price = float(request.POST.get("price") or 0)
        status = request.POST.get("status") == "true"
        
        data = apprisal_data(items=item_name)

        item.item_id = data["items"][0]["itemType"]["eid"]
        item.item_name = data["items"][0]["itemType"]["name"]
        item.quantity = quantity
        item.price = price
        item.status = status
        item.save()
        
        return redirect("/shop/items/")
    
    return render(request, "shop/items/add.html",{
        "main": main,
        "item": item,
        "status": 1 
    })
## REMOVE ITEM SELL ORDER
@login_required(login_url="/")
def remove_item_shop(request, item_id):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    cart = request.session.get("cart", {})

    try:
        item = Item.objects.get(item_id=item_id)
        
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session["cart"] = cart
        
        item.delete()
    except Item.DoesNotExist:
        pass
    
    return redirect("/shop/items/")

## VIEW LIST PENDING ORDERS
@login_required(login_url="/")
def pending_orders(request):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")
    
    main = CharacterEve.objects.filter(user=request.user, main_character=True).first()
    list_orders = Order.objects.filter(status = 0)
    
    for order in list_orders:
        order.user.username = order.user.username.replace("_"," ")
    
    return render(request, "shop/orders.html",{
        "main": main,
        "list_orders": list_orders
    })

## MANUAL UPDATE STATUS ORDER
@login_required(login_url="/")
def update_order_status(request, order_id, status):
    if not request.user.groups.filter(name="Admin").exists():
        return redirect("/dashboard/")

    order = Order.objects.get(id = order_id)
    order.status = status
    order.save()
    
    if order.status == 3:
        list_items = order.order_items.all()
        for item_order in list_items:
            item = item_order.item
            item.quantity += item_order.quantity
            item.save()
    
    return redirect("/shop/")