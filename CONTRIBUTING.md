# Contributing to this project

## Development Setup

## uv/Python

uv is used to manage Python and dependencies.

1) Install [uv](https://docs.astral.sh/uv/getting-started/installation/):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Run the commands with `uv run`, such as:
```bash
uv run manage.py runserver
```

## Using direnv

You may use [direnv](https://direnv.net/) to automatically add all tools to the PATH. In that case, use `uv sync` to install all packages. You can then run `pytest`, `python manage.py ...` directly.

## Database Setup

Apply database migrations:
```bash
uv run manage.py migrate
```

Generate demo data and create test users:
```bash
dev-db-generate --create-superuser
```

This creates test users:
- Admin: admin@example.com / password
- Producer: producer@example.com / password

## Development Server

Run the development server:
```bash
python manage.py runserver
```

The application will be available at http://localhost:8000

## Code Quality Tools

### Linting and Type Checking

Run the linter:
```bash
ruff check
```

Run type checking:
```bash
mypy
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:
```bash
pre-commit install
```

## Testing

Run tests with pytest:
```bash
pytest
```

## Docker
The project includes a Dockerfile. It is intended to use in production, not in development.
