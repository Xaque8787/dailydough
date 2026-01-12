# Docker Deployment Guide

This guide explains how to deploy and manage the application using Docker.

## Overview

The application uses a containerized deployment system with:

- **Multi-stage Docker builds** for optimized image size
- **Automated database migrations** on container startup
- **GitHub Actions** for CI/CD
- **Health checks** for container monitoring
- **Volume persistence** for database data

## Quick Start

### Local Development

Build and run locally using Docker Compose:

```bash
docker-compose -f docker-compose.local.yml up --build
```

The application will be available at `http://localhost:5710`

### Production Deployment

1. Update the `docker-compose.yml` file with your GitHub username and app name:

```yaml
image: ghcr.io/YOUR_GITHUB_USERNAME/YOUR_APP_NAME:latest
```

2. Set your secret key (optional, but recommended):

```bash
export SECRET_KEY="your-secure-random-secret-key"
```

3. Pull and run the latest image:

```bash
docker-compose pull
docker-compose up -d
```

## Version Management

The Docker image version is controlled by the `.dockerversion` file in the project root.

### To Deploy a New Version:

1. Update `.dockerversion` with the new version number:

```bash
echo "0.0.2" > .dockerversion
```

2. Commit and push to trigger the build:

```bash
git add .dockerversion
git commit -m "Bump version to 0.0.2"
git push
```

3. GitHub Actions will automatically build and push the new image with two tags:
   - `latest`
   - `0.0.2` (the version number)

## Migration System

### How It Works

The application includes an automated migration system that runs on every container startup:

1. **Container starts** → Entrypoint script checks if database exists
2. **If database exists** → Runs `run_migrations.py`
3. **Migration runner** → Scans `migrations/` directory for new migrations
4. **Executes migrations** → Runs pending migrations in alphabetical order
5. **Archives migrations** → Moves completed migrations to `migrations/old/`
6. **Application starts** → After migrations complete successfully

### Creating a New Migration

1. Create a new migration file in the `migrations/` directory:

**Format:** `YYYYMMDD_description.py`

**Example:** `20240115_add_user_preferences.py`

```python
def upgrade(conn):
    cursor = conn.cursor()

    cursor.execute("""
        ALTER TABLE users ADD COLUMN preferences TEXT DEFAULT '{}'
    """)

    conn.commit()
```

2. Rebuild and restart the container:

```bash
docker-compose down
docker-compose up --build
```

The migration will run automatically on startup.

### Migration Best Practices

- Use `IF NOT EXISTS` for safety
- Keep migrations focused and small
- Test migrations locally first
- Never modify already-applied migrations
- Use descriptive filenames

See [migrations/README.md](migrations/README.md) for detailed migration documentation.

## Docker Commands

### Local Development

```bash
# Build and start
docker-compose -f docker-compose.local.yml up --build

# Run in background
docker-compose -f docker-compose.local.yml up -d

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Stop containers
docker-compose -f docker-compose.local.yml down

# Rebuild without cache
docker-compose -f docker-compose.local.yml build --no-cache
```

### Production Deployment

```bash
# Pull latest image
docker-compose pull

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Check status
docker-compose ps
```

## Environment Variables

The following environment variables can be configured:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-this-in-production` | JWT secret key for authentication |
| `DATABASE_URL` | `sqlite:///app/data/database.db` | Database connection string |
| `TZ` | `America/New_York` | Timezone for the application |

### Setting Environment Variables

**Option 1: Environment file**

Create a `.env` file in the project root:

```bash
SECRET_KEY=your-super-secret-key-here
TZ=America/Chicago
```

**Option 2: Docker Compose override**

Edit `docker-compose.yml` and update the `environment` section.

**Option 3: Command line**

```bash
SECRET_KEY=mysecret docker-compose up -d
```

## Data Persistence

The database is stored in a Docker volume mounted at `./data:/app/data`.

### Backup Database

```bash
# Copy database from container
docker cp management-system:/app/data/database.db ./backup-$(date +%Y%m%d).db
```

### Restore Database

```bash
# Stop the container
docker-compose down

# Replace database file
cp backup-20240115.db ./data/database.db

# Start container
docker-compose up -d
```

## GitHub Actions CI/CD

The repository includes automated Docker builds using GitHub Actions.

### Triggers

Builds are triggered on:
- Pushes to `main` or `master` branch
- Changes to Docker-related files (Dockerfile, requirements.txt, etc.)
- Manual workflow dispatch

### Setup

1. Enable GitHub Actions in your repository
2. Ensure GitHub Packages is enabled (it's enabled by default)
3. Push to trigger a build

The workflow automatically:
- Builds for both `linux/amd64` and `linux/arm64`
- Pushes to GitHub Container Registry (ghcr.io)
- Tags with both `latest` and the version from `.dockerversion`
- Uses build caching for faster builds

### Accessing Built Images

Images are available at:
```
ghcr.io/YOUR_USERNAME/YOUR_REPO_NAME:latest
ghcr.io/YOUR_USERNAME/YOUR_REPO_NAME:0.0.1
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs
```

### Database errors

Check if data directory has correct permissions:
```bash
ls -la ./data
```

### Migration failures

View migration logs:
```bash
docker-compose logs | grep -A 20 "Running migrations"
```

Manually run migrations:
```bash
docker-compose exec app python /app/run_migrations.py
```

### Health check failing

Test the health check endpoint:
```bash
curl http://localhost:5710/
```

Check container health:
```bash
docker inspect --format='{{.State.Health.Status}}' management-system
```

## Security Considerations

1. **Always change the SECRET_KEY in production**
2. **Never commit `.env` files with secrets**
3. **Use strong, random secret keys** (generate with `openssl rand -hex 32`)
4. **Restrict container registry access** to authorized users
5. **Keep Docker images updated** by rebuilding regularly

## Performance Tuning

### Adjust Worker Count

Edit the `CMD` in `Dockerfile`:

```dockerfile
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "8", "-b", "0.0.0.0:5710"]
```

Recommended workers: `(2 x CPU cores) + 1`

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
```

## Support

For more information, see:
- [Migrations README](migrations/README.md)
- [Dockerfile](Dockerfile)
- [GitHub Actions Workflow](.github/workflows/docker-build.yml)
