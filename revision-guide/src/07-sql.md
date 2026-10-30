# Part 7 — SQL: Basics to Advanced

Examples use **PostgreSQL** syntax (differences with MySQL noted where important). Sample schema used throughout:

```sql
CREATE TABLE departments (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE employees (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    manager_id    INT REFERENCES employees(id),
    salary        NUMERIC(10,2) CHECK (salary > 0),
    hired_at      DATE NOT NULL DEFAULT CURRENT_DATE,
    is_active     BOOLEAN DEFAULT TRUE
);

CREATE TABLE orders (
    id          BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    amount      NUMERIC(12,2) NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 7.1 SQL Sub-languages

| Category | Commands |
|---|---|
| DDL (Definition) | `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME` |
| DML (Manipulation) | `INSERT`, `UPDATE`, `DELETE`, `MERGE` |
| DQL (Query) | `SELECT` |
| DCL (Control) | `GRANT`, `REVOKE` |
| TCL (Transaction) | `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT` |

## 7.2 Data Types (Common)

- Numeric: `SMALLINT`, `INT`, `BIGINT`, `NUMERIC(p,s)`/`DECIMAL` (exact — use for money), `REAL`/`DOUBLE PRECISION` (approximate).
- Text: `CHAR(n)` (fixed), `VARCHAR(n)`, `TEXT`.
- Date/time: `DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMPTZ` (store UTC — preferred), `INTERVAL`.
- Others: `BOOLEAN`, `UUID`, `JSON`/`JSONB` (binary, indexable), `ARRAY`, `ENUM`, `BYTEA`.

## 7.3 DDL and Constraints

```sql
ALTER TABLE employees ADD COLUMN phone VARCHAR(20);
ALTER TABLE employees ALTER COLUMN phone SET NOT NULL;
ALTER TABLE employees DROP COLUMN phone;
ALTER TABLE employees RENAME COLUMN name TO full_name;
ALTER TABLE employees ADD CONSTRAINT chk_email CHECK (email LIKE '%@%');

DROP TABLE IF EXISTS temp_data;          -- removes table + structure
TRUNCATE TABLE logs RESTART IDENTITY;    -- removes all rows fast, keeps structure
```

**Constraints:** `PRIMARY KEY` (unique + not null), `FOREIGN KEY` (referential integrity; `ON DELETE CASCADE | SET NULL | RESTRICT`), `UNIQUE`, `NOT NULL`, `CHECK`, `DEFAULT`.

**DELETE vs TRUNCATE vs DROP:**

| | DELETE | TRUNCATE | DROP |
|---|---|---|---|
| Removes | Selected rows (`WHERE`) | All rows | Whole table |
| Speed | Slower (row by row, logs each) | Fast | Fast |
| Triggers fire | Yes | No | No |
| Rollback | Yes | Yes in Postgres (not in MySQL) | Yes in Postgres |

## 7.4 Basic DML and Queries

```sql
INSERT INTO departments (name) VALUES ('Engineering'), ('Sales'), ('HR');

INSERT INTO employees (name, email, department_id, salary)
VALUES ('Anish', 'anish@x.com', 1, 120000)
RETURNING id;                                 -- Postgres

-- Upsert
INSERT INTO employees (email, name, salary) VALUES ('a@x.com', 'A', 50000)
ON CONFLICT (email) DO UPDATE SET salary = EXCLUDED.salary;
-- MySQL: INSERT ... ON DUPLICATE KEY UPDATE salary = VALUES(salary);

UPDATE employees SET salary = salary * 1.10 WHERE department_id = 1;
DELETE FROM employees WHERE is_active = FALSE;

SELECT DISTINCT department_id FROM employees;

SELECT name, salary
FROM employees
WHERE salary BETWEEN 50000 AND 150000
  AND name ILIKE 'a%'                 -- LIKE: % any chars, _ single char; ILIKE = case-insensitive
  AND department_id IN (1, 2)
  AND manager_id IS NOT NULL          -- never "= NULL"
ORDER BY salary DESC NULLS LAST, name
LIMIT 10 OFFSET 20;                   -- pagination (SQL Server: OFFSET ... FETCH NEXT)

SELECT name,
       CASE
         WHEN salary >= 150000 THEN 'High'
         WHEN salary >= 80000  THEN 'Mid'
         ELSE 'Low'
       END AS band,
       COALESCE(manager_id, 0) AS mgr,   -- first non-null
       NULLIF(salary, 0)                 -- NULL if equal
FROM employees;
```

### NULL semantics (three-valued logic)

- `NULL = NULL` → `NULL` (unknown), not true. Use `IS NULL` / `IS DISTINCT FROM`.
- Aggregates ignore NULLs (except `COUNT(*)`).
- `NOT IN (subquery)` returns no rows if the subquery contains a NULL → prefer `NOT EXISTS`.

## 7.5 Logical Order of Execution

```text
FROM / JOIN  →  WHERE  →  GROUP BY  →  HAVING  →  SELECT  →  DISTINCT  →  ORDER BY  →  LIMIT/OFFSET
```

That is why you cannot use a `SELECT` alias inside `WHERE` (it doesn't exist yet), but you can in `ORDER BY`. Window functions are computed after `HAVING`, before `ORDER BY`.

## 7.6 Aggregation: GROUP BY and HAVING

```sql
SELECT department_id,
       COUNT(*)            AS headcount,
       COUNT(manager_id)   AS with_manager,   -- counts non-null
       AVG(salary)::INT    AS avg_salary,
       MIN(salary), MAX(salary), SUM(salary),
       STRING_AGG(name, ', ' ORDER BY name) AS names  -- MySQL: GROUP_CONCAT
FROM employees
WHERE is_active
GROUP BY department_id
HAVING COUNT(*) > 5             -- filter groups (WHERE filters rows)
ORDER BY avg_salary DESC;

-- Conditional aggregation (pivot)
SELECT DATE_TRUNC('month', created_at) AS month,
       COUNT(*) FILTER (WHERE status = 'paid')     AS paid,
       COUNT(*) FILTER (WHERE status = 'refunded') AS refunded,
       SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) AS revenue
FROM orders
GROUP BY 1
ORDER BY 1;

-- Subtotals
SELECT department_id, status, SUM(amount)
FROM orders GROUP BY ROLLUP (department_id, status);  -- also CUBE, GROUPING SETS
```

## 7.7 Joins

```sql
-- INNER: only matching rows
SELECT e.name, d.name AS dept
FROM employees e
JOIN departments d ON d.id = e.department_id;

-- LEFT: all rows from left, NULLs when no match
SELECT d.name, COUNT(e.id) AS headcount        -- COUNT(e.id) not COUNT(*) → 0 for empty depts
FROM departments d
LEFT JOIN employees e ON e.department_id = d.id
GROUP BY d.name;

-- Anti-join: departments with NO employees
SELECT d.* FROM departments d
LEFT JOIN employees e ON e.department_id = d.id
WHERE e.id IS NULL;

-- RIGHT JOIN (mirror of LEFT), FULL OUTER JOIN (all rows from both)
SELECT * FROM a FULL OUTER JOIN b ON a.id = b.a_id;

-- CROSS JOIN: Cartesian product (every combination)
SELECT s.size, c.color FROM sizes s CROSS JOIN colors c;

-- SELF JOIN: employee with manager name
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;

-- Join with extra condition: put it in ON (not WHERE) for LEFT joins to keep unmatched rows
SELECT c.id, o.id
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'paid';
```

**Join algorithms** (chosen by the planner): Nested Loop (small inner/indexed), Hash Join (large unsorted equi-joins), Merge Join (both inputs sorted).

## 7.8 Set Operations

```sql
SELECT email FROM customers
UNION                 -- removes duplicates (sort/hash cost)
SELECT email FROM newsletter;

SELECT email FROM customers UNION ALL SELECT email FROM newsletter;  -- keeps dupes, faster
SELECT id FROM a INTERSECT SELECT id FROM b;
SELECT id FROM a EXCEPT SELECT id FROM b;       -- Oracle: MINUS
```

Column count and compatible types must match.

## 7.9 Subqueries

```sql
-- Scalar subquery
SELECT name, salary, (SELECT AVG(salary) FROM employees) AS company_avg FROM employees;

-- IN subquery
SELECT * FROM employees
WHERE department_id IN (SELECT id FROM departments WHERE name IN ('Engineering', 'Sales'));

-- Correlated subquery: runs per outer row — employees earning above their dept average
SELECT e.name, e.salary
FROM employees e
WHERE e.salary > (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id);

-- EXISTS / NOT EXISTS (stops at first match; NULL-safe)
SELECT c.* FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- Derived table
SELECT dept, avg_sal FROM (
    SELECT department_id AS dept, AVG(salary) AS avg_sal FROM employees GROUP BY department_id
) t WHERE avg_sal > 100000;

-- LATERAL: top 3 orders per customer
SELECT c.id, o.*
FROM customers c
CROSS JOIN LATERAL (
    SELECT * FROM orders WHERE customer_id = c.id ORDER BY amount DESC LIMIT 3
) o;
```

## 7.10 Common Table Expressions (CTEs)

```sql
WITH dept_stats AS (
    SELECT department_id, AVG(salary) AS avg_sal
    FROM employees GROUP BY department_id
),
high_paid AS (
    SELECT e.* FROM employees e
    JOIN dept_stats s USING (department_id)
    WHERE e.salary > s.avg_sal * 1.2
)
SELECT * FROM high_paid;
```

### Recursive CTE — hierarchy / org chart

```sql
WITH RECURSIVE org AS (
    SELECT id, name, manager_id, 1 AS level, name::TEXT AS path
    FROM employees WHERE manager_id IS NULL                 -- anchor: CEO
    UNION ALL
    SELECT e.id, e.name, e.manager_id, o.level + 1, o.path || ' > ' || e.name
    FROM employees e
    JOIN org o ON e.manager_id = o.id                        -- recursive step
)
SELECT * FROM org ORDER BY path;

-- Generate a date series (useful to fill gaps in reports)
WITH RECURSIVE days AS (
    SELECT DATE '2026-01-01' AS d
    UNION ALL SELECT d + 1 FROM days WHERE d < DATE '2026-01-31'
)
SELECT d FROM days;
-- Postgres shortcut: SELECT generate_series('2026-01-01'::date, '2026-01-31', '1 day');
```

## 7.11 Window Functions

Window functions compute a value **per row** over a set of related rows **without collapsing** them (unlike `GROUP BY`).

```sql
function() OVER (PARTITION BY ... ORDER BY ... ROWS/RANGE BETWEEN ... )
```

```sql
-- Ranking
SELECT name, department_id, salary,
       ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn,   -- 1,2,3,4
       RANK()       OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk,  -- 1,2,2,4
       DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS drnk, -- 1,2,2,3
       NTILE(4)     OVER (ORDER BY salary) AS quartile,
       PERCENT_RANK() OVER (ORDER BY salary) AS pct
FROM employees;

-- Top-N per group (classic interview question)
SELECT * FROM (
    SELECT e.*, DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS r
    FROM employees e
) t WHERE r <= 3;

-- Aggregates as windows
SELECT name, department_id, salary,
       AVG(salary) OVER (PARTITION BY department_id) AS dept_avg,
       salary - AVG(salary) OVER (PARTITION BY department_id) AS diff_from_avg,
       SUM(salary) OVER () AS company_total,
       ROUND(100.0 * salary / SUM(salary) OVER (PARTITION BY department_id), 2) AS pct_of_dept
FROM employees;

-- Running total & moving average
SELECT created_at::date AS day, amount,
       SUM(amount) OVER (ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
       AVG(amount) OVER (ORDER BY created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7
FROM orders;

-- LAG / LEAD: compare with previous / next row
SELECT month, revenue,
       LAG(revenue)  OVER (ORDER BY month) AS prev_month,
       revenue - LAG(revenue) OVER (ORDER BY month) AS mom_change,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2) AS mom_pct,
       LEAD(revenue) OVER (ORDER BY month) AS next_month
FROM monthly_revenue;

-- FIRST_VALUE / LAST_VALUE / NTH_VALUE
SELECT name, department_id,
       FIRST_VALUE(name) OVER w AS top_earner,
       LAST_VALUE(name)  OVER (w ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS lowest
FROM employees
WINDOW w AS (PARTITION BY department_id ORDER BY salary DESC);
```

**ROWS vs RANGE:** `ROWS` counts physical rows; `RANGE` groups peers with equal `ORDER BY` values. The default frame with `ORDER BY` is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` — the reason `LAST_VALUE` looks "wrong" without an explicit frame.

## 7.12 Classic SQL Interview Problems

```sql
-- 1. Second highest salary
SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);
-- Nth highest (N = 3)
SELECT DISTINCT salary FROM employees ORDER BY salary DESC OFFSET 2 LIMIT 1;

-- 2. Find duplicates
SELECT email, COUNT(*) FROM employees GROUP BY email HAVING COUNT(*) > 1;

-- 3. Delete duplicates, keep the lowest id
DELETE FROM employees e
USING employees e2
WHERE e.email = e2.email AND e.id > e2.id;
-- or with ROW_NUMBER():
DELETE FROM employees WHERE id IN (
  SELECT id FROM (SELECT id, ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) rn FROM employees) t
  WHERE rn > 1
);

-- 4. Employees earning more than their manager
SELECT e.name FROM employees e JOIN employees m ON e.manager_id = m.id WHERE e.salary > m.salary;

-- 5. Customers who ordered in every month of 2026 so far
SELECT customer_id FROM orders
WHERE created_at >= '2026-01-01'
GROUP BY customer_id
HAVING COUNT(DISTINCT DATE_TRUNC('month', created_at)) = EXTRACT(MONTH FROM now());

-- 6. Consecutive days login (gaps & islands)
WITH d AS (
  SELECT DISTINCT user_id, login_date::date AS day FROM logins
), g AS (
  SELECT user_id, day,
         day - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day))::INT AS grp
  FROM d
)
SELECT user_id, MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS streak
FROM g GROUP BY user_id, grp HAVING COUNT(*) >= 3;

-- 7. Cumulative % of revenue per customer (Pareto)
SELECT customer_id, total,
       SUM(total) OVER (ORDER BY total DESC) / SUM(total) OVER () AS cumulative_share
FROM (SELECT customer_id, SUM(amount) total FROM orders GROUP BY customer_id) t;

-- 8. Day-1 retention
SELECT f.first_day,
       COUNT(DISTINCT f.user_id) AS new_users,
       COUNT(DISTINCT l.user_id) AS returned_next_day
FROM (SELECT user_id, MIN(login_date) first_day FROM logins GROUP BY user_id) f
LEFT JOIN logins l ON l.user_id = f.user_id AND l.login_date = f.first_day + 1
GROUP BY f.first_day;
```

## 7.13 Indexes

An index is an auxiliary data structure that speeds up lookups at the cost of extra storage and slower writes.

| Index type | Good for |
|---|---|
| **B-Tree** (default) | `=`, `<`, `>`, `BETWEEN`, `ORDER BY`, prefix `LIKE 'abc%'` |
| Hash | Equality only |
| GIN | JSONB, arrays, full-text search (`@>`, `?`, `@@`) |
| GiST / SP-GiST | Geometric, ranges, nearest-neighbour |
| BRIN | Huge, naturally ordered tables (time-series) |

```sql
CREATE INDEX idx_emp_dept ON employees (department_id);
CREATE UNIQUE INDEX idx_emp_email ON employees (lower(email));       -- expression index
CREATE INDEX idx_orders_cust_date ON orders (customer_id, created_at DESC); -- composite
CREATE INDEX idx_orders_pending ON orders (created_at) WHERE status = 'pending'; -- partial
CREATE INDEX idx_cover ON orders (customer_id) INCLUDE (amount);      -- covering (index-only scans)
CREATE INDEX CONCURRENTLY idx_x ON big_table (col);                  -- no write lock
CREATE INDEX idx_meta ON products USING GIN (metadata jsonb_path_ops);
```

**Clustered vs non-clustered:** a clustered index defines the physical order of rows (InnoDB primary key; only one per table). Non-clustered (secondary) indexes store keys + a pointer (or PK in InnoDB). Postgres tables are heaps; `CLUSTER` is a one-time reorder.

**Composite index — leftmost prefix rule:** an index on `(a, b, c)` helps queries filtering on `a`, `a,b`, `a,b,c` — but not `b` alone or `c` alone. Put equality columns first, range columns last.

**When an index is NOT used:**

- Function/expression on the column: `WHERE LOWER(email) = ...` (create an expression index), `WHERE created_at::date = ...`.
- Leading wildcard: `LIKE '%abc'` (use trigram GIN index `pg_trgm`).
- Implicit type casts (`varchar_col = 123`).
- Low selectivity (e.g., boolean column, most rows match) — sequential scan is cheaper.
- `OR` across different columns (sometimes; may use bitmap OR).
- Stale statistics (`ANALYZE`).

## 7.14 Query Optimization and EXPLAIN

```sql
EXPLAIN ANALYZE
SELECT o.* FROM orders o
WHERE o.customer_id = 42 AND o.created_at > now() - INTERVAL '30 days'
ORDER BY o.created_at DESC
LIMIT 20;
```

Reading the plan:

- **Seq Scan** — full table scan (fine for small tables).
- **Index Scan** — uses index, fetches rows from the heap.
- **Index Only Scan** — all needed columns in the index (best).
- **Bitmap Heap Scan** — many rows via index, read pages in order.
- Compare **estimated rows vs actual rows** — big mismatches mean stale stats.
- Look for expensive **Sort**, **Hash**, nested loops over big sets, and high `Buffers` reads.

**Optimization checklist:**

1. Select only needed columns (avoid `SELECT *`).
2. Index columns used in `WHERE`, `JOIN`, `ORDER BY`; use composite/covering indexes.
3. Make predicates **sargable**: `created_at >= '2026-01-01' AND created_at < '2026-02-01'` instead of `EXTRACT(MONTH FROM created_at) = 1`.
4. Replace correlated subqueries with joins/window functions when slow.
5. Prefer `EXISTS` over `IN` for large subqueries; `UNION ALL` over `UNION` when duplicates are impossible.
6. **Keyset (cursor) pagination** instead of large `OFFSET`:

```sql
-- OFFSET 100000 must scan and discard 100k rows
SELECT * FROM orders WHERE (created_at, id) < ($last_created_at, $last_id)
ORDER BY created_at DESC, id DESC LIMIT 20;
```

7. Batch writes; avoid N+1 queries from application code.
8. Keep statistics fresh (`ANALYZE`), vacuum (Postgres MVCC creates dead tuples).
9. Partition very large tables; consider materialized views for heavy reports.

## 7.15 Transactions and ACID

- **Atomicity** — all or nothing.
- **Consistency** — constraints always hold.
- **Isolation** — concurrent transactions don't interfere (to the configured level).
- **Durability** — committed data survives crashes (write-ahead log).

```sql
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 1;
SAVEPOINT before_credit;
UPDATE accounts SET balance = balance + 500 WHERE id = 2;
-- ROLLBACK TO SAVEPOINT before_credit;
COMMIT;
```

### Isolation Levels and Anomalies

| Level | Dirty read | Non-repeatable read | Phantom read | Notes |
|---|---|---|---|---|
| Read Uncommitted | Possible | Possible | Possible | Postgres treats as Read Committed |
| Read Committed | No | Possible | Possible | Postgres default |
| Repeatable Read | No | No | Possible (No in PG) | MySQL InnoDB default |
| Serializable | No | No | No | May abort with serialization errors → retry |

- **Dirty read:** reading uncommitted data of another transaction.
- **Non-repeatable read:** same row read twice returns different values.
- **Phantom read:** same query returns new rows inserted by another transaction.
- **Lost update:** two transactions read-modify-write the same row; one overwrites the other. Prevent with `UPDATE ... SET x = x - 1`, `SELECT ... FOR UPDATE`, or optimistic locking.

```sql
-- Pessimistic locking
BEGIN;
SELECT stock FROM products WHERE id = 7 FOR UPDATE;      -- others wait
UPDATE products SET stock = stock - 1 WHERE id = 7;
COMMIT;

-- Job queue pattern: workers grab different rows without blocking
SELECT id FROM jobs WHERE status = 'queued'
ORDER BY id LIMIT 10 FOR UPDATE SKIP LOCKED;

-- Optimistic locking
UPDATE products SET stock = 9, version = version + 1
WHERE id = 7 AND version = 3;          -- 0 rows updated → someone else changed it → retry
```

**Deadlocks** occur when two transactions wait on each other's locks; the DB aborts one. Avoid by locking rows in a consistent order and keeping transactions short.

**MVCC** (Postgres, InnoDB): readers don't block writers and writers don't block readers; each transaction sees a snapshot.

## 7.16 Normalization

| Normal form | Rule |
|---|---|
| 1NF | Atomic values; no repeating groups/arrays in a column; each row unique |
| 2NF | 1NF + no partial dependency (non-key column depends on whole composite key) |
| 3NF | 2NF + no transitive dependency (non-key → non-key) |
| BCNF | Every determinant is a candidate key |

Example: `orders(order_id, customer_id, customer_name, product_id, product_name, qty)` violates 2NF/3NF → split into `customers`, `products`, `orders`, `order_items`.

**Denormalization** (duplicating data, summary tables, materialized views) trades write complexity for read speed — common in reporting/analytics (OLAP) systems.

**Relationships:** one-to-one (FK + UNIQUE), one-to-many (FK on the "many" side), many-to-many (junction table with two FKs and a composite PK/unique).

## 7.17 Views, Materialized Views, Functions, Triggers

```sql
CREATE VIEW active_employees AS
SELECT id, name, department_id FROM employees WHERE is_active;

CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT DATE_TRUNC('month', created_at) AS month, SUM(amount) AS revenue
FROM orders WHERE status = 'paid' GROUP BY 1;
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;  -- needs a unique index

-- Function (PL/pgSQL)
CREATE OR REPLACE FUNCTION dept_headcount(p_dept INT) RETURNS INT AS $$
BEGIN
  RETURN (SELECT COUNT(*) FROM employees WHERE department_id = p_dept);
END;
$$ LANGUAGE plpgsql STABLE;

-- Trigger: maintain updated_at
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_updated
BEFORE UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Stored procedure (can manage transactions)
CREATE PROCEDURE transfer(src INT, dst INT, amt NUMERIC) LANGUAGE plpgsql AS $$
BEGIN
  UPDATE accounts SET balance = balance - amt WHERE id = src;
  UPDATE accounts SET balance = balance + amt WHERE id = dst;
  COMMIT;
END; $$;
CALL transfer(1, 2, 100);
```

## 7.18 Working with JSON, Strings and Dates (PostgreSQL)

```sql
-- JSONB
SELECT metadata->>'color' AS color,              -- text
       metadata->'dims'->>'w' AS width,
       metadata #>> '{dims,h}' AS height
FROM products
WHERE metadata @> '{"brand": "acme"}'            -- containment (GIN-indexable)
  AND metadata ? 'warranty';                     -- key exists

UPDATE products SET metadata = jsonb_set(metadata, '{color}', '"red"');
SELECT jsonb_agg(row_to_json(e)) FROM employees e;          -- rows → JSON array
SELECT * FROM jsonb_to_recordset('[{"a":1},{"a":2}]') AS x(a INT);

-- Strings
SELECT UPPER(name), LENGTH(name), SUBSTRING(name FROM 1 FOR 3), TRIM(name),
       CONCAT(first, ' ', last), SPLIT_PART(email, '@', 2), REPLACE(name, 'a', 'A'),
       REGEXP_REPLACE(phone, '\D', '', 'g')
FROM employees;

-- Dates
SELECT now(), CURRENT_DATE, now() - INTERVAL '7 days',
       DATE_TRUNC('week', created_at), EXTRACT(DOW FROM created_at),
       AGE(now(), hired_at), TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI')
FROM orders;

-- Full-text search
SELECT * FROM articles
WHERE to_tsvector('english', title || ' ' || body) @@ plainto_tsquery('english', 'django orm');
```

## 7.19 Security, Roles and SQL Injection

```sql
CREATE ROLE app_readonly LOGIN PASSWORD '...';
GRANT CONNECT ON DATABASE shop TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
REVOKE DELETE ON orders FROM app_user;

-- Row-Level Security (multi-tenant)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::INT);
```

**SQL injection:** never build SQL with string concatenation of user input.

```python
# BAD
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")   # email = "' OR 1=1 --"
# GOOD (parameterized)
cursor.execute("SELECT * FROM users WHERE email = %s", [email])
```

```javascript
// BAD:  pool.query(`SELECT * FROM users WHERE id = ${req.params.id}`)
// GOOD:
pool.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
```

## 7.20 Scaling Databases

- **Vertical scaling** (bigger machine) vs **horizontal** (more machines).
- **Read replicas** — offload reads; beware replication lag (read-your-writes).
- **Connection pooling** — PgBouncer / RDS Proxy; DB connections are expensive.
- **Partitioning** (single DB, split table):

```sql
CREATE TABLE events (id BIGINT, created_at TIMESTAMPTZ, payload JSONB)
PARTITION BY RANGE (created_at);
CREATE TABLE events_2026_10 PARTITION OF events
  FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
-- Partition pruning: queries filtering on created_at only scan relevant partitions.
```

- **Sharding** (split across DBs by shard key, e.g., `tenant_id`) — complex cross-shard joins/transactions.
- **CAP theorem:** in a network partition choose Consistency or Availability. **OLTP** (transactions, normalized) vs **OLAP** (analytics, columnar, denormalized).
- **SQL vs NoSQL:** SQL — schema, joins, ACID, complex queries; NoSQL (MongoDB, DynamoDB, Redis, Cassandra) — flexible schema, horizontal scale, access-pattern-driven design, often eventual consistency.

## 7.21 Quick Reference — Postgres vs MySQL

| Feature | PostgreSQL | MySQL (InnoDB) |
|---|---|---|
| Auto-increment | `SERIAL` / `GENERATED ALWAYS AS IDENTITY` | `AUTO_INCREMENT` |
| Upsert | `ON CONFLICT ... DO UPDATE` | `ON DUPLICATE KEY UPDATE` |
| Returning rows | `RETURNING` | Not supported (use `LAST_INSERT_ID()`) |
| String aggregate | `STRING_AGG` | `GROUP_CONCAT` |
| Case-insensitive LIKE | `ILIKE` | Depends on collation (default CI) |
| JSON | `JSONB` with GIN indexes | `JSON` with generated-column indexes |
| Default isolation | Read Committed | Repeatable Read |
| Full outer join | Yes | No (emulate with UNION) |
