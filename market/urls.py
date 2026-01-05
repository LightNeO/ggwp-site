from django.urls import path
from .views import (
    ItemListAPIView,
    ItemDetailAPIView,
    ItemCreateAPIView,
    MyItemsAPIView,
    MyPurchasesAPIView,
    GameListAPIView,
    CategoryListAPIView,
)

urlpatterns = [
    path("api/items/", ItemListAPIView.as_view()),
    path("api/items/create/", ItemCreateAPIView.as_view()),
    path("api/items/my/", MyItemsAPIView.as_view()),
    path("api/items/purchased/", MyPurchasesAPIView.as_view()),
    path("api/items/<int:pk>/", ItemDetailAPIView.as_view()),
    path("api/games/", GameListAPIView.as_view()),
    path("api/categories/", CategoryListAPIView.as_view()),
]
