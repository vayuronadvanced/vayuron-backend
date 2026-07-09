# VAYURON Backend — Django + DRF + PostgreSQL

Status: **scaffold only** — no application logic implemented yet.

## Stack (planned)
- Python 3.14.6
- Django (latest LTS-compatible at implementation time)
- Django REST Framework
- PostgreSQL
- Gunicorn (production WSGI server)
- Nginx (reverse proxy, static/media serving)

## Structure
- `config/` — Django project package (settings split by environment, root urls, wsgi/asgi)
- `apps/` — one Django app per domain: core, accounts, contacts, careers, blog,
  newsletter, quotations, uploads, analytics
- `requirements/` — split pip requirement files (base/development/production/testing)
- `static/`, `media/`, `templates/` — Django static/media/template roots
- `logs/` — application log output (gitignored)
- `scripts/` — backend automation scripts (management commands, deploy hooks)
- `tests/` — project-level test config (pytest.ini / conftest.py go here)

## Getting started (once implemented)
```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements/development.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## API contract
All frontend-backend communication happens exclusively over REST (JSON) under
`/api/v1/...`. The frontend never talks to PostgreSQL directly.
