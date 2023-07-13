from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from carts.models import CartItem
from .models import Order, Payment, OrderProduct
from .forms import OrderForm
import requests

import json
from django.db.models import Q

import datetime

from django.core.mail import EmailMessage
from django.template.loader import render_to_string


# Create your views here.


def place_order(request, total=0, quantity=0,):
    current_user = request.user
    # if the cart item is 0 redirectto store page
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("store")

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (1 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store billing information inside table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.save()

            # GENERATE ORDER NUMBER
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number)
        context = {
            'order': order,
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'grand_total': grand_total,
            'tax': tax,
            'order_number': order_number,
        }
        return render(request, 'payments.html', context)

    else:
        return redirect('checkout')


def payments(request):
    # getting the payment data of customer
    payment_method = "khalti"
    token = request.GET.get("token")
    amount = request.GET.get("amount")
    orderID = request.GET.get("orderID")
    status = request.GET.get("status")
    # to check
    print(token, amount, orderID, status)

    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=orderID
    )

    # for Verifying khalti:
    url = "https://khalti.com/api/v2/payment/verify/"
    payload = {
        'token': token,
        'amount': amount,
    }
    headers = {
        'Authorization': 'Key test_secret_key_e614eb3b75e74acd911656189794d093'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    resp_dict = response.json()
    print(resp_dict)
    data = {
        "success": True
    }

    # store transaction detail on payment module
    payment = Payment(
        payment_id=token,
        user=request.user,
        amount_paid=amount,
        payment_method=payment_method,
        status=status,
    )
    payment.save()

    # payment success then order is_ordered is checked
    order.payment = payment
    order.is_ordered = True
    order.save()

    # mover the cart items to order prodcut table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.is_ordered = True
        orderproduct.save()

        # get the variation
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

    # cartitem delete after orderprodcut complete
    CartItem.objects.filter(user=request.user).delete()

    # send the order mail
    mail_subject = 'Thank You For Buying Our Product!'
    message = render_to_string('order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # send_order number & transaction id to sendData() via json
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def order_complete(request):
    return render(request, "order_complete.html")
