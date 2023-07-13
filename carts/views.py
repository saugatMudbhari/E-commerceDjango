from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from . models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from orders.forms import OrderForm


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# add_cart


def add_cart(request, product_id):
    current_user = request.user
    # get the product fro mprodcut_id
    product = Product.objects.get(id=product_id)

    # if user is authenticate
    if current_user.is_authenticated:
        product_variation = []  # get the variation and put it in prdcut _cvaritaion list
        if request.method == 'POST':  # checking for the epost req
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product_name=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(
            product=product, user=current_user).exists()  # check if the cart_ite mexist or not
        # get the cart_item
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(
                product=product,  user=current_user)  # filter the cart itmes

            # check if the current_variation is inside the existing_variation then increasing the qunatity of carat_item
            ex_var_list = []  # empty list #getting existin var list
            id = []  # id  of particular cart item
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list)

            if product_variation in ex_var_list:
                # increase cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1  # increament
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1,  user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

    else:
        product_variation = []  # get the variation and put it in prdcut _cvaritaion list
        if request.method == 'POST':  # checking for the epost req
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product_name=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except:
                    pass

        # getting the cart
        try:
            # get the cart using card_id present in the session
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:  # if no cart_id then creat cart
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(
            product=product, cart=cart).exists()  # check if the cart_ite mexist or not
        # get the cart_item
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(
                product=product, cart=cart)  # filter the cart itmes
            # check if the current_variation is inside the existing_variation then increasing the qunatity of carat_item
            ex_var_list = []  # empty list #getting existin var list
            id = []  # id  of particular cart item
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list)

            if product_variation in ex_var_list:
                # increase cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1  # increament
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')


# for removing product
def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id)
        # to decrease qunatity
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


# for removing  cart_item
def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


# cart
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        grand_total = 0
        tax = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (1 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'tax': tax,
    }
    return render(request, 'cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    grand_total = 0
    tax = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (1 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass  # just ignore

    form = OrderForm(initial={'email': request.user.email}
                     if request.user.is_authenticated else None)
    context = {
        'form': form,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'tax': tax,
    }
    return render(request, 'checkout.html', context)
