# Part 5 — Python: Basics to Advanced

## 5.1 How Python Runs

CPython compiles source to **bytecode** (`.pyc` in `__pycache__`) and executes it on a stack-based virtual machine. Everything is an **object** with an identity (`id()`), a type and a value. Python is **dynamically** and **strongly** typed (`'1' + 1` raises `TypeError`).

**Names are references.** Assignment binds a name to an object; it never copies.

```python
a = [1, 2]
b = a           # same object
b.append(3)
print(a)        # [1, 2, 3]
a is b          # True  (identity)
a == [1, 2, 3]  # True  (equality)

x = 256; y = 256; x is y   # True — small ints (-5..256) are cached; never rely on `is` for values
```

**Mutable:** `list`, `dict`, `set`, `bytearray`, user objects. **Immutable:** `int`, `float`, `bool`, `str`, `tuple`, `frozenset`, `bytes`, `None`.

## 5.2 Core Data Types

### Strings

```python
s = "Hello, World"
s.lower(), s.upper(), s.title()
s.split(", ")              # ['Hello', 'World']
", ".join(["a", "b"])      # 'a, b'
s.strip(), s.replace("l", "L"), s.startswith("He"), s.find("o")
s[::-1]                    # reverse
s[0:5]                     # slicing [start:stop:step]

name, score = "Anish", 92.456
f"{name:>10} | {score:.2f} | {score:08.3f} | {1_000_000:,}"
f"{name=}"                 # "name='Anish'"  (debug)
```

### Lists, Tuples, Sets, Dicts

```python
nums = [3, 1, 2]
nums.append(4); nums.extend([5, 6]); nums.insert(0, 0)
nums.pop(); nums.remove(3)
sorted(nums, reverse=True)       # new list
nums.sort(key=lambda x: -x)      # in-place

t = (1, 2, 3)
a, *rest = t                     # unpacking: a=1, rest=[2,3]
single = (1,)                    # comma makes the tuple

s = {1, 2, 3}
s | {4}, s & {1, 9}, s - {1}, s ^ {1, 9}   # union, intersection, difference, sym. diff

d = {"a": 1, "b": 2}
d.get("z", 0)                    # default if missing
d.setdefault("c", []).append(1)
d.items(), d.keys(), d.values()
merged = d | {"b": 99}           # 3.9+ merge
{**d, "x": 1}                    # unpack merge
del d["a"]; d.pop("b", None)
```

### Time complexity

| Operation | list | dict / set |
|---|---|---|
| Index / lookup | O(1) index, O(n) `in` | O(1) average |
| Append | O(1) amortized | O(1) |
| Insert/delete at start | O(n) | — |
| Sort | O(n log n) | — |

Use `collections.deque` for O(1) appends/pops at both ends.

## 5.3 Control Flow and Comprehensions

```python
# Comprehensions
squares = [x * x for x in range(10) if x % 2 == 0]
matrix_t = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
word_len = {w: len(w) for w in ["hi", "there"]}
unique = {x % 3 for x in range(10)}
gen = (x * x for x in range(10**9))   # generator expression — lazy, O(1) memory

# for/else — else runs if loop wasn't broken
for n in nums:
    if n < 0:
        break
else:
    print("no negatives")

# Walrus operator (3.8+)
if (n := len(data)) > 10:
    print(f"too long: {n}")

# enumerate / zip
for i, (name, age) in enumerate(zip(names, ages), start=1):
    print(i, name, age)

# Structural pattern matching (3.10+)
def handle(event):
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"click at {x},{y}"
        case {"type": "key", "key": "Enter" | "Return"}:
            return "submit"
        case [first, *others]:
            return f"list starting with {first}"
        case Point(x=0, y=0):
            return "origin"
        case _:
            return "unknown"
```

## 5.4 Functions

```python
def greet(name, greeting="Hello", *args, sep=", ", **kwargs):
    return f"{greeting}{sep}{name}"

greet("A", "Hi", sep=" ")

# Positional-only (/) and keyword-only (*) parameters
def f(a, b, /, c, *, d):
    ...
f(1, 2, 3, d=4)       # a,b positional-only; d keyword-only

# Mutable default argument pitfall
def add_item(item, bucket=[]):     # BAD — same list shared across calls
    bucket.append(item)
    return bucket

def add_item(item, bucket=None):   # GOOD
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket

# Lambdas, map/filter, functools
from functools import reduce, partial
square = lambda x: x * x
list(map(square, [1, 2]))
list(filter(lambda x: x > 1, [1, 2, 3]))
reduce(lambda acc, x: acc + x, [1, 2, 3], 0)
int_from_bin = partial(int, base=2)
int_from_bin("101")   # 5
```

### Scope — LEGB

Lookup order: **L**ocal → **E**nclosing → **G**lobal → **B**uilt-in.

```python
count = 0
def outer():
    total = 0
    def inner():
        nonlocal total       # modify enclosing variable
        global count         # modify global
        total += 1
        count += 1
        return total
    return inner

counter = outer()
counter(); counter()         # 2  — closure keeps `total` alive
```

## 5.5 Decorators

A decorator is a callable that takes a function and returns a new function.

```python
import time
import functools

def timer(func):
    @functools.wraps(func)                # preserves __name__, __doc__
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

# Decorator with arguments → three levels
def retry(times=3, exceptions=(Exception,), delay=0.5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    time.sleep(delay * 2 ** (attempt - 1))
        return wrapper
    return decorator

@timer
@retry(times=5, exceptions=(ConnectionError,))
def call_api():
    ...

# Built-in caching
@functools.lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

# Class-based decorator
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func, self.calls = func, 0
    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)
```

Decorators are applied bottom-up: `@a @b def f` ⇒ `f = a(b(f))`.

## 5.6 Iterators and Generators

```python
# Iterator protocol: __iter__ returns self, __next__ raises StopIteration
class Countdown:
    def __init__(self, start): self.current = start
    def __iter__(self): return self
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

# Generator — much simpler
def countdown(n):
    while n > 0:
        yield n
        n -= 1

def read_large_file(path):
    with open(path) as f:
        for line in f:          # file objects are lazy iterators
            yield line.rstrip("\n")

# Pipeline of generators — processes GBs with constant memory
lines = read_large_file("app.log")
errors = (l for l in lines if "ERROR" in l)
first_10 = list(itertools.islice(errors, 10))

# yield from — delegate to sub-generator
def flatten(items):
    for x in items:
        if isinstance(x, list):
            yield from flatten(x)
        else:
            yield x

# send() — coroutine-style generator
def averager():
    total = count = 0
    avg = None
    while True:
        value = yield avg
        total += value; count += 1
        avg = total / count
g = averager(); next(g); g.send(10); g.send(20)  # 15.0
```

### itertools / collections

```python
import itertools as it
from collections import Counter, defaultdict, deque, namedtuple, OrderedDict, ChainMap

it.chain([1], [2]); it.product("ab", repeat=2); it.permutations([1, 2, 3], 2)
it.combinations([1, 2, 3], 2); it.groupby(sorted(data, key=k), key=k)
it.accumulate([1, 2, 3]); it.count(10); it.cycle("ab"); it.batched(range(10), 3)  # 3.12

Counter("mississippi").most_common(2)     # [('i', 4), ('s', 4)]
graph = defaultdict(list); graph["a"].append("b")
q = deque(maxlen=3); q.appendleft(1); q.rotate(1)
Point = namedtuple("Point", "x y")
```

## 5.7 Object-Oriented Python

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    count = 0                          # class attribute (shared)

    def __init__(self, name: str):
        self.name = name               # instance attribute
        Shape.count += 1

    @abstractmethod
    def area(self) -> float: ...

    @classmethod
    def total(cls) -> int:             # receives the class — alternative constructors
        return cls.count

    @staticmethod
    def unit() -> str:                 # no self/cls — utility namespaced in class
        return "cm"

    def __str__(self):  return f"{self.name}: {self.area():.2f}{self.unit()}²"   # user-facing
    def __repr__(self): return f"{type(self).__name__}(name={self.name!r})"      # dev-facing


class Rectangle(Shape):
    def __init__(self, w: float, h: float):
        super().__init__("rect")
        self._w = w                    # "protected" by convention
        self.__secret = 1              # name-mangled → _Rectangle__secret
        self.h = h

    @property
    def w(self):                       # getter
        return self._w

    @w.setter
    def w(self, value):
        if value <= 0:
            raise ValueError("width must be positive")
        self._w = value

    def area(self):
        return self._w * self.h

    @classmethod
    def square(cls, side):
        return cls(side, side)


r = Rectangle.square(3)
r.w = 4
print(r, repr(r), Shape.total())
```

### Dunder (Magic) Methods

```python
class Money:
    __slots__ = ("amount", "currency")         # no __dict__ → less memory, faster attrs

    def __init__(self, amount, currency="INR"):
        self.amount, self.currency = amount, currency
    def __add__(self, other):                  # +
        self._check(other)
        return Money(self.amount + other.amount, self.currency)
    def __eq__(self, other):                   # ==
        return (self.amount, self.currency) == (other.amount, other.currency)
    def __lt__(self, other): return self.amount < other.amount
    def __hash__(self): return hash((self.amount, self.currency))  # needed if __eq__ defined
    def __bool__(self): return self.amount != 0
    def __repr__(self): return f"Money({self.amount}, {self.currency!r})"
    def _check(self, o):
        if o.currency != self.currency:
            raise ValueError("currency mismatch")

# Container protocol
class Playlist:
    def __init__(self, songs): self._songs = list(songs)
    def __len__(self): return len(self._songs)
    def __getitem__(self, i): return self._songs[i]        # enables indexing, slicing, iteration
    def __contains__(self, s): return s in self._songs
    def __iter__(self): return iter(self._songs)
    def __call__(self): return self._songs[0]              # instance is callable
```

### Inheritance and MRO

```python
class A:
    def hello(self): return "A"
class B(A):
    def hello(self): return "B" + super().hello()
class C(A):
    def hello(self): return "C" + super().hello()
class D(B, C):
    pass

D().hello()   # 'BCA'
D.__mro__     # (D, B, C, A, object) — C3 linearization; super() follows the MRO, not the parent
```

**Mixins** add reusable behaviour (heavily used in Django CBVs: `LoginRequiredMixin`, etc.).

### Dataclasses

```python
from dataclasses import dataclass, field, asdict

@dataclass(frozen=True, slots=True, order=True)
class Employee:
    name: str
    salary: float = 0.0
    skills: list[str] = field(default_factory=list)   # never use a mutable default directly

    def __post_init__(self):
        if self.salary < 0:
            raise ValueError("salary < 0")

e = Employee("A", 100, ["python"])
asdict(e)
```

Also know: `typing.NamedTuple`, `enum.Enum`, `Pydantic` models (validation; used by FastAPI, Django Ninja).

## 5.8 Context Managers

```python
with open("a.txt") as f, open("b.txt", "w") as g:
    g.write(f.read())

# Class-based
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False       # True would suppress the exception

# Generator-based
from contextlib import contextmanager, suppress

@contextmanager
def db_transaction(conn):
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()

with suppress(FileNotFoundError):
    os.remove("tmp.txt")
```

## 5.9 Exceptions

```python
class AppError(Exception):
    """Base for app errors."""

class NotFound(AppError):
    def __init__(self, resource, id_):
        super().__init__(f"{resource} {id_} not found")
        self.resource, self.id = resource, id_

try:
    value = int(user_input)
except (ValueError, TypeError) as e:
    logger.warning("bad input: %s", e)
    raise AppError("invalid number") from e      # exception chaining
else:
    print("runs only if no exception")
finally:
    print("always runs")

# Exception groups (3.11+)
try:
    raise ExceptionGroup("many", [ValueError(1), TypeError(2)])
except* ValueError as eg:
    print("value errors", eg.exceptions)
```

EAFP ("easier to ask forgiveness than permission") is idiomatic: try the operation and catch the exception rather than checking first.

## 5.10 Type Hints

```python
from typing import TypedDict, Protocol, Literal, Callable, TypeVar, Generic, Optional, Any, Final, overload
from collections.abc import Iterable, Iterator, Sequence, Mapping

def total(prices: list[float], discount: float | None = None) -> float: ...

Status = Literal["active", "inactive"]

class UserDict(TypedDict, total=False):
    id: int
    name: str

class SupportsClose(Protocol):          # structural typing (duck typing for type checkers)
    def close(self) -> None: ...

T = TypeVar("T")
def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None

# 3.12 generic syntax
def last[T](items: list[T]) -> T: return items[-1]
class Box[T]:
    def __init__(self, item: T): self.item = item
type Pair[T] = tuple[T, T]

Handler = Callable[[str, int], bool]
MAX_RETRIES: Final = 3
```

Check with `mypy` or `pyright`. Type hints are not enforced at runtime (use Pydantic for that).

## 5.11 Concurrency: Threads, Processes, Asyncio

**GIL (Global Interpreter Lock):** in standard CPython only one thread executes Python bytecode at a time. Consequences:

- **I/O-bound** → threads or `asyncio` work well (GIL released during I/O).
- **CPU-bound** → use `multiprocessing` / `ProcessPoolExecutor` (separate interpreters), or C extensions (NumPy). Python 3.13+ offers an experimental **free-threaded** (no-GIL) build.

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import requests

urls = [...]
with ThreadPoolExecutor(max_workers=10) as pool:              # I/O-bound
    futures = {pool.submit(requests.get, u, timeout=5): u for u in urls}
    for fut in as_completed(futures):
        print(futures[fut], fut.result().status_code)

def crunch(n): return sum(i * i for i in range(n))
if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:                        # CPU-bound
        print(list(pool.map(crunch, [10**6] * 8)))

# Thread safety
import threading
lock = threading.Lock()
counter = 0
def incr():
    global counter
    with lock:
        counter += 1
```

### asyncio

```python
import asyncio
import aiohttp

async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.json()

async def main():
    async with aiohttp.ClientSession() as session:
        # run concurrently
        results = await asyncio.gather(*(fetch(session, u) for u in urls), return_exceptions=True)

        # limit concurrency
        sem = asyncio.Semaphore(5)
        async def bounded(u):
            async with sem:
                return await fetch(session, u)

        # structured concurrency (3.11+)
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(bounded(urls[0]))
            t2 = tg.create_task(bounded(urls[1]))

        # timeout
        async with asyncio.timeout(3):
            await fetch(session, urls[2])

        # run blocking code without blocking the loop
        data = await asyncio.to_thread(blocking_io_function)

asyncio.run(main())
```

Never call blocking functions (`time.sleep`, `requests.get`) inside `async def` — use `await asyncio.sleep`, `httpx.AsyncClient`, etc.

## 5.12 Modules, Packages and Environments

```python
# package/
#   __init__.py
#   utils.py
from package.utils import helper       # absolute import
from .utils import helper              # relative import (inside package)

if __name__ == "__main__":             # runs only when executed directly
    main()
```

- Virtual envs: `python -m venv .venv && source .venv/bin/activate`; tools: `pip`, `pip-tools`, `poetry`, `uv`.
- `pyproject.toml` is the modern project config (dependencies, build, ruff/black/mypy config).
- Formatting & linting: `ruff`, `black`, `isort`; testing: `pytest`.

## 5.13 Memory Model and Internals

- **Reference counting** frees objects immediately when the count hits zero; a **cyclic garbage collector** (`gc` module) handles reference cycles.
- `sys.getrefcount(obj)`, `sys.getsizeof(obj)`, `tracemalloc` for leak hunting.
- **Shallow vs deep copy:**

```python
import copy
a = [[1, 2], [3]]
b = copy.copy(a)        # new outer list, same inner lists
c = copy.deepcopy(a)    # fully independent
b[0].append(99)         # affects a, not c
```

- **Interning:** short strings/identifiers may be interned; `sys.intern()`.
- **Descriptors:** objects with `__get__/__set__/__delete__`; power `property`, methods, `classmethod`, and Django model fields.

```python
class Positive:
    def __set_name__(self, owner, name): self.name = "_" + name
    def __get__(self, obj, objtype=None): return getattr(obj, self.name)
    def __set__(self, obj, value):
        if value <= 0: raise ValueError(f"{self.name[1:]} must be > 0")
        setattr(obj, self.name, value)

class Order:
    qty = Positive()
    def __init__(self, qty): self.qty = qty
```

## 5.14 Metaclasses (Advanced)

A metaclass is the "class of a class" — `type` by default. Used by Django ORM (`ModelBase`) to turn field declarations into a model.

```python
class RegistryMeta(type):
    registry = {}
    def __new__(mcls, name, bases, ns):
        cls = super().__new__(mcls, name, bases, ns)
        if bases:
            mcls.registry[name.lower()] = cls
        return cls

class Plugin(metaclass=RegistryMeta): ...
class CsvExporter(Plugin): ...
RegistryMeta.registry   # {'csvexporter': <class CsvExporter>}

# Often simpler: __init_subclass__
class Base:
    plugins = []
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        Base.plugins.append(cls)
```

## 5.15 Testing with pytest

```python
# test_cart.py
import pytest
from cart import Cart

@pytest.fixture
def cart():
    return Cart()

def test_add_item(cart):
    cart.add("apple", 2)
    assert cart.total_items == 2

@pytest.mark.parametrize("qty, expected", [(1, 10), (3, 30), (0, 0)])
def test_price(cart, qty, expected):
    cart.add("x", qty, price=10)
    assert cart.total == expected

def test_negative_qty_raises(cart):
    with pytest.raises(ValueError, match="positive"):
        cart.add("x", -1)

def test_external_api(mocker):                     # pytest-mock
    mock_get = mocker.patch("cart.requests.get")
    mock_get.return_value.json.return_value = {"rate": 1.1}
    assert Cart().convert(10) == 11

# unittest.mock directly
from unittest.mock import patch, MagicMock
with patch("module.send_email") as fake:
    do_signup()
    fake.assert_called_once_with("a@b.com")
```

## 5.16 Common Interview Snippets

```python
# Reverse words
" ".join(reversed("hello big world".split()))

# Anagram check
from collections import Counter
Counter("listen") == Counter("silent")

# Two sum — O(n)
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return seen[target - n], i
        seen[n] = i

# Flatten nested dict
def flatten(d, parent=""):
    out = {}
    for k, v in d.items():
        key = f"{parent}.{k}" if parent else k
        out.update(flatten(v, key) if isinstance(v, dict) else {key: v})
    return out

# LRU cache implementation
from collections import OrderedDict
class LRU:
    def __init__(self, cap): self.cap, self.d = cap, OrderedDict()
    def get(self, k):
        if k not in self.d: return -1
        self.d.move_to_end(k); return self.d[k]
    def put(self, k, v):
        self.d[k] = v; self.d.move_to_end(k)
        if len(self.d) > self.cap: self.d.popitem(last=False)

# Singleton
class Singleton:
    _instance = None
    def __new__(cls, *a, **kw):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Tricky outputs:**

```python
print([[0] * 2] * 2)        # [[0,0],[0,0]] but rows share the same list!
x = [[0] * 2] * 2; x[0][0] = 1; print(x)   # [[1,0],[1,0]] — use [[0]*2 for _ in range(2)]
print(0.1 + 0.2 == 0.3)     # False → math.isclose
print(bool([]), bool([0]))  # False True
print(round(2.5), round(3.5))  # 2 4 — banker's rounding
fs = [lambda: i for i in range(3)]; print([f() for f in fs])  # [2,2,2] — late binding
fs = [lambda i=i: i for i in range(3)]                       # [0,1,2]
```
