# Puffshop — Backend

A merch shop backend built with Django + Django REST Framework. Serves a JSON API consumed by a separate React frontend ([puffshop-frontend](../../merch-shop-frontend)).

## Tech stack

- Python / Django 6.1
- Django REST Framework
- SQLite (dev database)
- django-cors-headers (allows the React frontend to call this API)
- python-decouple (loads secrets from `.env`, keeps them out of source control)
- Pillow (required for `ImageField` on Product)

## Project structure

```
puffshop/
├── products/    # Category, Product models + list API (with category filter)
├── orders/      # Order, OrderItem models + checkout API
├── contact/     # ContactMessage model + contact form API
└── puffshop/    # settings, root urls
```

## Setup

```bash
# 1. Clone and enter the project
git clone <this-repo-url>
cd puffshop

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# then open .env and fill in SECRET_KEY (any random string works for local dev)

# 5. Run migrations
python manage.py migrate

# 6. Create an admin login
python manage.py createsuperuser

# 7. Run the server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` to manage products and orders, or `http://127.0.0.1:8000/api/products/` to see the raw API.

## Running tests

```bash
python manage.py test
```

## Design decisions

- **No customer accounts.** Checkout is guest-only, collecting delivery details directly. This was a deliberate scope decision for a small shop — admin access (Django's built-in auth) is separate from any customer-facing login system, which doesn't exist.
- **Price/name snapshotting.** `OrderItem` stores `product_name` and `price` at the moment of purchase, rather than referencing the live `Product`. This means changing a product's price later never changes what a past order shows the customer paid.
- **Stock locking.** Order creation runs inside `transaction.atomic()` with `select_for_update()` on the relevant products, preventing two simultaneous checkouts from overselling the same stock.
- **Duplicate line aggregation.** If a checkout request contains the same product across multiple line items, quantities are summed and validated as one combined amount before any stock check — this avoids a race where each line individually passes validation but together they exceed available stock.

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/products/` | List all products. Optional `?category=<slug>` filter. |
| POST | `/api/orders/` | Create an order. Validates stock, snapshots price/name, decrements stock. |
| POST | `/api/contact/` | Submit a contact form message. |

### `POST /api/orders/` request body

```json
{
  "full_name": "Jane Doe",
  "phone": "+1 555 000 0000",
  "street_address": "123 Pastel Lane",
  "city": "Springfield",
  "zip_code": "62701",
  "items": [
    { "product_id": 1, "quantity": 2 }
  ]
}
```

## Environment variables

See `.env.example`. Required:

- `SECRET_KEY` — Django's cryptographic signing key. Never commit a real one.
- `DEBUG` — `True` for local development, `False` for anything resembling production.
- `ALLOWED_HOSTS` — comma-separated list of hosts Django will serve (e.g. `127.0.0.1,localhost`).
