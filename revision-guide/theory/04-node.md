== intro
**What is Node.js?** Node.js is a program that lets you run **JavaScript outside the browser**, mainly on servers. It was created in 2009 by taking Chrome's V8 JavaScript engine and adding the ability to work with files, networks and the operating system. So you can use the same language for the frontend (React) and the backend (APIs, databases).

**What is a backend / server?** The backend is the part of an application users don't see. It receives HTTP requests from browsers or apps, applies business rules ("is this user allowed?", "is the item in stock?"), reads and writes the database, and sends back responses, usually JSON.

**What makes Node special: non-blocking I/O.** "I/O" (Input/Output) means talking to the outside world: reading files, querying databases, calling other APIs. These operations are *slow* compared to the CPU. Traditional servers often dedicate one thread per request, and that thread sits idle while waiting. Node uses **one main thread** and never waits. It starts the I/O, moves on to serve other requests, and handles the result when it arrives (the event loop). That makes Node very efficient for apps with many simultaneous connections: APIs, chat, real-time dashboards.

**A minimal server:**

```javascript
// save as server.js, run with: node server.js, then open http://localhost:3000
const http = require('http');
http.createServer((req, res) => {
  res.end('Hello from Node!');
}).listen(3000);
```

**Weakness:** heavy CPU calculations (image processing, big loops) block the single thread and freeze *every* request. Such work must be moved to worker threads or other services.

== 4.1
Node.js is made of three main pieces:

1. **V8:** the JavaScript engine (the same as in Chrome). It runs your JS code.
2. **libuv:** a C library that provides the **event loop** and handles asynchronous operations. For network operations it uses the operating system's efficient notification systems. For operations that have no async OS version (file system, DNS lookups, some crypto, compression), it uses a small **thread pool** (4 threads by default) running in the background.
3. **Core modules:** built-in libraries such as `fs` (files), `http` (web servers), `path`, `crypto`, `events` and `stream`.

**Your JavaScript runs on a single thread**, but the I/O work happens in parallel in the background. Picture a waiter (your JS thread) who takes orders and delivers food while the kitchen (libuv and the OS) cooks many dishes at the same time.

**I/O-bound vs CPU-bound:** an I/O-bound task spends most of its time *waiting* (database, network), and Node excels at these. A CPU-bound task spends its time *computing* (encryption of big files, video processing), and it blocks Node's thread.

== 4.2
You learned the browser event loop in 1.13. Node's event loop follows the same idea but has more structure. It goes round in a cycle of **phases**, and each phase has its own queue of callbacks:

1. **Timers:** callbacks from `setTimeout` and `setInterval` whose time has come.
2. **Pending callbacks:** some system-level callbacks deferred from the previous cycle.
3. **Poll:** the heart of the loop. It waits for new I/O events (incoming requests, finished file reads) and runs their callbacks.
4. **Check:** callbacks scheduled with `setImmediate`.
5. **Close callbacks:** e.g. when a socket closes.

**Between every callback**, Node first empties two high-priority queues: the **`process.nextTick` queue**, then the **promise microtask queue**.

Practical meaning: `process.nextTick` callbacks run first, then promises, then timers/immediates. Inside an I/O callback, `setImmediate` always runs before `setTimeout(..., 0)`. Most importantly, if your code runs a long synchronous computation, **none** of these phases can run. Every user waits. This is called "**blocking the event loop**".

== 4.3
A **module** is a file whose code is private unless exported. Node supports two systems (also see 1.16):

- **CommonJS** (`require` / `module.exports`): Node's original system. Modules load **synchronously**, and each is **cached** after its first `require`, so every file that requires it gets the *same* instance. That makes modules natural singletons, which is handy for a shared database connection.
- **ES Modules** (`import` / `export`): the modern standard. Enable it with `"type": "module"` in `package.json` or by using `.mjs` files.

**`package.json`** is your project's ID card. It lists the name and version, **dependencies** (libraries needed to run), **devDependencies** (only needed for development: test tools, TypeScript), and **scripts** (shortcuts like `npm run dev`). **`package-lock.json`** records the *exact* versions installed so everyone gets identical dependencies.

**npm** (Node Package Manager) downloads libraries from the npm registry into the `node_modules` folder. **Semantic versioning (semver)** is `MAJOR.MINOR.PATCH`. A major bump means breaking changes, minor means new features, patch means bug fixes.

== 4.4
Node comes with **core modules**, built-in libraries that need no installation:

- **`fs`** (file system): read, write, delete and list files and folders. Prefer the promise-based `fs/promises` with `await`. Avoid the `...Sync` functions in servers, because they block the event loop.
- **`path`:** build file paths safely across operating systems (Windows uses `\`, Linux/Mac use `/`).
- **`os`:** information about the machine (CPU count, memory, platform).
- **`url`:** parse and build URLs.
- **`crypto`:** hashing (turning data into a fixed "fingerprint", e.g. SHA-256), random IDs and tokens, encryption, and secure password hashing (`scrypt`).

**Hashing vs encryption:** a hash is one-way. You cannot get the original back, so use it for passwords. Encryption is two-way. With the key you can decrypt, so use it for data you need to read again.

== 4.5
Much of Node is **event-driven**: objects announce that "something happened", and other code that is listening reacts. The **`EventEmitter`** class provides this:

- **`emitter.on('eventName', listener)`** subscribes a function.
- **`emitter.emit('eventName', data)`** announces the event, and every listener is called with the data.
- **`emitter.once(...)`** listens only for the first occurrence.

Many core objects are EventEmitters: HTTP servers emit `'request'`, streams emit `'data'` and `'end'`, processes emit `'exit'`. It is the **Observer pattern** (1.20).

Note that listeners run **synchronously**, one after another, when `emit` is called. Always listen for `'error'` events. An `'error'` event without a listener crashes the process.

== 4.6
**Buffers.** JavaScript strings are text, but servers deal with raw **binary data**: images, files, network packets. A `Buffer` is a fixed-size chunk of raw bytes. You convert between buffers and strings using an *encoding* (utf8, base64, hex).

**Streams.** Imagine copying a 5 GB video file. Reading it all into memory first could crash the server. A **stream** processes data **piece by piece (in chunks)** as it flows, like drinking through a straw instead of swallowing a whole bottle at once. Memory use stays small and constant, and processing starts immediately.

Four types:

- **Readable:** a source you read from (file read stream, incoming HTTP request).
- **Writable:** a destination you write to (file write stream, HTTP response).
- **Duplex:** both readable and writable (a network socket).
- **Transform:** a duplex that modifies data passing through (compression, encryption).

You connect streams with **`pipeline()`** (or `.pipe()`): `readFile → gzip → writeFile`.

**Backpressure:** if the destination is slower than the source (slow network, slow disk), data would pile up in memory. Streams handle this automatically. The writable signals "I'm full", and the readable pauses until it drains.

== 4.7
Node's built-in **`http`** module can create a web server with no frameworks. You give it one function that is called for **every request**. It receives:

- **`req` (request):** method (`GET`, `POST`...), URL, headers, and the body, which arrives as a *stream* of chunks.
- **`res` (response):** you set the status code and headers, write the body, and call `end()`.

Doing everything by hand (parsing URLs, routing, reading JSON bodies, handling errors) gets repetitive quickly. That is why frameworks like **Express** exist. Seeing the raw version once helps you understand what frameworks do for you.

== 4.8
**Express** is the most popular minimal web framework for Node. It adds:

- **Routing:** map an HTTP method + URL pattern to a handler function: `app.get('/users/:id', handler)`. `:id` is a **route parameter**, available as `req.params.id`. Query strings (`?page=2`) appear in `req.query`, and parsed JSON bodies in `req.body`.
- **Middleware:** the central concept. A middleware is a function `(req, res, next)` that runs **in the middle**, between the request arriving and the response being sent. Middleware functions form a **pipeline** in the order you register them. Each one can read or modify `req`/`res`, end the request by sending a response, or call `next()` to pass control to the next one.

```text
request → [logger] → [parse JSON] → [check auth] → [route handler] → response
                                           │
                                           └─ not logged in? respond 401 and stop here
```

Typical middleware: logging, parsing bodies, CORS, security headers, authentication, validation, rate limiting.

- **Error-handling middleware** has **four** parameters `(err, req, res, next)` and is registered **last**. When any handler calls `next(error)` or throws, Express skips straight to it. That gives you one central place to format error responses.
- **Routers** (`express.Router()`) group related routes (all `/api/users` routes) into separate files.

**Layered architecture** keeps code organised as the app grows. **Routes** map URLs. **Controllers** handle HTTP details. **Services** hold the business logic. **Repositories** talk to the database. Each layer has one job, which makes it easy to test and change.

== 4.9
**Authentication (AuthN)** answers "**who are you?**" (logging in). **Authorization (AuthZ)** answers "**what are you allowed to do?**" (permissions, roles).

**Never store passwords as plain text.** Store a **hash** produced by a slow, salted algorithm (bcrypt, argon2). At login, hash the entered password the same way and compare. A **salt** is random data added before hashing, so identical passwords produce different hashes and pre-computed attack tables don't work.

Two common ways to remember a logged-in user:

1. **Sessions (stateful):** after login, the server stores a session record (in memory, a DB or Redis) and gives the browser a cookie containing just a random session ID. Each request sends the cookie, and the server looks up the session. It is easy to log users out instantly.
2. **JWT (JSON Web Token, stateless):** after login, the server creates a **signed** token containing the user's ID and role. The client sends it with each request (usually in the `Authorization: Bearer <token>` header). The server verifies the **signature** with its secret key, so it can trust the contents without a database lookup. Anyone can *read* a JWT, because it is only encoded, not encrypted. They just can't *modify* it without breaking the signature. JWTs are hard to revoke before they expire, so access tokens are kept **short-lived** (minutes) and paired with a longer-lived **refresh token**.

**Status codes:** `401 Unauthorized` means you are not logged in or the token is invalid. `403 Forbidden` means you are logged in but not allowed to do this.

== 4.10
Applications store data permanently in a **database**. From Node you connect using a **driver** (a library that speaks the database's protocol) or a higher-level tool:

- **Raw driver** (e.g. `pg` for PostgreSQL): you write SQL yourself. It gives full control and the best performance.
- **Query builder** (Knex): build SQL with JavaScript methods.
- **ORM** (Object-Relational Mapper: Prisma, TypeORM, Sequelize): work with database rows as JavaScript objects. The ORM writes the SQL for you.
- **ODM** (Mongoose) does the same for MongoDB, a *document* (NoSQL) database that stores JSON-like documents instead of table rows.

Key concepts:

- **Connection pool:** opening a database connection is slow. A pool keeps several connections open and lends them to requests as needed.
- **Parameterized queries:** always pass user values separately (`$1`, `?`) instead of building SQL strings. This prevents **SQL injection** attacks (see 7.19).
- **Transactions:** group several queries so they all succeed or all fail together. A money transfer must never debit one account without crediting the other.

== 4.11
A **cache** stores the result of slow work (database queries, external API calls) in fast storage, so the next request gets it instantly. **Redis** is an extremely fast **in-memory key-value store**, the most common cache for web apps.

**Cache-aside pattern** (the most common):

1. Request arrives → check the cache.
2. **Hit** (found): return the cached value. That is fast.
3. **Miss** (not found): query the database, save the result in the cache with an expiry time (**TTL**, time-to-live), and return it.
4. When the data changes, delete (**invalidate**) the cached copy.

The hardest part of caching is **invalidation**: making sure users never see outdated data for too long. Redis is also used for sessions, rate limiting, queues and pub/sub messaging.

== 4.12
A single Node process uses **one CPU core** for your JavaScript. Servers have many cores, so how do you use them all, and what about heavy computations?

- **Cluster module / PM2:** start **several copies (processes)** of your app, one per CPU core, all sharing the same port. Incoming connections are distributed among them. If one crashes, a new one is started. In cloud setups you often run multiple containers behind a **load balancer** instead.
- **Worker threads:** run CPU-heavy JavaScript (image resizing, report generation, complex calculations) on a **separate thread**, so the main event loop stays free to answer requests.
- **Child processes:** run *other programs* (a Python script, `ffmpeg`, shell commands) from Node.

**Horizontal scaling** (more machines or processes) generally requires your app to be **stateless**: don't keep sessions or uploaded files in the memory of one process. Store them in Redis, a database or object storage, so any instance can handle any request.

== 4.13
Some work shouldn't happen during the HTTP request: sending emails, generating PDFs, processing videos, calling slow third-party APIs. The user shouldn't wait for it, and if it fails it should be **retried** automatically.

A **job queue** solves this. The web server quickly **adds a job** to a queue (stored in Redis) and responds immediately. Separate **worker** processes take jobs from the queue and process them in the background, with retries, delays, priorities and scheduling. **BullMQ** is the popular Redis-based queue for Node (similar to Celery in Python, see 6.14).

== 4.14
Normal HTTP is **request → response**: the client always asks first, and the server can't push data on its own. For **real-time** features (chat, live notifications, multiplayer games, live dashboards) you need the server to send data whenever something happens.

- **WebSockets** open a **permanent two-way connection** between browser and server. Either side can send messages at any time.
- **Socket.IO** is a library on top of WebSockets that adds automatic reconnection, **rooms** (broadcast to a group, such as one chat room), events and fallbacks.
- **Server-Sent Events (SSE)** are a simpler one-way stream from server to client over normal HTTP, good for notifications and progress updates.

When running several server instances, use a shared message channel (e.g. the Redis adapter) so a message sent from one instance reaches clients connected to the others.

== 4.15
There are two kinds of errors in a server:

- **Operational errors:** expected problems in normal operation, such as invalid user input, a missing record, a timeout from another service. **Handle them**: return a proper status code and message.
- **Programmer errors:** bugs, such as reading a property of `undefined` or calling a function wrongly. The process may be in a broken state. The safest response is to **log it, crash, and let a process manager restart** the app.

**`unhandledRejection` / `uncaughtException`** are last-resort handlers for errors nobody caught. Log them and exit.

**Graceful shutdown:** when the server is told to stop (during a deploy), it should stop accepting new requests, **finish the requests in progress**, close database connections, and then exit. Users then don't get errors in the middle of a deploy.

== 4.16
**Configuration** (database URLs, API keys, port numbers) must not be hard-coded. It differs between your laptop, testing and production, and secrets must never be committed to Git. Use **environment variables**, often loaded from a `.env` file during development. **Validate them at startup** so the app fails immediately with a clear message if something is missing, instead of failing mysteriously later.

**Logging** records what your application is doing so you can debug problems in production, where you can't attach a debugger. Use **log levels** (`debug`, `info`, `warn`, `error`, `fatal`) and **structured logs** (JSON with fields like `userId`, `requestId`) so they can be searched in log tools. `pino` and `winston` are popular loggers. Never log passwords, tokens or personal data.

== 4.17
Security is about assuming that **anything coming from outside is potentially malicious**. The most common risks for Node APIs (many come from the **OWASP Top 10** list):

- **Injection** (SQL/NoSQL): attacker input changes your query. Prevent it with parameterized queries and validation.
- **Broken authentication / access control:** users accessing other users' data. Always check ownership on the server.
- **Sensitive data exposure:** use HTTPS, hash passwords, don't leak stack traces in production.
- **Misconfiguration:** missing security headers (use `helmet`), CORS that is too open.
- **Vulnerable dependencies:** run `npm audit` and keep packages updated.
- **Denial of service:** limit request rates and body sizes, and avoid regexes that can take exponential time.

== 4.18
For a Node server, performance mostly comes down to **keeping the event loop free** and **avoiding unnecessary work**:

- Never run long synchronous work in a request handler.
- Use streams for big data, and pagination for big lists.
- Reuse database connections (pools) and HTTP connections (keep-alive).
- Cache what is expensive and frequently requested.
- **Measure before optimising:** use profilers (`node --inspect` with Chrome DevTools, `clinic.js`) to find the real bottleneck instead of guessing.

== 4.19
For Node APIs you usually write:

- **Unit tests:** test services and helper functions in isolation, replacing the database or external APIs with **mocks** (fake implementations).
- **Integration tests:** send real HTTP requests to your Express app (using **Supertest**, without starting a real network server) and check the status code and JSON. Often run against a test database.

Test runners: **Jest**, **Vitest**, or Node's built-in `node:test`. A good test is independent (doesn't rely on other tests), repeatable and fast.

== 4.20
**REST** (REpresentational State Transfer) is a set of conventions for designing HTTP APIs:

- Everything is a **resource** identified by a URL using nouns, not verbs: `/users`, `/users/42`, `/users/42/orders`.
- The **HTTP method** says what to do: GET reads, POST creates, PUT replaces, PATCH partially updates, DELETE removes.
- **Status codes** say how it went: `2xx` success, `3xx` redirect, `4xx` client made a mistake, `5xx` server failed.
- **Stateless:** each request carries everything needed (e.g. its auth token). The server doesn't remember previous requests.

**Idempotent** means doing the same request several times has the same effect as doing it once. GET, PUT and DELETE are idempotent. POST is not: two POSTs create two records. That's why payment APIs use **idempotency keys**.
