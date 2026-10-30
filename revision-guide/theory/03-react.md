== intro
**What is React?** React is a JavaScript **library for building user interfaces**, created by Facebook (Meta) in 2013. A user interface (UI) is everything the user sees and interacts with: buttons, forms, lists, menus.

**The problem React solves.** With plain JavaScript you change the page by hand: find this element, change its text, add that class, remove that row. In a large app with lots of data changing, it becomes very hard to keep the page in sync with the data, and bugs creep in.

**React's idea:** you describe **what the UI should look like for the current data**, and React works out how to update the page efficiently whenever the data changes. You never touch the DOM directly.

```text
   data (state)  ──►  your component function  ──►  description of UI  ──►  React updates the real page
       ▲                                                                              │
       └──────────────────────── user clicks / types (events) ◄──────────────────────┘
```

**Components** are the building blocks: small, reusable, independent pieces of UI (`<Navbar />`, `<ProductCard />`, `<Button />`). You compose them like LEGO bricks to build whole pages.

**A first component:**

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);         // a piece of data that can change
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>Click me</button>
    </div>
  );
}
```

Clicking the button calls `setCount`. React then runs `Counter` again with the new `count`, compares the result with the old one, and updates only the `<p>` text on screen.

== 3.1
**Declarative vs imperative.** *Imperative* code gives step-by-step instructions ("find the list, create an li, set its text, append it"). *Declarative* code describes the end result ("the list shows these items"). React is declarative, which makes UIs easier to predict and debug.

**JSX** is the HTML-like syntax used inside React components. It is *not* HTML and not a string. A build tool converts it into plain JavaScript function calls that create lightweight objects describing the UI (called **React elements**). Inside JSX, curly braces `{ }` let you insert any JavaScript expression: variables, calculations, function calls. A few differences from HTML: `className` instead of `class`, `htmlFor` instead of `for`, event names in camelCase (`onClick`), and every tag must be closed.

**Virtual DOM.** Updating the real browser DOM is relatively slow. React keeps a lightweight copy of the UI as JavaScript objects (the "virtual DOM"). When data changes:

1. React calls your components again to produce a **new** virtual tree (this is called **rendering**).
2. It **compares** (diffs) the new tree with the previous one. This is called **reconciliation**.
3. It applies only the **differences** to the real DOM (the **commit**).

**Fiber** is the name of React's internal engine (since React 16). It splits rendering work into small units, so React can pause, prioritise urgent updates like typing over less urgent ones like a big list, and resume later. This is called **concurrent rendering**.

**Keys.** When rendering a list, give each item a stable, unique `key` (usually its database id). Keys let React tell which item is which between renders. Without good keys, React may reuse the wrong component for the wrong item, mixing up state such as checkbox values or input text.

== 3.2
A **component** is a JavaScript function that returns JSX. Its name must start with a capital letter (`UserCard`, not `userCard`) so React can tell it apart from HTML tags.

**Props** ("properties") are the inputs to a component, passed like HTML attributes: `<Avatar src="/me.png" size={40} />`. Inside the component they arrive as one object. Props are **read-only**: a component must never change its own props. Data flows **one way**, from parent to child. If a child needs to tell its parent something, the parent passes down a **callback function** as a prop, and the child calls it (e.g. `onSelect(id)`).

**`children`** is a special prop containing whatever you put *between* a component's opening and closing tags. It lets you build wrapper components like `<Card>...anything...</Card>` or `<Modal>...</Modal>`. This is called **composition**, and it is React's main way of reusing UI (instead of inheritance).

**Conditional rendering** means showing different UI based on data, using plain JavaScript: the ternary `cond ? <A/> : <B/>`, `cond && <A/>`, or an early `return`.

**Forms: controlled vs uncontrolled.** In a **controlled** input, React state holds the value. Each keystroke updates state, and state feeds the input's `value`. This gives full control for validation and formatting. In an **uncontrolled** input, the browser keeps the value and you read it when needed (via a ref or on submit). That is simpler, with less re-rendering.

== 3.3
**Hooks** are special functions, whose names start with `use`, that let function components "hook into" React features: remembering data (state), running side effects, accessing context and so on. Before hooks (2019), these features needed class components.

**Two rules you must follow** (React relies on the *order* hooks are called in to know which state belongs to which hook):

1. Call hooks only at the **top level** of a component, never inside `if` statements, loops or nested functions.
2. Call hooks only from **React components or custom hooks**, not from regular functions.

**State (`useState`)** is data that belongs to a component and can change over time: the text in an input, whether a menu is open, a list of todos. When you call the **setter** (`setCount`), React **re-renders** the component with the new value. Regular variables are reset on every render and changing them does nothing visible. State is *remembered* between renders.

- State updates are **asynchronous and batched**. Calling `setCount` does not change `count` immediately on the next line. The new value appears on the next render.
- When the new state depends on the old one, use the **function form** `setCount(c => c + 1)`, so it always uses the latest value.
- **Never mutate state** (`user.name = 'x'` or `todos.push(...)`). Always create a new object or array. React compares by reference, so a mutated object looks "unchanged" and the screen won't update.

**Side effects (`useEffect`).** Rendering should be *pure*: it only calculates UI. Anything that reaches outside the component is a **side effect**: fetching data, timers, subscriptions, manually touching the DOM, logging. `useEffect(fn, deps)` runs `fn` **after** React has updated the screen.

- The **dependency array** controls *when* it re-runs. No array: after every render. `[]`: only once after the first render ("mount"). `[userId]`: whenever `userId` changes.
- The function can return a **cleanup function**. React runs it before the effect runs again and when the component is removed ("unmounts"). Use it to cancel timers, unsubscribe and abort requests.

**Refs (`useRef`)** give you a box (`ref.current`) that survives re-renders, and changing it does **not** trigger a re-render. Two uses: (1) holding a reference to a DOM element (to focus an input, measure size), and (2) storing mutable values such as timer IDs.

**Memoisation (`useMemo`, `useCallback`).** Every render re-runs all the code in your component. `useMemo` caches the *result of a calculation* until its dependencies change. `useCallback` caches a *function* so it keeps the same identity between renders. They are performance tools. Use them when a calculation is expensive or when a stable reference matters, not everywhere.

**`useReducer`** is an alternative to `useState` for complex state. All the update logic lives in one **reducer** function, `(currentState, action) => newState`, and components **dispatch** actions such as `{ type: 'added', item }`. It is the same pattern Redux uses.

**`useContext`** reads a value from **Context**, React's way to share data (current user, theme, language) with many components deep in the tree without passing props through every level. Passing props through many levels is called **prop drilling**.

**React 19** adds `use()` (read a promise or context), **Actions** (async functions passed to forms), `useActionState`, `useFormStatus` and `useOptimistic` (show an expected result immediately while the server request is still running).

== 3.4
A **custom hook** is your own function, whose name starts with `use`, that calls other hooks. It lets you **extract and reuse stateful logic** between components. For example, "fetch data with loading and error states" or "sync a value with localStorage" can be written once and used anywhere.

Important: custom hooks share **logic**, not **state**. Each component that calls `useFetch()` gets its own independent copy of the state inside it.

Think of custom hooks as the React version of utility functions. They keep components short and focused on what to display.

== 3.5
This is the bug that confuses the most React developers, so it gets its own section.

Every render of a component is like a **snapshot**. The functions created during that render, such as event handlers and effect callbacks, **close over** (remember) the props and state **of that particular render** (see Closures, 1.6). If such a function lives on, like a `setInterval` created once in an effect with `[]` deps, it keeps seeing the *old* values forever. That is a **stale closure**.

**Fixes:** use the functional state update (`setCount(c => c + 1)`), list every value you use in the dependency array (the ESLint rule `react-hooks/exhaustive-deps` reminds you), or keep the latest value in a `ref`.

== 3.6
**When does a component re-render?** When (1) its own state changes, (2) its **parent** re-renders, which by default makes all children re-render too, or (3) a context value it reads changes.

Re-rendering is normally cheap and fine. It becomes a problem only with very large trees, expensive calculations or long lists. **Measure first** with React DevTools' *Profiler* before optimising.

Tools:

- **`React.memo(Component)`:** skip re-rendering a child when its props are the same as last time (compared shallowly). It only works if the props you pass are stable, which is why it pairs with `useCallback`/`useMemo`.
- **Keep state close to where it's used:** state at the top of the app makes the whole app re-render on every change.
- **Code splitting (`React.lazy` + `Suspense`):** don't download code for pages the user hasn't opened.
- **Virtualisation:** for lists of thousands of rows, render only the rows visible on screen.

== 3.7
As apps grow, certain **component patterns** help structure reusable UI:

- **Compound components:** a group of components that work together and share hidden state through context, like HTML's `<select>` and `<option>`. For example `<Tabs>`, `<Tabs.Tab>`, `<Tabs.Panel>`. The user of the component gets a flexible, readable API.
- **Higher-Order Component (HOC):** a function that takes a component and returns a new, enhanced one (`withAuth(Dashboard)`). It was common before hooks.
- **Render props:** a component receives a *function* as a prop and calls it to decide what to render, sharing its internal data with the caller.
- **Portals:** render a component into a different place in the DOM (such as directly under `<body>`) while keeping it in the same React tree. They are used for modals, tooltips and toasts, so they are not clipped by parent CSS.

Today, **custom hooks** are the preferred way to share logic. HOCs and render props are still found in older code and some libraries.

== 3.8
Normally, if any component throws an error while rendering, **the entire React app unmounts**, and the user sees a blank page. An **error boundary** is a component that catches errors from the components *inside* it and shows a fallback UI ("Something went wrong") instead, so the rest of the app keeps working. It is like a circuit breaker in a house: one faulty appliance doesn't black out the whole building.

Error boundaries catch errors during **rendering** and lifecycle methods. They do **not** catch errors in event handlers or async code (use `try/catch` there). They must be written as class components, or you can use the popular `react-error-boundary` package.

== 3.9
Before hooks, components with state had to be **classes**. You will still see them in older codebases.

Every component goes through a **lifecycle**:

1. **Mounting:** it is created and inserted into the page for the first time.
2. **Updating:** it re-renders because props or state changed.
3. **Unmounting:** it is removed from the page.

Class components have special methods that React calls at each stage (`componentDidMount`, `componentDidUpdate`, `componentWillUnmount`). With hooks, `useEffect` covers all three: the effect body ≈ mount/update, and the cleanup ≈ unmount.

== 3.10
**State management** means deciding *where* each piece of data lives and *how* components read and update it. A useful way to think about it is to sort state into categories:

- **Local UI state:** belongs to one component (is this dropdown open?). Use `useState`.
- **Shared state:** needed by a few nearby components. **Lift it up** to their closest common parent and pass it down as props.
- **Global client state:** needed all over the app (logged-in user, cart, theme). Use **Context** for rarely-changing values, or a store library: **Redux Toolkit** (structured, predictable, great dev tools), **Zustand** (minimal and simple).
- **Server state:** data that really lives on the backend (products, orders). It needs caching, background refreshing and loading/error handling. Use **TanStack Query** (React Query) or RTK Query instead of hand-written `useEffect` fetching.

**Redux core ideas:** the whole app's global state lives in one **store**. You never change it directly. You **dispatch** an **action** (a plain object describing *what happened*, e.g. `{ type: 'cart/itemAdded', payload: item }`). A **reducer** (a pure function) calculates the new state from the old state plus the action. Components **select** the slices of state they need. This one-way flow makes changes predictable and easy to debug.

== 3.11
A **single-page application (SPA)** loads one HTML page. When the user navigates, JavaScript swaps the content instead of asking the server for a whole new page, which is fast and smooth. **Routing** is mapping URLs (`/products/42`) to components, so the address bar, back button and bookmarks still work.

**React Router** concepts:

- **Routes:** the URL pattern → component mapping. **Dynamic segments** (`:id`) capture parts of the URL, which you read with `useParams()`.
- **Nested routes + `<Outlet />`:** shared layouts (navbar, sidebar) with changing inner content.
- **`<Link>` / `<NavLink>`:** navigate without a full page reload. Never use a plain `<a href>` for internal links.
- **`useNavigate()`:** navigate from code, e.g. after a form submit.
- **Search params (`?page=2`):** store filter and page state in the URL so it can be shared.
- **Protected routes:** redirect to `/login` if the user isn't authenticated.

== 3.12
Forms are one of the most common and fiddly parts of front-end work: tracking every field's value, validating input, showing error messages, handling submission and disabling the button while saving.

**React Hook Form** handles field state efficiently: it registers inputs, avoids re-rendering on every keystroke, and tracks errors and submission status. **Zod** defines validation rules as a schema (e.g. "email must be a valid email, password at least 8 characters"). Connected with a *resolver*, the schema validates the form, and the same schema gives you the TypeScript type of the form data.

Always validate on the **server** as well. Client-side validation is only for a better user experience, because users can bypass it.

== 3.13
**Where is the HTML produced?** This choice affects speed, SEO (search engines) and server cost.

- **CSR (Client-Side Rendering):** the server sends an almost empty HTML file plus JavaScript. The browser runs the JS to build the page. It is simple, but the first load is slower and less SEO-friendly.
- **SSR (Server-Side Rendering):** the server runs React on each request and sends ready-made HTML, so the user sees content immediately. Then JavaScript loads and **hydrates** the page, attaching event handlers so it becomes interactive.
- **SSG (Static Site Generation):** HTML is generated once at build time and served from a CDN. It is very fast, and good for content that rarely changes.
- **ISR:** static pages that are regenerated in the background every so often.

**Frameworks** like **Next.js** provide all of these plus routing and data fetching on top of React.

**React Server Components (RSC)** are components that run **only on the server**. They can read the database directly, and their code is never sent to the browser, so less JavaScript is downloaded. **Client Components** (marked `'use client'`) run in the browser and are needed for interactivity (state, effects, event handlers). You mix both: server components for data and layout, and client components for the interactive parts. **Server Actions** (`'use server'`) are functions that run on the server and that you can call directly from forms.

== 3.14
**Automated tests** are code that checks your code, so you can change things confidently without manually clicking through the app.

Kinds of tests:

- **Unit tests:** a single function or hook.
- **Component/integration tests:** render a component, interact with it, check the result.
- **End-to-end (E2E) tests:** a real browser drives the whole app (Playwright, Cypress).

**React Testing Library** encourages testing **the way a user uses the app**: find elements by their visible role or label ("the button named Save"), click and type, then check what appears on screen. Don't test internal details like state variable names. Tests written this way survive refactoring. **Jest** or **Vitest** run the tests and provide `expect` assertions and mocks (fake versions of functions or network calls).

== 3.15
This is a checklist of questions you should be able to answer **in your own words**. For each one, try explaining it out loud as if to a colleague, then check the relevant section above.
