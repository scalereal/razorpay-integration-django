from django.shortcuts import render
from .models import Order
from django.views.decorators.csrf import csrf_exempt
import razorpay
from payment_integration.config.settings.django import (
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
)
from .constants import PaymentStatus
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def home(request):
    if request.method == "POST":
        return render(request, "index.html")
    return render(request, "index.html")


def order_payment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        order = Order.objects.create(name=name, amount=amount)
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        payment_order = client.order.create(
            {"amount": int(order.amount), "currency": "INR", "payment_capture": "1"}
        )
        order.provider_order_id = payment_order["id"]
        order.save()
        callback_url = "http://" + "127.0.0.1:8000" + "/razorpay/success/"
        return render(
            request,
            "payment.html",
            {"callback_url": callback_url, "r_key": RAZORPAY_KEY_ID, "order": order},
        )
    return render(request, "payment.html")


@csrf_exempt
def success(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    payment_id = request.POST.get("razorpay_payment_id", "")
    provider_order_id = request.POST.get("razorpay_order_id", "")
    signature_id = request.POST.get("razorpay_signature", "")
    order = Order.objects.get(provider_order_id=provider_order_id)

    if "razorpay_signature" in request.POST:
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if not verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return render(request, "success.html")
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return render(request, "success.html")
    else:
        order.status = PaymentStatus.FAILURE
        order.save()
        return render(request, "success.html")
