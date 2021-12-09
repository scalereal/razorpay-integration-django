from django.shortcuts import render
from .models import Order
from django.views.decorators.csrf import csrf_exempt
import razorpay
from payment_integration.config.settings.django import (
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
)
from .constants import PaymentStatus

# Create your views here.


def home(request):
    if request.method == "POST":
        name = request.POST.get("name")
        amount = int(request.POST.get("amount")) * 100
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        payment_order = client.order.create(
            {"amount": amount, "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            name=name, amount=amount, provider_order_id=payment_order["id"]
        )
        order.save()
        callback_url = "http://" + "127.0.0.1:8000" + "/success"
        return render(
            request,
            "index.html",
            {"callback_url": callback_url, "r_key": RAZORPAY_KEY_ID, "order": order},
        )
    return render(request, "index.html")

