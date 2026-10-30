== intro
**What is JavaScript?** JavaScript (JS) is the programming language that web browsers understand. It was created in 1995 to make web pages interactive, for example to react to clicks or check a form before sending it. Today it also runs on servers (Node.js), phones (React Native) and desktops (Electron). It is the most widely used programming language in the world.

**Key characteristics, in plain words:**

- **Single-threaded:** it does one thing at a time. It still handles many tasks "at once" through asynchronous callbacks (explained in 1.13).
- **Dynamically typed:** a variable can hold a number now and a string later. The language does not check types in advance.
- **Functions are values:** you can store a function in a variable, pass it to another function, or return it from a function. Many advanced patterns build on this.
- **Prototype-based objects:** objects can inherit directly from other objects (explained in 1.7).

**Your first program.** Open the browser console (F12) and type:

```javascript
let name = 'World';                 // store a value in a variable
console.log('Hello, ' + name);      // print to the console → Hello, World

function square(n) {                // define a reusable function
  return n * n;
}
console.log(square(5));             // 25

if (square(5) > 20) {               // a condition
  console.log('big number');
}

for (let i = 1; i <= 3; i++) {      // a loop: runs with i = 1, 2, 3
  console.log('Count', i);
}
```

== 1.1
JavaScript code is plain text. To run it, a program called a **JavaScript engine** reads and executes it. Chrome and Node.js use the **V8** engine, Firefox uses SpiderMonkey and Safari uses JavaScriptCore.

The engine works roughly like this:

1. **Parsing:** it reads your text and checks the grammar. A typo here gives a `SyntaxError` before anything runs.
2. **Interpreting:** it quickly converts the code into simple instructions (*bytecode*) and starts running them.
3. **Optimising (JIT, "Just-In-Time" compiling):** while the code runs, the engine notices which functions are used often ("hot") and compiles them into fast machine code. If its assumptions turn out wrong (say a function that always got numbers suddenly gets a string), it throws the fast version away. That is called *de-optimising*.

The **host environment** is whatever is running the engine. The *browser* adds things like `document` (the page), `window` and `alert`. *Node.js* adds things like `fs` (files) and `http` (servers). The core language (variables, functions, arrays) is the same everywhere.

An **execution context** is the "workspace" the engine creates whenever it runs code. One is created for the whole file (global context) and a new one every time a function is called. It remembers the variables that exist, where to look for outer variables, and what `this` means. These contexts are stacked on the **call stack**. When a function is called its context is pushed on top, and when it returns that context is popped off.

== 1.2
**A variable is a named box that stores a value.** You create (declare) one with `let`, `const` or the older `var`.

- Use **`const`** by default. The name cannot be pointed at a different value later.
- Use **`let`** when the value must change (a counter, for example).
- Avoid **`var`**. It has confusing older rules, but you must understand it for interviews and legacy code.

**Scope** answers the question "where in my code can this variable be seen?"

- **Global scope:** declared outside everything, so visible everywhere.
- **Function scope:** declared inside a function, so visible only inside that function.
- **Block scope:** declared inside `{ }` (an `if`, a `for` loop) with `let`/`const`, so visible only inside those braces.

```javascript
const site = 'shop';            // global
function show() {
  const user = 'A';             // function scope
  if (true) {
    let temp = 1;               // block scope — exists only inside these braces
    console.log(site, user, temp); // all visible here
  }
  // console.log(temp);         // ReferenceError: temp is not defined here
}
```

Inner code can see outer variables, but outer code cannot see inner variables. Picture a house with one-way windows: from a small room you can look out into the hallway, but nobody in the hallway can see into the room. When the engine looks up a variable, it checks the current scope, then the one outside it, and so on until the global scope. This path is called the **scope chain**.

**Hoisting.** Before running a scope, the engine first scans it for declarations and reserves memory for them. This makes it *look as if* declarations were "lifted" (hoisted) to the top.

- `var` variables are hoisted *and* set to `undefined`, so reading them early gives `undefined` instead of an error.
- `let`/`const` are hoisted but *not initialised*. Reading them before the declaration line throws an error. The zone between the start of the scope and the declaration line is called the **Temporal Dead Zone (TDZ)**.
- **Function declarations** are hoisted completely, so you can call them before the line where they are written.

== 1.3
Every value in JavaScript has a **type**. There are two families:

**1. Primitive types** are simple, single values. They are *immutable*: you never change a primitive, you replace it with a new one.

| Type | Example | Meaning |
|---|---|---|
| `number` | `42`, `3.14`, `NaN`, `Infinity` | All numbers (integers and decimals share one type) |
| `string` | `'hello'`, `"hi"`, `` `hi ${x}` `` | Text |
| `boolean` | `true`, `false` | Yes/no |
| `undefined` | `undefined` | "A value was never assigned" |
| `null` | `null` | "Intentionally empty", set on purpose |
| `bigint` | `123n` | Integers larger than `Number` can safely hold |
| `symbol` | `Symbol('id')` | A guaranteed-unique identifier |

**2. Objects** are collections of values (arrays, functions, dates and plain `{}` objects are all objects). A variable holding an object stores a **reference**, like the address of a house, rather than the house itself. Copy the variable and you copy the address, so both variables lead to the **same** object.

```javascript
let a = 5;  let b = a;  b = 10;          // primitives are copied by value
console.log(a);                           // 5 — unaffected

let o1 = { n: 5 };  let o2 = o1;  o2.n = 10;  // objects are shared by reference
console.log(o1.n);                        // 10 — same object!
```

**Type coercion** means JavaScript automatically converting a value to another type, for example turning `'5'` into `5` when you do `'5' - 1`. It is convenient but surprising, so prefer the **strict equality** operator `===`, which never converts types.

**Truthy and falsy:** in a condition like `if (x)`, JavaScript converts `x` to true or false. Only eight values are **falsy** (`false`, `0`, `-0`, `0n`, `''`, `null`, `undefined`, `NaN`). Everything else, including `'0'`, `[]` and `{}`, is **truthy**.

**Shallow vs deep copy:** a *shallow copy* duplicates only the outer object. Nested objects are still shared. A *deep copy* duplicates everything, all the way down.

== 1.4
**A function is a reusable block of code with a name.** You define it once and *call* (run) it as many times as you want. It can take **parameters** (inputs) and **return** a value (output).

```javascript
function greet(name) {        // `name` is a parameter
  return 'Hello ' + name;     // `return` sends a value back to the caller
}
const message = greet('Anish'); // 'Anish' is the argument → message = 'Hello Anish'
```

**Parameters vs arguments:** parameters are the placeholder names in the definition. Arguments are the actual values passed when calling.

**Three ways to write a function:**

1. **Function declaration:** `function add(a, b) { ... }`. It is hoisted, so you can call it before the line where it is defined.
2. **Function expression:** `const add = function (a, b) { ... };`. The function is stored in a variable.
3. **Arrow function:** `const add = (a, b) => a + b;`. A short syntax, and for one-line bodies the result is returned automatically. Arrow functions do not have their own `this` (see 1.5).

**Default parameters** give a value when the caller passes nothing. **Rest parameters** (`...nums`) collect any number of arguments into an array. **Spread** (`...array`) does the opposite: it expands an array into separate arguments.

**First-class and higher-order functions.** In JavaScript, functions are values, just like numbers. A **higher-order function** takes a function as input or returns one. You already use these: `array.map(fn)`, `setTimeout(fn, 1000)` and `button.addEventListener('click', fn)`. A function passed in to be called later is a **callback**.

**Pure function:** given the same inputs, it always returns the same output and changes nothing outside itself. Pure functions are easy to test and reason about.

== 1.5
`this` is a special keyword that refers to **the object that is "running" the function right now**. Unlike normal variables, its value is **not** fixed where the function is written. It is decided by **how the function is called**.

An analogy: the word "me" depends on who says it. When Anish says "me", it means Anish. When Ravi says the same word, it means Ravi. `this` works the same way.

The rules, in order:

1. Called with **`new`**, e.g. `new User()`: `this` is the brand-new object being created.
2. Called with **`call`/`apply`/`bind`**: `this` is whatever object you explicitly pass in.
3. Called as a **method**, `obj.method()`: `this` is the object before the dot (`obj`).
4. Called as a **plain function**, `method()`: `this` is `undefined` in strict mode, or the global object otherwise.
5. **Arrow functions** have no `this` of their own. They use the `this` of the code around them. That is why arrows are handy inside callbacks.

The most common bug is taking a method out of its object, e.g. `const f = user.greet; f();`. There is no longer a "dot" in front, so `this` is lost. `bind` fixes this by creating a copy of the function whose `this` is permanently set.

- `fn.call(obj, a, b)` runs immediately, with arguments listed one by one.
- `fn.apply(obj, [a, b])` runs immediately, with arguments passed as an array.
- `fn.bind(obj)` does **not** run. It returns a new function with `this` locked.

== 1.6
**A closure is a function that remembers the variables from the place where it was created, even after that place has finished running.**

Normally, when a function finishes, its local variables are thrown away. But if an inner function is still using them, for example because it was returned or saved as a callback, JavaScript keeps those variables alive for it. Think of it as a "backpack" of variables the inner function carries around.

```javascript
function makeGreeter(greeting) {      // outer function
  return function (name) {            // inner function "closes over" greeting
    return greeting + ', ' + name;
  };
}
const hello = makeGreeter('Hello');   // makeGreeter has finished...
hello('Anish');                       // ...but 'Hello' is remembered → 'Hello, Anish'
```

**Why closures matter:**

- **Private data:** variables inside the outer function cannot be touched from outside, only through the functions you return (see the counter example below).
- **Function factories:** create customised functions (`makeGreeter('Hi')`, `makeGreeter('Namaste')`).
- **Callbacks and timers** remember the data they need.
- **React hooks** are built on closures. Each render's event handlers "see" the state of that render.

**Currying** turns a function of several arguments into a chain of one-argument functions: `add(1)(2)(3)`. It is used to pre-fill some arguments.

**Debounce** waits until the user *stops* doing something (typing in a search box) before running the function once. **Throttle** runs the function at most once per time period (for example, during scrolling). Both use a closure to remember the timer between calls.

== 1.7
**An object is a collection of named values called properties.** When a property holds a function, it is called a **method**.

```javascript
const user = {
  name: 'Anish',          // property
  age: 30,
  greet() {               // method
    return 'Hi, I am ' + this.name;
  },
};
user.name;          // dot notation → 'Anish'
user['age'];        // bracket notation (useful with variable keys)
user.city = 'Pune'; // add a property
delete user.age;    // remove a property
```

**Prototypes are how objects inherit in JavaScript.** Every object has a hidden link to another object, its **prototype**. When you ask for a property the object doesn't have, JavaScript automatically looks in the prototype, then in the prototype's prototype, and so on. This lookup path is the **prototype chain**. It ends at `Object.prototype`, whose prototype is `null`.

This is why every array has `.map()` and `.push()` even though you never wrote them. They live on `Array.prototype`, which all arrays link to. Methods are stored once and *shared* by all objects, which saves memory.

**Constructor functions** plus the `new` keyword were the original way to create many similar objects. `new` creates an empty object, links it to the constructor's `prototype`, runs the constructor with `this` pointing at the new object, and returns it. ES6 classes (next section) do exactly this with cleaner syntax.

**Getters and setters** look like normal properties but run a function when read or written. They are useful for computed values and validation.

== 1.8
**A class is a blueprint for creating objects.** It bundles data (fields) and behaviour (methods) into one unit. Each object made from a class is an **instance**. For example, the `Car` class is the design, and your car and my car are instances.

Main ideas of **Object-Oriented Programming (OOP)**:

- **Encapsulation:** keep data and the code that manages it together, and hide internal details. In JS, fields that start with `#` are truly private.
- **Inheritance:** a class can `extend` another and reuse its code. `SavingsAccount extends Account` means "a savings account *is an* account, with extras".
- **Polymorphism:** different classes can provide their own version of the same method, and calling code does not need to know which one it has.
- **Abstraction:** expose a simple interface (`deposit()`) and hide the complexity.

Parts of a class:

- **`constructor`** runs automatically when you call `new ClassName(...)`. It sets up the initial data.
- **Methods** are functions available on every instance.
- **`static`** members belong to the class itself, not to instances (e.g. `Account.count`).
- **`super(...)`** calls the parent class's constructor. **`super.method()`** calls the parent's version of a method.
- **getters/setters** (`get balance()`) let you read computed values like a property.

Under the hood, classes still use prototypes. They are "syntactic sugar" that makes prototypes easier to write.

== 1.9
**An array is an ordered list of values.** Each value sits at a numbered position called its **index**, starting at **0**.

```javascript
const fruits = ['apple', 'banana', 'cherry'];
fruits[0];          // 'apple'
fruits.length;      // 3
fruits.push('kiwi');// add to end
fruits.pop();       // remove from end
for (const f of fruits) console.log(f);   // loop over values
```

Modern JavaScript prefers **array methods** to hand-written loops. Each takes a *callback* function that runs for every element:

| Method | What it does | Returns |
|---|---|---|
| `map` | Transforms every item | New array, same length |
| `filter` | Keeps items where the callback returns true | New, possibly shorter array |
| `find` | First item matching a condition | One item or `undefined` |
| `some` / `every` | Does *any* / *all* match? | `true`/`false` |
| `reduce` | Combines all items into one value (sum, object, ...) | Anything |
| `forEach` | Runs code for each item | Nothing (`undefined`) |
| `sort` | Orders items (**changes the original!**) | Same array |

`reduce` takes the most practice. It carries an **accumulator** (a running result) through the array: `[1,2,3].reduce((total, n) => total + n, 0)` goes 0 → 1 → 3 → 6.

**Mutating vs non-mutating:** methods like `push`, `sort`, `splice` and `reverse` *change* the original array. `map`, `filter`, `slice`, `toSorted` and `toReversed` return *new* arrays and leave the original alone. React and Redux require the non-mutating style.

== 1.10
The JavaScript language is updated every year. The standard is called **ECMAScript**, so "ES6" means the 2015 edition and "ES2024" the 2024 edition. ES6 was the big modernisation. These features make code shorter and safer:

- **Destructuring:** unpack values from arrays or objects into variables in one line: `const { name, age } = user;` `const [first, second] = list;`
- **Spread `...`:** copy or merge, e.g. `{ ...user, age: 31 }` creates a new object with one field changed.
- **Template literals:** strings in backticks with `${expression}` placeholders, which can span multiple lines.
- **Optional chaining `?.`:** safely read deep properties. `user?.address?.city` returns `undefined` instead of crashing if `address` is missing.
- **Nullish coalescing `??`:** a default value only when the left side is `null`/`undefined`. Compare `||`, which also replaces `0` and `''`. That is why `0 ?? 10` is `0` but `0 || 10` is `10`.
- **Shorthand properties:** `{ name }` instead of `{ name: name }`.

== 1.11
Besides plain objects and arrays, JavaScript has specialised collections:

- **`Map`:** a key-value store like an object, but keys can be **any type** (even objects). It remembers insertion order and has a `.size`. Use it as a dictionary or cache.
- **`Set`:** a collection of **unique** values. Adding the same value twice keeps one copy. Use it to remove duplicates or for fast "have I seen this?" checks.
- **`WeakMap` / `WeakSet`:** like Map and Set, but keys must be objects and are held *weakly*. If nothing else references the key object, it can be garbage-collected (removed from memory) automatically. Use them to attach extra data to objects without causing memory leaks.

Rule of thumb: plain objects for fixed-shape records (`{ id, name }`), and `Map` for dynamic dictionaries where keys are added and removed often.

== 1.12
**Iteration** means going through items one by one. Arrays, strings, Maps and Sets are **iterable**: they follow a standard *iterator protocol*, so `for...of` and spread `[...x]` work on them. An **iterator** is an object with a `next()` method that returns `{ value, done }` each time it is called.

**Generators** (`function*`) are functions that can **pause and resume**. Each `yield` hands out one value and freezes the function until someone asks for the next value. This is useful for:

- **Lazy sequences:** produce values only when needed, even an infinite sequence of IDs.
- **Large data:** process a huge file or paginated API one piece at a time without loading everything into memory.

```javascript
function* threeSteps() {
  yield 'step 1';     // pause here
  yield 'step 2';     // pause here
  return 'done';
}
const g = threeSteps();
g.next();  // { value: 'step 1', done: false }
g.next();  // { value: 'step 2', done: false }
g.next();  // { value: 'done', done: true }
```

**Async generators** (`async function*` with `for await...of`) do the same for data that arrives over time, like pages from an API.

== 1.13
**Problem:** JavaScript has only one thread, which means it can do only one thing at a time. If it waited (blocked) for every network request, the page would freeze. **Solution:** the **event loop**.

Think of a restaurant with **one chef** (the JavaScript thread):

- The chef cooks one dish at a time. That is the **call stack**, the code currently running.
- Slow jobs like baking (timers, network requests, file reads) are handed to **helpers** (the browser or Node's background system). The chef does not wait for them.
- When a helper finishes, they put a ticket in a **queue**.
- Whenever the chef's hands are free (the call stack is empty), the chef takes the next ticket. That repeating check is the **event loop**.

There are two queues, and one has priority:

1. **Microtask queue (VIP):** promise callbacks (`.then`, code after `await`). It is emptied *completely* after each task.
2. **Macrotask/task queue (regular):** `setTimeout`, `setInterval`, clicks, I/O.

So the order is: run all synchronous code → run all microtasks → run one macrotask → run all microtasks again → and so on. This is why `Promise.then` runs **before** `setTimeout(..., 0)` even though the timeout is "0 ms". Note that `setTimeout(fn, 0)` means "*at least* 0 ms, after the current work", not "immediately".

== 1.14
**A Promise is an object representing a value that will be available later**, such as the result of a network request. It is like the buzzer you get at a food court: you don't have the food yet, but you have something that will tell you when it is ready, or that something went wrong.

A promise is always in one of three **states**:

1. **Pending:** still waiting.
2. **Fulfilled (resolved):** success, with a value.
3. **Rejected:** failure, with an error (the reason).

Once fulfilled or rejected, it is **settled** and never changes again.

**Before promises**, async code used nested callbacks, which made "callback hell" (pyramids of indentation that were hard to read and to handle errors in). Promises let you chain steps with `.then()` and handle all errors in one `.catch()`.

**`async`/`await`** is a cleaner syntax on top of promises:

- Marking a function `async` makes it always return a promise.
- Inside it, `await somePromise` *pauses that function* (not the whole program) until the promise settles, then gives you the value. If the promise rejects, `await` throws an error you can catch with `try/catch`.

```javascript
async function showUser() {
  try {
    const response = await fetch('/api/user/1'); // wait for the network
    const user = await response.json();          // wait for the body to be parsed
    console.log(user.name);
  } catch (error) {
    console.log('Something failed:', error.message);
  }
}
```

**Running things in parallel:** `await` one after another runs tasks *sequentially*. If tasks are independent, start them all and wait with `Promise.all([...])`. That is much faster.

== 1.15
**Errors** happen when something goes wrong while the program runs: calling a function that doesn't exist, bad input, a failed network request. If nothing handles an error, the program (or that piece of it) stops.

- **`throw`** creates (raises) an error yourself: `throw new Error('Price must be positive')`.
- **`try { } catch (e) { }`** runs risky code in `try`. If an error is thrown, control jumps to `catch` where you deal with it.
- **`finally { }`** always runs, error or not. Use it for clean-up such as hiding a loading spinner or closing a connection.

Built-in error types tell you what went wrong: `ReferenceError` (variable doesn't exist), `TypeError` (wrong kind of value, e.g. calling `undefined()`), `SyntaxError` (invalid code), `RangeError` (number out of range).

You can create **custom error classes** by extending `Error`. Callers can then check `if (e instanceof ValidationError)` and react differently to different problems.

**Good practice:** catch errors where you can actually *do something* about them (show a message, retry, use a fallback). Otherwise let them travel upward. Never silently swallow errors with an empty `catch {}`.

== 1.16
**A module is a separate file whose variables are private by default.** You choose what to share with `export` and pull it into another file with `import`. Modules let you split a large program into small, focused files, avoid name clashes, and reuse code.

There are two module systems you will meet:

- **ES Modules (ESM):** the official standard (`import`/`export`), used in browsers, React projects and modern Node.js. Imports are analysed *before* the code runs. That lets bundlers drop unused code, which is called **tree-shaking**.
- **CommonJS (CJS):** Node.js's original system (`require()` / `module.exports`). It is still very common in older Node projects.

**Named vs default exports:** a file can have many *named* exports (`export const PI`), imported with braces `{ PI }`. It can have one *default* export, imported with any name you like and no braces.

**Dynamic import**, `await import('./file.js')`, loads a module only when needed. React uses this for *code splitting* (loading a page's code only when the user visits that page).

== 1.17
Programs need memory to store their values. In JavaScript you never free memory yourself. A **garbage collector (GC)** automatically finds values that can no longer be reached from your code and frees them.

**Reachability:** a value is kept alive if it can be reached from a "root" (global variables, the currently running functions) through a chain of references. Everything else is garbage. The common algorithm is **mark-and-sweep**: *mark* everything reachable, then *sweep away* everything unmarked.

A **memory leak** happens when you *accidentally* keep references to things you no longer need, so the GC can't free them and memory usage keeps growing. Common causes:

- Event listeners or `setInterval` timers that are never removed.
- Global variables or caches that grow forever.
- Closures that capture large objects.
- References to DOM elements that have already been removed from the page.

The fix is usually "clean up after yourself": `removeEventListener`, `clearInterval`, bounded caches, and in React, effect cleanup functions.

== 1.18
In the browser, JavaScript interacts with the page through the **DOM (Document Object Model)**, a tree of objects representing every HTML element. Change the tree and the page updates.

```javascript
const title = document.querySelector('h1');      // find an element (CSS selector)
title.textContent = 'New title';                 // change its text
title.classList.add('highlight');                // add a CSS class
const li = document.createElement('li');         // create a new element
li.textContent = 'Item';
document.querySelector('ul').appendChild(li);    // insert it into the page
```

**Events** are things that happen: clicks, key presses, form submissions, scrolling. You react to them with `element.addEventListener('click', handler)`. The handler receives an **event object** with details (which element was clicked, mouse position, which key was pressed).

**Event propagation:** an event starts at the top of the page and travels *down* to the clicked element (the **capture** phase), then travels back *up* through every parent (the **bubble** phase). Bubbling makes **event delegation** possible: put one listener on a parent instead of hundreds of listeners on children.

**Browser storage:** `localStorage` keeps small string data permanently in the browser. `sessionStorage` keeps it until the tab is closed. **Cookies** are small values that are automatically sent to the server with each request, often used for login sessions.

**Web security basics:** **XSS** (Cross-Site Scripting) is when an attacker gets their script to run on your page, often by injecting HTML. Never insert untrusted text as HTML. **CSRF** tricks a logged-in user's browser into sending an unwanted request. **CORS** is the browser rule that controls which other websites may read responses from your server.

== 1.19
**Functional programming (FP)** is a style that builds programs from small, **pure** functions and avoids changing data in place. JavaScript supports FP very well because functions are values.

Core ideas:

- **Pure functions:** output depends only on input, with no side effects (no changing global variables, no network calls). They are easy to test: same input, same output, every time.
- **Immutability:** instead of modifying an object, create a new one with the change (`{ ...user, age: 31 }`). This prevents bugs where one part of the code unexpectedly changes data another part relies on. React depends on this to detect changes.
- **Composition:** combine small functions into bigger ones, like LEGO bricks. `pipe(trim, toLowerCase, replaceSpaces)` runs each function on the result of the previous one.
- **Declarative over imperative:** describe *what* you want (`users.filter(u => u.active)`) rather than *how*, step by step (a manual `for` loop with an index and a push).

== 1.20
**Design patterns** are proven, reusable solutions to problems that come up again and again in software design. They give developers a shared vocabulary ("let's use an observer here").

- **Singleton:** guarantees only **one** instance of something exists, such as a single database connection or a config object.
- **Observer / Pub-Sub:** objects *subscribe* to events and get notified when they happen, like following a channel on YouTube. DOM events, Node's EventEmitter, and Redux store subscriptions all use this.
- **Factory:** a function that decides *which* kind of object to create, so callers don't need to know the details.
- **Module:** hide private details and expose a public API (closures or ES modules).
- **Proxy:** an object that stands in front of another and intercepts operations (validation, logging, reactivity in Vue).
- **Decorator / Higher-order function:** wrap a function to add behaviour (logging, caching) without changing its code.

== 1.21
These are **classic interview exercises**. They test whether you really understand references, recursion and types.

- **Deep clone:** create a completely independent copy of a nested object. The tricky parts are handling nested objects (solved with *recursion*, a function calling itself), special types like `Date`/`Map`/`Set`, and **circular references** (an object that contains itself). Circular references are handled by remembering already-copied objects in a `WeakMap`.
- **Deep equal:** check whether two values have the same content, not just the same reference. `{a:1} === {a:1}` is `false` because they are two different objects in memory.
- **Flatten an object:** turn nested keys into dotted paths. It is useful for forms and logging.

In real projects, use `structuredClone()` for deep copies and a tested library (lodash `isEqual`) for deep equality.

== 1.22
These snippets show JavaScript's surprising corners: coercion, sorting, scope and references. For each one, **predict the output before reading the answer**, then reason about *why* using the concepts above. If you can explain every one of them, your fundamentals are solid.
