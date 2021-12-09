from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("payment/", views.order_payment, name="payment"),
    path("success/", views.success, name="success"),
]

