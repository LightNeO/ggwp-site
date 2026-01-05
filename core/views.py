from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import ProfileSerializer


def index(request):
    return render(request, "index.html")


def login_view(request):
    return render(request, "login.html")


def register_view(request):
    return render(request, "register.html")


def item_detail_view(request, pk):
    return render(request, "item_detail.html")


def profile_view(request):
    return render(request, "profile.html")


def sell_view(request):
    return render(request, "sell.html")


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
