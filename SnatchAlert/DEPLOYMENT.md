# SnatchAlert - Deployment Guide

Complete guide for deploying SnatchAlert to production.

## Pre-Deployment Checklist

### 1. Environment Configuration

- [ ] Create `.env` file from `.env.example`
- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up database credentials
- [ ] Configure email settings
- [ ] Set up media/static file storage

### 2. Database Setup

- [ ] Create production PostgreSQL database
- [ ] Configure database user with proper permissions
- [ ] Set up database backups
- [ ] Configure connection pooling (optional)

### 3. Security

- [ ] Change all default passwords
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure security headers

### 4. Static & Media Files

- [ ] Configure static file serving
- [ ] Set up media file storage (S3/Cloud Storage)
- [ ] Configure CDN (optional)

### 5. Monitoring & Logging

- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up performance monitoring
- [ ] Configure health checks

## Deployment Options

### Option 1: Traditional Server (Ubuntu/Debian)

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv postgresql nginx -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
```

#### 2. Database Setup

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE snatchalertdb;
CREATE USER snatch_user WITH PASSWORD 'your_secure_password';
ALTER ROLE snatch_user SET client_encoding TO 'utf8';
ALTER ROLE snatch_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE snatch_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE snatchalertdb TO snatch_user;
\q
```

#### 3. Application Setup

```bash
# Create app directory
sudo mkdir -p /var/www/snatchalert
cd /var/www/snatchalert

# Clone repository
git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
nano .env
# Add your production settings

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

#### 4. Gunicorn Setup

Create `/etc/systemd/system/snatchalert.service`:

```ini
[Unit]
Description=SnatchAlert Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/snatchalert
Environment="PATH=/var/www/snatchalert/venv/bin"
ExecStart=/var/www/snatchalert/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/snatchalert/snatchalert.sock \
          SnatchAlert.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Start and enable service
sudo systemctl start snatchalert
sudo systemctl enable snatchalert
```

#### 5. Nginx Setup

Create `/etc/nginx/sites-available/snatchalert`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 20M;

    location /static/ {
        alias /var/www/snatchalert/staticfiles/;
    }

    location /media/ {
        alias /var/www/snatchalert/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/snatchalert/snatchalert.sock;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/snatchalert /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. SSL Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "SnatchAlert.wsgi:application"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=snatchalertdb
      - POSTGRES_USER=snatch_user
      - POSTGRES_PASSWORD=your_secure_password
    restart: always

  web:
    build: .
    command: gunicorn SnatchAlert.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    restart: always

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

#### 3. Deploy

```bash
# Build and start
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f
```

### Option 3: Cloud Platforms

#### Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create snatchalert

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your_secret_key

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.10 snatchalert

# Create environment
eb create snatchalert-env

# Deploy
eb deploy

# Set environment variables
eb setenv DEBUG=False SECRET_KEY=your_secret_key
```

#### DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build settings
3. Add PostgreSQL database
4. Set environment variables
5. Deploy

## Production Settings

### settings.py Updates

```python
import os
from decouple import config

# Security
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/snatchalert/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

## Post-Deployment

### 1. Verification

- [ ] Test all API endpoints
- [ ] Verify database connections
- [ ] Check static/media file serving
- [ ] Test file uploads
- [ ] Verify email sending
- [ ] Check SSL certificate
- [ ] Test authentication flow

### 2. Monitoring Setup

```bash
# Install monitoring tools
pip install sentry-sdk

# Add to settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

### 3. Backup Strategy

```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U snatch_user snatchalertdb > /backups/snatchalert_$DATE.sql
```

### 4. Performance Optimization

```python
# Install Redis for caching
pip install django-redis

# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Maintenance

### Regular Tasks

1. **Daily**
   - Monitor error logs
   - Check system resources
   - Review API usage

2. **Weekly**
   - Database backups
   - Security updates
   - Performance review

3. **Monthly**
   - Update dependencies
   - Review and optimize queries
   - Clean up old data

### Update Procedure

```bash
# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart snatchalert
sudo systemctl restart nginx
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check Gunicorn service status
   - Verify socket file permissions
   - Check Nginx configuration

2. **Database Connection Error**
   - Verify database credentials
   - Check PostgreSQL service
   - Review firewall rules

3. **Static Files Not Loading**
   - Run collectstatic
   - Check Nginx configuration
   - Verify file permissions

4. **File Upload Errors**
   - Check media directory permissions
   - Verify client_max_body_size in Nginx
   - Check disk space

### Logs Location

```bash
# Application logs
/var/log/snatchalert/

# Nginx logs
/var/log/nginx/access.log
/var/log/nginx/error.log

# Gunicorn logs
journalctl -u snatchalert

# PostgreSQL logs
/var/log/postgresql/
```

## Security Best Practices

1. **Keep secrets secure**
   - Use environment variables
   - Never commit .env file
   - Rotate keys regularly

2. **Database security**
   - Use strong passwords
   - Limit database access
   - Enable SSL connections

3. **API security**
   - Implement rate limiting
   - Use HTTPS only
   - Validate all inputs

4. **Server security**
   - Keep system updated
   - Configure firewall
   - Use SSH keys
   - Disable root login

## Support

For deployment issues:
- Check logs first
- Review documentation
- Contact: support@snatchalert.com

---

**Good luck with your deployment! 🚀**
