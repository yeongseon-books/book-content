---
title: "SQLAlchemy 101 (4/10): ORM Basics: Defining Models with DeclarativeBase and mapped_column"
series: sqlalchemy-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- SQLAlchemy
- ORM
- DeclarativeBase
- mapped_column
- SQLite
last_reviewed: '2026-05-03'
seo_description: An ORM model class is the marriage of "a Python class plus a Core
  Table." DeclarativeBase is the container (a MetaData) for those bindings, and…
---

# SQLAlchemy 101 (4/10): ORM Basics: Defining Models with DeclarativeBase and mapped_column

In Core we worked directly with `Table` and `select()` to compose SQL expressions. The ORM lays one more layer on top: it maps rows to Python objects, tracks attribute changes, and emits SQL at the right moment. SQLAlchemy 2.x's ORM lets you express almost any model with three tools - `DeclarativeBase`, `Mapped[T]`, and `mapped_column(...)`. This article focuses on those three and shows, in concrete terms, how an ORM model is wired to a Core `Table`.

This is the 4th article in the SQLAlchemy 101 series.

![ORM Basics: defining models with DeclarativeBase and mapped_column](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-01-orm-basics-defining-models-with-declarat.en.png)

*ORM Basics: defining models with DeclarativeBase and mapped_column*

## Questions to Keep in Mind

- What is `DeclarativeBase`, and how does it relate to Core's `MetaData`?
- What is the difference between `Mapped[int]` and `Mapped[str | None]`?
- How does `mapped_column(...)` differ from Core's `Column(...)`?

## Big Picture

![sqlalchemy 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-02-why-it-matters.en.png)

*sqlalchemy 101 chapter 4 flow overview*

This picture places ORM Basics: Defining Models with DeclarativeBase and mapped_column inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why it matters

Core alone is enough to talk to a database. But as an application grows, several costs add up quickly.

- Hand-rolling row dicts gets painful. `user.email` is safer and easier to read than `row["email"]`.
- Domain rules need a home. ORM models are both data mappings and domain objects, so methods on the class can carry behavior next to the data.
- Change tracking becomes manual: you have to compare fields and build UPDATE statements yourself. The ORM's Unit of Work automates that (covered in Ep5).
- Walking relationships maps to JOINs. The ORM lets you express that as attribute access (`user.orders`) - we'll dig into that in Ep6.

The ORM is not magic; it is a thin layer above Core that absorbs these costs. Defining models is the first step.

## Mental Model

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-03-mental-model.en.png)

*Mental model*
> An ORM model class is the marriage of "a Python class plus a Core `Table`." `DeclarativeBase` is the container (a `MetaData`) for those bindings, and `mapped_column` is the helper that derives a `Column` from a type hint.

The picture is straightforward.

```text
DeclarativeBase
   └── metadata: MetaData       # Core's schema catalog (Ep2)
         └── tables: dict[str, Table]
               └── Table("users", ...)   <─── ORM class User maps here
                     └── Column("id", ...)
                     └── Column("email", ...)
```

The moment you define an ORM class, a Core `Table` object is created and registered in `Base.metadata`. That is why you can reuse Ep2's `metadata.create_all(engine)` to build the schema from ORM definitions. The ORM is not a separate world; it lives on top of the same Core machinery.

## Core concepts

![Core concepts](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-04-core-concepts.en.png)

*Core concepts*
### 1) DeclarativeBase

In 2.x, the ORM base class fits in one declaration:

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

`Base` plays two roles:

- It serves as the parent of every ORM model class, propagating the mapping machinery via inheritance.
- It owns a `MetaData` instance accessible as `Base.metadata`. Every model's `Table` lives there.

The `naming_convention` we recommended in Ep2 returns here. To share that convention with ORM models, inject a `MetaData` explicitly:

```python
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

With this in place, the indexes, foreign keys, and unique constraints SQLAlchemy generates carry stable, predictable names. That stability matters when Alembic later diffs your model against the database; clean names produce clean migrations.

### 2) Mapped[T] and mapped_column

The 2.x ORM model pattern looks like this:

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    nickname: Mapped[str | None] = mapped_column(String(50))
```

What each line buys you:

- `Mapped[int]`: this column maps to SQL `INTEGER` and is `NOT NULL`.
- `Mapped[str | None]`: `Optional`, so `NULL` is allowed. You don't need `nullable=True`.
- `mapped_column(...)`: takes essentially the same arguments as Core's `Column(...)`. `primary_key=True`, `unique=True`, `default=...`, `server_default=...` all work.
- `String(255)`: if you omit the type, `Mapped[str]` becomes a default `String` (which SQLite stores as `TEXT` via type affinity). When you need a length limit, declaring it explicitly is clearer.

### 3) __tablename__ and __table_args__

```python
from sqlalchemy import Index, UniqueConstraint

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("user_id", "external_ref", name="uq_orders_user_ext"),
        Index("ix_orders_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    external_ref: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[str] = mapped_column()
```

`__tablename__` is the equivalent of `Table(name=...)`. `__table_args__` is the home for constraints and indexes that you would have passed to `Table(...)` in Core. It is a tuple; the last element may be a dict to pass dialect options like `{"sqlite_autoincrement": True}`.

### 4) repr and debug readability

ORM objects do not print their interesting fields by default. If you debug often, this small habit pays off:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"
```

A small touch, but every time an object lands in a log it earns its keep.

## Before-After

### Before: pure Core INSERT and SELECT

```python
from sqlalchemy import MetaData, Table, Column, Integer, String, insert, select

metadata = MetaData()
users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(255), unique=True),
)

with engine.begin() as conn:
    metadata.create_all(conn)
    conn.execute(insert(users), [{"email": "a@x.com"}, {"email": "b@x.com"}])

with engine.connect() as conn:
    rows = conn.execute(select(users)).all()
    for row in rows:
        print(row.email)   # row is a Row; depends on the Table schema object
```

### After: same operations through ORM models

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, select

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add_all([User(email="a@x.com"), User(email="b@x.com")])
    session.commit()

    users_list = session.scalars(select(User)).all()
    for u in users_list:
        print(u.email)   # u is a User instance, a domain object
```

Two things changed. First, the elements of `users_list` are `User` instances rather than dict-like Rows. Second, you do not write SQL at insert time; you register objects with `add_all()` and `commit()` flushes them in one go. Those two shifts are the heart of what the ORM gives you.

## Step-by-step walkthrough

![Step-by-step walkthrough](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-05-step-by-step-walkthrough.en.png)

*Step-by-step walkthrough*
All you need is SQLite and SQLAlchemy 2.x. Save the following as a single file and run it; the flow becomes muscle memory quickly.

```python
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine("sqlite:///orm_demo.db", echo=False, future=True)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    nickname: Mapped[str | None] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([
            User(email="alice@example.com", nickname="alice"),
            User(email="bob@example.com"),
        ])
        session.commit()

    with Session(engine) as session:
        for u in session.scalars(select(User).order_by(User.id)).all():
            print(u, "nickname=", u.nickname)

if __name__ == "__main__":
    main()
```

Reading the flow step by step:

1. `create_engine` builds a SQLite engine (Ep1).
2. `Base.metadata.create_all(engine)` builds the `users` table from the ORM model.
3. A `Session` opens, `add_all` registers objects, and `commit()` issues INSERT statements.
4. A new `Session` runs `scalars(select(User))` to fetch ORM instances back.
5. The output is `User(id=1, email='alice@example.com')`, using the `__repr__` we defined.

The Session and Unit of Work mechanics get a thorough treatment in the next post. The goal here is to feel the loop: define a model, build the schema with `create_all`, then INSERT and SELECT through objects.

## Common mistakes

### 1) Forgetting Mapped[T] and falling back to plain class attributes

```python
class User(Base):
    __tablename__ = "users"
    id = mapped_column(primary_key=True)        # Works, but no type info
    email = mapped_column(String(255))
```

The model is created, but your IDE and type checker no longer know the type of `user.email`. As the codebase grows, the loss in safety and readability compounds. Prefer to always declare `Mapped[T]`.

### 2) Missing Optional, accidentally creating NOT NULL columns

```python
nickname: Mapped[str] = mapped_column(String(50))   # NOT NULL
```

To allow `NULL`, write `Mapped[str | None]`. If your schema intent and the Python type disagree, you will see runtime `IntegrityError` exceptions.

### 3) Confusing default with server_default

`default=...` runs in Python at INSERT time and sends the value as a parameter. `server_default=...` emits a SQL `DEFAULT` clause so the database itself fills the value. If you want defaults to apply when migrations or raw SQL inserts happen, you must include `server_default` (see Ep2).

### 4) Re-declaring a mapping with the same table name

If you declare the `User` class twice in the same process, SQLAlchemy will warn or raise. In test suites that reload modules often, either call `Base.metadata.clear()` in your fixture or keep a separate `Base` for tests.

### 5) Defining both an ORM class and a Core Table for the same name

If you define a `User` ORM class and also create `Table("users", metadata, ...)` somewhere, they conflict. Pick one source of truth for the schema. The pragmatic choice with ORM is that the model owns the definition; if you need a Core handle, reach for `User.__table__`.

## In production

- **Shared columns**: keep boilerplate columns like `id`, `created_at`, `updated_at` in a mixin class so each model stays focused.
- **Enum mapping**: a Python `enum.Enum` mapped via `Mapped[MyEnum]` automatically picks up the `Enum` SQL type. SQLite stores it as `VARCHAR`, with validation enforced at the ORM layer.
- **JSON fields**: `from sqlalchemy import JSON` lets you write `Mapped[dict] = mapped_column(JSON)` for serializable data, and SQLite supports it.
- **Test isolation**: hammering `drop_all/create_all` between tests is slow. SQLite's in-memory engine (`sqlite:///:memory:`) is the common pattern for fast, fixture-scoped setups.
- **Migrations seed**: to point Alembic's autogenerate at your ORM models, set `target_metadata = Base.metadata` in `env.py` (covered in the alembic-101 series).

## Checklist

- [ ] You declared a `Base` that subclasses `DeclarativeBase`.
- [ ] Every column is declared as `Mapped[T]: mapped_column(...)`.
- [ ] Nullable columns use `Optional` (`| None`).
- [ ] `__tablename__` is set explicitly (don't rely on guessing).
- [ ] Indexes and unique constraints are grouped under `__table_args__`.
- [ ] `Base.metadata` carries a `naming_convention`.
- [ ] `__repr__` is defined so logs print useful information.

## Exercises

1. Define a `Product(id, name, price, is_active)` model and create the SQLite table with `Base.metadata.create_all()`. Make `is_active` non-nullable with a default of `True`. Did you choose `default` or `server_default`, and why?
2. Add a unique constraint on `(name, price)` to the model from exercise 1. Place a `UniqueConstraint` inside `__table_args__` and INSERT the same `(name, price)` twice. What happens?
3. Take a column declared as `Mapped[str]` and try to INSERT `None`. What error appears? Copy the message verbatim and decide whether the error originates in Python or in the database engine.

## Answering the Opening Questions

- **What is `DeclarativeBase`, and how does it relate to Core's `MetaData`?**
  - The article treats ORM Basics: Defining Models with DeclarativeBase and mapped_column as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What is the difference between `Mapped[int]` and `Mapped[str | None]`?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How does `mapped_column(...)` differ from Core's `Column(...)`?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SQLAlchemy 101 (1/10): Getting Started with SQLAlchemy 2.x - Engine and Connection Demystified](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy 101 (2/10): SQLAlchemy Core - Modeling Schema as Python Objects with MetaData, Table, and Column](./02-core-metadata-table-types.md)
- [SQLAlchemy 101 (3/10): SQLAlchemy Core - select, insert, update, delete in 2.x Style](./03-core-select-insert-update-delete.md)
- **SQLAlchemy 101 (4/10): ORM Basics: Defining Models with DeclarativeBase and mapped_column (current)**
- SQLAlchemy 101 (5/10): Session in Depth: How Unit of Work and Identity Map Actually Work (upcoming)
- SQLAlchemy 101 (6/10): ORM Relationships: Connecting Both Sides Safely with relationship and back_populates (upcoming)
- SQLAlchemy 101 (7/10): Loading Strategies and the N+1 Problem: When to Pick lazy, joined, or selectin (upcoming)
- SQLAlchemy 101 (8/10): Events, hybrid_property, and custom types (upcoming)
- SQLAlchemy 101 (9/10): Async SQLAlchemy with aiosqlite and AsyncSession (upcoming)
- SQLAlchemy 101 (10/10): Production patterns: pools, observability, migrations, and deploys (upcoming)

<!-- toc:end -->

## References

- [SQLAlchemy 2.x ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Declarative Mapping with `DeclarativeBase`](https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html)
- [`mapped_column()` API reference](https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column)
- [Naming conventions in MetaData](https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions)

## Summary and what's next

The ORM's starting point is small. `DeclarativeBase` is a holder for `MetaData`. `Mapped[T]` declares the SQL type and nullability in one stroke. `mapped_column(...)` is Core's `Column(...)` paired with a type hint. Models built with these three become a SQLite schema the moment you call `Base.metadata.create_all(engine)`. In the next post we look at the `Session` itself - how it tracks object changes, and how the Unit of Work and Identity Map batch SQL on your behalf.

Tags: Python, SQLAlchemy, ORM, Database
