from rest_framework import generics, permissions
from .models import Item, Order, Game, Category
from .serializers import ItemSerializer, GameSerializer, CategorySerializer


class GameListAPIView(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        game_id = self.request.GET.get("game_id")
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        return queryset


class ItemListAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = Item.objects.filter(status="active")
        game_slug = self.request.GET.get("game")
        if game_slug:
            queryset = queryset.filter(category__game__slug__iexact=game_slug)
        return queryset


class ItemDetailAPIView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemCreateAPIView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class MyItemsAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(seller=self.request.user)


class MyPurchasesAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        item_ids = Order.objects.filter(buyer=self.request.user).values_list(
            "item_id", flat=True
        )
        return Item.objects.filter(id__in=item_ids)
