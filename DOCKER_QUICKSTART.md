# Docker Quick Start Guide

## 5-Minute Setup

### Option 1: Automated Setup (Recommended)

```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

Follow the prompts to set up for either local development or production.

### Option 2: Manual Setup

**Local Development:**
```bash
docker-compose -f docker-compose.local.yml up --build -d
```

**Production:**
```bash
# Update docker-compose.yml with your GitHub username and app name
docker-compose pull
docker-compose up -d
```

## Access Your Application

Open your browser to: **http://localhost:5710**

## Essential Commands

### Local Development

| Action | Command |
|--------|---------|
| Start | `docker-compose -f docker-compose.local.yml up -d` |
| Stop | `docker-compose -f docker-compose.local.yml down` |
| Rebuild | `docker-compose -f docker-compose.local.yml up --build -d` |
| View Logs | `docker-compose -f docker-compose.local.yml logs -f` |
| Restart | `docker-compose -f docker-compose.local.yml restart` |

### Production

| Action | Command |
|--------|---------|
| Start | `docker-compose up -d` |
| Stop | `docker-compose down` |
| Update | `docker-compose pull && docker-compose up -d` |
| View Logs | `docker-compose logs -f` |
| Restart | `docker-compose restart` |

## How Migrations Work

1. Create migration file: `migrations/YYYYMMDD_description.py`
2. Restart container: `docker-compose restart`
3. Migration runs automatically on startup
4. Completed migration moves to `migrations/old/`

Example migration:
```python
def upgrade(conn):
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE users ADD COLUMN new_field TEXT")
    conn.commit()
```

## Deploying New Versions

1. Update version:
   ```bash
   echo "0.0.2" > .dockerversion
   ```

2. Commit and push:
   ```bash
   git add .dockerversion
   git commit -m "Bump version to 0.0.2"
   git push
   ```

3. Wait for GitHub Actions to build (check Actions tab)

4. Update production:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## Troubleshooting

**Container won't start:**
```bash
docker-compose logs
```

**Database issues:**
```bash
# Check data directory
ls -la ./data

# Run migrations manually
docker-compose exec app python /app/run_migrations.py
```

**Health check failing:**
```bash
curl http://localhost:5710/
```

**Reset everything:**
```bash
docker-compose down
rm -rf data/*.db
docker-compose up -d
```

## Important Files

- `.dockerversion` - Version number for Docker images
- `docker-compose.yml` - Production configuration
- `docker-compose.local.yml` - Local development configuration
- `.env` - Environment variables (create if missing)
- `migrations/` - Database migrations
- `data/` - Database storage (persisted)

## Security

**Production Checklist:**
- [ ] Set a strong `SECRET_KEY` in `.env`
- [ ] Never commit `.env` to git
- [ ] Update `docker-compose.yml` with your registry path
- [ ] Restrict access to GitHub Container Registry
- [ ] Regularly update Docker images

Generate a secure key:
```bash
openssl rand -hex 32
```

## Need Help?

See detailed documentation:
- [DOCKER.md](DOCKER.md) - Complete Docker guide
- [migrations/README.md](migrations/README.md) - Migration system
- [.github/workflows/docker-build.yml](.github/workflows/docker-build.yml) - CI/CD workflow
