# Task 3 – Endpoints and cloud security (MC101)

Voting system API built with **FastAPI**, **SQLAlchemy ORM** and **Postgres**, run with **Docker Compose**.
It builds on Task 1 (auth, admin MFA) and Task 2 (logging to `logs/logs.log`, Docker).

## How to run the app

Prerequisite: Docker with Docker Compose v2 and a `.env` file:

```bash
cp .env.example .env     # Windows: copy .env.example .env
```
Then set at least `JWT_SECRET_KEY`, the `POSTGRES_*` values and (for admin login) the SMTP values.

### 1. Build the image with Docker Compose
```bash
docker compose build
```

### 2. Run the app with Docker Compose
```bash
docker compose up
```
(add `-d` to run in the background). This starts **two containers**: `voting-db` (Postgres) and `voting-api`, which waits until the database is healthy.
API: http://localhost:8000 – interactive docs: http://localhost:8000/docs

### 3. Stop the app with Docker Compose
```bash
docker compose down
```
`docker compose down -v` also deletes the database volume (empties all tables).

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/admin/register` | – | Register an admin |
| POST | `/admin/request-mfa` | – | Admin login step 1: password → one-time code by e-mail |
| POST | `/admin/login` | – | Admin login step 2: email + password + MFA code → token |
| GET | `/admin` | admin token | Info about the logged-in admin |
| DELETE | `/admin` | admin token | Delete the admin the token belongs to |
| POST | `/admin/candidate` | admin token | Register a candidate (`name`, `email`); the admin comes from the token |
| GET | `/admin/candidate` | – | List all candidates (public) |
| POST | `/user/register` | – | Register a user |
| POST | `/user/login` | – | Log in → token |
| GET | `/user` | user token | Info about the logged-in user |
| DELETE | `/user` | user token | Delete the user the token belongs to |
| POST | `/user/vote` | user token | Vote (`candidate_id`), one vote per user |
| GET | `/votes` | – | All votes + tally per candidate (public) |

Send the token as `Authorization: Bearer <token>`. In `/docs`, press **Authorize** and paste the token.

Notes
- **Admin login uses MFA** (from Task 1): call `/admin/request-mfa`, read the 6-digit code from the e-mail (Ethereal inbox), then call `/admin/login` with it. The code is single use, expires after 5 minutes and is locked after 5 wrong attempts.
- Errors: `401` missing/invalid token, `403` wrong role (e.g. a user token on an admin endpoint), `409` duplicate e-mail / already voted, `404` unknown candidate.
- `GET /votes` shows each vote (`vote_id`, `candidate_id`) and the count per candidate. The voter's id is **not** shown, so nobody can see who voted for whom.

## Database (Postgres + SQLAlchemy ORM)

Tables are defined in `models.py` and created at startup.

| Table | Columns |
|---|---|
| `admins` | id (PK), name, email (unique), password_hash, created_at, MFA fields |
| `users` | id (PK), name, email (unique), password_hash, created_at (same shape as admins) |
| `candidates` | **candidate_id** (PK, indexed), name, email (unique), **admin_id** → `admins.id` **ON DELETE SET NULL** |
| `votes` | **vote_id** (PK), **user_id** → `users.id` (**UNIQUE**), **candidate_id** → `candidates.candidate_id` |

- A vote for a candidate that does not exist is rejected (API → `404`, and the foreign key would reject it in the database even without the API check).
- `UNIQUE(user_id)` guarantees one vote per citizen, even for two simultaneous requests.
- Deleting an admin keeps their candidates (`admin_id` becomes `NULL`). Deleting a user keeps their vote counted (`user_id` becomes `NULL`).
- Passwords are hashed with bcrypt; MFA codes are stored hashed.
- The database container has **no published port**; only the API container can reach it.

## Logging

Everything is logged (minimum level `INFO`) to **`logs/logs.log`** (the folder is mounted into the container) and to the console (`docker compose logs -f`). Registrations, logins (ok/failed), MFA, candidate registration, votes, invalid tokens and deletions are logged. Passwords, MFA codes and tokens are never logged, and votes are logged without the chosen candidate.

## Tests

```bash
poetry install
poetry run pytest                      # in-memory SQLite
# same tests against a real Postgres:
TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/testdb poetry run pytest
```

## Run without Docker (optional)

Uncomment `DATABASE_URL=sqlite:///./app.db` in `.env`, then `poetry install` and `poetry run python main.py` (http://127.0.0.1:8000/docs).

## Docker notes
- Image: `python:3.12-slim`, only main Poetry dependencies, runs as a non-root user.
- Secrets come from `.env` (never baked into the image). Compose builds the `DATABASE_URL` from the `POSTGRES_*` values; keep the DB password URL-safe (letters and digits).
- On Linux, if `logs/` is not writable for the container user: `APP_UID=$(id -u) docker compose build`.
