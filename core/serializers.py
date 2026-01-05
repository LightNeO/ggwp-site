from rest_framework import serializers
from .models import CustomUser


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "avatar", "is_seller"]
        read_only_fields = ["is_seller"]
