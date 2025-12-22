# Deployment Guide

## Problem Solved
This guide solves the git pull conflict issue on PythonAnywhere by using environment-specific configuration files instead of hardcoded settings.

## Local Development Setup

1. **Environment File**: Your local `.env` file is already configured for development
2. **Database**: Uses PostgreSQL locally
3. **Debug Mode**: Enabled for development

## PythonAnywhere Production Deployment

### Step 1: Initial Setup on PythonAnywhere

1. **Clone/Pull your repository** (this will now work without conflicts):
   ```bash
   cd ~/mysite
   git pull origin main
   ```

2. **Create production environment file**:
   ```bash
   cp .env.production .env
   ```

3. **Edit the production .env file** with your actual values:
   ```bash
   nano .env
   ```
   
   Update these values:
   - `SECRET_KEY`: Generate a new secret key for production
   - `ALLOWED_HOSTS`: Add your PythonAnywhere domain
   - `DB_NAME`: Your MySQL database name (usually `yourusername$dbname`)
   - `DB_USER`: Your PythonAnywhere username
   - `DB_PASSWORD`: Your MySQL password
   - `DB_HOST`: Your MySQL host (usually `yourusername.mysql.pythonanywhere-services.com`)
   - `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`: Your email credentials

### Step 2: Database Configuration

If switching from PostgreSQL to MySQL on PythonAnywhere:

1. **Install MySQL client**:
   ```bash
   pip install mysqlclient
   ```

2. **Update requirements.txt** (add to your local repo and push):
   ```
   mysqlclient==2.2.0
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

### Step 3: Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 4: Reload Web App

Go to your PythonAnywhere web tab and click "Reload".

## Future Deployments

Now you can easily deploy updates:

1. **Local development**: Make changes, test locally
2. **Push to GitHub**: `git push origin main`
3. **Deploy to PythonAnywhere**:
   ```bash
   cd ~/mysite
   git pull origin main
   python manage.py migrate  # if there are new migrations
   python manage.py collectstatic --noinput  # if static files changed
   ```
4. **Reload web app** from PythonAnywhere dashboard

## Environment Files Summary

- `.env` - Local development (not tracked in git)
- `.env.example` - Template for new developers
- `.env.production` - Template for production deployment
- `settings.py` - Now uses environment variables instead of hardcoded values

## Benefits

✅ No more git pull conflicts
✅ Secure production secrets
✅ Easy environment switching
✅ Team-friendly development setup
✅ Production-ready configuration