# Part 6 — Django & Django REST Framework

## 6.1 Architecture: MTV and the Request Lifecycle

Django follows **MTV** — **M**odel (data), **T**emplate (presentation), **V**iew (business logic; the "controller" role is played by the framework + URLconf).

**Request lifecycle:**

1. WSGI/ASGI server (Gunicorn / Uvicorn) receives the request → `WSGIHandler`/`ASGIHandler`.
2. **Middleware** (request phase, top → bottom of `MIDDLEWARE`).
3. **URL resolver** matches `urls.py` patterns → view.
4. **View** runs (talks to models/ORM, services, cache).
5. Returns `HttpResponse` (template render or JSON).
6. **Middleware** (response phase, bottom → top).
7. Response sent to client.

```text
myproject/
  manage.py
  config/            # settings.py, urls.py, wsgi.py, asgi.py
  apps/
    orders/
      models.py  views.py  serializers.py  urls.py  admin.py
      services.py  selectors.py  signals.py  tasks.py  tests/
      migrations/
```

```bash
django-admin startproject config .
python manage.py startapp orders
python manage.py makemigrations && python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py shell_plus --print-sql   # django-extensions
```

## 6.2 Settings Essentials

```python
# settings.py
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.getenv("DEBUG") == "1"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "django_filters", "corsheaders",
    "apps.orders",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"], "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"], "HOST": os.environ["DB_HOST"], "PORT": 5432,
        "CONN_MAX_AGE": 60,          # persistent connections
        "ATOMIC_REQUESTS": False,
    }
}

AUTH_USER_MODEL = "users.User"      # set a custom user model at project start!
```

Split settings per environment (`base.py`, `dev.py`, `prod.py`) or use `django-environ`.

## 6.3 Models

```python
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True                         # no table; fields inherited


class Category(TimeStamped):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    def in_stock(self):
        return self.filter(stock__gt=0)


class Product(TimeStamped):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_active = models.BooleanField(default=True)
    tags = models.ManyToManyField("Tag", blank=True, related_name="products")
    metadata = models.JSONField(default=dict, blank=True)

    objects = ProductQuerySet.as_manager()      # Product.objects.active().in_stock()

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["category", "status"])]
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="price_non_negative"),
            models.UniqueConstraint(fields=["category", "name"], name="uniq_product_per_category"),
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Order(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(Product, through="OrderItem")   # M2M with extra data
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
```

**`on_delete` options:** `CASCADE` (delete children), `PROTECT` (block deletion), `RESTRICT`, `SET_NULL` (needs `null=True`), `SET_DEFAULT`, `SET(...)`, `DO_NOTHING`.

**`null` vs `blank`:** `null=True` → DB column allows NULL; `blank=True` → form/validation allows empty. For strings prefer `blank=True` with `""` instead of `null=True`.

### Model inheritance

| Type | Tables | Use |
|---|---|---|
| Abstract base (`abstract = True`) | Only children | Shared fields (timestamps) |
| Multi-table | Parent + child joined 1:1 | Real "is-a" with queries on parent |
| Proxy (`proxy = True`) | Same table | Different Python behaviour / manager / admin |

## 6.4 ORM — QuerySets

QuerySets are **lazy** — no SQL runs until evaluated (iteration, `list()`, slicing with step, `len()`, `bool()`, `repr()`). They are also **cached** after evaluation.

```python
from django.db.models import Q, F, Count, Sum, Avg, Max, Value, Case, When, Subquery, OuterRef, Exists
from django.db.models.functions import Coalesce, Lower, TruncMonth

Product.objects.all()
Product.objects.filter(price__gte=100, category__slug="phones")   # JOIN via __
Product.objects.exclude(status="draft")
Product.objects.get(pk=1)                    # DoesNotExist / MultipleObjectsReturned
Product.objects.filter(name__icontains="pro").order_by("-price")[:10]  # LIMIT 10
Product.objects.values("id", "name")         # dicts
Product.objects.values_list("id", flat=True) # [1, 2, ...]
Product.objects.only("id", "name")           # defer other columns
Product.objects.exists(); Product.objects.count()
obj, created = Product.objects.get_or_create(name="X", defaults={"price": 1, "category": c})
Product.objects.update_or_create(name="X", defaults={"price": 2})

# Field lookups
# exact, iexact, contains, icontains, in, gt, gte, lt, lte, startswith, range,
# isnull, date, year, month, regex

# Q objects: OR / NOT
Product.objects.filter(Q(price__lt=10) | Q(stock=0), ~Q(status="draft"))

# F expressions: reference columns, atomic updates (avoid race conditions)
Product.objects.filter(stock__lt=F("reorder_level"))
Product.objects.filter(pk=1).update(stock=F("stock") - 1)

# Aggregation (whole table) vs annotation (per row)
Product.objects.aggregate(avg=Avg("price"), total=Sum("stock"))
Category.objects.annotate(n=Count("products")).filter(n__gt=5).order_by("-n")

# Group by month
(Order.objects.annotate(month=TruncMonth("created_at"))
     .values("month").annotate(revenue=Sum("total")).order_by("month"))

# Conditional expressions
Product.objects.annotate(
    tier=Case(When(price__gte=1000, then=Value("premium")), default=Value("standard"))
)

# Subqueries
latest = Order.objects.filter(user=OuterRef("pk")).order_by("-created_at")
User.objects.annotate(
    last_order_total=Subquery(latest.values("total")[:1]),
    has_orders=Exists(Order.objects.filter(user=OuterRef("pk"))),
)

# Bulk operations — far fewer queries
Product.objects.bulk_create([Product(name=f"p{i}", price=1, category=c) for i in range(1000)], batch_size=500)
Product.objects.bulk_update(products, ["price"], batch_size=500)
Product.objects.filter(status="draft").delete()

# Raw SQL when needed (still parameterized)
Product.objects.raw("SELECT * FROM shop_product WHERE price > %s", [100])
from django.db import connection
with connection.cursor() as cur:
    cur.execute("SELECT count(*) FROM shop_product WHERE stock = %s", [0])
    cur.fetchone()

print(qs.query)            # see SQL
qs.explain(analyze=True)   # EXPLAIN on Postgres
```

### The N+1 Problem: `select_related` vs `prefetch_related`

```python
# N+1: 1 query for orders + 1 query per order for user
for o in Order.objects.all():
    print(o.user.email)

# select_related → SQL JOIN — for ForeignKey / OneToOne (forward)
for o in Order.objects.select_related("user"):
    print(o.user.email)                 # 1 query total

# prefetch_related → separate query + Python join — for M2M & reverse FK
for o in Order.objects.prefetch_related("items__product"):
    for item in o.items.all():          # 3 queries total, regardless of N
        print(item.product.name)

# Prefetch object for filtered/optimized prefetches
from django.db.models import Prefetch
Order.objects.prefetch_related(
    Prefetch("items", queryset=OrderItem.objects.select_related("product").filter(quantity__gt=1),
             to_attr="big_items")
)
```

Detect N+1 with `django-debug-toolbar`, `nplusone`, or `assertNumQueries` in tests.

## 6.5 Transactions and Concurrency

```python
from django.db import transaction

@transaction.atomic
def place_order(user, cart):
    # SELECT ... FOR UPDATE — lock rows until the transaction ends
    products = Product.objects.select_for_update().filter(id__in=cart.keys())
    order = Order.objects.create(user=user)
    for p in products:
        qty = cart[p.id]
        if p.stock < qty:
            raise ValueError(f"{p.name} out of stock")    # rolls back everything
        p.stock = F("stock") - qty
        p.save(update_fields=["stock"])
        OrderItem.objects.create(order=order, product=p, quantity=qty, unit_price=p.price)

    # Run side effects only after a successful commit
    transaction.on_commit(lambda: send_order_email.delay(order.id))
    return order

# Savepoints with nested atomic blocks
with transaction.atomic():
    create_user()
    try:
        with transaction.atomic():      # savepoint
            risky()
    except IntegrityError:
        pass                            # outer transaction still alive
```

Race-condition tools: `F()` expressions, `select_for_update(nowait=True / skip_locked=True)`, unique constraints + `IntegrityError` handling, optimistic locking with a `version` column.

## 6.6 Migrations

```bash
python manage.py makemigrations orders
python manage.py migrate
python manage.py showmigrations
python manage.py sqlmigrate orders 0003      # show SQL
python manage.py migrate orders 0002         # roll back
python manage.py squashmigrations orders 0001 0010
```

```python
# Data migration
from django.db import migrations

def forwards(apps, schema_editor):
    Product = apps.get_model("shop", "Product")       # use historical model!
    Product.objects.filter(status="").update(status="draft")

class Migration(migrations.Migration):
    dependencies = [("shop", "0004_product_status")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
```

**Zero-downtime tips:** add nullable columns first, backfill in batches, then add NOT NULL; create indexes concurrently on Postgres (`AddIndexConcurrently`, `atomic = False`); never rename/drop columns used by running code in the same deploy.

## 6.7 Views

### Function-Based Views

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET", "POST"])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product-detail", pk=pk)
    else:
        form = ProductForm(instance=product)
    return render(request, "shop/detail.html", {"product": product, "form": form})
```

### Class-Based Views

```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    paginate_by = 20
    template_name = "shop/list.html"
    context_object_name = "products"

    def get_queryset(self):
        qs = super().get_queryset().select_related("category")
        if q := self.request.GET.get("q"):
            qs = qs.filter(name__icontains=q)
        return qs

class ProductCreateView(PermissionRequiredMixin, CreateView):
    model = Product
    fields = ["name", "price", "category"]
    permission_required = "shop.add_product"
    success_url = reverse_lazy("product-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
```

CBV flow: `as_view()` → `dispatch()` → `get()/post()` → `get_queryset()`/`get_context_data()` → `render_to_response()`.

### URLs

```python
from django.urls import path, include
urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", product_detail, name="product-detail"),
    path("blog/<slug:slug>/", post_detail),
    path("api/", include("apps.api.urls")),
]
# reverse("product-detail", kwargs={"pk": 1}); in templates {% url 'product-detail' pk=1 %}
```

## 6.8 Templates and Forms (Quick)

```django
{% extends "base.html" %}
{% load static %}
{% block content %}
  {% for p in products %}
    <h3>{{ p.name|title }}</h3> <p>{{ p.price|floatformat:2 }}</p>
  {% empty %}
    <p>No products.</p>
  {% endfor %}
  <form method="post">{% csrf_token %}{{ form.as_p }}<button>Save</button></form>
{% endblock %}
```

```python
from django import forms
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "category"]
    def clean_price(self):
        price = self.cleaned_data["price"]
        if price > 1_000_000:
            raise forms.ValidationError("Too expensive")
        return price
    def clean(self):                      # cross-field validation
        data = super().clean()
        return data
```

Templates auto-escape HTML (XSS protection); `|safe` disables it — use carefully.

## 6.9 Middleware

```python
import time, logging, uuid
logger = logging.getLogger(__name__)

class RequestTimingMiddleware:
    def __init__(self, get_response):          # once at startup
        self.get_response = get_response

    def __call__(self, request):               # every request
        request.request_id = str(uuid.uuid4())
        start = time.monotonic()
        response = self.get_response(request)  # → next middleware / view
        response["X-Request-ID"] = request.request_id
        logger.info("%s %s %.1fms", request.method, request.path, (time.monotonic() - start) * 1000)
        return response

    def process_exception(self, request, exception):
        logger.exception("unhandled error id=%s", request.request_id)
        return None                            # let Django handle it
```

Other hooks: `process_view`, `process_template_response`. Order in `MIDDLEWARE` matters (e.g., `SecurityMiddleware` first, `SessionMiddleware` before `AuthenticationMiddleware`, `CorsMiddleware` high up).

## 6.10 Signals

```python
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
# Register in AppConfig.ready(): import apps.users.signals
```

Common signals: `pre_save`, `post_save`, `pre_delete`, `post_delete`, `m2m_changed`, `request_started`, `user_logged_in`. **Caution:** signals hide control flow, are not fired by `bulk_create`/`update()`/`QuerySet.delete()` (for pre/post_save) — prefer explicit service functions for business logic.

## 6.11 Authentication and Permissions

```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

# Usage
from django.contrib.auth import authenticate, login, logout
user = authenticate(request, username=email, password=pw)
if user: login(request, user)

user.has_perm("shop.change_product")
user.groups.add(Group.objects.get(name="editors"))
```

Passwords are hashed with PBKDF2 by default (Argon2 supported). Sessions stored in DB/cache; CSRF middleware protects cookie-authenticated POSTs.

## 6.12 Django REST Framework (DRF)

### Serializers

```python
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "category", "category_id", "discounted_price"]
        read_only_fields = ["stock"]

    def get_discounted_price(self, obj):
        return obj.price * 90 / 100

    def validate_price(self, value):                    # field-level
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

    def validate(self, attrs):                          # object-level
        if attrs.get("name", "").lower() == "test":
            raise serializers.ValidationError({"name": "Reserved name"})
        return attrs


class OrderCreateSerializer(serializers.Serializer):    # nested writes
    items = serializers.ListField(child=serializers.DictField(), min_length=1)

    def create(self, validated_data):
        return place_order(self.context["request"].user, validated_data["items"])
```

Flow: `serializer = S(data=request.data)` → `is_valid(raise_exception=True)` → `validated_data` → `save()` calls `create()` or `update()` → `serializer.data` for output.

### Views, ViewSets, Routers

```python
from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
    return Response({"ok": True})


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["name", "category__name"]
    ordering_fields = ["price", "created_at"]

    def get_queryset(self):
        return Product.objects.active().select_related("category").prefetch_related("tags")

    def get_serializer_class(self):
        return ProductListSerializer if self.action == "list" else ProductSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="restock")
    def restock(self, request, pk=None):
        product = self.get_object()
        qty = int(request.data.get("quantity", 0))
        Product.objects.filter(pk=product.pk).update(stock=F("stock") + qty)
        return Response({"status": "restocked"}, status=status.HTTP_200_OK)


# urls.py
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
urlpatterns = router.urls
# GET/POST /products/, GET/PUT/PATCH/DELETE /products/{id}/, POST /products/{id}/restock/
```

Hierarchy: `APIView` → `GenericAPIView` (+ mixins: `ListModelMixin`, `CreateModelMixin`, …) → concrete generics (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`) → `ViewSet` / `ModelViewSet`.

### Authentication, Permissions, Throttling, Pagination

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.UserRateThrottle",
                                 "rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"user": "1000/day", "anon": "100/day"},
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
}

# Custom object-level permission
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):            # view-level
        return request.user.is_authenticated
    def has_object_permission(self, request, view, obj): # called by get_object()
        return request.method in SAFE_METHODS or obj.owner_id == request.user.id

# Custom exception handler
from rest_framework.views import exception_handler
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {"error": {"status": response.status_code, "detail": response.data}}
    return response
```

Pagination options: `PageNumberPagination`, `LimitOffsetPagination`, `CursorPagination` (stable & efficient for large/real-time datasets).

## 6.13 Caching

```python
CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache",
                      "LOCATION": "redis://127.0.0.1:6379/1"}}

from django.core.cache import cache
from django.views.decorators.cache import cache_page

def get_dashboard(user_id):
    key = f"dashboard:{user_id}"
    return cache.get_or_set(key, lambda: build_dashboard(user_id), timeout=300)

cache.delete("dashboard:1")

@cache_page(60 * 15)                 # per-view cache
def product_list(request): ...
# Template fragment cache: {% load cache %}{% cache 500 sidebar %}...{% endcache %}
```

## 6.14 Celery (Background Tasks)

```python
# config/celery.py
import os
from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# apps/orders/tasks.py
from celery import shared_task

@shared_task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True, max_retries=5)
def send_order_email(self, order_id):
    order = Order.objects.select_related("user").get(pk=order_id)   # pass IDs, not objects
    send_mail("Order placed", f"#{order.id}", None, [order.user.email])

# Periodic tasks (celery beat)
CELERY_BEAT_SCHEDULE = {
    "nightly-report": {"task": "apps.reports.tasks.nightly", "schedule": crontab(hour=2, minute=0)},
}
```

```bash
celery -A config worker -l info --concurrency=4
celery -A config beat -l info
```

Best practices: idempotent tasks, pass primitive IDs, call `.delay()` inside `transaction.on_commit`, set time limits, use separate queues for slow/fast tasks.

## 6.15 Async Django

Django supports async views (3.1+), async ORM methods (`aget`, `acreate`, `afilter` iteration via `async for`) and ASGI deployment.

```python
from django.http import JsonResponse
import httpx

async def weather(request):
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.example.com/weather")
    product = await Product.objects.aget(pk=1)
    count = await Product.objects.filter(stock=0).acount()
    return JsonResponse({"weather": r.json(), "out_of_stock": count})

from asgiref.sync import sync_to_async
result = await sync_to_async(legacy_sync_function)()
```

Real-time features (WebSockets) use **Django Channels**.

## 6.16 Testing Django

```python
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.fixture
def api_client(django_user_model):
    user = django_user_model.objects.create_user(username="a", email="a@x.com", password="pw")
    client = APIClient()
    client.force_authenticate(user)
    return client

@pytest.mark.django_db
def test_create_product(api_client, category):
    resp = api_client.post(reverse("product-list"),
                           {"name": "Phone", "price": "999.00", "category_id": category.id},
                           format="json")
    assert resp.status_code == 201
    assert Product.objects.filter(name="Phone").exists()

@pytest.mark.django_db
def test_list_has_no_n_plus_one(api_client, django_assert_num_queries, products):
    with django_assert_num_queries(3):
        api_client.get(reverse("product-list"))
```

Tools: `pytest-django`, `factory_boy` (test data), `freezegun` (time), `responses`/`respx` (mock HTTP), `TestCase` (wraps each test in a transaction), `TransactionTestCase` (for on_commit/real transactions), `override_settings`.

## 6.17 Security Checklist

- `DEBUG = False`, strong `SECRET_KEY` from env, correct `ALLOWED_HOSTS`.
- `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`.
- Built-in protections: CSRF tokens, template auto-escaping (XSS), ORM parameterization (SQL injection), clickjacking (`X-Frame-Options`), password hashing & validators.
- Never use `extra()` / raw SQL with string formatting.
- Validate uploads; serve media from a separate domain/bucket.
- `python manage.py check --deploy`.

## 6.18 Performance and Deployment

- Fix N+1 (`select_related`/`prefetch_related`), use `only()/defer()`, `values()` for read-only data, `iterator(chunk_size=…)` for huge loops, `bulk_*` for writes, `exists()` instead of `count() > 0`.
- Add DB indexes for filter/order columns; analyse with `EXPLAIN`.
- Cache aggressively (Redis), use CDN for static files (`collectstatic`, WhiteNoise/S3).
- Run with Gunicorn (`gunicorn config.wsgi -w 4 -k gthread`) or Uvicorn for ASGI, behind Nginx.
- Connection pooling (`CONN_MAX_AGE`, PgBouncer, Django 5.1 native pool option for psycopg3).
- Offload slow work to Celery; monitor with Sentry, Prometheus, APM.

## 6.19 Service Layer Pattern (Clean Django)

```python
# services.py — writes / business logic
def product_create(*, name: str, price: Decimal, category: Category, user) -> Product:
    product = Product(name=name, price=price, category=category, created_by=user)
    product.full_clean()
    product.save()
    audit_log(user, "product_created", product.id)
    return product

# selectors.py — reads
def product_list(*, filters: dict | None = None) -> QuerySet[Product]:
    qs = Product.objects.active().select_related("category")
    return ProductFilter(filters or {}, qs).qs

# Views stay thin: validate input → call service/selector → serialize output
```

## 6.20 Interview Questions Checklist

- Explain the request/response lifecycle and middleware order.
- `select_related` vs `prefetch_related`; how to detect N+1.
- QuerySet laziness and caching; when is a query executed?
- `F()` and `Q()` objects; `annotate` vs `aggregate`.
- How `transaction.atomic` and `select_for_update` work; `on_commit`.
- `null` vs `blank`; `on_delete` options; custom user model.
- Signals: pros/cons; why they don't fire on `bulk_create`/`update`.
- CBV vs FBV; mixins and MRO.
- DRF: serializer validation flow, ViewSets vs APIView, permissions (`has_permission` vs `has_object_permission`), throttling, pagination.
- Celery: idempotency, retries, beat; why pass IDs.
- WSGI vs ASGI; async views.
- How Django protects against CSRF, XSS, SQL injection, clickjacking.
