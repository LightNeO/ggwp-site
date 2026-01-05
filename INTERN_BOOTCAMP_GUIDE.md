# GGWP Marketplace: The Absolute Zero-to-Hero Intern Bootcamp 🎓

This is a **100% self-contained** manual. If you have nothing but this file, you can build, configure, and deploy the GGWP Marketplace to the cloud using **PostgreSQL**.

---

## 🏗️ Chapter 1: The Blueprint & Local DB

### 1.1 The Folder Structure
```text
ggwp-site/
├── .env                  # Secrets & API Keys
├── requirements.txt      # Dependencies
├── build.sh              # Production build script
├── config/               # Project Settings
├── core/                 # Users & Auth Bridge
├── market/               # Marketplace Logic
├── wallet/               # Payments & Orders
├── media/                # Uploads
└── templates/            # Frontend HTML
```

### 1.2 Local Database: PostgreSQL Installation
Unlike SQLite, PostgreSQL is a professional-grade server. You **must** install it locally.
1. Download **PostgreSQL** from [postgresql.org](https://www.postgresql.org/download/).
2. During installation, set a password for the `postgres` user.
3. Open **pgAdmin** or **psql** and create a database:
   ```sql
   CREATE DATABASE ggwp_db;
   ```
4. This database is now ready for your Django project to connect to.

### 1.3 Environment & Dependencies
```powershell
python -m venv venv
.\venv\Scripts\activate

# File: requirements.txt
django==5.0.1
djangorestframework==3.15.2
psycopg2-binary==2.9.10
python-dotenv==1.0.1
stripe==11.4.0
pillow>=11.0.0
djoser==2.3.1
gunicorn==23.0.0
whitenoise==6.8.2

pip install -r requirements.txt
```

### 1.4 Initialization Commands
```powershell
django-admin startproject config .
python manage.py startapp core
python manage.py startapp market
python manage.py startapp wallet
mkdir templates
mkdir media
```

---

## ⚙️ Chapter 2: Configuration

### 2.1 File: `.env`
```text
DB_NAME=ggwp_db
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_HOST=127.0.0.1
DB_PORT=5432
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 2.2 File: `config/settings.py` (Production Ready)
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-is-...")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost 127.0.0.1 .render.com").split()

# Render Production Specifics
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if "render.com" in h or "onrender.com" in h]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "core",
    "market",
    "wallet",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.TokenAuthMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_USER_MODEL = "core.CustomUser"
REST_FRAMEWORK = { "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.TokenAuthentication",) }
TEMPLATES = [{ "BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True, "OPTIONS": { "context_processors": [ "django.template.context_processors.debug", "django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages", ] } }]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL, MEDIA_ROOT = "/media/", BASE_DIR / "media"
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': { 'console': { 'class': 'logging.StreamHandler' } },
    'root': { 'handlers': ['console'], 'level': 'INFO' },
}
```

---

## 🔒 Chapter 3: Security & Bridge

### 3.1 File: `core/middleware.py`
```python
from rest_framework.authtoken.models import Token
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token_key = request.COOKIES.get('auth_token')
        if token_key:
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                request.user = token.user
            except Token.DoesNotExist:
                request.user = AnonymousUser()
        return None
```

---

## 📦 Chapter 4: Data Models

### 4.1 File: `core/models.py`
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_seller = models.BooleanField(default=False)
```

### 4.2 File: `market/models.py`
```python
from django.db import models
from django.conf import settings

class Game(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    def __str__(self): return self.name

class Category(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    def __str__(self): return f"{self.game.name} - {self.name}"

class Item(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to="items/", blank=True, null=True)
    status = models.CharField(max_length=20, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buys")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sales")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="completed")
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 🧠 Chapter 5: API Layer (DRF)

### 5.1 File: `market/serializers.py`
```python
from rest_framework import serializers
from .models import Item, Order, Game, Category

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class ItemSerializer(serializers.ModelSerializer):
    seller_username = serializers.ReadOnlyField(source="seller.username")
    game_name = serializers.ReadOnlyField(source="category.game.name")
    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ["seller", "status"]
```

---

## 🕹️ Chapter 6: Logic (Views)

### 6.1 File: `market/views.py`
```python
from rest_framework import generics, permissions
from .models import Item, Game, Category, Order
from .serializers import ItemSerializer

class ItemListAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    def get_queryset(self):
        queryset = Item.objects.filter(status="active")
        game = self.request.GET.get("game")
        if game: queryset = queryset.filter(category__game__slug__iexact=game)
        return queryset

class ItemCreateAPIView(generics.CreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer): serializer.save(seller=self.request.user)

class MyItemsAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self): return Item.objects.filter(seller=self.request.user)
```

### 6.2 File: `wallet/views.py`
```python
import stripe
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from market.models import Item, Order
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_item_checkout_session(request, item_id):
    item = Item.objects.get(id=item_id)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": item.title}, "unit_amount": int(item.price * 100)}, "quantity": 1}],
        mode="payment",
        success_url=f"http://localhost:8000/wallet/success/?item_id={item_id}",
    )
    return redirect(session.url, code=303)
```

---

## 🗺️ Chapter 7: Routing

### 7.1 File: `config/urls.py`
```python
from django.contrib import admin
from django.urls import path, include
from core.views import *

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
]

from django.views.static import serve
from django.urls import re_path
from django.conf import settings

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
```

---

## 🎨 Chapter 8: The Frontend (All 8 Templates)

### 8.1 File: `templates/base.html`
```html
<nav>
    <a href="/">Home</a>
    <a href="/login/" id="login-link">Login</a>
    <a href="/register/" id="register-link">Register</a>
    <a href="/sell/" id="sell-link" style="display: none;">Sell</a>
    <a href="/profile/" id="profile-link" style="display: none;">Profile</a>
    <a href="#" id="logout-link" style="display: none;" onclick="logout()">Logout</a>
</nav>
<script>
    (function () {
        const token = localStorage.getItem('auth_token');
        if (token) {
            document.getElementById('login-link').style.display = 'none';
            document.getElementById('register-link').style.display = 'none';
            ['sell-link', 'profile-link', 'logout-link'].forEach(id => document.getElementById(id).style.display = 'inline');
        }
    })();
    function logout() {
        localStorage.removeItem('auth_token');
        document.cookie = "auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        window.location.href = '/';
    }
</script>
```

---

## 🚀 Chapter 9: Operational Setup
1.  **Migrate**: `python manage.py makemigrations` and `python manage.py migrate`.
2.  **Superuser**: `python manage.py createsuperuser`.
3.  **Data**: Create a `Game` (slug: `dota-2`) and a `Category` in `/admin/`.
4.  **Launch**: `python manage.py runserver 8000`.

---

## 🌍 Chapter 10: Cloud Deployment (GitHub & Render)

### 10.1 Prepare for GitHub
1. Create a repository on GitHub.
2. Create a `.gitignore` file (Note: No SQLite database here!):
```text
venv/
*.pyc
.env
staticfiles/
media/
```
3. Push your code:
```powershell
git init
git add .
git commit -m "Launch ready"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 10.2 Create Build Script (`build.sh`)
```bash
#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
mkdir -p media/items media/avatars
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py initadmin
```

### 10.3 Render Setup in Detail

#### Step 1: Create the Cloud Database
1. Go to your **Render Dashboard** and click **New +** -> **PostgreSQL**.
2. **Name**: `ggwp-db` (or anything you like).
3. **Database**: `ggwp_db`
4. **User**: `postgres` (default)
5. **Region**: Choose the one closest to you (e.g., Oregon or Frankfurt).
6. Click **Create Database**.
7. **CRITICAL**: Once created, find the **Connection Details** section. You will need these for Step 3.

#### Step 2: Create the Web Service
1. Click **New +** -> **Web Service**.
2. Connect your **GitHub Repository**.
3. **Name**: `ggwp-marketplace`
4. **Environment**: `Python 3`
5. **Region**: Must be the **SAME** as your database region.
6. **Branch**: `main`
7. **Build Command**: `./build.sh`
8. **Start Command**: `gunicorn config.wsgi:application`

#### Step 3: Configure Environment Variables
Inside your Web Service, go to the **Env** tab and add these **Secrets**:

| Key | Value Source |
| :--- | :--- |
| `SECRET_KEY` | Generate a random 50-character string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
| `DB_NAME` | From Render Postgres "Database" field |
| `DB_USER` | From Render Postgres "User" field |
| `DB_PASSWORD` | From Render Postgres "Password" field |
| `DB_HOST` | From Render Postgres "Hostname" field |
| `DB_PORT` | `5432` |
| `STRIPE_PUBLIC_KEY` | Your Stripe Test Public Key |
| `STRIPE_SECRET_KEY` | Your Stripe Test Secret Key |

#### Step 4: Verify & Launch
1. Watch the **Logs** in Render. You should see "Collecting static files" and "Applying migrations."
2. Once the log says `Listening at: http://0.0.0.0:10000`, click your service URL.
3. **Success**: You are live! Login, list an item, and try a test purchase in production.

#### Step 5: Create a Production Admin User (Free Tier Workaround)
On the Render Free Tier, the "Shell" is a paid feature. To create your admin user for free, we use a custom script.

**1. Create the Script locally at `core/management/commands/initadmin.py`:**
```python
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "adminpass123")
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
```

**2. Configure Render:**
- In your **Render Dashboard**, go to **Web Service** -> **Env**.
- Add `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD`.
- **Save Changes**. Our `build.sh` will now create the admin automatically!

### ⚠️ Important: Production Media Files
Render's filesystem is **ephemeral**. This means:
- When you upload an image (Item or Avatar), it will work **immediately**.
- **BUT**, whenever you redeploy your code or Render restarts your server, those images will **DISAPPEAR**.
- For a "Real" production app, you would use a service like **Cloudinary** or **AWS S3** to store images permanently. 
- For this bootcamp, we are serving them directly from the server as a workaround.

#### Final Fix for Images in Chapter 7 (urls.py):
Ensure your `config/urls.py` explicitly serves media files even when not in DEBUG mode:
```python
from django.views.static import serve
from django.urls import re_path
# ... at the bottom of the file ...
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
```

Congratulations! You've built and deployed a modern digital marketplace using PostgreSQL! 🌐
