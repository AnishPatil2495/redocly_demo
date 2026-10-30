# Part 0 — Foundations: Read This First

This guide assumes you are starting from zero. This first part explains the big picture: what programming is, how the web works, and how all the technologies in this guide fit together. Every later section begins with a shaded **"Understand the concept"** box written in plain language. Read that box first, then study the code examples beneath it.

## 0.1 How to Use This Guide

1. **Read the concept box** for a section. Make sure you can explain the idea out loud in your own words.
2. **Type the code examples yourself** instead of copying them. Change values and see what happens. You learn by breaking things.
3. **Run JavaScript** in your browser console (press `F12` and open the *Console* tab) or with Node.js (`node file.js`). **Run Python** with `python file.py` or the interactive shell `python`. **Run SQL** in a free online playground (search "PostgreSQL online") or a local PostgreSQL install.
4. **Recommended order for a complete beginner:** Part 0 → JavaScript → TypeScript → React → Node.js → SQL → Python → Django. JavaScript comes first because React, Node and TypeScript all build on it. SQL is easier to learn before Django, because Django generates SQL for you.
5. Don't try to memorise everything on the first pass. Go through once for understanding, then again for detail.

## 0.2 What Is Programming?

A computer can only follow very precise, very small instructions. **Programming** means writing those instructions in a **programming language**, which is a strict, human-readable notation that a tool then translates into something the machine can execute.

Every program, however large, is built from a handful of ideas:

| Idea | Plain meaning | Example |
|---|---|---|
| **Value / data** | A piece of information | `42`, `"Anish"`, `true` |
| **Variable** | A labelled box that holds a value | `age = 30` |
| **Operator** | Combines values | `+`, `-`, `==`, `>` |
| **Condition** | Do something only if a rule is true | `if age >= 18 ...` |
| **Loop** | Repeat something | "for every user in the list..." |
| **Function** | A named, reusable recipe of steps | `calculateTax(salary)` |
| **Data structure** | A way to organise many values | list `[1,2,3]`, dictionary `{name: "A"}` |
| **Input / Output** | Data coming in (keyboard, network, file) and going out (screen, response) | reading a form, showing a page |

**Compiled vs interpreted languages.** A *compiled* language (C, Go) is translated fully into machine code before it runs. An *interpreted* language (Python, JavaScript) is read and executed by another program, called the **interpreter** or **engine**, at run time. Modern JavaScript and Python engines mix both approaches for speed.

**Static vs dynamic typing.** In a *statically typed* language (TypeScript, Java), the kind of value a variable holds is checked *before* the program runs. In a *dynamically typed* language (JavaScript, Python), it is only known *while* the program runs. Static typing catches mistakes earlier; dynamic typing is quicker to write.

## 0.3 How the Web Works

When you type `https://shop.com/products` into a browser:

1. **DNS lookup:** the browser asks a DNS server, "what is the IP address of `shop.com`?" (a bit like looking up a phone number in a contacts list).
2. **Connection:** the browser opens a TCP connection to that address. With **HTTPS** it is encrypted using TLS.
3. **HTTP request:** the browser sends a text message like `GET /products`.
4. **Server:** a program on the server (written with Node/Express or Python/Django, for example) receives the request, maybe reads a **database**, and builds a **response**.
5. **HTTP response:** the server replies with a **status code** (`200 OK`, `404 Not Found`), **headers** (metadata) and a **body** (HTML, JSON, an image...).
6. **Rendering:** the browser turns HTML + CSS + JavaScript into the page you see.

```text
  Browser (client)  ── HTTP request ──►  Web server (Node / Django)  ──SQL──►  Database
        ▲                                         │                         (PostgreSQL)
        └──────────── HTTP response (HTML/JSON) ◄─┘
```

**Client vs server.** The *client* is the program asking for something (usually the browser or a mobile app). The *server* is the program answering. One server handles requests from thousands of clients.

**HTTP methods** express intent: `GET` (read), `POST` (create), `PUT`/`PATCH` (update), `DELETE` (remove).

**JSON** (JavaScript Object Notation) is the most common format for exchanging data between client and server:

```json
{ "id": 7, "name": "Laptop", "price": 999.99, "tags": ["electronics", "sale"] }
```

**An API** (Application Programming Interface) is a defined set of requests a program accepts. A **REST API** exposes data as URLs (`/api/products/7`) and uses HTTP methods to act on them.

## 0.4 The Three Languages of the Browser

- **HTML** describes *structure and content*: headings, paragraphs, buttons, forms.
- **CSS** describes *appearance*: colours, layout, fonts, spacing.
- **JavaScript** describes *behaviour*: what happens when you click, fetching data, updating the page without a reload.

```html
<button id="hello">Say hello</button>              <!-- HTML: a button -->
<style> #hello { background: navy; color: white; } </style>   <!-- CSS: styling -->
<script>
  document.getElementById('hello').addEventListener('click', () => alert('Hello!')); // JS: behaviour
</script>
```

The **DOM** (Document Object Model) is the browser's in-memory tree representation of the HTML. JavaScript changes the page by changing the DOM.

## 0.5 Frontend, Backend, Database: Where Each Technology Fits

| Layer | Job | Technologies in this guide |
|---|---|---|
| **Frontend** (runs in the browser) | Shows the UI, reacts to the user | JavaScript, TypeScript, **React** |
| **Backend** (runs on a server) | Business rules, security, talking to the database, APIs | **Node.js + Express**, **Python + Django / DRF** |
| **Database** | Stores data permanently and lets you query it | **SQL** (PostgreSQL, MySQL) |

A typical **full-stack** feature, such as "show my orders", touches all three layers. A React component calls `GET /api/orders`. A Django or Express view checks who you are, runs a SQL query, and returns JSON. React then displays the list.

- **JavaScript** is the language of the browser. **Node.js** lets the same language run on servers.
- **TypeScript** is JavaScript plus *types*, which catch mistakes before the code runs.
- **React** is a JavaScript *library* for building user interfaces out of reusable *components*.
- **Python** is a general-purpose language known for readability. **Django** is a Python *framework* for building web backends quickly.
- **SQL** (Structured Query Language) is the language used to ask relational databases for data.

**Library vs framework.** You call a *library* when you need it (React, lodash). A *framework* calls *your* code and dictates the structure of your project (Django, Next.js). People describe this as "inversion of control".

## 0.6 Essential Tools

- **Terminal / command line:** a text interface to run programs (`cd folder`, `ls`, `node app.js`, `python manage.py runserver`).
- **Code editor:** VS Code is the most common choice.
- **Package managers:** **npm** for JavaScript and **pip** for Python. They download libraries other people wrote (`npm install react`, `pip install django`).
- **Git:** version control. It records snapshots ("commits") of your code so you can go back, collaborate and review changes. **GitHub** hosts Git repositories online.
- **Browser DevTools (F12):** Console (run JS, see errors), Elements (inspect HTML/CSS), Network (see every HTTP request).
- **Debugger:** pause code on a line (a *breakpoint*) and inspect variables. Use `debugger;` in JS or `breakpoint()` in Python.

## 0.7 Core Computer-Science Ideas You Will Meet

**Memory: stack and heap.** Programs store short-lived values for the function that is currently running on the *stack* (fast, small, automatically cleaned up). Objects that live longer or grow (lists, objects) go on the *heap*. Variables often hold a *reference* (an address) to something on the heap. That is why two variables can point to the *same* object.

**Synchronous vs asynchronous.** *Synchronous* code runs one step after another, and each step waits for the previous one to finish. *Asynchronous* code starts a slow task (a network request, reading a file) and continues with other work, handling the result later. Think of ordering coffee: you don't stand frozen at the counter. You get a buzzer and sit down, and the buzzer is the "callback". JavaScript, Node.js and Python's `asyncio` all rely on this idea.

**Big-O notation** describes how the work grows as the input grows:

| Notation | Name | Example |
|---|---|---|
| O(1) | Constant | Look up a key in a dictionary |
| O(log n) | Logarithmic | Binary search, database index lookup |
| O(n) | Linear | Loop over a list once |
| O(n log n) | Linearithmic | Good sorting algorithms |
| O(n²) | Quadratic | A loop inside a loop over the same list |

**Errors and exceptions.** When something goes wrong at run time (dividing by zero, a missing file), the program *throws/raises* an exception. You can *catch* it and handle it gracefully, or let it crash the program.

**Security basics.** Never trust input from users. Validate it and escape it. Store passwords only as *hashes* (one-way scrambled values). Keep secrets (API keys, passwords) out of your code, in *environment variables*.

## 0.8 Glossary of Common Terms

| Term | Meaning |
|---|---|
| **Syntax** | The grammar rules of a language |
| **Runtime** | The environment where code executes (browser, Node.js, Python interpreter) |
| **Compile / transpile** | Translate code into another form (TypeScript → JavaScript) |
| **Bug** | A mistake that causes wrong behaviour |
| **Refactor** | Restructure code without changing what it does |
| **Dependency** | A library your project needs |
| **Environment variable** | A configuration value supplied from outside the code |
| **Endpoint** | A specific URL + method of an API, e.g. `POST /api/users` |
| **Authentication** | Proving *who* you are (login) |
| **Authorization** | Deciding *what* you are allowed to do (permissions) |
| **CRUD** | Create, Read, Update, Delete: the four basic data operations |
| **ORM** | Object-Relational Mapper: lets you use database rows as objects in code (Django ORM, Prisma) |
| **Cache** | A fast temporary copy of data to avoid repeating slow work |
| **Deployment** | Putting your application on a server so others can use it |
| **Unit test** | Code that automatically checks a small piece of other code |
