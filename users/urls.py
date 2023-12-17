from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import routers

from .views import EmailTokenObtainPairView, RegisterView, UserProfileViewSet


urlpatterns = [
    path("users/", RegisterView.as_view(), name="user-registration"),
    path(
        "users/me/",
        UserProfileViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "update"}
        ),
        name="profile_info",
    ),
    path("users/token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

app_name = "users"
