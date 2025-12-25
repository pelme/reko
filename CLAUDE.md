# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Reko is a Django-based webapp that enables customers to buy food directly from local farmers. The application handles producer storefronts, product listings, shopping carts, and order management with pickup scheduling.

## Technology Stack

- **Python**: 3.13 (managed via uv)
- **Framework**: Django 5.2
- **UI Components**: htpy (Python-based HTML generation)
- **Database**: PostgreSQL
- **Type Checking**: mypy with strict mode and django-stubs
- **Linting**: ruff with specific rule sets (Pyflakes, pycodestyle, isort, flake8-bugbear, flake8-django, etc.)
- **Testing**: pytest with pytest-django and factory-boy

## Development Commands

### Setup
```bash
# Apply database migrations
uv run manage.py migrate

# Generate demo data and create test users (admin@example.com / password, producer@example.com / password)
uv run dev-db-generate --create-superuser
```

### Running the Application
```bash
# Start development server (accessible at http://localhost:8000/demo)
uv run manage.py runserver

# Run a single test file
uv run pytest reko/reko/models_test.py

# Run all tests
uv run pytest
```

### Code Quality
```bash
# Run linter
uv run ruff check

# Auto-fix linting issues
uv run ruff check --fix

# Format code
uv run ruff format

# Run type checker (targets reko/ directory only)
uv run mypy
```


## Architecture

### Settings Organization
Django settings are split into:
- `reko/settings/_base.py`: Shared configuration (database, installed apps, middleware, templates)
- `reko/settings/dev.py`: Development-specific settings
- `reko/settings/prod.py`: Production-specific settings

Default settings module: `reko.settings.dev`

### Core Models (reko/reko/models.py)

**User Model**: Custom user model (`AUTH_USER_MODEL = "reko.User"`) using email as username field. Supports many-to-many relationships with producers and rings. Implements custom permission system via `has_perm()` and `has_module_perms()`.

**Producer**: Represents farmers/producers. Key fields include `slug` (for URL generation), contact info, `color_palette` (for UI theming), and many-to-many relationship with pickups. Custom `generate_order_number()` method uses `select_for_update()` to prevent race conditions.

**Product**: Belongs to a producer. Stores VAT-inclusive pricing with separate `vat_factor` field. Uses imagekit for generating responsive image thumbnails (`card_thumbnail`).

**Ring**: Represents geographical distribution groups. Links producers to pickup locations.

**Pickup**: Scheduled pickup events with date, time range, and location. Can be published/unpublished.

**Order**: Customer orders linked to producer and pickup. Uses Django signing to generate order secrets for secure URL access. Implements email confirmation via `confirmation_email()` method.

**OrderProduct**: Individual line items in an order, denormalized to preserve historical pricing data.

### Key QuerySets
All main models have custom QuerySets with `filter_by_admin(user)` methods that scope results based on user permissions (superusers see all, regular users see only their assigned producers).

### Shopping Cart (reko/reko/cart.py)
Cookie-based cart implementation using query string serialization. Cart data is stored per-producer in cookies named `cart-{producer.slug}`.

### UI Components (reko/reko/components.py)
Uses htpy library for type-safe HTML generation in Python. All views return htpy elements that render to HTML. Components follow a functional approach with decorators like `@h.with_children`.

### URL Structure
- `/`: Homepage
- `/om-oss`: About page
- `/admin/`: Django admin
- `/{producer_slug}`: Producer storefront
- `/{producer_slug}/bestall`: Order/checkout page
- `/{producer_slug}/bestallning/{order_secret}`: Order confirmation (signed URL)

## Important Conventions

### Database
- Uses atomic requests (`ATOMIC_REQUESTS = True`) for transaction safety
- Database URL configured via `dj-database-url` (defaults to `postgres:///reko`)
- Timezone: Europe/Stockholm, Language: sv-se (Swedish)

### Sessions
Uses signed cookie-based sessions (`SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"`), no database-backed sessions.

### Testing
- Test files use `*_test.py` naming convention
- pytest configured with `--reuse-db` for faster test runs
- Uses factory-boy for test data generation

### Type Checking
- Strict mypy configuration enabled
- django-stubs plugin for Django-specific type checking
- Uses `django_stubs_ext.monkeypatch()` in settings

