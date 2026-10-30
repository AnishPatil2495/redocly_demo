# Part 4 — Node.js: Basics to Advanced

## 4.1 Architecture

Node.js = **V8** (JS engine) + **libuv** (C library: event loop, thread pool, async I/O) + core bindings (fs, net, crypto, zlib, http).

- **Single-threaded event loop** for JavaScript execution.
- **Non-blocking I/O:** network I/O uses OS async mechanisms (epoll/kqueue/IOCP); file system, DNS lookup, crypto and zlib use the **libuv thread pool** (default 4 threads, `UV_THREADPOOL_SIZE`).
- Great for I/O-bound workloads (APIs, real-time); CPU-heavy work blocks the loop → use worker threads or offload.

## 4.2 The Node.js Event Loop Phases

```text
   ┌───────────────────────────┐
┌─>│           timers          │  setTimeout / setInterval callbacks
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │     pending callbacks     │  deferred I/O callbacks (e.g. TCP errors)
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │       idle, prepare       │  internal
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           poll            │  retrieve new I/O events; run I/O callbacks
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           check           │  setImmediate callbacks
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
└──┤      close callbacks      │  socket.on('close')
   └───────────────────────────┘
Between every callback: process.nextTick queue, then Promise microtask queue
```

```javascript
const fs = require('fs');

setTimeout(() => console.log('timeout'), 0);
setImmediate(() => console.log('immediate'));
process.nextTick(() => console.log('nextTick'));
Promise.resolve().then(() => console.log('promise'));
console.log('sync');
// sync, nextTick, promise, then timeout/immediate (order not guaranteed in main module)

fs.readFile(__filename, () => {
  setTimeout(() => console.log('timeout in I/O'), 0);
  setImmediate(() => console.log('immediate in I/O')); // ALWAYS first inside an I/O callback
});
```

`process.nextTick` runs before promise microtasks. Recursive `nextTick` can starve the event loop.

## 4.3 Modules

```javascript
// CommonJS
const path = require('node:path');
module.exports = { sum };          // or exports.sum = sum (never reassign `exports`)
// Module wrapper: (function (exports, require, module, __filename, __dirname) { ... })
// Modules are cached after first require → effectively singletons

// ESM — "type": "module" in package.json or .mjs
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const __dirname = path.dirname(fileURLToPath(import.meta.url)); // or import.meta.dirname (Node 20.11+)
```

**package.json essentials:** `"type"`, `"main"`, `"exports"` (entry points & conditional exports), `"scripts"`, `"engines"`, `dependencies` vs `devDependencies` vs `peerDependencies`. Semver: `^1.2.3` (minor+patch), `~1.2.3` (patch only). Commit lock files; use `npm ci` in CI.

## 4.4 Core Modules

### File System

```javascript
import { readFile, writeFile, mkdir, readdir, stat, rm } from 'node:fs/promises';
import { existsSync, createReadStream } from 'node:fs';

await mkdir('./out', { recursive: true });
await writeFile('./out/a.json', JSON.stringify({ a: 1 }, null, 2));
const data = JSON.parse(await readFile('./out/a.json', 'utf8'));
for (const entry of await readdir('.', { withFileTypes: true })) {
  console.log(entry.name, entry.isDirectory());
}
// Avoid *Sync methods in request handlers — they block the event loop
```

### path, os, url, crypto

```javascript
import path from 'node:path';
path.join('a', 'b', '../c');           // 'a/c'
path.resolve('src', 'index.js');       // absolute path
path.extname('file.tar.gz');           // '.gz'

import os from 'node:os';
os.cpus().length; os.freemem(); os.platform();

import crypto from 'node:crypto';
crypto.randomUUID();
crypto.createHash('sha256').update('data').digest('hex');
crypto.randomBytes(32).toString('hex');
// Password hashing: scrypt (built-in) or bcrypt/argon2
const salt = crypto.randomBytes(16);
const hash = crypto.scryptSync('password', salt, 64);
crypto.timingSafeEqual(hashA, hashB); // constant-time comparison
```

## 4.5 EventEmitter

```javascript
import { EventEmitter, once } from 'node:events';

class OrderService extends EventEmitter {
  place(order) {
    // ... save
    this.emit('order:placed', order);
  }
}

const svc = new OrderService();
svc.on('order:placed', (o) => console.log('send email', o.id));
svc.once('order:placed', () => console.log('first order only'));
svc.on('error', (err) => console.error(err)); // unhandled 'error' event crashes the process!
svc.place({ id: 1 });

const [value] = await once(svc, 'order:placed'); // promise-based wait
```

Listeners run **synchronously** in registration order. Default max listeners warning at 10 (`setMaxListeners`).

## 4.6 Buffers and Streams

**Buffer:** fixed-size raw binary data outside the V8 heap.

```javascript
const buf = Buffer.from('hello', 'utf8');
buf.toString('base64');     // 'aGVsbG8='
Buffer.alloc(10);           // zero-filled
Buffer.concat([b1, b2]);
```

**Streams** process data in chunks → constant memory for huge files. Four types: **Readable**, **Writable**, **Duplex** (socket), **Transform** (zlib, crypto).

```javascript
import { createReadStream, createWriteStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';
import { Transform } from 'node:stream';
import zlib from 'node:zlib';

// Compress a 10GB file using ~constant memory; pipeline handles errors + cleanup
await pipeline(
  createReadStream('big.log'),
  zlib.createGzip(),
  createWriteStream('big.log.gz'),
);

// Custom transform: uppercase
const upper = new Transform({
  transform(chunk, enc, cb) { cb(null, chunk.toString().toUpperCase()); },
});

// Async iteration over a readable
import readline from 'node:readline';
const rl = readline.createInterface({ input: createReadStream('data.csv') });
for await (const line of rl) { /* process each line */ }

// Streaming an HTTP response
app.get('/download', (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  createReadStream('report.csv').pipe(res);
});
```

**Backpressure:** when a writable can't keep up, `write()` returns `false`; wait for `'drain'`. `pipe()`/`pipeline()` handle this automatically.

## 4.7 HTTP Server from Scratch

```javascript
import http from 'node:http';

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (req.method === 'GET' && url.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ ok: true }));
  }

  if (req.method === 'POST' && url.pathname === '/echo') {
    let body = '';
    for await (const chunk of req) body += chunk;
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(body);
  }

  res.writeHead(404).end('Not found');
});

server.listen(3000, () => console.log('listening on 3000'));
```

## 4.8 Express.js In Depth

```javascript
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';

const app = express();

// Global middleware (order matters!)
app.use(helmet());                                   // security headers
app.use(cors({ origin: ['https://app.example.com'], credentials: true }));
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(rateLimit({ windowMs: 15 * 60_000, limit: 100 }));

// Custom middleware: request logging
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => console.log(`${req.method} ${req.originalUrl} ${res.statusCode} ${Date.now() - start}ms`));
  next();
});

// Router
const users = express.Router();
users.get('/', async (req, res) => {
  const { page = 1, limit = 20 } = req.query;
  res.json(await UserService.list({ page: +page, limit: +limit }));
});
users.get('/:id', async (req, res, next) => {
  try {
    const user = await UserService.get(req.params.id);
    if (!user) throw new NotFoundError('User not found');
    res.json(user);
  } catch (e) { next(e); }   // Express 5 forwards rejected promises automatically
});
app.use('/api/users', users);

// 404 handler
app.use((req, res) => res.status(404).json({ message: 'Route not found' }));

// Error-handling middleware: 4 arguments, registered LAST
class AppError extends Error {
  constructor(message, status = 500) { super(message); this.status = status; }
}
class NotFoundError extends AppError { constructor(m) { super(m, 404); } }

app.use((err, req, res, next) => {
  const status = err.status ?? 500;
  if (status >= 500) console.error(err);
  res.status(status).json({
    message: status >= 500 ? 'Internal Server Error' : err.message,
    ...(process.env.NODE_ENV !== 'production' && { stack: err.stack }),
  });
});

app.listen(process.env.PORT ?? 3000);
```

### Async wrapper (Express 4)

```javascript
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
router.get('/', asyncHandler(async (req, res) => res.json(await svc.list())));
```

### Layered Architecture

```text
src/
  routes/        → URL → controller mapping
  controllers/   → parse req, call service, shape res (no business logic)
  services/      → business logic, transactions
  repositories/  → DB access (SQL/ORM)
  models/        → schemas / entities
  middlewares/   → auth, validation, error handling
  config/        → env parsing & validation
  utils/
```

## 4.9 Authentication and Authorization

### JWT

```javascript
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

async function login(req, res) {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }
  const accessToken = jwt.sign({ sub: user.id, role: user.role }, process.env.JWT_SECRET, { expiresIn: '15m' });
  const refreshToken = jwt.sign({ sub: user.id }, process.env.REFRESH_SECRET, { expiresIn: '7d' });

  res.cookie('refreshToken', refreshToken, {
    httpOnly: true, secure: true, sameSite: 'strict', maxAge: 7 * 24 * 3600 * 1000,
  });
  res.json({ accessToken });
}

function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ message: 'No token' });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ message: 'Invalid or expired token' });
  }
}

const authorize = (...roles) => (req, res, next) =>
  roles.includes(req.user.role) ? next() : res.status(403).json({ message: 'Forbidden' });

router.delete('/:id', authenticate, authorize('admin'), deleteUser);
```

**JWT structure:** `header.payload.signature` (base64url). Payload is *encoded, not encrypted* — never store secrets in it. Short-lived access token + rotating refresh token; store refresh token in `HttpOnly` cookie. **Sessions** are stateful (server store like Redis), easy to revoke; JWTs are stateless, harder to revoke (use denylist or short expiry).

**401 vs 403:** 401 = not authenticated; 403 = authenticated but not allowed.

## 4.10 Databases from Node

```javascript
// PostgreSQL with pg — ALWAYS parameterize (prevents SQL injection)
import pg from 'pg';
const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 10 });

const { rows } = await pool.query('SELECT * FROM users WHERE email = $1', [email]);

// Transaction
const client = await pool.connect();
try {
  await client.query('BEGIN');
  await client.query('UPDATE accounts SET balance = balance - $1 WHERE id = $2', [amt, from]);
  await client.query('UPDATE accounts SET balance = balance + $1 WHERE id = $2', [amt, to]);
  await client.query('COMMIT');
} catch (e) {
  await client.query('ROLLBACK');
  throw e;
} finally {
  client.release();
}

// Mongoose (MongoDB)
const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true, lowercase: true },
  name: String,
  posts: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Post' }],
}, { timestamps: true });
userSchema.index({ email: 1 });
userSchema.pre('save', async function () {
  if (this.isModified('password')) this.password = await bcrypt.hash(this.password, 12);
});
const User = mongoose.model('User', userSchema);
await User.find({ name: /an/i }).populate('posts').lean().limit(10);

// Prisma
const user = await prisma.user.create({ data: { email, posts: { create: [{ title: 'Hi' }] } } });
const users = await prisma.user.findMany({ where: { email: { contains: '@x.com' } }, include: { posts: true } });
await prisma.$transaction([prisma.a.update(...), prisma.b.update(...)]);
```

## 4.11 Caching with Redis

```javascript
import { createClient } from 'redis';
const redis = createClient({ url: process.env.REDIS_URL });
await redis.connect();

// Cache-aside pattern
async function getProduct(id) {
  const key = `product:${id}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const product = await db.product.findUnique({ where: { id } });
  await redis.set(key, JSON.stringify(product), { EX: 300 }); // TTL 5 min
  return product;
}
// Invalidate on write: await redis.del(`product:${id}`)
```

Use cases: caching, sessions, rate limiting (`INCR` + `EXPIRE`), pub/sub, queues (BullMQ), distributed locks.

## 4.12 Scaling Node.js

### Cluster (multi-process on one machine)

```javascript
import cluster from 'node:cluster';
import os from 'node:os';

if (cluster.isPrimary) {
  for (let i = 0; i < os.availableParallelism(); i++) cluster.fork();
  cluster.on('exit', (w) => { console.log(`worker ${w.process.pid} died`); cluster.fork(); });
} else {
  startServer();  // workers share the same port
}
// In production often PM2 (`pm2 start app.js -i max`) or Kubernetes replicas instead.
```

### Worker Threads (CPU-bound work)

```javascript
// main.js
import { Worker } from 'node:worker_threads';
function runHeavy(n) {
  return new Promise((resolve, reject) => {
    const w = new Worker(new URL('./fib-worker.js', import.meta.url), { workerData: n });
    w.once('message', resolve);
    w.once('error', reject);
  });
}

// fib-worker.js
import { parentPort, workerData } from 'node:worker_threads';
const fib = (n) => (n < 2 ? n : fib(n - 1) + fib(n - 2));
parentPort.postMessage(fib(workerData));
```

| | `cluster` | `worker_threads` | `child_process` |
|---|---|---|---|
| Unit | Process | Thread | Process |
| Memory | Separate | Shared possible (`SharedArrayBuffer`) | Separate |
| Use | Scale HTTP across cores | CPU-intensive JS | Run external commands/scripts |

### child_process

```javascript
import { exec, spawn, execFile } from 'node:child_process';
spawn('ls', ['-la'], { stdio: 'inherit' });   // streams, for long-running/large output
execFile('git', ['status'], (err, stdout) => console.log(stdout)); // safer than exec (no shell)
```

## 4.13 Background Jobs and Queues

```javascript
import { Queue, Worker } from 'bullmq';
const emailQueue = new Queue('emails', { connection });

await emailQueue.add('welcome', { userId: 1 }, { attempts: 3, backoff: { type: 'exponential', delay: 1000 } });

new Worker('emails', async (job) => {
  await sendWelcomeEmail(job.data.userId);
}, { connection, concurrency: 5 });
```

## 4.14 Real-time: WebSockets / Socket.IO

```javascript
import { Server } from 'socket.io';
const io = new Server(httpServer, { cors: { origin: '*' } });

io.use((socket, next) => {               // auth middleware
  try { socket.user = jwt.verify(socket.handshake.auth.token, SECRET); next(); }
  catch { next(new Error('unauthorized')); }
});

io.on('connection', (socket) => {
  socket.join(`room:${socket.user.sub}`);
  socket.on('chat:message', (msg) => io.to(msg.roomId).emit('chat:message', msg));
  socket.on('disconnect', () => console.log('bye'));
});
// Scale horizontally with the Redis adapter.
```

Alternatives: Server-Sent Events (one-way server → client over HTTP), long polling.

## 4.15 Error Handling and Process Management

```javascript
// Operational errors (expected: invalid input, timeouts) → handle & respond
// Programmer errors (bugs) → crash and let the process manager restart

process.on('unhandledRejection', (reason) => { logger.error(reason); throw reason; });
process.on('uncaughtException', (err) => { logger.fatal(err); process.exit(1); });

// Graceful shutdown
const server = app.listen(3000);
async function shutdown(signal) {
  console.log(`${signal} received`);
  server.close(async () => {          // stop accepting new connections
    await pool.end();
    await redis.quit();
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 10_000).unref(); // force exit
}
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
```

## 4.16 Configuration and Logging

```javascript
// Validate env at startup — fail fast
import { z } from 'zod';
const Env = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
});
export const env = Env.parse(process.env);
// Node 20.6+: node --env-file=.env app.js

// Structured logging with pino
import pino from 'pino';
const logger = pino({ level: env.NODE_ENV === 'production' ? 'info' : 'debug' });
logger.info({ userId: 1, orderId: 9 }, 'order placed');
```

## 4.17 Security Checklist

- Validate and sanitize all input (Zod/Joi); parameterized queries (SQL injection); avoid `eval`.
- `helmet` for headers; strict CORS; rate limiting; request size limits.
- Hash passwords with bcrypt/argon2; never log secrets/tokens.
- NoSQL injection: reject objects where strings are expected (`{ "$gt": "" }`).
- Prototype pollution: don't deep-merge untrusted objects.
- `npm audit`, Dependabot; pin versions; lockfiles.
- HTTPS, secure cookies (`HttpOnly`, `Secure`, `SameSite`), CSRF protection for cookie auth.
- Avoid ReDoS (catastrophic regex backtracking); avoid blocking sync calls.

## 4.18 Performance

- Never block the event loop: avoid sync fs/crypto, giant `JSON.parse`, heavy loops in handlers.
- Use streams for large data; pagination for large queries.
- Connection pooling for DBs; HTTP keep-alive agents.
- Cache (in-memory LRU, Redis, HTTP cache headers / ETags), compression.
- Profile: `node --inspect`, `--prof`, `clinic.js`, `0x` flame graphs; measure event loop lag (`perf_hooks.monitorEventLoopDelay`).
- Memory leaks: heap snapshots in Chrome DevTools; watch for growing global caches, listeners, closures.

## 4.19 Testing Node

```javascript
// Jest/Vitest + Supertest
import request from 'supertest';
import { app } from '../src/app';

describe('GET /api/users/:id', () => {
  it('returns 404 for unknown user', async () => {
    const res = await request(app).get('/api/users/999');
    expect(res.status).toBe(404);
  });

  it('returns user', async () => {
    vi.spyOn(UserService, 'get').mockResolvedValue({ id: 1, name: 'A' });
    const res = await request(app).get('/api/users/1').set('Authorization', `Bearer ${token}`);
    expect(res.body).toMatchObject({ id: 1 });
  });
});

// Built-in test runner (Node 18+)
import { test } from 'node:test';
import assert from 'node:assert/strict';
test('adds', () => assert.equal(1 + 1, 2));
```

## 4.20 REST API Design Quick Reference

| Method | Purpose | Idempotent | Typical success |
|---|---|---|---|
| GET | Read | Yes | 200 |
| POST | Create | No | 201 + Location |
| PUT | Replace | Yes | 200 / 204 |
| PATCH | Partial update | Not necessarily | 200 |
| DELETE | Remove | Yes | 204 |

Status codes: 200 OK, 201 Created, 204 No Content, 301/302 Redirect, 304 Not Modified, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Unprocessable Entity, 429 Too Many Requests, 500 Internal Error, 502 Bad Gateway, 503 Service Unavailable.

Good practices: plural nouns (`/users/42/orders`), versioning (`/v1`), pagination (`?page=&limit=` or cursor-based), filtering/sorting via query params, consistent error shape, idempotency keys for payments, OpenAPI documentation.
