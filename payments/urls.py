from rest_framework import routers
from django.urls import path
from .views import PaymentViewSet, OrderSuccess, OrderCancel


router = routers.DefaultRouter()

router.register(r"payments", PaymentViewSet, basename="payment-detail")

urlpatterns = [
    path("payments/paid_successfully/", OrderSuccess.as_view(), name="order_success"),
    path("payments/cancel", OrderCancel.as_view(), name="order_cancel"),
] + router.urls

app_name = "payments"
