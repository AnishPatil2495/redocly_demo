== intro
**What is a database?** A database is an organised store of data that lives permanently, unlike variables, which disappear when a program stops. It lets many users read and change the data safely at the same time.

**What is a relational database?** It stores data in **tables**, like spreadsheets:

- A **table** holds one kind of thing (`employees`, `orders`).
- Each **row** (record) is one item (one employee).
- Each **column** (field) is one attribute with a fixed data type (`name`, `salary`).
- A **primary key** uniquely identifies each row (usually `id`).
- A **foreign key** is a column that points to a row in another table (an employee's `department_id` refers to `departments.id`). These links are the **relations**.

```text
departments                 employees
+----+-------------+        +----+--------+---------------+--------+
| id | name        |        | id | name   | department_id | salary |
+----+-------------+        +----+--------+---------------+--------+
|  1 | Engineering | ◄───── |  1 | Anish  |       1       | 120000 |
|  2 | Sales       | ◄─┐    |  2 | Ravi   |       1       |  90000 |
+----+-------------+   └─── |  3 | Priya  |       2       |  70000 |
                            +----+--------+---------------+--------+
```

**What is SQL?** **SQL (Structured Query Language)** is the standard language for working with relational databases. It is **declarative**: you describe *what* data you want, and the database decides *how* to get it efficiently.

```sql
SELECT name, salary          -- which columns
FROM employees               -- which table
WHERE salary > 80000         -- which rows
ORDER BY salary DESC;        -- in what order
```

Popular relational databases are **PostgreSQL**, **MySQL**, **SQLite**, **SQL Server** and **Oracle**. Core SQL is the same in all of them, with small dialect differences. A **DBMS** (Database Management System) is the software that runs the database.

== 7.1
SQL commands fall into families according to their purpose:

- **DDL (Data Definition Language)** defines the *structure*: create, change or delete tables, columns and indexes.
- **DML (Data Manipulation Language)** changes the *data*: add rows (`INSERT`), change them (`UPDATE`), remove them (`DELETE`).
- **DQL (Data Query Language)** *reads* data: `SELECT`. This is what you'll write most.
- **DCL (Data Control Language)** manages *permissions*: who can read or change what.
- **TCL (Transaction Control Language)** groups changes into all-or-nothing **transactions**.

== 7.2
Every column has a **data type** that restricts what values it can hold. This protects data quality (you can't put "abc" into a number column) and lets the database store and compare values efficiently.

Choosing well:

- Use **`INT`/`BIGINT`** for IDs and counts. Use `BIGINT` for tables that may exceed about 2 billion rows.
- Use **`NUMERIC`/`DECIMAL`** for **money**. They are exact, while `FLOAT` can produce rounding errors like `0.1 + 0.2 = 0.30000000000000004`.
- Use **`VARCHAR(n)`** for text with a maximum length, and **`TEXT`** for unlimited text.
- Use **`TIMESTAMPTZ`** (timestamp with time zone) for moments in time, stored in UTC. Use **`DATE`** for calendar days.
- Use **`BOOLEAN`** for yes/no, **`UUID`** for globally unique IDs, and **`JSONB`** (PostgreSQL) for flexible semi-structured data.

**NULL** is a special marker meaning "**unknown / no value**". It is not zero and not an empty string (see 7.4).

== 7.3
**`CREATE TABLE`** defines a table's columns and their types. **`ALTER TABLE`** changes an existing table. **`DROP TABLE`** deletes it entirely.

**Constraints** are rules the database **enforces automatically**, so bad data can never get in, whatever application or person writes to it:

- **`PRIMARY KEY`**: unique and never NULL. It identifies each row.
- **`FOREIGN KEY` / `REFERENCES`**: the value must exist in the other table (you can't assign an employee to department 99 if it doesn't exist). This is called **referential integrity**. `ON DELETE` decides what happens to the referencing rows when the referenced row is deleted: delete them too (`CASCADE`), set the column to NULL (`SET NULL`), or refuse the delete (`RESTRICT`).
- **`UNIQUE`**: no two rows may have the same value (e.g. email).
- **`NOT NULL`**: a value is required.
- **`CHECK`**: a custom rule, e.g. `salary > 0`.
- **`DEFAULT`**: the value used when none is provided.

== 7.4
The four basic data operations are known as **CRUD**: **C**reate (`INSERT`), **R**ead (`SELECT`), **U**pdate (`UPDATE`), **D**elete (`DELETE`).

**Always include a `WHERE` clause on `UPDATE` and `DELETE`.** Without it, *every* row in the table is changed or deleted.

Anatomy of a `SELECT`:

- **`SELECT`** chooses the columns (or `*` for all). You can compute new columns and rename them with `AS`.
- **`FROM`** chooses the table.
- **`WHERE`** filters rows using conditions: comparisons (`=`, `<>`, `>`), `AND`/`OR`/`NOT`, `IN (list)`, `BETWEEN a AND b`, `LIKE 'pattern'` (`%` = any characters, `_` = one character), `IS NULL`.
- **`ORDER BY`** sorts (`ASC` ascending is the default, `DESC` descending).
- **`LIMIT` / `OFFSET`** return only some rows, which is used for pagination.
- **`DISTINCT`** removes duplicate rows.
- **`CASE WHEN ... THEN ... ELSE ... END`** is SQL's if/else, used inside queries.

**NULL logic:** because NULL means "unknown", any comparison with NULL gives *unknown* rather than true or false. So `WHERE manager_id = NULL` never matches anything. You must write `IS NULL` / `IS NOT NULL`. `COALESCE(a, b)` returns the first non-NULL value, which makes it handy for defaults.

== 7.5
You *write* a query starting with `SELECT`, but the database *processes* the clauses in a different, **logical order**:

1. **FROM / JOIN**: gather the tables and combine them.
2. **WHERE**: filter individual rows.
3. **GROUP BY**: form groups.
4. **HAVING**: filter groups.
5. **SELECT**: compute the output columns (and aliases).
6. **DISTINCT**: remove duplicates.
7. **ORDER BY**: sort.
8. **LIMIT / OFFSET**: cut the result.

Knowing this explains many errors. You can't use a column alias from `SELECT` inside `WHERE` (it hasn't been computed yet), and you can't use aggregates like `COUNT()` in `WHERE` (groups don't exist yet), which is why `HAVING` exists.

== 7.6
**Aggregate functions** compute **one value from many rows**: `COUNT` (how many), `SUM` (total), `AVG` (average), `MIN`, `MAX`.

```sql
SELECT COUNT(*), AVG(salary) FROM employees;   -- one row for the whole table
```

**`GROUP BY`** splits rows into **groups** that share the same value(s) and computes the aggregates **per group**, for example "average salary *per department*". Picture sorting employees into piles by department and then counting each pile. Every column in `SELECT` must either be in the `GROUP BY` or be inside an aggregate function.

**`WHERE` vs `HAVING`:** `WHERE` filters **rows before** grouping ("only active employees"). `HAVING` filters **groups after** aggregation ("only departments with more than 5 people").

**Conditional aggregation** counts or sums only the rows that meet a condition (`FILTER (WHERE ...)` or `SUM(CASE WHEN ...)`). It turns rows into columns, which is called a **pivot**, and is very common in reports.

== 7.7
A **JOIN** combines rows from two (or more) tables based on a related column, usually a foreign key matching a primary key. Joins are how you put normalised data back together ("show each employee *with their department name*").

Think of two circles that overlap (a Venn diagram):

- **`INNER JOIN`** (or just `JOIN`) returns only rows that have a match in **both** tables. Employees without a department are dropped.
- **`LEFT JOIN`** returns **all** rows from the left table, plus matching data from the right. Where there is no match, the right-side columns are `NULL`. Use it for "all departments, *even those with no employees*".
- **`RIGHT JOIN`** is the mirror image of LEFT JOIN, and is rarely used.
- **`FULL OUTER JOIN`** returns all rows from both sides, matched where possible.
- **`CROSS JOIN`** returns every combination of rows (rows in A × rows in B).
- **Self join** joins a table to itself, e.g. matching employees with their managers, who are also in the `employees` table. Table **aliases** (`e`, `m`) tell the two copies apart.

```text
INNER:  A ∩ B          LEFT:  all of A (+ B where it matches)          FULL: A ∪ B
```

**Anti-join pattern:** `LEFT JOIN ... WHERE right.id IS NULL` finds rows in A that have **no** match in B ("customers who never ordered").

== 7.8
**Set operations** stack the results of two queries **vertically** (one under the other), while joins combine tables side by side. Both queries must return the same number of columns with compatible types.

- **`UNION`**: all rows from both, with duplicates removed.
- **`UNION ALL`**: all rows from both, keeping duplicates. It is faster because it doesn't check for duplicates.
- **`INTERSECT`**: only rows appearing in both.
- **`EXCEPT`**: rows in the first but not in the second.

== 7.9
A **subquery** is a query nested inside another query. You use the result of one question to answer another, e.g. "employees earning more than **the average salary**", where the average is itself a query.

- **Scalar subquery:** returns a single value, usable anywhere a value is expected.
- **`IN (subquery)`:** returns a list of values to match against.
- **Correlated subquery:** refers to the outer query's current row, so it conceptually runs **once per outer row** ("above the average *of their own* department"). Powerful, but it can be slow on large tables.
- **`EXISTS (subquery)`:** true if the subquery returns at least one row. It stops as soon as it finds one, and it handles NULLs correctly. Prefer **`NOT EXISTS`** over `NOT IN`.
- **Derived table:** a subquery in `FROM`, treated like a temporary table.
- **`LATERAL`:** a subquery in `FROM` that can refer to columns of tables before it, e.g. "the top 3 orders *for each* customer".

== 7.10
A **CTE (Common Table Expression)**, written with **`WITH name AS (...)`**, gives a name to a subquery so you can refer to it like a table in the main query. CTEs make complex queries **readable**: you can build the logic step by step, like intermediate variables in code, instead of nesting subqueries inside subqueries.

A **recursive CTE** refers to *itself*, which lets SQL walk through **hierarchies and graphs** such as org charts (employee → manager → manager's manager), category trees, folder structures and threaded comments. It has two parts joined by `UNION ALL`:

1. The **anchor** member is the starting rows (e.g. the CEO, who has no manager).
2. The **recursive** member joins the table to the rows found in the previous step (e.g. the employees whose manager is in the previous level).

It repeats until a step finds no new rows.

== 7.11
**Window functions** are among the most powerful and most-asked-about SQL features.

They calculate a value **for each row using a group of related rows (a "window")**, while **keeping every row** in the result. `GROUP BY`, in contrast, collapses each group into one row.

Example: show every employee **and** their department's average salary next to them. With `GROUP BY` you'd lose the individual employees. With a window function you keep them:

```sql
SELECT name, department_id, salary,
       AVG(salary) OVER (PARTITION BY department_id) AS dept_avg
FROM employees;
```

The **`OVER (...)`** clause defines the window:

- **`PARTITION BY`** splits rows into groups. The function restarts for each group, like GROUP BY but without collapsing rows.
- **`ORDER BY`** sets the order of rows inside each partition. It is needed for rankings, running totals and "previous/next row" functions.
- **Frame** (`ROWS BETWEEN ...`) sets exactly which rows around the current one to include, e.g. "the 6 previous rows plus this one" for a 7-day moving average.

Families of window functions:

- **Ranking:** `ROW_NUMBER()` (1, 2, 3, 4, always unique), `RANK()` (1, 2, 2, 4, ties share a rank and leave a gap), `DENSE_RANK()` (1, 2, 2, 3, no gaps), `NTILE(n)` (split into n buckets).
- **Aggregates as windows:** `SUM`, `AVG`, `COUNT` with `OVER` give running totals, percentages of a total, and group averages.
- **Offset functions:** `LAG()` reads a value from the **previous** row and `LEAD()` from the **next** row. They are perfect for "change compared to last month".
- **`FIRST_VALUE` / `LAST_VALUE`:** the first or last value in the window.

Because window functions are computed *after* `WHERE`, you can't filter on them directly. Wrap the query in a subquery or CTE and filter outside (that is the "top N per group" pattern).

== 7.12
These are **classic interview problems**. Each one combines the building blocks above. Before reading a solution, try to answer three questions: *What does each output row represent? Which tables do I need? Do I need grouping, a window, or a self-join?*

The "**gaps and islands**" trick in problem 6 deserves an explanation. For consecutive dates, the date minus its row number stays **constant**, so that difference can be used as a group identifier for each streak.

== 7.13
An **index** is a separate data structure that helps the database **find rows quickly without reading the whole table**. It is just like the index at the back of a book: instead of reading every page to find "closures", you look up the word and jump straight to page 42.

- **Without an index,** finding `WHERE email = 'a@x.com'` means a **full table scan**, checking every row. That's fine for 100 rows and painfully slow for 100 million.
- **With an index** on `email`, the database searches a sorted tree structure (a **B-tree**) and finds the row in a few steps, in O(log n) time.

**The trade-off:** indexes take extra disk space, and **every INSERT, UPDATE and DELETE must also update every index**. So index the columns you frequently **filter on (`WHERE`), join on (`JOIN`) and sort by (`ORDER BY`)**, not every column.

Key ideas:

- **Primary keys and UNIQUE constraints** get an index automatically.
- A **composite index** covers several columns, e.g. `(customer_id, created_at)`. Column order matters, like a phone book sorted by last name and then first name: it helps you search by last name, or last + first name, but not by first name alone. This is the **leftmost-prefix rule**.
- A **covering index** contains all the columns a query needs, so the database never has to visit the table itself.
- A **partial index** indexes only some rows (e.g. only `status = 'pending'`).
- A **clustered index** decides the *physical order* of the table's rows on disk. A table can have only one, and in MySQL InnoDB it is the primary key.

== 7.14
**`EXPLAIN`** shows the **query plan**: the step-by-step strategy the database's **query planner (optimizer)** chose to run your query. That includes which indexes it will use, the order it joins tables in, and how many rows it expects at each step. **`EXPLAIN ANALYZE`** actually runs the query and shows **real times and row counts** next to the estimates.

How to read it at a basic level:

- **Seq Scan** means the whole table was read. On a big table with a selective `WHERE`, this usually means a missing index.
- **Index Scan / Index Only Scan** means an index was used. That is good.
- Look for the step with the **largest time**, and for **estimated rows far from actual rows** (outdated statistics, so run `ANALYZE`).

**Sargable** ("Search ARGument ABLE") means a condition is written so an index *can* be used. Wrapping the column in a function (`WHERE YEAR(created_at) = 2026`) usually prevents index use. Rewrite it as a range on the raw column (`created_at >= '2026-01-01' AND created_at < '2027-01-01'`).

**Keyset pagination:** `OFFSET 100000` still makes the database walk past 100,000 rows. Instead, remember the last row you showed and ask for rows "after" it, which is fast at any depth.

== 7.15
A **transaction** is a group of SQL statements treated as **one indivisible unit of work**: either **all** of them take effect (`COMMIT`) or **none** do (`ROLLBACK`). The classic example is a bank transfer. Subtracting from account A and adding to account B must happen together. If the server crashes in between, neither change should remain.

**ACID** describes the guarantees of a reliable transaction:

- **Atomicity:** all or nothing.
- **Consistency:** the data moves from one valid state to another. All constraints still hold.
- **Isolation:** transactions running at the same time don't see each other's half-finished work. How strictly is controlled by the **isolation level**.
- **Durability:** once committed, the data survives crashes and power loss, because it is written to a log on disk first.

**Concurrency anomalies** (problems that happen when transactions run at the same time):

- **Dirty read:** you read another transaction's changes before it commits, and it may still roll back.
- **Non-repeatable read:** you read the same row twice in one transaction and get different values, because someone committed in between.
- **Phantom read:** you run the same query twice and *new rows* appear.
- **Lost update:** two transactions read the same value, both modify it, and the second overwrites the first's change.

Higher **isolation levels** prevent more anomalies but allow less concurrency (more waiting or retries). **Locks** (`SELECT ... FOR UPDATE`) make other transactions wait for a row. **Optimistic locking** uses a version number and retries if someone else changed the row first. A **deadlock** is two transactions each waiting for a lock the other holds. The database detects it and cancels one of them.

**MVCC** (Multi-Version Concurrency Control), used by PostgreSQL and InnoDB, keeps multiple versions of rows, so **readers never block writers and writers never block readers**. Each transaction sees a consistent snapshot.

== 7.16
**Normalization** is the process of organising tables to **avoid duplicated data**. Duplication causes **anomalies**:

- **Update anomaly:** a customer's address is stored in 50 order rows, and you update 49 of them by mistake. Now the data contradicts itself.
- **Insert anomaly:** you can't record a new product until someone orders it, because products only exist inside order rows.
- **Delete anomaly:** deleting the last order of a customer also deletes the only record of that customer.

The cure is to store **each fact in exactly one place** and link tables with foreign keys. The normal forms are steps towards that:

- **1NF:** each cell holds a single value (no comma-separated lists), and each row is unique.
- **2NF:** every non-key column depends on the **whole** primary key (this matters for composite keys).
- **3NF:** non-key columns depend **only on the key**, not on other non-key columns. For example, `department_name` doesn't belong in `employees`. It belongs in `departments`.

A popular summary of 3NF: every column must depend on "*the key, the whole key, and nothing but the key*".

**Denormalization** deliberately adds some duplication back (summary tables, cached totals) to make reads faster, accepting extra work to keep the copies in sync. It is common in analytics and reporting.

== 7.17
- A **view** is a **saved query** that you can use like a table. It stores no data. It just runs its query each time you use it. Use views to simplify complex queries or to expose only certain columns to certain users.
- A **materialized view** stores the query **result** physically, so it is fast to read. It must be **refreshed** to pick up changes. It suits heavy reports and dashboards.
- **Functions** and **stored procedures** are code stored and run **inside the database** (in PostgreSQL, using the PL/pgSQL language). They are useful for logic that must run close to the data.
- A **trigger** automatically runs a function **when an event happens** on a table (before or after INSERT/UPDATE/DELETE). Examples are setting `updated_at` automatically or writing audit logs.

Use database-side logic thoughtfully. It's powerful, but it is harder to version, test and debug than application code.

== 7.18
Modern databases offer many built-in **functions** for working with specific kinds of data:

- **JSON / JSONB** (PostgreSQL): store flexible, semi-structured data in a column, and still query inside it (`->` returns JSON, `->>` returns text). GIN indexes make it fast to search. This gives you some NoSQL-style flexibility inside a relational database.
- **String functions:** change case, cut, search, replace, split and concatenate text.
- **Date/time functions:** current time, add or subtract intervals, truncate to a day or month (`DATE_TRUNC`, very common for reports), extract parts like the year or weekday, and format dates.
- **Full-text search:** search natural-language text by words, ignoring word forms ("running" matches "run"), with ranking. That is far better than `LIKE '%word%'`.

== 7.19
**Database security** has two sides:

1. **Access control:** create separate database **roles/users** with the **minimum permissions** they need (the *principle of least privilege*). For example, a reporting tool gets read-only access. **Row-Level Security** can restrict which rows each user sees, which is useful in multi-tenant apps.

2. **SQL injection**, the most famous web vulnerability. It happens when user input is **pasted directly into SQL text**. An attacker types SQL code into a form field and changes the meaning of your query. For example, they can bypass login or delete tables:

```text
Code:   "SELECT * FROM users WHERE email = '" + input + "'"
Input:  ' OR '1'='1
Result: SELECT * FROM users WHERE email = '' OR '1'='1'   ← returns every user!
```

**The fix is always parameterized queries (prepared statements).** The SQL text and the values are sent to the database **separately**, so input is always treated as data, never as code. ORMs like Django's and Prisma do this automatically.

== 7.20
When an application grows, a single database server can become the bottleneck. Common strategies, roughly in the order teams adopt them:

1. **Optimise first:** indexes, better queries, caching (often the cheapest and most effective step).
2. **Vertical scaling:** a bigger server with more CPU, RAM and faster disks. It is simple but has limits.
3. **Connection pooling:** reuse database connections efficiently.
4. **Read replicas:** copies of the database that receive all changes from the main (primary) server. Reads are spread across replicas, and writes still go to the primary. Replicas may lag slightly behind.
5. **Partitioning:** split one huge table into smaller pieces (e.g. one per month) inside the same database. Queries touch only the relevant pieces.
6. **Sharding:** split data across **multiple database servers** by a **shard key** (e.g. customer ID). It is very scalable but complex, because cross-shard queries and transactions are hard.

**CAP theorem:** when the network between servers fails (a Partition), a distributed system must choose between **C**onsistency (everyone sees the same latest data) and **A**vailability (every request gets an answer).

**SQL vs NoSQL:** relational (SQL) databases offer strong structure, relationships, joins and ACID transactions. NoSQL databases (document: MongoDB; key-value: Redis; wide-column: Cassandra) trade some of that for flexible schemas and easier horizontal scaling. Choose based on the shape of your data and how you'll query it.

== 7.21
PostgreSQL and MySQL are the two most popular open-source relational databases. The SQL you write is about 90% identical. This table lists the differences you are most likely to run into when switching between them or answering interview questions.
