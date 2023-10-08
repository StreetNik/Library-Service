from rest_framework import routers

from .views import BookViewSet


router = routers.DefaultRouter()

router.register(r"books-list", BookViewSet, basename="book-detail")

urlpatterns = [] + router.urls

app_name = "books"
