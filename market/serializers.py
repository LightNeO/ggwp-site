from rest_framework import serializers
from .models import Item, Order, Game, Category


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["id", "name", "slug", "image"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "game"]


class ItemSerializer(serializers.ModelSerializer):
    seller_username = serializers.ReadOnlyField(source="seller.username")
    category_name = serializers.ReadOnlyField(source="category.name")
    game_name = serializers.ReadOnlyField(source="category.game.name")

    class Meta:
        model = Item
        fields = [
            "id",
            "title",
            "price",
            "description",
            "image",
            "seller",
            "seller_username",
            "category",
            "category_name",
            "game_name",
            "status",
        ]
        read_only_fields = ["seller", "status"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
