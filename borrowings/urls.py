from rest_framework import routers
from django.urls import path

from .views import BorrowingViewSet


router = routers.DefaultRouter()

router.register(r"borrowings", BorrowingViewSet, basename="borrowing-detail")

urlpatterns = [
    path(
        "borrowings/<int:pk>/return/",
        BorrowingViewSet.as_view({"post": "return_borrowing"}),
        name="return-borrowing",
    ),
] + router.urls

app_name = "borrowings"
