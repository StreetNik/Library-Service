from rest_framework import routers
from django.urls import path

from .views import BorrowingViewSet, BorrowingReturnedSuccessfully

router = routers.DefaultRouter()

router.register(r"borrowings", BorrowingViewSet, basename="borrowing-detail")

urlpatterns = [
    path("borrowings/<int:borrowing_id>/returned-successfully",
         BorrowingReturnedSuccessfully.as_view(),
         name="borrowing-returned-successfully"),
] + router.urls

app_name = "borrowings"
