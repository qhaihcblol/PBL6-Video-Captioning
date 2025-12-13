# Database Setup Guide

## Prerequisites

- PostgreSQL 14+ installed
- PostgreSQL service running

## Setup Steps

### 1. Start PostgreSQL (if not running)

```powershell
# Check if PostgreSQL is running
Get-Service postgresql*

# Start PostgreSQL if stopped
Start-Service postgresql-x64-14  # Replace with your version
```

### 2. Create Database

```powershell
# Connect to PostgreSQL
psql -U postgres

# In psql console:
CREATE DATABASE see_for_me;
CREATE USER see_for_me_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE see_for_me TO see_for_me_user;

# Exit psql
\q
```

### 3. Update .env file

```env
DATABASE_URL=postgresql://see_for_me_user:your_password_here@localhost:5432/see_for_me
```

Or use default postgres user:

```env
DATABASE_URL=postgresql://postgres:your_postgres_password@localhost:5432/see_for_me
```

### 4. Create First Migration

```powershell
# From backend directory with venv activated
alembic revision --autogenerate -m "Initial migration"
```

### 5. Apply Migration

```powershell
alembic upgrade head
```

### 6. Verify Tables Created

```powershell
psql -U postgres -d see_for_me

# In psql:
\dt  # List all tables - should see: users, videos, sample_videos, alembic_version
\d users  # Describe users table
```

## Alternative: Use Docker for PostgreSQL

```powershell
# Run PostgreSQL in Docker
docker run --name see-for-me-postgres `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=see_for_me `
  -p 5432:5432 `
  -d postgres:14

# Update .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/see_for_me
```

## Troubleshooting

### Connection refused

- Make sure PostgreSQL service is running
- Check port 5432 is not blocked by firewall
- Verify DATABASE_URL in .env is correct

### Permission denied

- Make sure user has proper privileges
- Try using `postgres` superuser for development

### Alembic errors

- Make sure all models are imported in `alembic/env.py`
- Check DATABASE_URL is accessible
- Run `alembic current` to check migration status
