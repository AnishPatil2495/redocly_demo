== intro
**What is Python?** Python is a general-purpose programming language created by Guido van Rossum in 1991. It is famous for **readability**: its code looks almost like English, and it uses **indentation** (spaces at the start of lines) instead of curly braces to group code. It is used for web backends (Django, FastAPI, Flask), data analysis, machine learning and AI, automation scripts, and much more.

**Your first program** (save as `hello.py` and run `python hello.py`):

```python
name = "World"                      # a variable — no `let`/`const` needed
print(f"Hello, {name}!")            # f-string: insert values inside {}

def square(n):                      # define a function with `def`
    return n * n                    # the indented block is the function body

if square(5) > 20:                  # a condition — note the colon and indentation
    print("big number")

for i in range(1, 4):               # loop: i = 1, 2, 3
    print("Count", i)

fruits = ["apple", "banana"]        # a list
person = {"name": "Anish", "age": 30}  # a dictionary (key → value)
print(person["name"])
```

**Python vs JavaScript, quick map:** `def` ↔ `function`; `None` ↔ `null`; `True/False` ↔ `true/false`; `and/or/not` ↔ `&&/||/!`; list `[]` ↔ array `[]`; dict `{}` ↔ object `{}`; indentation ↔ `{ }`; `#` comment ↔ `//`.

**The Zen of Python** (type `import this`) sums up the philosophy: "Readability counts", "Simple is better than complex", "There should be one obvious way to do it".

== 5.1
When you run `python app.py`, the standard interpreter (called **CPython**, because it's written in C) first **compiles** your code into **bytecode**, simple instructions stored in `__pycache__` folders, and then a **virtual machine** executes that bytecode line by line.

**Everything in Python is an object**: numbers, strings, functions, classes, even modules. Every object has:

- an **identity**, its address in memory (`id(x)`);
- a **type** (`type(x)`), which decides what operations it supports;
- a **value**.

**Variables are labels (names), not boxes.** `a = [1, 2]` creates a list object and sticks the label `a` on it. `b = a` sticks a *second label* on the **same** object. It doesn't copy. That's why changing the list through `b` is visible through `a`.

**`is` vs `==`:** `==` asks "do they have equal *values*?" `is` asks "are they the *same object*?" Use `is` only for `None` (`if x is None`).

**Mutable vs immutable.** *Mutable* objects can be changed in place (lists, dicts, sets). *Immutable* objects cannot (ints, strings, tuples). "Changing" an immutable value actually creates a new object. Only immutable values can be dictionary keys or set members, because they must be *hashable* (have a stable hash value).

**Dynamic but strong typing:** a variable can refer to any type (dynamic), but Python won't silently mix incompatible types. `"1" + 1` is an error, unlike JavaScript.

== 5.2
Python's built-in data types cover most needs:

- **`int`, `float`:** whole numbers (unlimited size) and decimal numbers. Use `decimal.Decimal` for money, because floats have rounding errors.
- **`str`:** text. It is immutable, and has many useful methods (`split`, `join`, `strip`, `replace`, `upper`). **f-strings** (`f"Hi {name}"`) are the modern way to format text.
- **`bool`:** `True`/`False`. **`None`** means "no value".
- **`list`:** an ordered, changeable collection: `[1, "a", 3.5]`. It is like a JS array.
- **`tuple`:** an ordered, **unchangeable** collection: `(1, 2)`. Use it for fixed groups of values, such as coordinates or returning multiple values from a function.
- **`set`:** an unordered collection of **unique** items, with very fast membership checks (`x in s`) and math-like operations (union, intersection).
- **`dict`:** a **key → value** mapping, `{"name": "A"}`. It is the most important Python data structure, with very fast lookup by key. It keeps insertion order.

**Indexing and slicing:** positions start at 0. Negative indexes count from the end (`-1` is the last). Slicing `s[start:stop:step]` extracts a part. `stop` is *not* included.

**Choosing a structure:** need order and duplicates? Use a list. Need uniqueness or fast "is it there?" checks? Use a set. Need to look things up by a name or ID? Use a dict. Need a fixed record? Use a tuple or dataclass.

== 5.3
**Control flow** decides which code runs and how often:

- **`if` / `elif` / `else`:** choose between branches.
- **`for item in collection`:** loop over any iterable (list, string, dict, file lines). Use `range(n)` for counting, `enumerate()` to get index and value together, and `zip()` to loop over several lists in parallel.
- **`while condition`:** repeat as long as the condition is true.
- **`break`** exits a loop early. **`continue`** skips to the next iteration.

**Comprehensions** are a concise, very "Pythonic" way to build a new list, dict or set from another collection, combining a loop and an optional filter in one line:

```python
# the long way
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x * x)

# the comprehension way — same result
squares = [x * x for x in range(10) if x % 2 == 0]
```

Read it as: "give me `x * x` **for** each `x` in `range(10)` **if** `x` is even". A **generator expression** uses `( )` instead of `[ ]` and produces values lazily, one at a time, without building the whole list in memory.

**Pattern matching** (`match`/`case`, Python 3.10+) compares a value against *shapes* (dict structure, list length, class type) and extracts parts of it. It is far more powerful than a simple switch statement.

== 5.4
A **function**, defined with `def`, is a named, reusable block of code. Python has very flexible parameter options:

- **Positional arguments:** matched by position, e.g. `greet("A", "Hi")`.
- **Keyword arguments:** matched by name, e.g. `greet(name="A", greeting="Hi")`. These are clearer and the order doesn't matter.
- **Default values:** `def greet(name, greeting="Hello")`.
- **`*args`** collects extra positional arguments into a tuple. **`**kwargs`** collects extra keyword arguments into a dict. They are used to write flexible functions and wrappers.

**The mutable default argument trap:** default values are created **once**, when the function is defined, not each time it is called. So a default list or dict is *shared between calls* and keeps growing. Use `None` as the default and create the list inside the function.

**`lambda`** creates a tiny anonymous one-expression function, e.g. `lambda x: x * 2`. It is used as a short argument to `sorted(key=...)`, `map` and `filter`.

**Scope (LEGB rule):** when Python looks up a name, it searches the **L**ocal function, then any **E**nclosing functions, then the **G**lobal (module) level, then **B**uilt-ins (`len`, `print`). To *assign* to an outer variable you must declare it with `global` or `nonlocal`. Without that, assigning creates a new local variable.

**Closures** work just like in JavaScript: an inner function remembers variables from the outer function that created it.

== 5.5
A **decorator** is a function that **wraps another function to add behaviour before and/or after it**, without changing that function's code. You apply it with `@decorator_name` on the line above a function definition.

Think of gift wrapping: the gift (your function) stays the same, but the wrapping adds something around it. Common uses are timing, logging, caching results, retrying on failure, and checking permissions. Django's `@login_required` is one example.

How it works, step by step:

1. Functions are objects, so they can be passed to other functions.
2. A decorator receives the original function and defines an inner **wrapper** function that does extra work and calls the original.
3. The decorator returns the wrapper.
4. `@timer` above `def f` is just shorthand for `f = timer(f)`. The name `f` now points to the wrapper.

```python
def shout(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)     # call the original
        return result.upper()              # add behaviour after
    return wrapper

@shout
def greet(name):
    return f"hello {name}"

greet("anish")   # 'HELLO ANISH'
```

Always use `@functools.wraps(func)` on the wrapper so the decorated function keeps its original name and docstring. A **decorator with arguments** (`@retry(times=3)`) needs one extra outer layer: a function that receives the arguments and returns the actual decorator.

== 5.6
**Iteration** is going through items one by one. Anything you can loop over with `for` is an **iterable** (lists, strings, dicts, files). Behind the scenes, `for` asks the iterable for an **iterator**, an object with a `__next__()` method that returns the next item each time and raises `StopIteration` when there are no more.

A **generator** is the easiest way to create an iterator. It's a function that uses **`yield`** instead of `return`. Each `yield` produces one value and **pauses** the function, keeping all its local variables. The next request resumes right after the `yield`.

Why this matters: **laziness**. A generator produces values *on demand*, so it can process a 50 GB log file or an endless stream using almost no memory, because only one item exists at a time. You can chain generators into processing **pipelines**: read lines → filter errors → parse → take the first 10.

**`itertools`** and **`collections`** are standard-library toolboxes. `itertools` has tools for combining, slicing and grouping iterators. `collections` adds `Counter` (count things), `defaultdict` (a dict with automatic default values), `deque` (a fast double-ended queue) and `namedtuple` (a tuple with named fields).

== 5.7
**Object-Oriented Programming (OOP)** organises code around **objects** that bundle data (**attributes**) and behaviour (**methods**). A **class** is the blueprint, and an **object/instance** is one thing built from it. (The concepts are the same as in JavaScript, see 1.8.)

Python specifics:

- **`__init__`** is the initialiser, called automatically when you create an object: `Rectangle(3, 4)`.
- **`self`** is the first parameter of every instance method and refers to the object the method was called on. Python passes it automatically. It is like JS's `this`, but explicit.
- **Instance attributes** (`self.name`) are separate for each object. **Class attributes** (defined directly in the class body) are shared by all instances.
- **`@classmethod`** receives the *class* (`cls`) instead of an instance. It is often used as an alternative constructor (`Rectangle.square(3)`). **`@staticmethod`** receives neither. It's just a utility function kept inside the class.
- **`@property`** makes a method behave like an attribute. You use it for computed values or to validate values when they are set.
- **Privacy is by convention:** `_name` means "internal, please don't touch". `__name` triggers *name mangling* (renamed internally) to avoid clashes in subclasses. Nothing is truly private.
- **Inheritance:** `class Rectangle(Shape)` reuses and extends `Shape`. **`super()`** calls the parent's version of a method.
- **Abstract base classes (`ABC`)** define methods subclasses *must* implement.

**Dunder ("double underscore") methods** such as `__str__`, `__eq__`, `__add__` and `__len__` let your objects work with Python's built-in syntax: `print(obj)`, `a == b`, `a + b`, `len(obj)`, `obj[i]`, `for x in obj`. Python calls them automatically. This is how Python's "protocols" work.

**MRO (Method Resolution Order):** with multiple inheritance, Python follows a fixed, predictable order to find which parent's method to use (shown by `Class.__mro__`). `super()` follows this order. Django's class-based views rely heavily on this through **mixins** (small classes that add one feature each).

**Dataclasses** (`@dataclass`) automatically generate `__init__`, `__repr__` and `__eq__` for classes that mainly hold data, which removes a lot of boilerplate.

== 5.8
Some resources must always be **released** after use, even if an error occurs: files must be closed, database transactions committed or rolled back, locks released. Forgetting this leads to leaks and corrupted data.

A **context manager**, used with the **`with`** statement, guarantees the setup and cleanup:

```python
with open("data.txt") as f:     # setup: open the file
    content = f.read()          # use it
# cleanup: the file is closed automatically here — even if read() raised an error
```

Under the hood, an object is a context manager if it has `__enter__` (runs at the start, and its return value goes into `as f`) and `__exit__` (always runs at the end and receives any exception). The `@contextmanager` decorator lets you write one as a simple generator: code before `yield` is the setup and code after it is the cleanup. Django's `transaction.atomic()` is a context manager.

== 5.9
An **exception** is Python's way of signalling that something went wrong at run time (a file not found, a bad conversion, a missing key). If nothing handles it, the program stops and prints a **traceback** (the chain of calls that led to the error). Read tracebacks from the **bottom**: the last line says what went wrong.

- **`try:`** contains code that might fail.
- **`except SomeError as e:`** handles that specific error type. Catch *specific* exceptions, never a bare `except:`, which would also hide bugs.
- **`else:`** runs only if no exception happened.
- **`finally:`** always runs, for cleanup.
- **`raise`** throws an exception yourself. **`raise NewError(...) from e`** links a new error to its original cause.

Common built-ins: `ValueError` (right type, bad value), `TypeError` (wrong type), `KeyError` (missing dict key), `IndexError` (list position out of range), `AttributeError`, `FileNotFoundError`, `ZeroDivisionError`.

Create **custom exceptions** by subclassing `Exception`, which gives your app meaningful error types (`NotFound`, `PaymentFailed`).

**EAFP vs LBYL:** Python style prefers "**E**asier to **A**sk **F**orgiveness than **P**ermission" (try it and catch the error) over "**L**ook **B**efore **Y**ou **L**eap" (check every condition first).

== 5.10
Python is dynamically typed, but since Python 3.5 you can add **type hints**: optional annotations describing what types variables, parameters and return values should have:

```python
def total(prices: list[float], discount: float = 0.0) -> float:
    ...
```

Key point: **Python itself ignores type hints at run time.** They are checked by separate tools (**mypy**, **pyright**, your editor) before running, much like TypeScript checks JavaScript. Benefits are the same as TypeScript: catching bugs early, better autocomplete, and self-documenting code.

Useful hint tools: `X | None` (may be None), `Literal["a", "b"]` (exact values), `TypedDict` (a dict with fixed keys), `Protocol` (structural typing: "any object that has these methods"), and generics with `TypeVar` or the new `def f[T](...)` syntax. Libraries like **Pydantic** *do* use type hints at run time to validate data. FastAPI and Django Ninja are built on that.

== 5.11
**Concurrency** means making progress on several tasks during overlapping time periods. **Parallelism** means literally running them at the same instant on multiple CPU cores.

**The GIL (Global Interpreter Lock):** in standard CPython, only **one thread can execute Python code at a time**. This has big consequences:

- For **I/O-bound** work (waiting for network, disk, database), threads still help a lot. While one thread waits, the GIL is released and another runs. Use `threading` / `ThreadPoolExecutor`, or `asyncio`.
- For **CPU-bound** work (heavy calculations), threads do *not* speed things up. Use **multiple processes** (`multiprocessing` / `ProcessPoolExecutor`). Each process has its own interpreter and its own GIL, so they truly run in parallel.

**`asyncio`** is Python's version of JavaScript's event loop and `async/await`. One thread runs many **coroutines** (functions defined with `async def`). Whenever a coroutine hits `await` on something slow, it pauses and lets another coroutine run. It is ideal for handling thousands of network connections efficiently (FastAPI, async Django). Rule: never call **blocking** functions (`time.sleep`, `requests.get`) inside async code, because they freeze the whole loop. Use async libraries (`httpx`, `aiohttp`) or `asyncio.to_thread`.

**Race condition:** when threads share data and the result depends on unlucky timing. Protect shared data with a **Lock**.

== 5.12
- A **module** is simply a `.py` file. You use its contents in another file with `import`.
- A **package** is a folder of modules, traditionally marked by an `__init__.py` file. Packages let you organise large projects (`myapp/services/payment.py`).
- **`if __name__ == "__main__":`** runs code only when the file is executed directly, not when it's imported by another file.

**Virtual environments** (`venv`) give each project its **own isolated set of installed packages**, so project A can use Django 4 while project B uses Django 5 on the same computer. Always create one per project.

**pip** installs packages from PyPI (the Python Package Index). Dependencies are listed in `requirements.txt` or, in modern projects, `pyproject.toml`. Tools like **Poetry** and **uv** manage environments and lock exact versions.

== 5.13
How Python manages memory, in simple terms:

- **Reference counting:** every object keeps a count of how many names or containers refer to it. When the count drops to zero, the memory is freed immediately.
- **Garbage collector:** reference counting can't free **cycles** (A refers to B and B refers to A, but nothing else refers to either). Python's cyclic garbage collector periodically finds and frees these.

**Shallow vs deep copy** (the same idea as JavaScript, see 1.3): `copy.copy()` creates a new outer container but shares the inner objects. `copy.deepcopy()` copies everything recursively.

**Descriptors** are an advanced mechanism: objects stored on a class that control what happens when an attribute is read or set on its instances. `@property`, methods and **Django model fields** all work through descriptors.

== 5.14
In Python, **classes are objects too**, and the thing that creates a class is called a **metaclass**. The default metaclass is `type`. A custom metaclass can automatically modify or register classes **at the moment they are defined**.

You will rarely write one yourself, but it explains "magic" in frameworks. When you write a Django model with `name = models.CharField()`, Django's metaclass reads those field declarations and builds the database mapping, the `objects` manager and more. For most needs, the simpler **`__init_subclass__`** hook or a class decorator is enough.

== 5.15
**pytest** is the most popular Python testing framework. A test is simply a function whose name starts with `test_`, using plain `assert` statements. Pytest finds and runs them automatically and shows clear failure messages.

Key concepts:

- **Fixtures** (`@pytest.fixture`) are reusable setup code (a test user, a database, an API client), injected into a test just by naming them as parameters.
- **Parametrize** runs the same test with many different inputs.
- **`pytest.raises`** checks that code raises the expected exception.
- **Mocking** (`unittest.mock`, `pytest-mock`) replaces real dependencies (a network call, sending an email) with fakes you control, so tests are fast and reliable and you can check how they were called.

== 5.16
These are common interview snippets and "predict the output" puzzles. For each puzzle, explain *why* it behaves that way using the concepts above: references, mutability, late binding of closures, and floating-point precision.
