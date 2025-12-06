# SnatchAlert - Quick Start Guide

Get the SnatchAlert backend up and running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Step-by-Step Setup

### 1. Database Setup

Open PostgreSQL and create the database:

```sql
CREATE DATABASE snatchalertdb;
CREATE USER snatch_user WITH PASSWORD 'SnatchAlert123';
ALTER ROLE snatch_user SET client_encoding TO 'utf8';
ALTER ROLE snatch_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE snatch_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE snatchalertdb TO snatch_user;
```

### 2. Install Dependencies

```bash
cd SnatchAlert
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Load Sample Data

```bash
python manage.py seed_data
```

This creates:
- 3 test users (admin, police officer, regular user)
- Sample incidents, locations, and stolen items
- IMEI records and area alerts
- Safety tips

### 5. Start the Server

```bash
python manage.py runserver
```

## Access the Application

- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/
- **API Base URL**: http://localhost:8000/api/

## Test Credentials

After running seed_data, use these credentials:

### Admin User
- Username: `admin`
- Password: `admin123`
- Role: Admin (full access)

### Authority User (Police)
- Username: `police_officer`
- Password: `police123`
- Role: Authority (can manage alerts)

### Regular User
- Username: `john_doe`
- Password: `user123`
- Role: User (can report incidents)

## Quick API Test

### 1. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "user123"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Get Your Profile

```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. List Incidents

```bash
curl -X GET http://localhost:8000/api/reports/incidents/
```

### 4. Check IMEI Status

```bash
curl -X POST http://localhost:8000/api/reports/imei/check/ \
  -H "Content-Type: application/json" \
  -d '{"imei": "123456789012345"}'
```

### 5. Get Crime Heatmap

```bash
curl -X GET "http://localhost:8000/api/reports/heatmap/?days=30&city=Lahore"
```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/api/docs/ for interactive documentation
2. **Create an Incident**: Use the Swagger UI to test incident creation
3. **Check Analytics**: View crime heatmaps and safety scores
4. **Admin Panel**: Login to http://localhost:8000/admin/ with admin credentials

## Common Issues

### Database Connection Error
- Make sure PostgreSQL is running
- Verify database credentials in `settings.py`
- Check if the database exists

### Migration Errors
```bash
python manage.py makemigrations --empty core
python manage.py migrate --fake-initial
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## API Endpoints Overview

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT token
- `GET /api/auth/profile/` - Get user profile

### Incidents
- `GET /api/reports/incidents/` - List all incidents
- `POST /api/reports/incidents/create/` - Create incident
- `GET /api/reports/incidents/{id}/` - Get incident details
- `PATCH /api/reports/incidents/{id}/update/` - Update incident

### IMEI Tracking
- `POST /api/reports/imei/register/` - Register stolen IMEI
- `POST /api/reports/imei/check/` - Check IMEI status
- `GET /api/reports/imei/list/` - List all IMEIs (admin)

### Analytics
- `GET /api/reports/heatmap/` - Crime heatmap data
- `GET /api/reports/safety-score/` - Area safety scores
- `GET /api/reports/statistics/` - Crime statistics

### Alerts & Tips
- `GET /api/reports/alerts/` - List active alerts
- `GET /api/core/safety-tips/` - List safety tips
- `POST /api/core/feedback/` - Submit feedback

## Development Tips

### Enable Debug Toolbar (Optional)
```bash
pip install django-debug-toolbar
```

### Create Custom Superuser
```bash
python manage.py createsuperuser
```

### Clear Database and Reseed
```bash
python manage.py flush
python manage.py seed_data
```

### Run Tests
```bash
python manage.py test
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in settings
2. Configure proper `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Set up proper database (not SQLite)
5. Configure static/media file serving
6. Enable HTTPS
7. Set up email backend for password reset

## Support

For issues or questions:
- Check the main README.md
- Visit API documentation at /api/docs/
- Review Django logs for errors

---

Happy coding! 🚀
