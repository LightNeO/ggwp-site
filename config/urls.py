from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    index,
    login_view,
    register_view,
    item_detail_view,
    profile_view,
    sell_view,
    ProfileAPIView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("wallet/", include("wallet.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("profile/", profile_view),
    path("sell/", sell_view),
    path("api/profile/", ProfileAPIView.as_view()),
    path("", include("market.urls")),
    path("", index, name="home"),
    path("login/", login_view),
    path("register/", register_view),
    path("items/<int:pk>/", item_detail_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
