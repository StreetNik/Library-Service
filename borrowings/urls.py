from rest_framework import routers

from .views import BorrowingViewSet


router = routers.DefaultRouter()

router.register(r"borrowings", BorrowingViewSet, basename="borrowing-detail")

urlpatterns = [] + router.urls

app_name = "borrowings"
