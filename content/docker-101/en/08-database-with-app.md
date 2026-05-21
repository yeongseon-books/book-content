---
series: docker-101
episode: 8
title: "Docker 101 (8/10): Running with a Database"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Docker
  - Postgres
  - Compose
  - Migration
  - Healthcheck
seo_description: Run PostgreSQL and FastAPI together with Compose, including healthchecks, automated Alembic migrations, and idempotent seeding.
last_reviewed: '2026-05-15'
---

# Docker 101 (8/10): Running with a Database

The app-database boundary is where container demos turn into real systems. A web container can start successfully while the database is still warming up, migrations can lag behind the runtime schema, and seed data can quietly stop being repeatable once several environments exist.

That is why a dependable database setup has a rhythm: persist the data, wait for honest readiness, then apply migrations in a controlled place before the application begins serving traffic.

This is post 8 in the Docker 101 series. It uses PostgreSQL and FastAPI to show how Compose, healthchecks, migrations, and idempotent seeding fit together when the goal is not just “it boots” but “it boots predictably.”


![docker 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/08/08-01-concept-at-a-glance.en.png)
*docker 101 chapter 8 flow overview*

## Questions to Keep in Mind

- Running *PostgreSQL with Compose?
- Healthchecks* and *startup order?
- Automating *Alembic migrations?

## Why It Matters

If the app starts *before* the DB is ready, you get *cold-start incidents*. If migrations are *not automated*, deployments become *manual*.

> *The app-DB seam is the *most common incident site* and the *biggest automation opportunity*.*

## Key Terms

- **Migration**: schema *versioning*.
- **Seed**: initial *baseline data*.
- **Healthcheck**: DB *readiness signal*.
- **Init container**: a *one-shot* migration container.
- **Volume**: persistent *DB data*.

## Before/After

**Before**: *manual SQL* in every new environment. Migrations are *order-dependent*.

**After**: `docker compose up` brings up *DB + migration + app* *in order* with one line.

## Hands-on: App + DB in 5 Steps

### Step 1 — `compose.yaml`

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: app
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d app"]
      interval: 5s
      retries: 10

  migrate:
    image: myapi:1.0
    command: ["alembic", "upgrade", "head"]
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:dev@db/app
    depends_on:
      db: { condition: service_healthy }

  web:
    image: myapi:1.0
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:dev@db/app
    depends_on:
      migrate: { condition: service_completed_successfully }

volumes:
  pgdata:
```

### Step 2 — Initialize Alembic

```bash
docker compose run --rm migrate alembic init alembic
docker compose run --rm migrate alembic revision --autogenerate -m "init"
```

### Step 3 — Seed

```python
# app/seed.py
def seed(session) -> None:
    if session.query(User).count() == 0:
        session.add(User(email="admin@example.com"))
        session.commit()
```

```yaml
seed:
  image: myapi:1.0
  command: ["python", "-m", "app.seed"]
  depends_on:
    migrate: { condition: service_completed_successfully }
```

### Step 4 — Bring it up and verify

```bash
docker compose up -d
docker compose exec db psql -U postgres -d app -c "\dt"
curl http://localhost:8000/users
```

### Step 5 — Backup

```bash
docker compose exec db pg_dump -U postgres app > app.sql
```

### Verify right after you run it

- `docker compose exec db psql -U postgres -d app -c "\dt"` should show the migrated tables, and `curl http://localhost:8000/users` should prove that the web service can read through the database boundary.
- Run the seed twice and confirm that records do not duplicate; that is the operational test for idempotency.

### If it does not work, check this first

- If the web service crashes on startup, inspect `docker compose logs migrate` before the web logs; schema drift is often the first failure.
- If backups look empty, verify that data actually landed in the named volume before debugging `pg_dump` flags.

## What to Notice in This Code

- *condition: service_healthy* guarantees *real* readiness.
- `migrate` is a *one-shot init container*.
- *Seeds* must be *idempotent*.

## Five Common Mistakes

1. **Connecting via `depends_on` alone.** Without a healthcheck, *cold-start fails*.
2. **Running migrations from the *web entrypoint*.** *Each worker re-runs* them.
3. **Mounting the DB via *bind mount*.** Permission and performance issues.
4. **Keeping the *default `POSTGRES_PASSWORD`*.** Immediate compromise once exposed.
5. **No *backup procedure*.** Game over after an incident.

## How This Shows Up in Production

Real deployments use *managed DBs* like RDS / Cloud SQL, but local and CI converge on the same Compose to keep *environment parity*.

## How a Senior Engineer Thinks

- *Migrations must be *automatic, idempotent, single-runner*.
- *Healthchecks must be honest* for startup order to mean anything.
- *DB data lives in a named volume and gets backed up*.
- *Seeds* are about *idempotency*.
- *Passwords come from a secret store; never default*.

## Checklist

- [ ] DB has a *healthcheck*.
- [ ] *Migration* is *separated as one-shot*.
- [ ] Data is on a *named volume*.
- [ ] A *backup command* is documented.

## Practice Problems

1. Bring up *postgres + migrate + web* with Compose and verify *ordered startup*.
2. Make Alembic migrations *run automatically*.
3. Write *idempotent seed data*.

## Wrap-up and Next Steps

A clean app-DB seam drops *team setup cost* toward *zero*. Next, *image optimization* makes builds and pulls fast.

## Answering the Opening Questions

- **Running *PostgreSQL with Compose?**
  - The article treats Running with a Database as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Healthchecks* and *startup order?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Automating *Alembic migrations?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Docker 101 (1/10): What Is Docker?](./01-what-is-docker.md)
- [Docker 101 (2/10): Images and Containers](./02-image-and-container.md)
- [Docker 101 (3/10): Writing a Dockerfile](./03-dockerfile.md)
- [Docker 101 (4/10): Volumes and Networks](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): Environment Variables and Configuration](./06-env-and-config.md)
- [Docker 101 (7/10): Containerizing a Python App](./07-python-app-containerize.md)
- **Running with a Database (current)**
- Image Optimization (upcoming)
- Production-Ready Docker (upcoming)

<!-- toc:end -->

## References

### Official docs

- [PostgreSQL official image](https://hub.docker.com/_/postgres)
- [Compose - service_completed_successfully](https://docs.docker.com/compose/compose-file/05-services/#depends_on)
- [Alembic documentation](https://alembic.sqlalchemy.org/)
- [pg_isready](https://www.postgresql.org/docs/current/app-pg-isready.html)

### Verification and troubleshooting

- [docker compose run reference](https://docs.docker.com/reference/cli/docker/compose/run/)

Tags: Docker, Postgres, Compose, Migration, Healthcheck
