# CryptoDesk API

A secure, scalable REST API platform for managing crypto asset watchlists.
Users can register, authenticate, and maintain a personal watchlist of crypto assets. Admins manage the master list of available assets.

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
│   ├── main.py                 
│   ├── config.py                
│   ├── database.py              
│   ├── dependencies.py          
│   │
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── models.py        
│   │   │   ├── schemas.py      
│   │   │   ├── service.py       
│   │   │   └── router.py       
│   │   │
│   │   ├── users/
│   │   │   ├── models.py       
│   │   │   ├── schemas.py       
│   │   │   ├── service.py       
│   │   │   └── router.py        
│   │   │
│   │   ├── assets/
│   │   │   ├── models.py       
│   │   │   ├── schemas.py       
│   │   │   ├── service.py       
│   │   │   └── router.py        
│   │   │
│   │   └── watchlist/
│   │       ├── models.py        
│   │       ├── schemas.py       
│   │       ├── service.py       
│   │       └── router.py        
│   │
│   └── utils/
│       ├── security.py          
│       ├── cache.py            
│       └── logger.py            
│
├── alembic/                     
├── web/                         # Next.js frontend
├── tests/
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Prerequisites

Make sure the following are installed and running before setup:

| Requirement | Version | Check |
|---|---|---|
| Python | 3.12+ | `python --version` |
| uv | latest | `uv --version` |
| PostgreSQL | any recent | `psql --version` |
| Redis | any recent | `redis-cli ping` |
| Node.js | 18+ | `node --version` |

**Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Start Redis** (if not running):
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis
```

---

## Local Setup — Backend

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

Open `.env` and fill in your values:

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

API running at `http://localhost:8000`
Swagger UI at `http://localhost:8000/docs`
ReDoc at `http://localhost:8000/redoc`

---

## Local Setup — Frontend

```bash
cd web
npm install
npm run dev
```

✅ Frontend running at `http://localhost:3000`

---

## Quick Test — Create an Admin User

After setup, promote a registered user to admin via psql to test admin-only endpoints:

```bash
psql -U postgres -d cryptodesk_db
```

```sql
-- verify your user exists
SELECT id, email, username, role FROM users;

-- promote to admin
UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
```

Then use the admin account to test `POST /api/v1/assets/`, `PUT`, and `DELETE` endpoints in Swagger.

---



**Log levels:**
- `INFO` — successful operations (logins, registrations, cache hits/misses, CRUD actions)
- `WARNING` — suspicious or failed events (wrong password, ownership violations, token misuse)

---

## Security Practices

- Passwords hashed with **bcrypt** — plain passwords never stored or logged
- JWT access tokens expire in **15 minutes** — limits stolen token window
- Refresh tokens **rotated** on every use — replay attacks are detectable
- Refresh tokens stored as **hashes** in DB — raw tokens never persisted
- **Rate limiting** on login endpoint — 5 requests/minute per IP
- Input **validation** on every endpoint via Pydantic
- SQLAlchemy ORM throughout — **no raw SQL**, no injection risk
- Ownership checks on all watchlist mutations — users can't touch other users' data
- **Soft deletes** on assets — preserves referential integrity
---

## Frontend

The Next.js frontend lives in `/web`:

- Registration and login pages
- JWT-protected dashboard
- Watchlist management (add, view, remove assets)
- Error and success feedback from API responses

```bash
cd web
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## License

MIT — see [LICENSE](./LICENSE)
