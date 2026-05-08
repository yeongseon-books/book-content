
# Running with a Database

> Docker 101 series (8/10)

<!-- a-grade-intro:begin -->

**Core question**: How do you run your containerized *Python app* together with *PostgreSQL* properly?

> *The heart of a DB container is the *three-step rhythm* of *persistence, readiness, and migrations*.*

<!-- a-grade-intro:end -->

## What You Will Learn

- Running *PostgreSQL with Compose*
- *Healthchecks* and *startup order*
- Automating *Alembic migrations*
- *Seed data* patterns
- Five common pitfalls

## Why It Matters

If the app starts *before* the DB is ready, you get *cold-start incidents*. If migrations are *not automated*, deployments become *manual*.

> *The app-DB seam is the *most common incident site* and the *biggest automation opportunity*.*

## Concept at a Glance

```mermaid
flowchart LR
    Compose["compose.yaml"] --> Db["postgres + healthcheck"]
    Db -->|service_healthy| Mig["alembic upgrade head"]
    Mig --> Web["fastapi"]
```

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

- [What Is Docker?](./01-what-is-docker.md)
- [Images and Containers](./02-image-and-container.md)
- [Writing a Dockerfile](./03-dockerfile.md)
- [Volumes and Networks](./04-volume-and-network.md)
- [Docker Compose](./05-docker-compose.md)
- [Environment Variables and Configuration](./06-env-and-config.md)
- [Containerizing a Python App](./07-python-app-containerize.md)
- **Running with a Database (current)**
- Image Optimization (upcoming)
- Production-Ready Docker (upcoming)
## References

- [PostgreSQL official image](https://hub.docker.com/_/postgres)
- [Compose - service_completed_successfully](https://docs.docker.com/compose/compose-file/05-services/#depends_on)
- [Alembic documentation](https://alembic.sqlalchemy.org/)
- [pg_isready](https://www.postgresql.org/docs/current/app-pg-isready.html)

Tags: Docker, Postgres, Compose, Migration, Healthcheck

---

© 2026 YeongseonBooks. All rights reserved.
