# Part 1 — JavaScript: Basics to Advanced

## 1.1 How JavaScript Runs

JavaScript is a single-threaded, dynamically typed, prototype-based language with first-class functions. It runs inside a **host environment** (browser, Node.js, Deno, Bun) that provides APIs such as the DOM, `fetch`, timers, and file system access.

**Engine pipeline (V8):** source → parser → AST → Ignition (bytecode interpreter) → TurboFan (optimizing JIT compiler). Hot functions are optimized based on observed types; if types change ("megamorphic" call sites), code is deoptimized. Practical takeaway: keep object shapes consistent (initialize all properties in the constructor, in the same order).

**Execution context** has three parts:

1. **Variable environment** — `var` declarations and function declarations.
2. **Lexical environment** — `let`, `const`, `class` bindings, plus a reference to the outer environment (this chain is the *scope chain*).
3. **`this` binding**.

Each context is created in two phases: **creation** (hoisting — memory allocated for declarations) and **execution** (code runs line by line).

## 1.2 Variables, Scope and Hoisting

| Keyword | Scope | Hoisted? | Re-declare | Re-assign | TDZ |
|---|---|---|---|---|---|
| `var` | Function | Yes, initialized to `undefined` | Yes | Yes | No |
| `let` | Block | Yes, uninitialized | No | Yes | Yes |
| `const` | Block | Yes, uninitialized | No | No (binding only) | Yes |

```javascript
console.log(a); // undefined   (var hoisted & initialized)
var a = 1;

console.log(b); // ReferenceError: Cannot access 'b' before initialization (TDZ)
let b = 2;

const obj = { x: 1 };
obj.x = 2;      // OK — const freezes the binding, not the value
// obj = {};    // TypeError

// Function declarations are fully hoisted; function expressions are not
hoisted();      // works
function hoisted() { return 'hi'; }

notHoisted();   // TypeError: notHoisted is not a function
var notHoisted = function () {};
```

**Classic loop bug** — `var` is function-scoped, so all callbacks share one `i`:

```javascript
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i)); // 3 3 3
for (let j = 0; j < 3; j++) setTimeout(() => console.log(j)); // 0 1 2 (new binding per iteration)
```

## 1.3 Data Types

**Primitives (7):** `string`, `number`, `bigint`, `boolean`, `undefined`, `symbol`, `null`. Primitives are immutable and compared by value.
**Reference type:** `object` (includes arrays, functions, dates, maps, sets…). Compared by reference.

```javascript
typeof null;          // 'object'  (historical bug)
typeof function(){};  // 'function'
typeof 10n;           // 'bigint'
Array.isArray([]);    // true — the reliable array check

0.1 + 0.2 === 0.3;                     // false (IEEE-754 double)
Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON; // true
Number.MAX_SAFE_INTEGER;               // 9007199254740991 → use BigInt beyond
NaN === NaN;                           // false → use Number.isNaN(x)
Object.is(NaN, NaN);                   // true
Object.is(0, -0);                      // false
```

### Type Coercion and Equality

`==` performs coercion; `===` does not. Always prefer `===` except `x == null` (checks both `null` and `undefined`).

```javascript
'5' + 3      // '53'  (+ with a string concatenates)
'5' - 3      // 2     (- coerces to number)
[] + {}      // '[object Object]'
[] == false  // true  ([] → '' → 0, false → 0)
null == 0    // false (null only == undefined)
!!''         // false

// Falsy values: false, 0, -0, 0n, '', null, undefined, NaN — everything else is truthy
```

### Copying: Shallow vs Deep

```javascript
const original = { a: 1, nested: { b: 2 } };

const shallow = { ...original };          // or Object.assign({}, original)
shallow.nested.b = 99;                    // also changes original.nested.b!

const deep = structuredClone(original);   // modern deep clone (handles Map, Set, Date, cycles)
// JSON.parse(JSON.stringify(o)) loses functions, undefined, Dates, Maps
```

## 1.4 Functions

```javascript
// Declaration
function add(a, b = 0) { return a + b; }    // default parameter

// Expression & arrow
const mul = (a, b) => a * b;

// Rest & spread
function sum(...nums) { return nums.reduce((acc, n) => acc + n, 0); }
sum(...[1, 2, 3]); // 6

// IIFE
(function () { /* private scope */ })();

// Higher-order function
const withLogging = (fn) => (...args) => {
  console.log('calling with', args);
  return fn(...args);
};
```

**Arrow functions vs regular functions:**

- No own `this` — they capture `this` lexically from the enclosing scope.
- No `arguments` object, cannot be used with `new`, no `prototype`.
- Ideal for callbacks; avoid as object methods that need `this`.

## 1.5 `this` Binding Rules

Precedence (highest first):

1. **`new` binding** — `new Foo()` → `this` is the new object.
2. **Explicit** — `call`, `apply`, `bind`.
3. **Implicit** — `obj.method()` → `this` is `obj`.
4. **Default** — standalone call → `undefined` in strict mode, `globalThis` otherwise.
5. Arrow functions ignore all rules and use lexical `this`.

```javascript
const user = {
  name: 'Anish',
  greet() { return `Hi ${this.name}`; },
  greetLater() { setTimeout(() => console.log(this.name), 0); }, // arrow keeps this
};

const g = user.greet;
g();                        // 'Hi undefined' — lost implicit binding
g.call({ name: 'Ravi' });   // 'Hi Ravi'
g.apply({ name: 'Ravi' }, []);
const bound = g.bind(user); // permanently bound
bound();                    // 'Hi Anish'
```

### Polyfill for `bind` (common interview question)

```javascript
Function.prototype.myBind = function (ctx, ...preset) {
  const fn = this;
  return function (...later) {
    return fn.apply(ctx, [...preset, ...later]);
  };
};
```

## 1.6 Closures

A **closure** is a function bundled with references to its surrounding lexical environment. The inner function keeps access to outer variables even after the outer function returns.

```javascript
function createCounter() {
  let count = 0;                 // private state
  return {
    inc: () => ++count,
    dec: () => --count,
    get: () => count,
  };
}
const c = createCounter();
c.inc(); c.inc();
c.get(); // 2

// Memoization with closures
function memoize(fn) {
  const cache = new Map();
  return function (...args) {
    const key = JSON.stringify(args);
    if (!cache.has(key)) cache.set(key, fn.apply(this, args));
    return cache.get(key);
  };
}

// once()
function once(fn) {
  let called = false, result;
  return (...args) => (called ? result : (called = true, result = fn(...args)));
}
```

**Uses:** data privacy, factories, memoization, currying, debouncing, React hooks (each render closes over its props/state — the root of the "stale closure" bug).

### Currying and Partial Application

```javascript
const curry = (fn) =>
  function curried(...args) {
    return args.length >= fn.length
      ? fn.apply(this, args)
      : (...next) => curried.apply(this, [...args, ...next]);
  };

const add3 = curry((a, b, c) => a + b + c);
add3(1)(2)(3); // 6
add3(1, 2)(3); // 6
```

### Debounce and Throttle

```javascript
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function throttle(fn, interval) {
  let last = 0;
  return function (...args) {
    const now = Date.now();
    if (now - last >= interval) {
      last = now;
      fn.apply(this, args);
    }
  };
}
// debounce → search box (fire after the user stops typing)
// throttle → scroll/resize handlers (fire at most every N ms)
```

## 1.7 Objects and Prototypes

Every object has an internal `[[Prototype]]` link. Property lookup walks the **prototype chain** until `null`.

```javascript
const animal = { eats: true, walk() { return 'walking'; } };
const dog = Object.create(animal);   // dog.[[Prototype]] = animal
dog.barks = true;
dog.walk();                          // 'walking' (found on prototype)
Object.getPrototypeOf(dog) === animal; // true
dog.hasOwnProperty('eats');          // false
Object.hasOwn(dog, 'barks');         // true (modern)

// Constructor function (pre-ES6 pattern)
function Person(name) { this.name = name; }
Person.prototype.hello = function () { return `I am ${this.name}`; };
const p = new Person('A');
p.__proto__ === Person.prototype;    // true
```

**What `new` does:** (1) creates an empty object, (2) links its prototype to `Constructor.prototype`, (3) calls the constructor with `this` = new object, (4) returns the object (unless the constructor returns another object).

### Object utilities

```javascript
const o = { a: 1, b: 2 };
Object.keys(o);      // ['a','b']
Object.values(o);    // [1,2]
Object.entries(o);   // [['a',1],['b',2]]
Object.fromEntries([['x', 1]]); // { x: 1 }

Object.freeze(o);    // shallow: no add/remove/change
Object.seal(o);      // no add/remove, can change existing

Object.defineProperty(o, 'secret', {
  value: 42, writable: false, enumerable: false, configurable: false,
});

// Getters / setters
const temp = {
  _c: 0,
  get f() { return this._c * 9 / 5 + 32; },
  set f(v) { this._c = (v - 32) * 5 / 9; },
};
```

## 1.8 Classes (ES6+)

Classes are syntactic sugar over prototypes, with some extras (private fields, static blocks).

```javascript
class Account {
  static #count = 0;           // private static
  #balance = 0;                // private instance field

  constructor(owner) {
    this.owner = owner;
    Account.#count++;
  }

  deposit(amount) {
    if (amount <= 0) throw new RangeError('Amount must be positive');
    this.#balance += amount;
    return this;               // enables chaining
  }

  get balance() { return this.#balance; }

  static get count() { return Account.#count; }
}

class SavingsAccount extends Account {
  constructor(owner, rate) {
    super(owner);              // must call before using `this`
    this.rate = rate;
  }
  addInterest() {
    return this.deposit(this.balance * this.rate);
  }
}

const s = new SavingsAccount('Anish', 0.05).deposit(1000).addInterest();
s.balance;         // 1050
Account.count;     // 1
// s.#balance      // SyntaxError — truly private
```

## 1.9 Arrays — Essential Methods

```javascript
const users = [
  { id: 1, name: 'A', age: 30, role: 'admin' },
  { id: 2, name: 'B', age: 22, role: 'user' },
  { id: 3, name: 'C', age: 35, role: 'user' },
];

users.map(u => u.name);                   // ['A','B','C']
users.filter(u => u.age > 25);            // A, C
users.find(u => u.id === 2);              // B
users.findIndex(u => u.id === 2);         // 1
users.findLast(u => u.role === 'user');   // C (ES2023)
users.some(u => u.role === 'admin');      // true
users.every(u => u.age > 18);             // true
users.reduce((sum, u) => sum + u.age, 0); // 87

// Group by (ES2024)
Object.groupBy(users, u => u.role); // { admin: [A], user: [B, C] }

// Group by with reduce (works everywhere)
const byRole = users.reduce((acc, u) => {
  (acc[u.role] ??= []).push(u);
  return acc;
}, {});

// Non-mutating versions (ES2023)
const sorted = users.toSorted((a, b) => a.age - b.age);
const reversed = users.toReversed();
const replaced = users.with(0, { ...users[0], name: 'Z' });

// Mutating: push, pop, shift, unshift, splice, sort, reverse, fill
[3, 1, 10].sort();          // [1, 10, 3]  — default sort is lexicographic!
[3, 1, 10].sort((a, b) => a - b); // [1, 3, 10]

[[1, [2]], [3]].flat(Infinity);   // [1, 2, 3]
['a b', 'c'].flatMap(s => s.split(' ')); // ['a','b','c']
Array.from({ length: 3 }, (_, i) => i * 2); // [0,2,4]
[...new Set([1, 1, 2])];          // [1, 2] — dedupe
[1, 2, 3].at(-1);                 // 3
```

### Implement `map` and `reduce` polyfills

```javascript
Array.prototype.myMap = function (cb, thisArg) {
  const out = [];
  for (let i = 0; i < this.length; i++) {
    if (i in this) out[i] = cb.call(thisArg, this[i], i, this);
  }
  return out;
};

Array.prototype.myReduce = function (cb, init) {
  let i = 0, acc = init;
  if (arguments.length < 2) {
    if (!this.length) throw new TypeError('Reduce of empty array with no initial value');
    acc = this[0]; i = 1;
  }
  for (; i < this.length; i++) acc = cb(acc, this[i], i, this);
  return acc;
};
```

## 1.10 Modern Syntax (ES6 → ES2024)

```javascript
// Destructuring with defaults, renaming, rest
const { name: userName = 'guest', ...rest } = { name: 'A', age: 1, role: 'x' };
const [first, , third = 0] = [1, 2];

// Optional chaining & nullish coalescing
const city = user?.address?.city ?? 'Unknown';  // ?? only falls back for null/undefined
const count = 0 || 10;   // 10
const count2 = 0 ?? 10;  // 0

// Logical assignment
opts.timeout ??= 3000;
opts.retries ||= 3;
opts.enabled &&= isAllowed;

// Template literals & tagged templates
const tag = (strings, ...vals) => strings.raw.join('|') + vals.join(',');
tag`a${1}b${2}`;

// Computed keys & shorthand
const key = 'dynamic';
const o2 = { [key]: 1, userName };

// Numeric separators, exponent
const big = 1_000_000;  2 ** 10;

// Symbol — unique keys, well-known symbols
const id = Symbol('id');
const objWithSym = { [id]: 123 };
```

## 1.11 Map, Set, WeakMap, WeakSet

```javascript
const m = new Map([['a', 1]]);
m.set({ k: 1 }, 'object key OK');  // any key type, keeps insertion order
m.size;

const s = new Set([1, 2, 2]);       // unique values
s.has(2);
// ES2025 Set methods: union, intersection, difference, isSubsetOf...
new Set([1, 2]).union(new Set([2, 3])); // Set {1,2,3}

// WeakMap: keys must be objects, held weakly (garbage-collectable), not iterable
const privateData = new WeakMap();
class Thing {
  constructor() { privateData.set(this, { secret: 1 }); }
}
```

**When to use Map over Object:** frequent add/remove, non-string keys, need size/order, avoiding prototype key collisions.

## 1.12 Iterators and Generators

```javascript
// Custom iterable
const range = {
  from: 1, to: 4,
  [Symbol.iterator]() {
    let cur = this.from, last = this.to;
    return { next: () => (cur <= last ? { value: cur++, done: false } : { value: undefined, done: true }) };
  },
};
[...range]; // [1,2,3,4]

// Generator — pausable function
function* idGen() {
  let id = 0;
  while (true) {
    const reset = yield ++id;
    if (reset) id = 0;
  }
}
const gen = idGen();
gen.next().value;      // 1
gen.next().value;      // 2
gen.next(true).value;  // 1

// Async generator — paginate an API
async function* fetchPages(url) {
  let next = url;
  while (next) {
    const res = await fetch(next).then(r => r.json());
    yield res.items;
    next = res.nextPage;
  }
}
for await (const items of fetchPages('/api/items?page=1')) console.log(items);
```

## 1.13 The Event Loop

JavaScript has one call stack. Async work is delegated to the host (Web APIs / libuv); completed callbacks are queued.

- **Call stack** — synchronous code.
- **Microtask queue** — Promise callbacks (`then/catch/finally`), `queueMicrotask`, `MutationObserver`, `await` continuations.
- **Macrotask (task) queue** — `setTimeout`, `setInterval`, I/O, UI events, `MessageChannel`.

**Algorithm:** run one macrotask → drain *all* microtasks → render (browser) → next macrotask.

```javascript
console.log('1 sync');
setTimeout(() => console.log('2 timeout'), 0);
Promise.resolve().then(() => console.log('3 micro'));
queueMicrotask(() => console.log('4 micro'));
(async () => {
  console.log('5 async start (sync)');
  await null;
  console.log('6 after await (micro)');
})();
console.log('7 sync');

// Output: 1, 5, 7, 3, 4, 6, 2
```

## 1.14 Promises and Async/Await

A Promise is in one of three states: **pending**, **fulfilled**, **rejected**. Once settled it is immutable.

```javascript
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function getUser(id) {
  return new Promise((resolve, reject) => {
    if (!id) return reject(new Error('id required'));
    setTimeout(() => resolve({ id, name: 'A' }), 100);
  });
}

getUser(1)
  .then(u => u.name)
  .then(console.log)
  .catch(console.error)
  .finally(() => console.log('done'));

// Combinators
await Promise.all([p1, p2]);        // all fulfill, or reject on first rejection
await Promise.allSettled([p1, p2]); // [{status:'fulfilled',value}, {status:'rejected',reason}]
await Promise.race([p1, timeout]);  // first to settle
await Promise.any([p1, p2]);        // first to fulfill; AggregateError if all reject

// Promise.withResolvers (ES2024)
const { promise, resolve, reject } = Promise.withResolvers();
```

### async/await patterns

```javascript
// Sequential (slow) vs parallel (fast)
async function sequential() {
  const a = await fetchA();  // waits
  const b = await fetchB();  // then waits
  return [a, b];
}
async function parallel() {
  const [a, b] = await Promise.all([fetchA(), fetchB()]);
  return [a, b];
}

// Error handling
async function load() {
  try {
    const res = await fetch('/api');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(err);
    throw err;
  }
}

// Timeout + abort
async function fetchWithTimeout(url, ms = 5000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}
// or: fetch(url, { signal: AbortSignal.timeout(5000) })

// Retry with exponential backoff
async function retry(fn, retries = 3, delay = 500) {
  try {
    return await fn();
  } catch (e) {
    if (retries === 0) throw e;
    await wait(delay);
    return retry(fn, retries - 1, delay * 2);
  }
}

// Concurrency limit (run N at a time)
async function mapLimit(items, limit, fn) {
  const results = [];
  let i = 0;
  const workers = Array.from({ length: limit }, async () => {
    while (i < items.length) {
      const idx = i++;
      results[idx] = await fn(items[idx]);
    }
  });
  await Promise.all(workers);
  return results;
}
```

### Implement `Promise.all` (interview favourite)

```javascript
function promiseAll(promises) {
  return new Promise((resolve, reject) => {
    const results = [];
    let done = 0;
    if (promises.length === 0) return resolve(results);
    promises.forEach((p, i) => {
      Promise.resolve(p).then((val) => {
        results[i] = val;
        if (++done === promises.length) resolve(results);
      }, reject);
    });
  });
}
```

## 1.15 Error Handling

```javascript
class ValidationError extends Error {
  constructor(field, message) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}

try {
  throw new ValidationError('email', 'Invalid email');
} catch (e) {
  if (e instanceof ValidationError) console.log(e.field, e.message);
  else throw e;
} finally {
  // always runs
}

// Error cause (ES2022)
throw new Error('Failed to save user', { cause: originalErr });

// Global handlers
window.addEventListener('unhandledrejection', (e) => console.error(e.reason));
```

## 1.16 Modules

```javascript
// ES Modules (static, analyzable, tree-shakable, async loading)
export const PI = 3.14;
export default function area(r) { return PI * r * r; }
import area, { PI } from './math.js';
import * as math from './math.js';

// Dynamic import → code splitting
const { default: chart } = await import('./chart.js');

// CommonJS (Node legacy: synchronous, dynamic)
const fs = require('fs');
module.exports = { helper };
```

| ESM | CommonJS |
|---|---|
| `import/export` | `require/module.exports` |
| Static, hoisted, tree-shakable | Dynamic, runtime |
| Live bindings | Copies of exported values |
| Top-level `await` allowed | No top-level await |
| `this` is `undefined` at top level | `this` is `module.exports` |

## 1.17 Memory Management and Performance

- Garbage collection uses **mark-and-sweep** (generational: young/old space in V8).
- **Common leaks:** forgotten timers/intervals, detached DOM nodes, global variables, closures holding large objects, event listeners never removed, unbounded caches (use `WeakMap`/LRU).
- Use `WeakRef` and `FinalizationRegistry` only for advanced caching scenarios.

```javascript
// Leak: listener never removed
function attach() {
  const big = new Array(1e6).fill('*');
  window.addEventListener('resize', () => console.log(big.length));
}
// Fix: keep a reference and removeEventListener, or use AbortController
const ac = new AbortController();
window.addEventListener('resize', handler, { signal: ac.signal });
ac.abort(); // removes listener
```

## 1.18 Browser and DOM Essentials

```javascript
// Event delegation — one listener for many children
document.querySelector('#list').addEventListener('click', (e) => {
  const item = e.target.closest('li[data-id]');
  if (item) console.log('clicked', item.dataset.id);
});

// Phases: capture (top→down) → target → bubble (bottom→up)
el.addEventListener('click', fn, { capture: true, once: true, passive: true });
e.stopPropagation();  // stop bubbling
e.preventDefault();   // stop default action (form submit, link nav)

// Intersection Observer — lazy loading / infinite scroll
const io = new IntersectionObserver((entries) => {
  entries.forEach((en) => en.isIntersecting && loadMore());
});
io.observe(document.querySelector('#sentinel'));
```

**Storage:** `localStorage` (persistent, ~5MB, sync, strings only), `sessionStorage` (per tab), cookies (sent with requests; use `HttpOnly`, `Secure`, `SameSite`), IndexedDB (large structured async storage).

**Rendering:** DOM + CSSOM → render tree → layout (reflow) → paint → composite. Avoid layout thrashing (reading `offsetHeight` after writes in a loop); animate `transform`/`opacity`.

**Security:** XSS (never inject untrusted HTML; use `textContent`; CSP), CSRF (SameSite cookies, CSRF tokens), CORS (server-side header controlling cross-origin reads).

## 1.19 Functional Programming Concepts

- **Pure functions** — same input → same output, no side effects.
- **Immutability** — return new objects instead of mutating.
- **Composition** — build complex functions from small ones.

```javascript
const compose = (...fns) => (x) => fns.reduceRight((v, f) => f(v), x);
const pipe = (...fns) => (x) => fns.reduce((v, f) => f(v), x);

const slugify = pipe(
  (s) => s.trim(),
  (s) => s.toLowerCase(),
  (s) => s.replace(/\s+/g, '-'),
);
slugify('  Hello World '); // 'hello-world'
```

## 1.20 Design Patterns in JavaScript

```javascript
// Singleton (module scope is a natural singleton)
let instance;
export function getDb() { return (instance ??= createConnection()); }

// Observer / Pub-Sub — basis of EventEmitter, Redux subscribe
class EventBus {
  #events = new Map();
  on(evt, fn) {
    if (!this.#events.has(evt)) this.#events.set(evt, new Set());
    this.#events.get(evt).add(fn);
    return () => this.#events.get(evt).delete(fn); // unsubscribe
  }
  emit(evt, ...args) { this.#events.get(evt)?.forEach((fn) => fn(...args)); }
}

// Factory
function createShape(type) {
  const shapes = { circle: () => new Circle(), square: () => new Square() };
  return shapes[type]?.() ?? (() => { throw new Error('Unknown shape'); })();
}

// Proxy — validation, reactivity (Vue 3 uses this)
const validated = new Proxy({}, {
  set(target, prop, value) {
    if (prop === 'age' && !Number.isInteger(value)) throw new TypeError('age must be int');
    target[prop] = value;
    return true;
  },
});
```

## 1.21 Deep Clone and Deep Equal (Interview Implementations)

```javascript
function deepClone(value, seen = new WeakMap()) {
  if (value === null || typeof value !== 'object') return value;
  if (seen.has(value)) return seen.get(value);       // handle cycles
  if (value instanceof Date) return new Date(value);
  if (value instanceof Map) return new Map([...value].map(([k, v]) => [k, deepClone(v, seen)]));
  if (value instanceof Set) return new Set([...value].map(v => deepClone(v, seen)));
  const out = Array.isArray(value) ? [] : Object.create(Object.getPrototypeOf(value));
  seen.set(value, out);
  for (const key of Reflect.ownKeys(value)) out[key] = deepClone(value[key], seen);
  return out;
}

function deepEqual(a, b) {
  if (Object.is(a, b)) return true;
  if (typeof a !== 'object' || typeof b !== 'object' || !a || !b) return false;
  const ka = Object.keys(a), kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  return ka.every((k) => deepEqual(a[k], b[k]));
}

// Flatten an object: { a: { b: 1 } } → { 'a.b': 1 }
function flattenObj(obj, prefix = '', out = {}) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === 'object' && !Array.isArray(v)) flattenObj(v, key, out);
    else out[key] = v;
  }
  return out;
}
```

## 1.22 Quick Revision — Tricky Output Questions

```javascript
// 1
console.log([1, 2, 3] + [4]);       // '1,2,34'
// 2
console.log(typeof typeof 1);       // 'string'
// 3
const x = { a: 1 };
const y = x; y.a = 2;
console.log(x.a);                   // 2
// 4
console.log([10, 1, 3].sort());     // [1, 10, 3]
// 5
let n = 1;
{ let n = 2; }
console.log(n);                     // 1
// 6
console.log(1 < 2 < 3, 3 > 2 > 1);  // true false   (true > 1 → 1 > 1)
// 7
const fn = () => arguments;         // ReferenceError in modules (no own arguments)
// 8
console.log(+'', +' ', +'a');       // 0 0 NaN
// 9
for (const k in [7, 8]) console.log(typeof k); // 'string' 'string' — for...in gives keys
```
