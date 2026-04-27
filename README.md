<img width="1280" height="320" alt="FastAPI • PostgreSQL • Docker" src="https://github.com/user-attachments/assets/4dca2877-f712-4f57-9ef6-c2e1b4c2f05a" />

# 📦 Inventory Management API

A production-ready REST API for inventory management built with **FastAPI**, **PostgreSQL**, and **Docker**. Designed with clean architecture, JWT authentication, role-based access control, and full test coverage — ready to deploy and easy to extend.

---

## ✨ Features

- 🔐 **JWT Authentication** — secure login with bcrypt password hashing
- 👥 **Role-Based Access Control** — `admin` and `user` roles with protected endpoints
- 📦 **Product Management** — full CRUD with SKU validation, pagination, and search
- 🗂️ **Category Management** — organize products into categories
- 📊 **Inventory Control** — stock adjustments with negative-stock prevention and low-stock alerts
- 🐳 **Dockerized** — one command to spin up the full environment
- 🧪 **Automated Tests** — pytest suite covering auth, CRUD, validation, and edge cases
- 📖 **Auto-generated API docs** — Swagger UI at `/docs`, ReDoc at `/redoc`
- ⚡ **Pydantic v2 validation** — strict input validation on every endpoint

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111 |
| Language | Python 3.11+ |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + Passlib (bcrypt) |
| Testing | Pytest + HTTPX |
| Containerization | Docker + Docker Compose |

---

## 📁 Project Structure

```
inventory-api/
├── app/
│   ├── main.py                  # FastAPI application, CORS, router setup
│   ├── core/
│   │   ├── config.py            # Settings loaded from environment variables
│   │   ├── security.py          # JWT creation/decoding, password hashing
│   │   └── exceptions.py        # Custom HTTP exception classes
│   ├── db/
│   │   ├── base.py              # SQLAlchemy declarative base
│   │   └── session.py           # Engine, SessionLocal, get_db dependency
│   ├── models/
│   │   ├── user.py              # User ORM model
│   │   ├── category.py          # Category ORM model
│   │   └── product.py           # Product ORM model (with stock constraints)
│   ├── schemas/
│   │   ├── user.py              # User Pydantic schemas
│   │   ├── auth.py              # Token and login schemas
│   │   ├── category.py          # Category Pydantic schemas
│   │   └── product.py           # Product Pydantic schemas (with StockUpdate)
│   ├── crud/
│   │   ├── user.py              # User database operations
│   │   ├── category.py          # Category database operations
│   │   └── product.py           # Product database operations (with filters)
│   ├── services/
│   │   ├── auth.py              # Auth logic, JWT deps, get_current_user
│   │   └── inventory.py         # Stock adjustment business logic
│   └── api/
│       └── routes/
│           ├── auth.py          # /auth endpoints (register, login, me)
│           ├── users.py         # /users endpoints
│           ├── categories.py    # /categories endpoints
│           ├── products.py      # /products endpoints + stock
│           └── health.py        # /health check
├── tests/
│   ├── conftest.py              # Fixtures: DB, client, users, tokens
│   ├── test_auth.py             # Auth endpoint tests
│   ├── test_products.py         # Product CRUD + stock tests
│   └── test_categories_users.py # Category and user management tests
├── alembic/
│   ├── env.py                   # Alembic migration environment
│   └── versions/
│       └── 001_initial_migration.py
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh                # Waits for DB, runs migrations, starts server
├── requirements.txt
├── pytest.ini
├── alembic.ini
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Option 1: Docker (Recommended)

The fastest way to get everything running — no need to install PostgreSQL or configure anything.

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/inventory-api.git
cd inventory-api
```

**2. Copy the environment file**

```bash
cp .env.example .env
```

> Edit `.env` if you want to change passwords or the secret key (recommended for production).

**3. Start the stack**

```bash
docker-compose up --build
```

That's it. The API will be live at **http://localhost:8000**.

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/api/v1/health

**4. Stop the stack**

```bash
docker-compose down
```

To also remove the database volume:

```bash
docker-compose down -v
```

---

### Option 2: Local Development

**Prerequisites:** Python 3.11+, PostgreSQL running locally.

**1. Clone and create a virtual environment**

```bash
git clone https://github.com/yourusername/inventory-api.git
cd inventory-api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment**

```bash
cp .env.example .env
# Edit .env with your local PostgreSQL credentials
```

**4. Create the database**

```bash
psql -U postgres -c "CREATE USER inventory_user WITH PASSWORD 'inventory_pass';"
psql -U postgres -c "CREATE DATABASE inventory_db OWNER inventory_user;"
```

**5. Run migrations**

```bash
alembic upgrade head
```

**6. Start the server**

```bash
uvicorn app.main:app --reload
```

---

## 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | Full PostgreSQL connection string |
| `SECRET_KEY` | — | JWT signing secret (min 32 chars, keep it secret) |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime in minutes |
| `DEBUG` | `false` | Enable debug mode |
| `POSTGRES_USER` | `inventory_user` | PostgreSQL username (Docker) |
| `POSTGRES_PASSWORD` | `inventory_pass` | PostgreSQL password (Docker) |
| `POSTGRES_DB` | `inventory_db` | PostgreSQL database name (Docker) |

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Register a new user |
| `POST` | `/api/v1/auth/login` | Public | Login and receive JWT token |
| `GET` | `/api/v1/auth/me` | 🔒 User | Get current user profile |

> **Note:** The very first registered user automatically receives the `admin` role.

### Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/users/` | 🛡️ Admin | List all users |
| `GET` | `/api/v1/users/{id}` | 🔒 User | Get user (own profile or admin) |
| `PATCH` | `/api/v1/users/{id}` | 🔒 User | Update user (own profile or admin) |
| `PATCH` | `/api/v1/users/{id}/role` | 🛡️ Admin | Change user role |
| `DELETE` | `/api/v1/users/{id}` | 🛡️ Admin | Deactivate user account |

### Categories

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/categories/` | 🔒 User | List all categories |
| `POST` | `/api/v1/categories/` | 🛡️ Admin | Create a category |
| `GET` | `/api/v1/categories/{id}` | 🔒 User | Get a category |
| `PATCH` | `/api/v1/categories/{id}` | 🛡️ Admin | Update a category |
| `DELETE` | `/api/v1/categories/{id}` | 🛡️ Admin | Delete a category |

### Products

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/products/` | 🔒 User | List products (paginated, searchable) |
| `POST` | `/api/v1/products/` | 🛡️ Admin | Create a product |
| `GET` | `/api/v1/products/low-stock` | 🔒 User | List low-stock products |
| `GET` | `/api/v1/products/{id}` | 🔒 User | Get a product |
| `PATCH` | `/api/v1/products/{id}` | 🛡️ Admin | Update a product |
| `DELETE` | `/api/v1/products/{id}` | 🛡️ Admin | Delete a product |
| `POST` | `/api/v1/products/{id}/stock` | 🛡️ Admin | Adjust stock quantity |

### Query Parameters for `GET /api/v1/products/`

| Parameter | Type | Description |
|---|---|---|
| `page` | int | Page number (default: 1) |
| `size` | int | Results per page (default: 20, max: 100) |
| `search` | string | Search by name or SKU |
| `category_id` | int | Filter by category |
| `low_stock_only` | bool | Show only low-stock items |

---

## 🧪 Running Tests

Tests use SQLite in-memory — **no PostgreSQL required** to run the test suite.

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_auth.py -v

# Run a specific test
pytest tests/test_products.py::TestStockManagement::test_cannot_go_below_zero -v
```

---

## 📬 Example Requests

### Register & Login

```bash
# Register (first user = admin)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "SecurePass1",
    "full_name": "Admin User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SecurePass1"}'

# Response:
# { "access_token": "eyJ0eXAi...", "token_type": "bearer" }
```

### Create a Category

```bash
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Electronics", "description": "Electronic devices and accessories"}'
```

### Create a Product

```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mechanical Keyboard",
    "sku": "KB-MX-001",
    "price": "129.99",
    "stock_quantity": 75,
    "low_stock_threshold": 10,
    "category_id": 1
  }'
```

### Adjust Stock

```bash
# Add 50 units
curl -X POST http://localhost:8000/api/v1/products/1/stock \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 50, "reason": "Restocking from supplier"}'

# Remove 10 units (sale / dispatch)
curl -X POST http://localhost:8000/api/v1/products/1/stock \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": -10, "reason": "Order #4521 fulfilled"}'
```

### List Products with Filters

```bash
# Search + paginate
curl "http://localhost:8000/api/v1/products/?search=keyboard&page=1&size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Only low-stock items
curl "http://localhost:8000/api/v1/products/low-stock" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🏗️ Architecture Decisions

**Why this structure?**  
The project follows a layered architecture: routes handle HTTP concerns, services hold business logic, crud handles database operations, and models/schemas define the data shapes. This separation keeps each layer thin, testable, and replaceable.

**Why SQLite for tests?**  
Using an in-memory SQLite database in tests means zero external dependencies — anyone can clone the repo and run `pytest` instantly. The test schema is created fresh for each test function, ensuring complete isolation.

**Why Alembic?**  
Migrations are version-controlled and reproducible. The `entrypoint.sh` runs `alembic upgrade head` automatically on startup, so the database schema is always in sync.

**First user = admin?**  
A pragmatic bootstrapping approach. The first registered user gets admin rights, which lets you immediately set up the system without manual database seeds. In production, you could lock down the register endpoint after initial setup.

---

## 📄 License

MIT — free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change. Please make sure tests pass before submitting a PR.

```bash
pytest --cov=app
```
