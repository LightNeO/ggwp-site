from django.urls import path
from .views import create_item_checkout_session, payment_success, stripe_webhook

urlpatterns = [
    path("buy/<int:item_id>/", create_item_checkout_session, name="checkout"),
    path("success/", payment_success, name="payment_success"),
    path("webhook/", stripe_webhook, name="stripe_webhook"),
]
