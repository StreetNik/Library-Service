from rest_framework import routers
from django.urls import path

from .views import PaymentViewSet


router = routers.DefaultRouter()

router.register(r"payments", PaymentViewSet, basename="payment-detail")

urlpatterns = [] + router.urls

app_name = "payments"
