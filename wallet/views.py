import stripe
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from market.models import Item, Order
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_item_checkout_session(request, item_id):
    item = Item.objects.get(id=item_id)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.title,
                    },
                    "unit_amount": int(item.price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"http://localhost:8000/wallet/success/?item_id={item_id}",
        cancel_url="http://localhost:8000/wallet/cancel/",
    )
    return redirect(session.url, code=303)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    if event["type"] == "checkout.session.completed":
        pass
    return JsonResponse({"status": "success"})


def payment_success(request):
    item_id = request.GET.get("item_id")
    item = Item.objects.get(id=item_id) if item_id else None

    if item and item.status == "active" and request.user.is_authenticated:
        Order.objects.create(
            buyer=request.user,
            seller=item.seller,
            item=item,
            amount=item.price,
            status="completed",
        )
        item.status = "sold"
        item.save()

    return render(request, "success.html", {"item": item})
