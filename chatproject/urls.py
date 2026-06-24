from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Chat App URLs
    path("", include("chat.urls")),

    # Accounts App URLs
    path("accounts/", include("accounts.urls")),
]