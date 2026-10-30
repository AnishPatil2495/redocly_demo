# Part 2 — TypeScript: Basics to Advanced

## 2.1 Why TypeScript

TypeScript is a **statically typed superset** of JavaScript that compiles (transpiles) to plain JS. Types are erased at runtime — they exist only for the compiler and editor. Benefits: early error detection, refactoring safety, self-documenting APIs, excellent IntelliSense.

**Structural typing ("duck typing"):** compatibility is based on shape, not on declared names.

```typescript
interface Point { x: number; y: number }
const p = { x: 1, y: 2, z: 3 };
const q: Point = p;            // OK — p has at least x and y
// const r: Point = { x: 1, y: 2, z: 3 }; // Error: excess property check on literals
```

## 2.2 Key `tsconfig.json` Options

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,                  // enables all strict checks below
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true, // arr[i] is T | undefined
    "exactOptionalPropertyTypes": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "sourceMap": true,
    "jsx": "react-jsx",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

## 2.3 Basic Types

```typescript
let id: number = 1;
let name: string = 'Anish';
let active: boolean = true;
let big: bigint = 100n;
let nothing: null = null;
let notSet: undefined = undefined;

let list: number[] = [1, 2];
let list2: Array<string> = ['a'];
let tuple: [string, number] = ['age', 30];
let namedTuple: [name: string, age?: number] = ['A'];
let readonlyArr: readonly number[] = [1, 2];

let anything: any = 4;       // opts out of type checking — avoid
let safe: unknown = 4;       // must narrow before use — prefer over any
if (typeof safe === 'number') safe.toFixed(2);

function fail(msg: string): never { throw new Error(msg); } // never returns
function log(msg: string): void { console.log(msg); }

// Literal types
let dir: 'up' | 'down' = 'up';
const PORT = 3000;           // type is literal 3000
```

## 2.4 Interfaces vs Type Aliases

```typescript
interface User {
  readonly id: number;
  name: string;
  email?: string;                  // optional
  [key: string]: unknown;          // index signature
}

interface Admin extends User { permissions: string[] }

// Declaration merging — only interfaces
interface Window { myGlobal: string }

type ID = string | number;         // unions — only type aliases
type Point = { x: number; y: number };
type Point3D = Point & { z: number }; // intersection
type Handler = (e: Event) => void;
```

| | `interface` | `type` |
|---|---|---|
| Object shapes | Yes | Yes |
| Unions / primitives / tuples | No | Yes |
| Declaration merging | Yes | No |
| `extends` | Yes | Via `&` |
| Mapped/conditional types | No | Yes |

Rule of thumb: `interface` for public object contracts and class shapes; `type` for unions, utility compositions and everything else.

## 2.5 Functions

```typescript
function add(a: number, b: number = 0): number { return a + b; }
const greet = (name: string, greeting?: string): string => `${greeting ?? 'Hi'} ${name}`;
function sum(...nums: number[]): number { return nums.reduce((a, b) => a + b, 0); }

// Function type
type BinaryOp = (a: number, b: number) => number;

// Overloads
function parse(input: string): number;
function parse(input: number): string;
function parse(input: string | number) {
  return typeof input === 'string' ? Number(input) : String(input);
}

// `this` parameter
function onClick(this: HTMLButtonElement, e: MouseEvent) { this.disabled = true; }
```

## 2.6 Narrowing and Type Guards

```typescript
function format(v: string | number | Date | null) {
  if (v == null) return '';                 // null/undefined narrowing
  if (typeof v === 'string') return v.toUpperCase();
  if (typeof v === 'number') return v.toFixed(2);
  if (v instanceof Date) return v.toISOString();
}

// `in` narrowing
type Fish = { swim: () => void };
type Bird = { fly: () => void };
function move(a: Fish | Bird) { 'swim' in a ? a.swim() : a.fly(); }

// User-defined type guard
function isString(x: unknown): x is string { return typeof x === 'string'; }

// Assertion function
function assertDefined<T>(v: T, msg = 'missing'): asserts v is NonNullable<T> {
  if (v == null) throw new Error(msg);
}
```

### Discriminated Unions + Exhaustiveness

```typescript
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rect'; w: number; h: number }
  | { kind: 'triangle'; base: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case 'circle':   return Math.PI * s.radius ** 2;
    case 'rect':     return s.w * s.h;
    case 'triangle': return 0.5 * s.base * s.height;
    default: {
      const _exhaustive: never = s; // compile error if a case is missing
      return _exhaustive;
    }
  }
}

// Typical API state modelling
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string };
```

## 2.7 Generics

```typescript
function identity<T>(value: T): T { return value; }
identity<string>('a');
identity(42);                      // inferred T = number

// Constraints
function getLength<T extends { length: number }>(x: T) { return x.length; }

// keyof constraint — type-safe property access
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key]; }
getProp({ a: 1, b: 'x' }, 'b');    // string
// getProp({ a: 1 }, 'z');         // Error

// Generic interfaces & defaults
interface ApiResponse<T = unknown> {
  data: T;
  error?: string;
  status: number;
}

// Generic class
class Stack<T> {
  private items: T[] = [];
  push(item: T) { this.items.push(item); }
  pop(): T | undefined { return this.items.pop(); }
  peek(): T | undefined { return this.items.at(-1); }
}

// Generic fetch helper
async function http<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) throw new Error(res.statusText);
  return res.json() as Promise<T>;
}
const users = await http<User[]>('/api/users');
```

## 2.8 Built-in Utility Types

```typescript
interface Todo { id: number; title: string; done: boolean; tags?: string[] }

type A = Partial<Todo>;                  // all optional
type B = Required<Todo>;                 // all required
type C = Readonly<Todo>;                 // all readonly
type D = Pick<Todo, 'id' | 'title'>;     // subset
type E = Omit<Todo, 'id'>;               // remove keys
type F = Record<'admin' | 'user', number>; // { admin: number; user: number }
type G = Exclude<'a' | 'b' | 'c', 'a'>;  // 'b' | 'c'
type H = Extract<'a' | 'b', 'a' | 'z'>;  // 'a'
type I = NonNullable<string | null>;     // string
type J = ReturnType<typeof setTimeout>;
type K = Parameters<(a: number, b: string) => void>; // [number, string]
type L = Awaited<Promise<Promise<number>>>; // number
type M = InstanceType<typeof Date>;
type N = Uppercase<'hi'>;                 // 'HI' (also Lowercase, Capitalize, Uncapitalize)

// Common patterns
type CreateTodoDto = Omit<Todo, 'id'>;
type UpdateTodoDto = Partial<Omit<Todo, 'id'>> & Pick<Todo, 'id'>;
```

## 2.9 Advanced Types

### `keyof`, `typeof`, indexed access

```typescript
const config = { host: 'localhost', port: 5432 } as const;
type Config = typeof config;             // { readonly host: 'localhost'; readonly port: 5432 }
type ConfigKey = keyof Config;           // 'host' | 'port'
type Port = Config['port'];              // 5432

const ROLES = ['admin', 'editor', 'viewer'] as const;
type Role = (typeof ROLES)[number];      // 'admin' | 'editor' | 'viewer'
```

### Mapped Types

```typescript
type MyReadonly<T> = { readonly [K in keyof T]: T[K] };
type MyPartial<T> = { [K in keyof T]?: T[K] };
type Mutable<T> = { -readonly [K in keyof T]: T[K] };   // remove modifier
type Nullable<T> = { [K in keyof T]: T[K] | null };

// Key remapping with `as`
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
type UserGetters = Getters<{ name: string; age: number }>;
// { getName: () => string; getAge: () => number }

// Filter keys by value type
type PickByType<T, V> = { [K in keyof T as T[K] extends V ? K : never]: T[K] };
```

### Conditional Types and `infer`

```typescript
type IsString<T> = T extends string ? true : false;

// Distributive over unions
type ToArray<T> = T extends any ? T[] : never;
type X = ToArray<string | number>;        // string[] | number[]
type NoDistribute<T> = [T] extends [any] ? T[] : never; // (string | number)[]

// infer — extract inner types
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type ElementType<T> = T extends (infer U)[] ? U : T;
type UnwrapPromise<T> = T extends Promise<infer U> ? UnwrapPromise<U> : T;

// Deep partial (recursive)
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};
```

### Template Literal Types

```typescript
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type Route = `/api/${'users' | 'orders'}`;
type Endpoint = `${HttpMethod} ${Route}`;     // 'GET /api/users' | ...

type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickHandler = EventName<'click'>;       // 'onClick'

// Extract route params: '/users/:id/posts/:postId' → 'id' | 'postId'
type Params<S extends string> =
  S extends `${string}:${infer P}/${infer Rest}` ? P | Params<Rest>
  : S extends `${string}:${infer P}` ? P
  : never;
type R = Params<'/users/:id/posts/:postId'>;  // 'id' | 'postId'
```

### `satisfies` operator (TS 4.9+)

```typescript
type Colors = Record<'primary' | 'secondary', string | [number, number, number]>;

const palette = {
  primary: '#f00',
  secondary: [0, 128, 255],
} satisfies Colors;      // validates shape BUT keeps the narrow inferred type

palette.primary.toUpperCase();   // OK — known to be string
palette.secondary.map(n => n);   // OK — known to be tuple
```

### Branded / Nominal Types

```typescript
type Brand<T, B extends string> = T & { readonly __brand: B };
type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

const toUserId = (s: string) => s as UserId;
function getUser(id: UserId) { /* ... */ }
getUser(toUserId('u_1'));
// getUser('o_1' as OrderId); // Error — prevents mixing IDs
```

## 2.10 Classes in TypeScript

```typescript
abstract class Repository<T extends { id: number }> {
  protected items = new Map<number, T>();
  constructor(protected readonly tableName: string) {}   // parameter property

  abstract validate(item: T): boolean;

  save(item: T): T {
    if (!this.validate(item)) throw new Error('Invalid');
    this.items.set(item.id, item);
    return item;
  }
  findById(id: number): T | undefined { return this.items.get(id); }
}

interface Product { id: number; name: string; price: number }

class ProductRepo extends Repository<Product> implements Iterable<Product> {
  constructor() { super('products'); }
  validate(p: Product) { return p.price >= 0; }
  override findById(id: number) { return super.findById(id); }
  *[Symbol.iterator]() { yield* this.items.values(); }
}
```

Access modifiers: `public` (default), `protected` (class + subclasses), `private` (TS compile-time only), `#private` (JS runtime-private). `readonly` prevents re-assignment.

## 2.11 Enums vs Union Literals

```typescript
enum Status { Active = 'ACTIVE', Inactive = 'INACTIVE' }   // emits runtime object
const enum Dir { Up, Down }                                // inlined, no runtime object

// Often preferred: union + as const object (no TS-only runtime emit)
const STATUS = { Active: 'ACTIVE', Inactive: 'INACTIVE' } as const;
type StatusT = (typeof STATUS)[keyof typeof STATUS];       // 'ACTIVE' | 'INACTIVE'
```

Numeric enums are reverse-mapped and accept any number — a common source of bugs. Prefer string enums or union types.

## 2.12 Decorators (TS 5 Standard Decorators)

```typescript
function log<T extends (...args: any[]) => any>(target: T, ctx: ClassMethodDecoratorContext) {
  return function (this: unknown, ...args: Parameters<T>): ReturnType<T> {
    console.log(`→ ${String(ctx.name)}`, args);
    return target.apply(this, args);
  } as T;
}

class Calculator {
  @log
  add(a: number, b: number) { return a + b; }
}
```

Frameworks like NestJS, TypeORM and Angular use (legacy) `experimentalDecorators` with `emitDecoratorMetadata`.

## 2.13 Declaration Files and Module Augmentation

```typescript
// types/env.d.ts
declare namespace NodeJS {
  interface ProcessEnv {
    DATABASE_URL: string;
    NODE_ENV: 'development' | 'production' | 'test';
  }
}

// Untyped JS library
declare module 'legacy-lib' {
  export function doThing(x: string): number;
}

// Augment Express Request
declare global {
  namespace Express {
    interface Request { user?: { id: string; role: string } }
  }
}
export {};
```

## 2.14 TypeScript with React

```tsx
import { useState, useRef, useReducer, createContext, useContext, type ReactNode, type ComponentProps } from 'react';

type ButtonProps = ComponentProps<'button'> & {
  variant?: 'primary' | 'ghost';
  loading?: boolean;
};

export function Button({ variant = 'primary', loading, children, ...rest }: ButtonProps) {
  return (
    <button className={variant} disabled={loading || rest.disabled} {...rest}>
      {loading ? 'Loading…' : children}
    </button>
  );
}

// State & refs
const [user, setUser] = useState<User | null>(null);
const inputRef = useRef<HTMLInputElement>(null);

// Events
const onChange = (e: React.ChangeEvent<HTMLInputElement>) => setValue(e.target.value);
const onSubmit = (e: React.FormEvent<HTMLFormElement>) => e.preventDefault();

// Generic component
type ListProps<T> = { items: T[]; render: (item: T) => ReactNode; keyOf: (item: T) => string };
function List<T>({ items, render, keyOf }: ListProps<T>) {
  return <ul>{items.map(i => <li key={keyOf(i)}>{render(i)}</li>)}</ul>;
}

// Typed reducer
type Action = { type: 'inc' } | { type: 'set'; payload: number };
function reducer(state: number, action: Action): number {
  switch (action.type) {
    case 'inc': return state + 1;
    case 'set': return action.payload;
  }
}

// Typed context with safe hook
type AuthCtx = { user: User | null; login: (u: User) => void };
const AuthContext = createContext<AuthCtx | null>(null);
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
```

## 2.15 TypeScript with Node/Express

```typescript
import express, { type Request, type Response, type NextFunction } from 'express';
import { z } from 'zod';

const CreateUser = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  age: z.number().int().positive().optional(),
});
type CreateUserDto = z.infer<typeof CreateUser>;   // derive TS type from runtime schema

const app = express();
app.use(express.json());

app.post('/users', (req: Request<{}, {}, CreateUserDto>, res: Response, next: NextFunction) => {
  const parsed = CreateUser.safeParse(req.body);
  if (!parsed.success) return res.status(400).json(parsed.error.flatten());
  res.status(201).json({ id: 1, ...parsed.data });
});
```

**Key insight:** TS types vanish at runtime, so validate external input (HTTP bodies, env vars, JSON files) with a runtime schema (Zod, Valibot, io-ts) and *infer* the static type from it.

## 2.16 Type Challenges (Practice)

```typescript
// 1. MyPick
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };

// 2. TupleToUnion
type TupleToUnion<T extends readonly unknown[]> = T[number];

// 3. Last element of tuple
type Last<T extends unknown[]> = T extends [...infer _, infer L] ? L : never;

// 4. DeepReadonly
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends (...a: any[]) => any ? T[K]
    : T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

// 5. Union to intersection
type UnionToIntersection<U> =
  (U extends any ? (x: U) => void : never) extends (x: infer I) => void ? I : never;

// 6. Required keys of T
type RequiredKeys<T> = { [K in keyof T]-?: {} extends Pick<T, K> ? never : K }[keyof T];
```

## 2.17 Variance, `any` vs `unknown` vs `never` — Summary

- `any`: disables checking in both directions (assignable to/from everything).
- `unknown`: top type — anything assignable *to* it; must narrow before use.
- `never`: bottom type — assignable to everything, nothing assignable to it (except `never`). Represents impossible states.
- Function parameters are checked **contravariantly** under `strictFunctionTypes` (for function-type properties, not methods).
- `object` = any non-primitive; `{}` = any non-nullish value; `Object` — avoid.
