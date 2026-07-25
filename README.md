# VAYURON Advanced Systems — Backend

Django + Django REST Framework API powering the Vayuron Advanced Systems
website: authentication, contact enquiries, career applications, blog CMS,
newsletter subscriptions, quotation requests, and file uploads.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Scripts / Management Commands](#scripts--management-commands)
- [API](#api)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

This is the sole source of business logic and data persistence for the
Vayuron platform. The React frontend never talks to PostgreSQL directly —
every read/write goes through this REST API. Uploaded files (resumes,
images, certificates) are stored on disk (`MEDIA_ROOT`); PostgreSQL stores
only metadata and file paths.

## Features

- Token-based authentication and account management (`apps/accounts`) with
  email verification support.
- Contact form submission handling (`apps/contacts`).
- Career listings and job applications (`apps/careers`).
- Blog CMS — posts and categories (`apps/blog`).
- Newsletter subscription management (`apps/newsletter`).
- Quotation/enquiry requests (`apps/quotations`).
- Centralized file upload handling (`apps/uploads`).
- Site-wide analytics endpoints (`apps/analytics`).
- Shared/core utilities used across apps (`apps/core`).
- Environment-specific settings (development / testing / production) via
  `django-environ`.
- CORS configured for the Vite dev server and production frontend origins.

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | Django 5.2 |
| API | Django REST Framework 3.16 |
| Auth | djangorestframework-simplejwt (JWT) |
| Database | PostgreSQL (via `psycopg`) |
| Config | django-environ (`.env` file support) |
| CORS | django-cors-headers |
| Filtering | django-filter |
| Images | Pillow |
| Testing | pytest, pytest-django, pytest-cov, factory-boy |
| WSGI/ASGI server | Gunicorn (production), Django dev server (local) |

## Folder Structure

```
backend/
├── apps/
│   ├── accounts/        Authentication, user accounts, email verification
│   ├── analytics/        Site analytics endpoints
│   ├── blog/              Blog posts & categories (CMS)
│   ├── careers/           Job listings & applications
│   ├── contacts/          Contact form submissions
│   ├── core/                Shared/cross-app utilities
│   ├── newsletter/         Newsletter subscriptions
│   ├── quotations/         Quotation/enquiry requests
│   └── uploads/             Centralized file upload handling
│   (each app: migrations/, tests/, admin.py, apps.py, models.py,
│    permissions.py, serializers.py, urls.py, views.py)
├── config/
│   ├── settings/
│   │   ├── base.py         Shared settings
│   │   ├── development.py   Local dev overrides
│   │   ├── testing.py        Test-run overrides
│   │   └── production.py     Production overrides
│   ├── urls.py              Root URL routing (mounts each app under /api/)
│   ├── asgi.py
│   └── wsgi.py
├── requirements/
│   ├── base.txt             Core dependencies (all environments)
│   ├── development.txt       + dev tools
│   ├── testing.txt            + pytest stack
│   └── production.txt         + production-only packages
├── scripts/                 Backend-specific helper scripts
├── static/                  Collected static files (production)
├── media/                   Uploaded user files (gitignored)
├── templates/                Django templates (e.g. transactional emails)
├── logs/                     Application logs
├── manage.py
├── .env.example
└── .gitignore
```

## Setup

Prerequisites: **Python 3.11+**, **PostgreSQL 14+**, **pip/venv**.

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements/development.txt

cp .env.example .env      # then edit values (see below)

# Create the database (PostgreSQL must be running):
#   createdb vayuron_db   (or via psql/pgAdmin)

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

| Service | URL |
|---|---|
| API root | http://127.0.0.1:8000/api/ |
| Django Admin | http://127.0.0.1:8000/admin/ |

## Environment Variables

Copy `.env.example` to `.env` and fill in real values — **never commit the
actual `.env` file**.

| Variable | Purpose | Required? |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | Which settings module to load, e.g. `config.settings.development` | Yes |
| `DJANGO_SECRET_KEY` | Django's cryptographic secret key | Yes (always set a real value, even locally) |
| `DJANGO_DEBUG` | `True`/`False` — verbose error pages when `True` | Yes |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hostnames | Yes |
| `POSTGRES_DB` | Database name | Yes |
| `POSTGRES_USER` | Database user | Yes |
| `POSTGRES_PASSWORD` | Database password | Yes |
| `POSTGRES_HOST` | Database host, e.g. `localhost` | Yes |
| `POSTGRES_PORT` | Database port, default `5432` | Yes |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins allowed to call the API (e.g. the Vite dev URL) | Yes |
| `FRONTEND_URL` | Used for the "View site" link in Django Admin | Yes |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` | SMTP settings for transactional email (contact forms, newsletters) | Production only — dev uses the console email backend |
| `DEFAULT_FROM_EMAIL` | From-address for outgoing email | Production only |
| `MEDIA_ROOT` | Filesystem path for uploaded files | Yes |
| `STATIC_ROOT` | Filesystem path for collected static files | Yes (for `collectstatic` in production) |

## Scripts / Management Commands

Standard Django management commands via `python manage.py <command>`:

| Command | Purpose |
|---|---|
| `runserver` | Start the local dev server |
| `migrate` | Apply database migrations |
| `makemigrations` | Generate new migrations from model changes |
| `createsuperuser` | Create an admin account |
| `collectstatic` | Gather static files into `STATIC_ROOT` (production) |
| `test` | Run the Django test suite |

Backend-specific helper scripts live in `backend/scripts/`; cross-repo
scripts (e.g. database backup) live in the workspace-level
[`scripts/`](../scripts/README.md).

## API

All endpoints are namespaced by app under `/api/`:

| Base path | App | Covers |
|---|---|---|
| `/api/accounts/` | `apps.accounts` | Auth, registration, email verification, password reset |
| `/api/analytics/` | `apps.analytics` | Site analytics data |
| `/api/blog/` | `apps.blog` | Blog posts, categories |
| `/api/careers/` | `apps.careers` | Job listings, applications |
| `/api/contacts/` | `apps.contacts` | Contact form submissions |
| `/api/core/` | `apps.core` | Shared/site-wide endpoints |
| `/api/newsletter/` | `apps.newsletter` | Newsletter subscriptions |
| `/api/quotations/` | `apps.quotations` | Quotation/enquiry requests |
| `/api/uploads/` | `apps.uploads` | File upload handling |
| `/admin/` | Django Admin | Content/data management UI |
| `/__debug__/` | Django Debug Toolbar | Development only (`DEBUG=True`) |

Full request/response schemas: see [`../documentation/api/`](../documentation/README.md)
and the importable collection in [`../postman/`](../postman/README.md).

## Testing

```bash
pip install -r requirements/testing.txt
pytest
pytest --cov            # with coverage report
```

Each app has its own `tests/` directory. Prefer `factory-boy` factories
over hand-rolled fixtures for new tests.

## Deployment

Production runs via **Gunicorn** behind **Nginx** on a Hostinger VPS.

```bash
pip install -r requirements/production.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi:application -c ../deployment/gunicorn/gunicorn.conf.py
```

See [`../deployment/README.md`](../deployment/README.md) for the full Nginx
config, the Gunicorn systemd service file, SSL setup, and the VPS
initial-setup script.

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `django.db.utils.OperationalError: could not connect to server` | PostgreSQL isn't running, or `POSTGRES_*` values in `.env` are wrong. |
| CORS errors from the frontend | Add the frontend's origin (e.g. `http://localhost:5173`) to `CORS_ALLOWED_ORIGINS`. |
| `SECRET_KEY` errors on startup | `.env` is missing or `DJANGO_SECRET_KEY` isn't set — copy from `.env.example` and set a real value. |
| Migrations conflict / out of sync | Run `python manage.py makemigrations` then `python manage.py migrate`; if apps diverged, check for un-committed migration files. |
| Emails not sending in development | Expected — dev uses the console email backend by default; emails print to the terminal instead of sending. |
| 403/permission errors on file upload endpoints | Check `MEDIA_ROOT` exists and is writable by the process running Django. |

## Contributing

1. Branch off `main`; keep changes scoped to a single app where possible.
2. Follow PEP 8; run existing linters/formatters if configured.
3. Add or update tests for any model, serializer, or view change.
4. Run `python manage.py makemigrations --check` before committing to catch
   missing migrations.
5. Never commit `.env`, `media/`, `logs/`, or `.venv/` — all are gitignored.
6. Open a PR using the templates in the workspace root's `.github/`.
