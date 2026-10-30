# Part 3 — React: Basics to Advanced

## 3.1 Core Ideas

- **Declarative UI:** describe *what* the UI should look like for a given state; React figures out *how* to update the DOM.
- **Components:** functions that take props and return JSX.
- **Unidirectional data flow:** data goes down via props; events go up via callbacks.
- **UI = f(state):** re-rendering is just calling the component function again.

### JSX

JSX compiles to `jsx()` calls (React 17+ automatic runtime), producing plain objects (React elements).

```jsx
const el = <h1 className="title">Hello {name}</h1>;
// compiles to → jsx('h1', { className: 'title', children: ['Hello ', name] })

// Rules: one root (or <>…</> Fragment), className/htmlFor, camelCase events,
// {} for expressions, self-close empty tags, style={{ color: 'red' }}
```

### Virtual DOM, Reconciliation and Fiber

1. State changes → React re-renders the component → new element tree.
2. **Reconciliation / diffing:** compares new tree vs previous. Heuristics: different element type ⇒ destroy and rebuild subtree; same type ⇒ update props; lists are matched by `key`.
3. **Commit phase:** applies the minimal DOM mutations, runs layout effects, then passive effects.

**Fiber** (React 16+) is the reconciliation engine: work is split into units so rendering can be paused, prioritized and resumed — enabling **concurrent rendering** (React 18+).

**Render phase** (pure, may run multiple times, interruptible) vs **commit phase** (side effects, synchronous).

### Keys

```jsx
// Bad — index keys break state when items are reordered/inserted
{todos.map((t, i) => <TodoItem key={i} todo={t} />)}
// Good — stable unique id
{todos.map(t => <TodoItem key={t.id} todo={t} />)}

// Trick: changing `key` resets a component's state entirely
<ProfileForm key={userId} userId={userId} />
```

## 3.2 Components and Props

```jsx
function Avatar({ src, size = 40, alt = '' }) {
  return <img src={src} width={size} height={size} alt={alt} />;
}

// children & composition
function Card({ title, children, footer }) {
  return (
    <section className="card">
      <h2>{title}</h2>
      <div>{children}</div>
      {footer && <footer>{footer}</footer>}
    </section>
  );
}

<Card title="Profile" footer={<button>Save</button>}>
  <Avatar src="/me.png" />
</Card>
```

**Conditional rendering:**

```jsx
{isLoggedIn ? <Dashboard /> : <Login />}
{items.length > 0 && <List items={items} />}   // careful: {0 && <X/>} renders "0"
{items.length ? <List /> : null}
```

**Controlled vs uncontrolled inputs:**

```jsx
// Controlled — React state is the source of truth
const [email, setEmail] = useState('');
<input value={email} onChange={e => setEmail(e.target.value)} />

// Uncontrolled — DOM holds the value; read via ref / FormData
const ref = useRef(null);
<input defaultValue="x" ref={ref} />
```

## 3.3 Hooks — Complete Reference

**Rules of Hooks:** only call at the top level (not in loops/conditions/nested functions) and only from React functions or custom hooks. React relies on call order to associate state with hooks.

### useState

```jsx
const [count, setCount] = useState(0);
const [data, setData] = useState(() => expensiveInit()); // lazy initializer — runs once

setCount(count + 1);             // uses the value from this render
setCount(c => c + 1);            // functional update — use when new state depends on old

// State updates are batched (automatic batching in React 18 for all updates)
function handle() {
  setCount(c => c + 1);
  setCount(c => c + 1);          // final: +2 ; with setCount(count + 1) twice → +1
}

// Objects/arrays: always create new references (immutability)
setUser(u => ({ ...u, name: 'New' }));
setTodos(ts => ts.map(t => (t.id === id ? { ...t, done: !t.done } : t)));
setTodos(ts => ts.filter(t => t.id !== id));
```

### useEffect

Synchronizes a component with an **external system** (network, subscriptions, timers, DOM APIs). Runs *after* paint.

```jsx
useEffect(() => {
  // runs after every render if no deps array
});

useEffect(() => {
  // runs once after mount
}, []);

useEffect(() => {
  const controller = new AbortController();
  let ignore = false;

  async function load() {
    try {
      const res = await fetch(`/api/users/${userId}`, { signal: controller.signal });
      const json = await res.json();
      if (!ignore) setUser(json);
    } catch (e) {
      if (e.name !== 'AbortError') setError(e);
    }
  }
  load();

  return () => {           // cleanup: runs before next effect & on unmount
    ignore = true;
    controller.abort();
  };
}, [userId]);              // re-run when userId changes (avoids race conditions)
```

In development with `<StrictMode>`, effects run **mount → unmount → mount** to surface missing cleanups.

**You might not need an effect:**

```jsx
// Bad — derived state via effect causes an extra render
const [fullName, setFullName] = useState('');
useEffect(() => setFullName(`${first} ${last}`), [first, last]);

// Good — compute during render
const fullName = `${first} ${last}`;

// Bad — resetting state on prop change via effect. Good — use `key`.
// Bad — handling user events in effects. Good — do it in the event handler.
```

### useLayoutEffect

Same signature as `useEffect`, but fires synchronously **after DOM mutations, before paint**. Use for measuring layout (tooltip positioning) to avoid flicker. Blocks painting — use sparingly.

### useRef

```jsx
const inputRef = useRef(null);
useEffect(() => inputRef.current.focus(), []);
<input ref={inputRef} />

// Mutable value that persists across renders WITHOUT causing re-render
const renderCount = useRef(0);
renderCount.current++;

// Keep the latest value for use in callbacks / intervals
const savedCallback = useRef(callback);
useEffect(() => { savedCallback.current = callback; }, [callback]);
```

### useMemo and useCallback

```jsx
// Memoize an expensive computation
const visibleTodos = useMemo(() => filterTodos(todos, tab), [todos, tab]);

// Memoize a function reference (useful when passed to memoized children / effect deps)
const handleSelect = useCallback((id) => setSelected(id), []);

// useCallback(fn, deps) === useMemo(() => fn, deps)
```

Do not memoize everything — it has a cost. Use it when (1) the computation is expensive, (2) referential stability matters for `React.memo` children or effect dependencies. The **React Compiler** (React 19 ecosystem) can auto-memoize.

### useReducer

```jsx
const initialState = { items: [], loading: false, error: null };

function reducer(state, action) {
  switch (action.type) {
    case 'FETCH_START':   return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS': return { ...state, loading: false, items: action.payload };
    case 'FETCH_ERROR':   return { ...state, loading: false, error: action.error };
    case 'REMOVE':        return { ...state, items: state.items.filter(i => i.id !== action.id) };
    default: throw new Error(`Unknown action ${action.type}`);
  }
}

const [state, dispatch] = useReducer(reducer, initialState);
dispatch({ type: 'FETCH_START' });
```

Prefer `useReducer` when state has multiple sub-values that change together or next state depends on complex logic.

### useContext

```jsx
const ThemeContext = createContext('light');

function App() {
  const [theme, setTheme] = useState('dark');
  const value = useMemo(() => ({ theme, setTheme }), [theme]); // avoid re-render storms
  return (
    <ThemeContext.Provider value={value}>
      <Toolbar />
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  const { theme, setTheme } = useContext(ThemeContext);
  return <button onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}>{theme}</button>;
}
```

All consumers re-render when the context value changes. Split contexts (state vs dispatch) or use a store library for frequently changing global state.

### Other Hooks

```jsx
// useId — stable unique ids (SSR-safe) for accessibility
const id = useId();
<label htmlFor={id}>Email</label><input id={id} />

// useTransition — mark updates as non-urgent (keeps input responsive)
const [isPending, startTransition] = useTransition();
const onChange = (e) => {
  setQuery(e.target.value);                         // urgent
  startTransition(() => setResults(search(e.target.value))); // can be interrupted
};

// useDeferredValue — defer re-rendering of an expensive part
const deferredQuery = useDeferredValue(query);
<SlowList query={deferredQuery} />

// useImperativeHandle — expose a custom API to a parent ref
function FancyInput({ ref }) {       // React 19: ref is a normal prop
  const inner = useRef();
  useImperativeHandle(ref, () => ({ focus: () => inner.current.focus() }));
  return <input ref={inner} />;
}

// useSyncExternalStore — subscribe to external stores safely in concurrent mode
const isOnline = useSyncExternalStore(
  (cb) => { window.addEventListener('online', cb); window.addEventListener('offline', cb);
            return () => { window.removeEventListener('online', cb); window.removeEventListener('offline', cb); }; },
  () => navigator.onLine,
);
```

### React 19 Hooks and APIs

```jsx
// use() — read a promise or context (can be called conditionally)
function Comments({ commentsPromise }) {
  const comments = use(commentsPromise);   // suspends until resolved
  return comments.map(c => <p key={c.id}>{c.text}</p>);
}

// Actions + useActionState — form handling with pending & errors
async function updateName(prevState, formData) {
  const error = await saveName(formData.get('name'));
  return error ? { error } : { error: null };
}
function NameForm() {
  const [state, formAction, isPending] = useActionState(updateName, { error: null });
  return (
    <form action={formAction}>
      <input name="name" />
      <SubmitButton />
      {state.error && <p>{state.error}</p>}
    </form>
  );
}

// useFormStatus — status of the parent <form>
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>{pending ? 'Saving…' : 'Save'}</button>;
}

// useOptimistic — show the result instantly while the request is in flight
const [optimisticTodos, addOptimistic] = useOptimistic(todos, (state, newTodo) => [...state, newTodo]);
```

Other React 19 changes: `ref` as a prop (no more `forwardRef` for new code), `<Context>` usable directly as provider, document metadata (`<title>`, `<meta>`) hoisting, ref cleanup functions.

## 3.4 Custom Hooks

Custom hooks extract reusable **stateful logic** (not state itself — every call gets its own state).

```jsx
function useFetch(url) {
  const [state, setState] = useState({ data: null, loading: true, error: null });

  useEffect(() => {
    const controller = new AbortController();
    setState(s => ({ ...s, loading: true }));
    fetch(url, { signal: controller.signal })
      .then(r => { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then(data => setState({ data, loading: false, error: null }))
      .catch(error => error.name !== 'AbortError' && setState({ data: null, loading: false, error }));
    return () => controller.abort();
  }, [url]);

  return state;
}

function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

function useLocalStorage(key, initial) {
  const [value, setValue] = useState(() => {
    try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : initial; }
    catch { return initial; }
  });
  useEffect(() => { localStorage.setItem(key, JSON.stringify(value)); }, [key, value]);
  return [value, setValue];
}

function usePrevious(value) {
  const ref = useRef();
  useEffect(() => { ref.current = value; }, [value]);
  return ref.current;
}

function useInterval(callback, delay) {
  const saved = useRef(callback);
  useEffect(() => { saved.current = callback; }, [callback]);
  useEffect(() => {
    if (delay == null) return;
    const id = setInterval(() => saved.current(), delay);
    return () => clearInterval(id);
  }, [delay]);
}

function useOnClickOutside(ref, handler) {
  useEffect(() => {
    const listener = (e) => { if (!ref.current || ref.current.contains(e.target)) return; handler(e); };
    document.addEventListener('mousedown', listener);
    return () => document.removeEventListener('mousedown', listener);
  }, [ref, handler]);
}
```

## 3.5 Stale Closures — The Most Common Hook Bug

```jsx
function Timer() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setCount(count + 1);   // BUG: `count` is always 0 (captured from first render)
    }, 1000);
    return () => clearInterval(id);
  }, []);                     // missing dependency

  // FIX 1: functional update → setCount(c => c + 1)
  // FIX 2: add count to deps (interval re-created every tick)
  // FIX 3: keep latest value in a ref
}
```

Always enable `eslint-plugin-react-hooks` (`exhaustive-deps`).

## 3.6 Performance Optimization

```jsx
// React.memo — skip re-render if props are shallow-equal
const Row = React.memo(function Row({ item, onSelect }) {
  return <li onClick={() => onSelect(item.id)}>{item.name}</li>;
});

function List({ items }) {
  const [selected, setSelected] = useState(null);
  const onSelect = useCallback((id) => setSelected(id), []); // stable ref → memo works
  return <ul>{items.map(i => <Row key={i.id} item={i} onSelect={onSelect} />)}</ul>;
}
```

**Why does a component re-render?** (1) its state changed, (2) its parent re-rendered, (3) a context it uses changed. Props changing is *not* itself a trigger — parent re-render is.

**Techniques:**

- Move state down (colocate) so fewer components re-render.
- Lift content up — pass expensive subtrees as `children` (they don't re-render when the wrapper's state changes).
- Code splitting with `React.lazy` + `Suspense`.
- Virtualize long lists (`react-window`, `@tanstack/react-virtual`).
- Debounce input; use `useTransition`/`useDeferredValue`.
- Avoid creating new objects/arrays in props unnecessarily.
- Profile with React DevTools Profiler; check "why did this render".

```jsx
const Settings = lazy(() => import('./Settings'));

<Suspense fallback={<Spinner />}>
  <Settings />
</Suspense>
```

## 3.7 Advanced Component Patterns

### Compound Components

```jsx
const TabsContext = createContext(null);

function Tabs({ defaultIndex = 0, children }) {
  const [active, setActive] = useState(defaultIndex);
  return <TabsContext.Provider value={{ active, setActive }}>{children}</TabsContext.Provider>;
}
Tabs.List = function TabList({ children }) {
  return <div role="tablist">{children}</div>;
};
Tabs.Tab = function Tab({ index, children }) {
  const { active, setActive } = useContext(TabsContext);
  return <button role="tab" aria-selected={active === index} onClick={() => setActive(index)}>{children}</button>;
};
Tabs.Panel = function Panel({ index, children }) {
  const { active } = useContext(TabsContext);
  return active === index ? <div role="tabpanel">{children}</div> : null;
};

<Tabs>
  <Tabs.List><Tabs.Tab index={0}>A</Tabs.Tab><Tabs.Tab index={1}>B</Tabs.Tab></Tabs.List>
  <Tabs.Panel index={0}>Panel A</Tabs.Panel>
  <Tabs.Panel index={1}>Panel B</Tabs.Panel>
</Tabs>
```

### Higher-Order Components (HOC)

```jsx
function withAuth(Component) {
  return function Wrapped(props) {
    const { user } = useAuth();
    if (!user) return <Navigate to="/login" />;
    return <Component {...props} user={user} />;
  };
}
export default withAuth(Dashboard);
```

### Render Props

```jsx
function MouseTracker({ render }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  return <div onMouseMove={e => setPos({ x: e.clientX, y: e.clientY })}>{render(pos)}</div>;
}
<MouseTracker render={({ x, y }) => <p>{x}, {y}</p>} />
```

Custom hooks have largely replaced HOCs and render props for logic reuse.

### Controlled/Uncontrolled hybrid & Portals

```jsx
// Portal — render outside parent DOM (modals, tooltips); events still bubble through React tree
function Modal({ open, onClose, children }) {
  if (!open) return null;
  return createPortal(
    <div className="backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>{children}</div>
    </div>,
    document.body,
  );
}
```

## 3.8 Error Boundaries

Catch rendering errors in the subtree (not in event handlers, async code, or SSR). Must be class components (or use `react-error-boundary`).

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, info) { logToService(error, info.componentStack); }
  render() {
    if (this.state.hasError) return this.props.fallback ?? <h2>Something went wrong.</h2>;
    return this.props.children;
  }
}
```

## 3.9 Class Component Lifecycle (for legacy code)

| Phase | Methods |
|---|---|
| Mount | `constructor` → `getDerivedStateFromProps` → `render` → `componentDidMount` |
| Update | `getDerivedStateFromProps` → `shouldComponentUpdate` → `render` → `getSnapshotBeforeUpdate` → `componentDidUpdate` |
| Unmount | `componentWillUnmount` |
| Error | `getDerivedStateFromError`, `componentDidCatch` |

Hook equivalents: `componentDidMount` ≈ `useEffect(fn, [])`; `componentDidUpdate` ≈ `useEffect(fn, [deps])`; `componentWillUnmount` ≈ cleanup function; `shouldComponentUpdate` ≈ `React.memo`.

## 3.10 State Management

| Kind of state | Tool |
|---|---|
| Local UI state | `useState` / `useReducer` |
| Shared across a subtree | Lift state up / Context |
| Global client state | Redux Toolkit, Zustand, Jotai |
| Server state (cache, refetch) | TanStack Query, RTK Query, SWR |
| URL state | Router search params |
| Form state | React Hook Form + Zod |

### Redux Toolkit

```jsx
import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchTodos = createAsyncThunk('todos/fetch', async () => {
  const res = await fetch('/api/todos');
  return res.json();
});

const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [], status: 'idle' },
  reducers: {
    added(state, action) { state.items.push(action.payload); }, // Immer makes "mutation" safe
    toggled(state, action) {
      const t = state.items.find(t => t.id === action.payload);
      if (t) t.done = !t.done;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTodos.pending, (s) => { s.status = 'loading'; })
      .addCase(fetchTodos.fulfilled, (s, a) => { s.status = 'idle'; s.items = a.payload; })
      .addCase(fetchTodos.rejected, (s) => { s.status = 'failed'; });
  },
});

export const { added, toggled } = todosSlice.actions;
export const store = configureStore({ reducer: { todos: todosSlice.reducer } });

// In components
const todos = useSelector((s) => s.todos.items);
const dispatch = useDispatch();
dispatch(added({ id: 1, title: 'x', done: false }));
```

**Redux principles:** single source of truth, state is read-only (change via actions), changes via pure reducers. Middleware (thunk, saga, listener) handle side effects.

### Zustand

```jsx
import { create } from 'zustand';
const useCart = create((set, get) => ({
  items: [],
  add: (item) => set((s) => ({ items: [...s.items, item] })),
  total: () => get().items.reduce((sum, i) => sum + i.price, 0),
}));
const items = useCart((s) => s.items);  // selector → re-render only when items change
```

### TanStack Query (server state)

```jsx
const { data, isLoading, error } = useQuery({
  queryKey: ['users', page],
  queryFn: () => fetch(`/api/users?page=${page}`).then(r => r.json()),
  staleTime: 60_000,
});

const queryClient = useQueryClient();
const mutation = useMutation({
  mutationFn: (user) => fetch('/api/users', { method: 'POST', body: JSON.stringify(user) }),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
});
```

## 3.11 Routing (React Router v6/v7)

```jsx
import { createBrowserRouter, RouterProvider, Outlet, Link, NavLink, useParams, useNavigate, useSearchParams, Navigate } from 'react-router-dom';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <Home /> },
      { path: 'users/:id', element: <UserPage />, loader: ({ params }) => fetchUser(params.id) },
      { path: 'admin', element: <RequireAuth><Admin /></RequireAuth> },
      { path: '*', element: <NotFound /> },
    ],
  },
]);

function Layout() { return <><nav><NavLink to="/">Home</NavLink></nav><Outlet /></>; }

function UserPage() {
  const { id } = useParams();
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  return <button onClick={() => navigate('/')}>Back</button>;
}

function RequireAuth({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}
```

## 3.12 Forms — React Hook Form + Zod

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});
type FormValues = z.infer<typeof schema>;

export function LoginForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => { await login(values); };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
      <input type="password" {...register('password')} />
      <button disabled={isSubmitting}>Login</button>
    </form>
  );
}
```

## 3.13 Rendering Strategies and Server Components

| Strategy | When HTML is generated | Use case |
|---|---|---|
| CSR | In browser | Dashboards behind auth |
| SSR | Per request on server | Personalized, SEO pages |
| SSG | At build time | Docs, blogs, marketing |
| ISR | Build + revalidate periodically | E-commerce catalogs |
| Streaming SSR | Server streams chunks with Suspense | Faster TTFB/FCP |

**Hydration:** attaching event listeners to server-rendered HTML. Mismatches (e.g., `Date.now()` or `window` used during render) cause hydration errors.

**React Server Components (Next.js App Router):**

```tsx
// app/users/page.tsx — Server Component (default): runs only on server, can access DB, zero JS shipped
import { db } from '@/lib/db';
import LikeButton from './LikeButton';

export default async function UsersPage() {
  const users = await db.user.findMany();
  return users.map(u => <div key={u.id}>{u.name} <LikeButton id={u.id} /></div>);
}

// app/users/LikeButton.tsx — Client Component: interactivity, hooks, browser APIs
'use client';
import { useState } from 'react';
export default function LikeButton({ id }: { id: number }) {
  const [liked, setLiked] = useState(false);
  return <button onClick={() => setLiked(!liked)}>{liked ? '♥' : '♡'}</button>;
}

// Server Action
'use server';
export async function createUser(formData: FormData) {
  await db.user.create({ data: { name: String(formData.get('name')) } });
  revalidatePath('/users');
}
```

## 3.14 Testing React

```jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('increments counter', async () => {
  render(<Counter />);
  await userEvent.click(screen.getByRole('button', { name: /increment/i }));
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});

test('loads users', async () => {
  global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => [{ id: 1, name: 'A' }] });
  render(<Users />);
  expect(await screen.findByText('A')).toBeInTheDocument(); // findBy waits
});

// Testing a custom hook
import { renderHook, act } from '@testing-library/react';
const { result } = renderHook(() => useCounter());
act(() => result.current.inc());
expect(result.current.count).toBe(1);
```

Query priority: `getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByTestId`. Mock network with MSW for realistic tests.

## 3.15 Interview Questions Checklist

- Difference between state and props; why state is immutable.
- What triggers a re-render; how `React.memo`, `useMemo`, `useCallback` relate.
- Why keys matter; why index keys are bad.
- `useEffect` vs `useLayoutEffect`; effect cleanup; StrictMode double invocation.
- Controlled vs uncontrolled components.
- Context performance pitfalls.
- How batching works in React 18.
- What is Fiber / concurrent rendering / Suspense.
- SSR vs CSR vs SSG; hydration; Server Components vs Client Components.
- How to prevent race conditions in data fetching.
- Lifting state up vs global stores; server state vs client state.
