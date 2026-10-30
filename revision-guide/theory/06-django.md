== intro
**What is Django?** Django is a **web framework** for Python, first released in 2005. A framework gives you a ready-made structure and tools for the common jobs every web application needs, so you focus on *your* features instead of reinventing the basics. Django's motto is "*the web framework for perfectionists with deadlines*", and it follows a "**batteries included**" philosophy. Out of the box it provides:

- an **ORM** to work with databases using Python classes instead of SQL;
- **migrations** to evolve the database structure safely;
- **URL routing**, **views** and **templates**;
- **authentication** (users, passwords, permissions, sessions);
- an automatic **admin panel** to manage your data;
- **forms** and validation;
- **security protections** (CSRF, XSS, SQL injection, clickjacking) enabled by default.

**Django REST Framework (DRF)** is a library on top of Django for building **REST APIs** that return JSON. It's what you use when the frontend is React or a mobile app.

**Project vs app:** a Django **project** is the whole website (settings, root URLs). It is made of several **apps**, each a self-contained feature module (`users`, `orders`, `payments`) with its own models, views and URLs. Apps keep large codebases organised and can be reused.

== 6.1
**MTV (Model–Template–View)** is how Django divides responsibilities:

- **Model:** your **data** and its rules. It is a Python class describing a database table.
- **Template:** the **presentation**, i.e. HTML with placeholders that get filled with data.
- **View:** the **logic** that receives a request, gets or changes data through models, and returns a response (a rendered template or JSON).

(This is the same idea as MVC: Django's "view" ≈ MVC's "controller", and Django's "template" ≈ MVC's "view".)

**What happens when a request arrives:**

1. A web server (Gunicorn for **WSGI**, the traditional synchronous interface, or Uvicorn for **ASGI**, the newer interface that supports async) passes the request to Django.
2. Django wraps it in an `HttpRequest` object and passes it through each **middleware** in order (security, sessions, authentication...).
3. The **URL dispatcher** compares the path with your `urls.py` patterns and picks the matching view.
4. The **view** runs your code and returns an `HttpResponse`.
5. The response passes back through the middleware in **reverse** order and is sent to the browser.

**`manage.py`** is the command-line tool for your project: start the dev server, create migrations, open a shell, create admin users, run tests.

== 6.2
`settings.py` is the **central configuration** of a Django project: which apps are installed, which database to use, middleware, templates, static files, security settings, time zone, and so on.

Important settings explained:

- **`SECRET_KEY`:** used to sign sessions, password-reset tokens and CSRF tokens. It must be secret and never committed to Git.
- **`DEBUG`:** shows detailed error pages. It must be `False` in production, because the debug pages leak sensitive information.
- **`ALLOWED_HOSTS`:** the domain names your site may be served from, which protects against host-header attacks.
- **`INSTALLED_APPS`:** every app (yours and third-party) that Django should load.
- **`DATABASES`:** connection details.
- **`MIDDLEWARE`:** the ordered list of middleware.
- **`AUTH_USER_MODEL`:** your custom user model. Set it **at the very start** of a project, because changing it later is painful.

Good practice: read secrets and environment-specific values from **environment variables**, and keep separate settings for development and production.

== 6.3
A **model** is a Python class that represents a **database table**. Each **attribute** (field) is a **column**, and each **instance** of the class is a **row**. You define your data once in Python, and Django creates the table and generates all the SQL for you.

```python
class Book(models.Model):                       # → table "app_book"
    title = models.CharField(max_length=200)    # → column VARCHAR(200)
    published = models.DateField()              # → column DATE
    price = models.DecimalField(max_digits=6, decimal_places=2)
# Django automatically adds:  id = primary key, auto-incrementing
```

**Field types** match data types: `CharField` (short text), `TextField` (long text), `IntegerField`, `DecimalField` (money), `BooleanField`, `DateTimeField`, `JSONField`, `EmailField`, and so on. **Field options** add rules: `unique=True`, `default=...`, `null=True` (database allows NULL), `blank=True` (forms allow empty), `choices=...`, `db_index=True`.

**Relationships between tables** (the core of relational databases, see 7.16):

- **`ForeignKey`** is a **many-to-one** relationship. Many orders belong to one user. It stores the user's id in the order table. **`on_delete`** decides what happens to the orders when the user is deleted (delete them too, block the deletion, or set the field to NULL).
- **`ManyToManyField`** is **many-to-many**. A product has many tags and a tag has many products. Django creates a hidden linking ("junction") table. Use `through=` to define it yourself when you need extra columns (e.g. quantity in an order item).
- **`OneToOneField`** is **one-to-one**. Each user has exactly one profile.

**`related_name`** sets the name used to go backwards: `user.orders.all()`.

**`Meta` class options:** default ordering, database indexes, constraints (unique combinations, check rules), and the table name.

**Managers and QuerySets:** `Product.objects` is the **manager**, the entry point for database queries. You can add custom query methods (`Product.objects.active()`) so filtering rules live in one place.

== 6.4
The **ORM (Object-Relational Mapper)** lets you query the database with Python instead of SQL. Django translates your Python calls into SQL, runs them, and turns the resulting rows back into Python objects.

A **QuerySet** represents a database query. Key properties:

- **Lazy:** building a QuerySet (`Product.objects.filter(price__gt=100)`) does **not** touch the database. The SQL runs only when you actually need the data: when you loop over it, call `list()`, `len()`, print it, and so on. You can keep chaining `.filter().exclude().order_by()` for free.
- **Chainable:** each method returns a new QuerySet, so you build queries step by step.
- **Cached:** once evaluated, a QuerySet keeps its results, so looping over it twice doesn't hit the database twice.

**Lookups** use double underscores: `price__gte=100` (≥), `name__icontains="pro"` (case-insensitive contains), `category__name="Phones"` (follow a relationship, which creates a JOIN), `created_at__year=2026`.

- **`Q` objects** build complex conditions with OR (`|`) and NOT (`~`).
- **`F` expressions** refer to a column's value *inside the database*. For example, `stock=F("stock") - 1` is done by the database atomically, avoiding race conditions where two requests read the same old value.
- **`aggregate()`** computes one summary over the whole QuerySet (total, average). **`annotate()`** adds a computed value to **each** row (e.g. the number of products per category).

**The N+1 query problem** is the most common ORM performance bug. You fetch a list of N orders (1 query), then access `order.user` for each one, and Django runs **one more query per order** (N queries). With 100 orders that's 101 queries instead of 1 or 2. The fixes:

- **`select_related("user")`** for ForeignKey/OneToOne: Django fetches the related row in the **same query using a SQL JOIN**.
- **`prefetch_related("items")`** for many-to-many and reverse relations: Django runs **one extra query** for all related objects and matches them up in Python.

== 6.5
A **transaction** groups several database operations into one **all-or-nothing** unit (see ACID in 7.15). If anything fails midway, everything is **rolled back** as if nothing happened. Placing an order, for example, creates the order, adds the items and decreases stock. You never want only half of that done.

- **`transaction.atomic`** (decorator or `with` block) makes the enclosed code one transaction. An exception inside means a rollback. Nested `atomic` blocks create **savepoints**, so an inner block can fail without undoing the outer one.
- **`transaction.on_commit(fn)`** runs `fn` only **after** the transaction has successfully committed. It is perfect for sending emails or starting background tasks, which should never happen if the data was rolled back.

**Concurrency problems:** two users buy the last item at the same moment. Both read `stock = 1`, both sell, and the stock becomes -1. Solutions:

- **`select_for_update()`** **locks** the selected rows until the transaction ends, so the second request waits until the first has finished.
- **`F()` expressions** do the arithmetic inside the database in a single atomic statement.
- **Database constraints** (e.g. `stock >= 0`) act as a final safety net.

== 6.6
Your models change over time: new fields, renamed tables, new relationships. **Migrations** are Django's version control for the database structure (**schema**).

1. You change `models.py`.
2. **`makemigrations`** compares your models with the previous migrations and writes a new migration file describing the changes ("add column `phone` to `user`").
3. **`migrate`** applies all unapplied migrations to the database. Django records which ones have run in a `django_migrations` table.

Migration files are committed to Git, so every developer and every server builds the exact same database structure. **Data migrations** (`RunPython`) transform existing data, e.g. filling a new column. In production, be careful with large tables: some operations lock the table, so big changes are done in small, backwards-compatible steps.

== 6.7
A **view** is a Python callable that **takes a request and returns a response**. That's the whole contract. Django supports two styles:

- **Function-Based Views (FBV):** a plain function `def my_view(request): ...`. They are explicit and easy to read, and good for unique or simple logic.
- **Class-Based Views (CBV):** a class with methods per HTTP method (`get()`, `post()`). Django ships **generic CBVs** for common patterns (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`) that do most of the work for you: you configure attributes like `model` and `template_name` and override small hooks like `get_queryset()`. Behaviour is combined through **mixins** (`LoginRequiredMixin`).

**URLconf (`urls.py`)** maps URL patterns to views. **Path converters** like `<int:pk>` capture parts of the URL and pass them as arguments to the view. Give each URL a **`name`** so you can build links with `reverse()` or `{% url %}` instead of hard-coding paths.

== 6.8
**Templates** are HTML files with special syntax that Django fills with data:

- `{{ variable }}` outputs a value, and **filters** transform it: `{{ name|upper }}`, `{{ price|floatformat:2 }}`.
- `{% tag %}` adds logic: `{% if %}`, `{% for %}`, `{% url %}`, `{% csrf_token %}`.
- **Template inheritance:** a `base.html` defines the common layout with `{% block %}` placeholders, and child templates `{% extends %}` it and fill in the blocks. You write the header and footer once.
- **Auto-escaping:** Django converts characters like `<` into `&lt;` automatically, so user content can't inject scripts (XSS protection).

**Forms** handle the full cycle of user input: render HTML inputs, receive submitted data, **validate** it (`is_valid()`), give clean Python values (`cleaned_data`), and show error messages. A **ModelForm** builds a form automatically from a model and can save it directly.

When React is your frontend, you mostly use DRF serializers instead of templates and forms, but the concepts are the same.

== 6.9
**Middleware** is a layer of code that wraps **every** request and response, like a chain of checkpoints. Each middleware can inspect or modify the request on the way **in**, stop it early by returning a response itself (for example, blocking a banned IP), and inspect or modify the response on the way **out**.

```text
Request  → SecurityMW → SessionMW → AuthMW → [ your view ] → AuthMW → SessionMW → SecurityMW → Response
```

Built-in middleware provides security headers, sessions, CSRF protection, authentication (`request.user`) and more. Custom middleware is for cross-cutting concerns that apply to all requests: logging, timing, request IDs, multi-tenant detection. **Order matters:** for example, authentication needs the session, so `SessionMiddleware` must come before `AuthenticationMiddleware`.

== 6.10
**Signals** let one part of the code **notify** other parts that something happened, without them being directly connected (the Observer pattern again). For example, *after a User is saved for the first time, automatically create a Profile*. You write a **receiver** function and connect it to a signal like `post_save` for a specific model.

Built-in signals fire around model saves and deletes, many-to-many changes, requests, and logins.

**Use them sparingly.** Signals make the flow of code hard to follow ("where did this record come from?"), and some bulk operations (`bulk_create`, `queryset.update()`) **don't** trigger them. For your own business logic, calling a function explicitly from a service is usually clearer.

== 6.11
Django ships a complete **authentication system**:

- A **User** model (username, password, email, `is_staff`, `is_superuser`, ...). Most projects define a **custom user model** (e.g. logging in with email) at the start.
- **Password hashing:** passwords are never stored in plain text. Django stores a salted hash (PBKDF2 by default, Argon2 optional) and handles checking it.
- **Sessions:** after `login()`, Django remembers the user via a session cookie, and `request.user` is available in every view. Anonymous visitors get an `AnonymousUser`.
- **Permissions and groups:** every model automatically gets add/change/delete/view permissions. Assign them to users or to **groups** (roles like "Editors") and check them with `user.has_perm(...)`.
- Tools to protect views: `@login_required`, `LoginRequiredMixin` and `PermissionRequiredMixin`.

== 6.12
**Django REST Framework (DRF)** turns Django into an API server that speaks JSON, which is what React and mobile apps consume. Its main building blocks:

**1. Serializers** convert between complex Python objects (model instances) and simple data types that can become JSON, in **both directions**:

- **Serialization (output):** model instance → dict → JSON response.
- **Deserialization (input):** JSON request body → validated Python data → saved model.

They also **validate** input: field types, required fields, and custom rules (`validate_<field>` for one field, `validate()` for rules involving several fields). A **`ModelSerializer`** builds its fields automatically from a model, much like a ModelForm.

**2. Views** handle requests. DRF offers increasing levels of automation:

- `APIView`: you write `get()`, `post()` and so on yourself.
- **Generic views** (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`) implement common patterns from a `queryset` and `serializer_class`.
- **ViewSets** (`ModelViewSet`) put list, create, retrieve, update and delete in **one class**. Combined with a **Router**, which generates all the URLs automatically, you get a full CRUD API in a few lines.

**3. Authentication** identifies who is calling (session, token, JWT via `simplejwt`). **Permissions** decide if they may proceed: `has_permission` is checked for every request to the view, and `has_object_permission` for a specific object (e.g. "only the owner can edit this post").

**4. Throttling** limits how many requests a client can make (rate limiting). **Pagination** splits large lists into pages. **Filtering, search and ordering** let clients ask for specific data via query parameters.

== 6.13
**Caching** in Django means storing the results of expensive work so it doesn't have to be redone on every request (see the cache-aside explanation in 4.11). Django provides one caching API with pluggable backends (Redis is the most common in production) at several levels:

- **Low-level cache API:** `cache.get` / `cache.set` / `cache.get_or_set` for any value you choose. This gives the most control.
- **Per-view cache:** `@cache_page(seconds)` caches a view's entire response.
- **Template fragment cache:** caches part of a template.

Always think about **invalidation**: when the underlying data changes, delete or refresh the cached copy, or keep the timeout short.

== 6.14
**Celery** is a **distributed task queue** for Python. It runs slow or scheduled work **in the background**, outside the request/response cycle. It is the Python equivalent of BullMQ (4.13).

How it works:

1. Your view calls `send_email.delay(user_id)`. This puts a **message** describing the task on a **broker** (Redis or RabbitMQ) and returns immediately. The user doesn't wait.
2. Separate **worker** processes listen to the broker, pick up tasks and execute them.
3. Failed tasks can be **retried** automatically with increasing delays.
4. **Celery Beat** is a scheduler that adds tasks on a timetable (e.g. "every night at 2 am, generate reports").

Best practices: pass **IDs** rather than model objects (the data may change before the task runs), make tasks **idempotent** (safe to run twice), and start tasks inside `transaction.on_commit` so they never run for data that was rolled back.

== 6.15
Traditionally Django is **synchronous**: each request occupies a worker until it finishes, including all the time spent waiting for external APIs. Modern Django (3.1+) also supports **async views** (`async def`), running under **ASGI** servers like Uvicorn. While one request awaits a slow network call, the same worker can serve other requests (see asyncio in 5.11).

The ORM offers async versions of its methods (`aget`, `acreate`, `acount`, `async for`). Sync-only code can be called from async code with `sync_to_async`. For **WebSockets** and real-time features, Django uses the **Channels** package.

Async helps most when views spend their time *waiting* on other services. It does not make CPU-heavy code faster.

== 6.16
Django has strong built-in testing support:

- Each test runs inside a **database transaction that is rolled back** afterwards, so tests don't affect each other. A separate test database is created automatically.
- The **test client** (or DRF's `APIClient`) sends fake requests to your views without a real server, and lets you force-authenticate a user.
- With **pytest-django** you write tests as simple functions and mark those that need the database with `@pytest.mark.django_db`.
- **factory_boy** generates realistic test objects with minimal code.
- `assertNumQueries` or `django_assert_num_queries` **catch N+1 regressions** by asserting how many SQL queries a view runs.

== 6.17
Django protects you from many common attacks **by default**. Understanding *how* is a frequent interview topic:

- **SQL injection:** the ORM always sends values separately from the SQL text (parameterization). Raw SQL must also use parameters.
- **XSS (Cross-Site Scripting):** templates auto-escape output.
- **CSRF (Cross-Site Request Forgery):** forms must include a secret `{% csrf_token %}` that other websites can't know, so they can't forge requests on behalf of your logged-in users.
- **Clickjacking:** an `X-Frame-Options` header prevents your site from being embedded invisibly in another site.
- **Passwords:** salted, slow hashing plus strength validators.

**Your job** is not to disable these protections and to configure production correctly: `DEBUG=False`, secret key from the environment, HTTPS-only cookies, HSTS. `manage.py check --deploy` lists what's missing.

== 6.18
Most Django performance problems come from the **database**: too many queries (N+1), fetching more columns or rows than needed, or missing indexes. So the checklist is about doing less database work, caching results, and moving slow work to background tasks.

**Deployment basics:** Django's `runserver` is for development only. In production, an application server (**Gunicorn** for WSGI, **Uvicorn** for ASGI) runs several worker processes, usually behind **Nginx** (which handles HTTPS and serves static files) or a cloud load balancer. **Static files** (CSS, JS, images) are collected with `collectstatic` and served by Nginx, WhiteNoise or a CDN. **Media files** (user uploads) go to object storage such as S3.

== 6.19
As projects grow, putting all logic in views or models becomes messy. Business rules get duplicated between the API, the admin, management commands and Celery tasks. A common solution is a **service layer**:

- **Services** (`services.py`) are functions that perform *actions*, such as creating an order or charging a card. They contain the business rules, validation and transactions.
- **Selectors** (`selectors.py`) are functions that *fetch* data, with the right filters and query optimisations.
- **Views** stay thin: parse input → call a service or selector → return the serialized output.

Each piece of business logic then has exactly one home, can be reused from anywhere, and is easy to unit-test.

== 6.20
For each question below, try to explain the answer **out loud in your own words**, as you would to an interviewer, then check the section above that covers it.
