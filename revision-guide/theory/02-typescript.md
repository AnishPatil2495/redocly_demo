== intro
**What is TypeScript?** TypeScript (TS) is JavaScript **plus types**. Microsoft created it in 2012. You write `.ts`/`.tsx` files, and the TypeScript **compiler** (`tsc`) checks them for mistakes and then converts them into normal JavaScript, because browsers and Node only understand JS.

**What is a "type"?** A type describes *what kind of value* something is and what you can do with it: a `number` can be added, a `string` can be upper-cased, a `User` has a `name` and an `email`.

**Why bother?** In JavaScript, many mistakes show up only when the code runs, sometimes in production in front of users:

```javascript
function total(price, qty) { return price * qty; }
total('10', 2);         // JS happily returns 20... or worse, 'abc' * 2 = NaN
user.nmae;              // typo → undefined, no warning
```

With TypeScript, the editor underlines these errors **as you type**:

```typescript
function total(price: number, qty: number): number { return price * qty; }
total('10', 2);         // ❌ Error: Argument of type 'string' is not assignable to 'number'
```

Benefits: fewer bugs, safe refactoring (rename something and TS shows every place that broke), autocomplete in the editor, and types that work as living documentation. **Important:** types exist only at compile time. They are removed from the final JavaScript and do **not** check data at run time.

== 2.1
TypeScript is a **superset** of JavaScript: every valid JavaScript program is also valid TypeScript. You can adopt it gradually, one file at a time.

**Type annotations** are the `: type` you write after a variable or parameter: `let age: number = 30`. Often you don't need them, because TypeScript **infers** (works out) the type from the value: `let age = 30` is already known to be a `number`.

**Structural typing** is a key idea. TypeScript compares types by their **shape** (which properties they have), not by their names. If an object has all the properties an interface requires, it is accepted, even if it was never declared as that interface. This matches how JavaScript itself works ("if it walks like a duck and quacks like a duck, it's a duck").

**The compile step:**

```text
app.ts ──(tsc / Vite / esbuild / ts-node)──►  type-check  ──►  app.js (types removed)  ──►  run in browser/Node
```

== 2.2
`tsconfig.json` is the configuration file that tells the TypeScript compiler how strict to be and what JavaScript to produce. Every TS project has one at its root.

The most important settings for a beginner:

- **`strict: true`** turns on all the safety checks. Always use it in new projects.
- **`strictNullChecks`** (part of strict) means `null` and `undefined` are not silently allowed everywhere, which prevents the famous "cannot read property of undefined" crash.
- **`noImplicitAny`** makes TS report an error when it can't work out a type, instead of silently giving up and using `any`.
- **`target`** sets which JavaScript version to output (e.g. ES2022).
- **`module`** sets which module system to output (ESM or CommonJS).
- **`outDir` / `rootDir`** set where compiled files go and where source files live.
- **`jsx`** controls how React's JSX is compiled.
- **`paths`** adds import shortcuts such as `@/components/Button`.

== 2.3
These are the building blocks. You attach them with a colon after a name.

- **`number`, `string`, `boolean`:** the everyday primitives.
- **Arrays:** `number[]` or `Array<number>`, a list where every item is a number.
- **Tuples:** `[string, number]`, a fixed-length array where each position has a specific type (e.g. `['age', 30]`).
- **`any`:** "turn off type checking for this value". It is an escape hatch. Avoid it, because it spreads and hides bugs.
- **`unknown`:** "could be anything, but you must check before using it". It is the *safe* version of `any`, and the right type for data whose shape you don't know yet (like JSON from an API).
- **`void`:** the function returns nothing useful.
- **`never`:** a value that can never exist, for example the return type of a function that always throws, or the leftover case after you've handled every possibility.
- **`null` / `undefined`:** the empty values. With strict mode you must include them explicitly, e.g. `string | null`.
- **Literal types:** an exact value as a type, e.g. `'up' | 'down'` allows only those two strings.

**Union types** (`A | B`) mean "either A or B": `let id: string | number`.

== 2.4
Both **interfaces** and **type aliases** let you give a name to the shape of an object, so you can reuse it:

```typescript
interface User { id: number; name: string; email?: string }  // ? = optional property
type Product = { id: number; title: string; price: number };

const u: User = { id: 1, name: 'Anish' };      // OK — email is optional
```

- **`interface`** is designed for object shapes. It can be *extended* (`interface Admin extends User`) and *merged* (declaring the same interface twice combines them, which is useful for adding fields to library types).
- **`type`** can name *anything*: object shapes, unions (`'admin' | 'user'`), tuples, functions and computed types.

**Modifiers:** `?` makes a property optional. `readonly` prevents it from being changed after creation.

**Intersection** (`A & B`) means "has everything from A **and** B". Use it to combine types.

Practical rule: use `interface` for objects and public APIs, and `type` for unions and anything more complex. Consistency within a project matters more than the choice itself.

== 2.5
In TypeScript you annotate a function's **parameters** and, optionally, its **return type**: `function add(a: number, b: number): number`. TypeScript then checks that callers pass the right arguments and that the function really returns what it promises.

- **Optional parameters** (`name?: string`) may be left out. Their value is then `undefined`.
- **Default parameters** (`b = 0`) are automatically optional.
- **Function types** describe the shape of a function so you can type callbacks: `type Callback = (error: Error | null, data?: string) => void`.
- **Overloads** let one function have several call signatures, for example returning a `number` when given a `string` and a `string` when given a `number`.

Annotating return types on exported functions is good practice. If you accidentally return the wrong thing, the error appears inside the function, not somewhere far away where it is used.

== 2.6
When a value can be several types (`string | number`), TypeScript only lets you use what's common to *all* of them. **Narrowing** is how you prove to TypeScript which specific type you have at a given point, using ordinary JavaScript checks:

- `typeof x === 'string'` checks primitives.
- `x instanceof Date` checks class instances.
- `'swim' in animal` checks whether a property exists.
- `x == null` checks for null/undefined.
- **Type guards** are your own functions returning `x is Type`.

Inside the `if` block, TypeScript *knows* the narrower type, so autocomplete and checks become precise.

**Discriminated unions** are one of TypeScript's most useful patterns. Every member of a union has a common property with a unique literal value, the *discriminant* (often `kind`, `type` or `status`). Switching on it narrows to exactly one member. Combined with a `never` check in the `default` branch, TypeScript will **warn you if you forget to handle a case**. This is perfect for modelling states like `loading | success | error`.

== 2.7
**Generics let you write code that works with many types while keeping type safety.** They are "type parameters", placeholders for a type that's filled in when the code is used. They are written in angle brackets: `<T>`.

An analogy: a shipping box labelled "Box of ___". Once you fill in "Box of Books", everyone knows what comes out. Without generics you'd either write a separate box for every item (`BookBox`, `ToyBox`) or use `any` and lose all safety.

```typescript
function firstItem<T>(items: T[]): T | undefined {
  return items[0];
}
const n = firstItem([1, 2, 3]);        // T = number → n is number | undefined
const s = firstItem(['a', 'b']);       // T = string → s is string | undefined
```

- **Constraints** (`<T extends { length: number }>`) say "T can be any type, *as long as* it has a `length`".
- **`keyof`** with generics lets you safely access properties: `getProp(obj, key)` only accepts real keys of `obj`.
- Generics appear everywhere: `Array<T>`, `Promise<T>`, `useState<T>()`, `Map<K, V>`, and API response wrappers like `ApiResponse<User>`.

== 2.8
TypeScript ships with ready-made **utility types**. These are generic "type functions" that transform an existing type into a new one, so you don't have to repeat yourself.

Imagine a `User` type with `id`, `name`, `email` and `password`:

- **`Partial<User>`** makes all fields optional, which suits an "update" form where any field may change.
- **`Required<User>`** makes all fields mandatory.
- **`Readonly<User>`** means no field can be changed.
- **`Pick<User, 'id' | 'name'>`** keeps only some fields, for a public profile.
- **`Omit<User, 'password'>`** removes some fields, for an API response without secrets.
- **`Record<'admin' | 'user', number>`** builds an object type with given keys and value type.
- **`ReturnType<typeof fn>` / `Parameters<typeof fn>`** extract a function's return type or parameter types.
- **`Awaited<Promise<X>>`** gives you `X`, the value inside a promise.

They keep related types **in sync**: when `User` changes, every derived type updates automatically.

== 2.9
This section is about **type-level programming**: using TypeScript's type system to *compute* new types from existing ones. Most application code doesn't need it, but library code and well-typed APIs do. Understanding it also helps you read complex error messages.

- **`typeof value`** (in a type position) gets the type of an existing variable. **`keyof Type`** gets a union of its property names. **`Type['prop']`** reads the type of one property (an *indexed access*).
- **`as const`** freezes a value into its most specific literal type (e.g. `'admin'` instead of `string`) and makes it read-only.
- **Mapped types** (`{ [K in keyof T]: ... }`) loop over every key of a type and build a new one. This is how `Partial` and `Readonly` are implemented.
- **Conditional types** (`T extends U ? X : Y`) are an "if/else" for types.
- **`infer`** captures a part of a type inside a conditional, e.g. "the type that this Promise wraps".
- **Template literal types** build string types from other string types (`` `on${Capitalize<Event>}` `` → `'onClick'`).
- **`satisfies`** checks that a value matches a type *without* widening it, so you keep the precise inferred type.
- **Branded types** prevent mixing up values that share a basic type, such as a `UserId` string and an `OrderId` string.

== 2.10
TypeScript adds safety features on top of JavaScript classes:

- **Access modifiers:** `public` (anyone can use it, the default), `private` (only inside this class), `protected` (this class and subclasses). These are checked only by the compiler. JavaScript's `#field` syntax is private at run time too.
- **`readonly`:** a property that can be set only in the constructor.
- **Parameter properties:** `constructor(private name: string)` declares and assigns a field in one go.
- **`abstract` classes:** cannot be instantiated directly. They define methods that subclasses *must* implement. They work as a template for a family of classes.
- **`implements`:** a class promises to satisfy an interface's shape, and the compiler checks the promise.
- **`override`:** marks a method that replaces a parent's method, so TS errors if the parent method doesn't exist (catching typos and renamed methods).
- **Generic classes:** `class Stack<T>` works for stacks of any type.

== 2.11
An **enum** ("enumeration") is a named set of constants, like days of the week or order statuses. It makes code more readable than magic strings or numbers scattered around.

```typescript
enum OrderStatus { Pending = 'PENDING', Shipped = 'SHIPPED', Delivered = 'DELIVERED' }
let s: OrderStatus = OrderStatus.Shipped;
```

Unlike most TypeScript features, enums **generate real JavaScript objects** at run time. Many teams prefer the simpler alternative: a **union of string literals** (`type Status = 'PENDING' | 'SHIPPED'`), optionally backed by an `as const` object. It produces no extra code, works naturally with JSON from APIs, and gives the same autocomplete.

Avoid **numeric enums** unless you have a reason. TypeScript lets *any* number be assigned to them, which defeats the purpose.

== 2.12
A **decorator** is a special function, written with `@name` above a class, method or property, that wraps or modifies the thing it decorates. It is a declarative way to add behaviour like logging, validation, dependency injection or routing without cluttering the main code.

```typescript
@Controller('/users')        // NestJS: this class handles /users routes
class UsersController {
  @Get(':id')                // this method handles GET /users/:id
  findOne() { ... }
}
```

Frameworks such as **NestJS**, **Angular** and **TypeORM** are built around decorators. TypeScript 5 supports the official ECMAScript decorator standard. Older frameworks use the earlier "experimental" version, enabled with `experimentalDecorators` in tsconfig.

== 2.13
**Declaration files (`.d.ts`)** contain *only types*, with no runnable code. They describe the shape of JavaScript code so TypeScript can type-check how you use it. When you install a plain-JS library, its types often come from a separate `@types/library-name` package (e.g. `npm i -D @types/express`).

You write your own `.d.ts` when:

- A library has no types: `declare module 'old-lib' { ... }`.
- You want to type global things such as `process.env` variables or `window` additions.
- You want to **augment** (extend) an existing type, for example adding a `user` property to Express's `Request` after your auth middleware sets it.

`declare` tells TypeScript "this exists at run time, trust me, here is its type". It produces no JavaScript.

== 2.14
Using TypeScript with React means typing:

- **Props:** describe what a component accepts with an interface or type. TS then errors if a parent forgets a required prop or passes the wrong type.
- **State:** `useState<User | null>(null)` when the initial value doesn't reveal the full type.
- **Refs:** `useRef<HTMLInputElement>(null)` so `ref.current.focus()` is known to be valid.
- **Events:** `React.ChangeEvent<HTMLInputElement>`, `React.FormEvent<HTMLFormElement>` and so on, so `e.target.value` is typed.
- **Children:** `ReactNode` is anything React can render.
- **Context:** create it with a type and a helper hook that throws if used outside the provider.

Use `ComponentProps<'button'>` to accept every native button attribute, so wrapper components behave like real HTML elements. **Generic components** (`List<T>`) let one component render lists of any item type with full type safety.

== 2.15
On the backend, TypeScript types the request and response objects of your server framework. The most important lesson is that **TypeScript cannot check data coming from outside your program at run time**: HTTP request bodies, query strings, environment variables, database results, third-party APIs. The types are gone when the code runs, so a client can send anything.

The solution is a **runtime validation library** such as **Zod**. You define a *schema* once. Zod validates real data against it at run time, and you can **derive the TypeScript type from the schema** (`z.infer<typeof Schema>`), so the type and the validation can never disagree.

== 2.16
These are **type challenges**: small puzzles where you rebuild built-in utility types or create new ones. They are a good way to practise mapped types, conditional types and `infer`. Try to write each one yourself before reading the solution. Search "type-challenges" on GitHub for hundreds more, graded from easy to extreme.

== 2.17
A summary of the special types, which interviewers often ask about:

- **`any`:** "I give up on types". Anything goes in and anything comes out. It is unsafe.
- **`unknown`:** "I don't know yet". Anything goes in, but you must narrow it before using it. It is safe.
- **`never`:** "this cannot happen". Nothing goes in. It is used for exhaustiveness checks and functions that never return.
- **`void`:** "returns nothing meaningful".

**Variance** describes when one type can be used where another is expected. For example, a function that accepts any `Animal` can safely be used where a function accepting a `Dog` is required, but not the other way round. You rarely need the theory, but it explains some confusing callback errors.
