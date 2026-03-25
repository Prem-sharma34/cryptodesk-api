# CryptoDesk API

A secure, scalable REST API platform for managing crypto asset watchlists — built as part of the PrimeTrade.ai Backend Developer Intern assignment.

Users can register, authenticate, and maintain a personal watchlist of crypto assets. Admins manage the master list of available assets.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI 0.135 |
| Database | PostgreSQL + SQLAlchemy 2.0 ORM |
| Migrations | Alembic |
| Auth | JWT (Access + Refresh Token rotation) |
| Password Hashing | passlib + bcrypt |
| Caching | Redis 7 |
| Rate Limiting | slowapi |
| Package Manager | uv |
| Frontend | Next.js (in `/web`) |

---

## Features

**Authentication**
- User registration and login with bcrypt password hashing
- JWT access token (15 min) + refresh token rotation (7 days)
- Refresh token stored as a hash in the database — never raw
- Rate limiting on login endpoint (brute force protection)
- Secure logout with token revocation

**Role-Based Access Control**
- Two roles: `user` and `admin`
- Admin routes protected via dependency injection
- Users can only access and mutate their own data

**Assets (Admin)**
- Full CRUD for crypto assets (BTC, ETH, etc.)
- Soft delete — assets are deactivated, not removed
- Redis caching on asset list with 5-minute TTL
- Cache invalidation on any write operation

**Watchlist (User)**
- Add/remove crypto assets from personal watchlist
- Ownership verification on every mutating operation
- Unique constraint prevents duplicate watchlist entries
- Enriched responses — returns full asset details, not just IDs

**General**
- API versioning under `/api/v1/`
- Input validation via Pydantic on every endpoint
- Auto-generated Swagger UI at `/docs`
- Modular project structure — each feature is a self-contained module

---

## Project Structure

```
cryptodesk-api/
├── app/
│   ├── main.py                  # FastAPI app, router registration, middleware
│   ├── config.py                # Environment variables via Pydantic BaseSettings
│   ├── database.py              # SQLAlchemy engine, session, DeclarativeBase
│   ├── dependencies.py          # Shared deps: get_db, get_current_user, get_current_admin
│   │
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── models.py        # RefreshToken model
│   │   │   ├── schemas.py       # RegisterRequest, LoginRequest, TokenResponse
│   │   │   ├── service.py       # register, login, refresh, logout logic
│   │   │   └── router.py        # /api/v1/auth endpoints
│   │   │
│   │   ├── users/
│   │   │   ├── models.py        # User model
│   │   │   ├── schemas.py       # UserResponse, UpdateUserRequest
│   │   │   ├── service.py       # profile, update, delete logic
│   │   │   └── router.py        # /api/v1/users endpoints
│   │   │
│   │   ├── assets/
│   │   │   ├── models.py        # Asset model
│   │   │   ├── schemas.py       # AssetCreate, AssetResponse
│   │   │   ├── service.py       # CRUD + cache invalidation
│   │   │   └── router.py        # /api/v1/assets endpoints
│   │   │
│   │   └── watchlist/
│   │       ├── models.py        # WatchlistItem model
│   │       ├── schemas.py       # WatchlistItemCreate, WatchlistItemResponse
│   │       ├── service.py       # add, list, update, remove with ownership checks
│   │       └── router.py        # /api/v1/watchlist endpoints
│   │
│   └── utils/
│       ├── security.py          # JWT encode/decode, bcrypt hash/verify
│       └── cache.py             # Redis get/set/delete helpers
│
├── alembic/                     # Database migration files
├── web/                         # Next.js frontend
├── tests/
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- PostgreSQL running locally
- Redis running locally

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Prem-sharm34/cryptodesk-api.git
cd cryptodesk-api
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values (see table below).

### 4. Create the database

```bash
psql -U postgres -c "CREATE DATABASE cryptodesk_db;"
```

### 5. Run migrations

```bash
uv run alembic upgrade head
```

### 6. Start the API

```bash
uv run uvicorn app.main:app --reload
```

API is now running at `http://localhost:8000`
Swagger UI available at `http://localhost:8000/docs`

---

## Environment Variables

Example `.env`:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/cryptodesk_db
SECRET_KEY=your-random-32-byte-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://localhost:6379
```

Generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API Endpoints

Full interactive documentation is available at `/docs` once the server is running.

### Auth — `/api/v1/auth`

| Method | Path | Description | Auth |
|---|---|---|---|
| POST | `/register` | Register a new user | None |
| POST | `/login` | Login, returns access + refresh tokens | None |
| POST | `/refresh` | Rotate refresh token, get new access token | Refresh token |
| POST | `/logout` | Revoke refresh token | Bearer token |
| GET | `/me` | Get current user info | Bearer token |

### Users — `/api/v1/users`

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/me` | Get own profile | User |
| PUT | `/me` | Update own profile | User |
| DELETE | `/me` | Delete own account | User |
| GET | `/` | List all users | Admin |
| PATCH | `/{user_id}/deactivate` | Deactivate a user | Admin |

### Assets — `/api/v1/assets`

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/` | List all active assets (Redis cached) | User |
| GET | `/{asset_id}` | Get asset details | User |
| POST | `/` | Create new asset | Admin |
| PUT | `/{asset_id}` | Update asset | Admin |
| DELETE | `/{asset_id}` | Soft-delete asset | Admin |

### Watchlist — `/api/v1/watchlist`

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/` | Get own watchlist with asset details | User |
| POST | `/` | Add asset to watchlist | User |
| PATCH | `/{item_id}` | Update notes on watchlist item | User |
| DELETE | `/{item_id}` | Remove asset from watchlist | User |

---

## Database Schema

```
users
├── id (UUID, PK)
├── email (unique, indexed)
├── username (unique, indexed)
├── hashed_password
├── role (enum: user | admin)
├── is_active
├── created_at
└── updated_at

refresh_tokens
├── id (UUID, PK)
├── user_id (FK → users.id, CASCADE)
├── token_hash (unique)
├── expires_at
├── is_revoked
└── created_at

assets
├── id (UUID, PK)
├── symbol (unique, indexed)
├── name
├── description
├── is_active
├── created_at
└── updated_at

watchlist_items
├── id (UUID, PK)
├── user_id (FK → users.id, CASCADE)
├── asset_id (FK → assets.id, CASCADE)
├── notes
├── created_at
└── UNIQUE(user_id, asset_id)
```

---

## Security Practices

- Passwords hashed with **bcrypt** — plain passwords never stored or logged
- JWT access tokens expire in **15 minutes** — limits stolen token window
- Refresh tokens are **rotated** on every use — replay attacks are detectable
- Refresh tokens stored as **hashes** in DB — raw tokens never persisted
- **Rate limiting** on login endpoint — 5 requests/minute per IP
- Input **validation** on every endpoint via Pydantic
- SQLAlchemy ORM used throughout — **no raw SQL**, no injection risk
- Ownership checks on all watchlist mutations — users can't touch other users' data
- **Soft deletes** on assets — preserves referential integrity

---

## Scalability Notes

**Stateless API** — JWTs carry all claims. No server-side sessions. Multiple API instances can run behind a load balancer with zero session-affinity requirements.

**Redis Caching** — The asset list (read-heavy, rarely written) is cached with a 5-minute TTL. Cache is invalidated on every write. This pattern shields the database as traffic scales.

**Database Read Replicas** — SQLAlchemy 2.0 supports multiple engines. Write operations route to the primary; read-heavy endpoints (asset list, watchlist) can route to replicas with minimal code changes.

**Modular Structure** — Each module (auth, users, assets, watchlist) is fully self-contained with its own router, schemas, service, and models. Any module can be extracted into an independent microservice as load demands grow. The auth module, for example, is a natural candidate to become a standalone Auth Service.

**Async-ready** — FastAPI supports full async/await. Migrating to async SQLAlchemy 2.0 sessions would allow the event loop to handle significantly more concurrent connections without additional infrastructure.

**Containerised** — Docker Compose bundles the API, PostgreSQL, and Redis into a single deployable unit. Migrating to Kubernetes requires no application changes — only infrastructure configuration.

---

## Frontend

The Next.js frontend lives in `/web`. It provides:

- Registration and login pages
- JWT-protected dashboard
- Watchlist management (add, view, remove assets)
- Error and success feedback from API responses

To run the frontend:

```bash
cd web
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## License

MIT — see [LICENSE](./LICENSE)
