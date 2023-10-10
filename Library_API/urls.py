from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/book/", include("books.urls")),
    path("api/user/", include("users.urls")),
    path("api/", include("borrowings.urls"))
]
