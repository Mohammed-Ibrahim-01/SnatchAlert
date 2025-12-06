# ✅ SnatchAlert Setup Complete!

Your SnatchAlert backend is now up and running!

## 🎉 Server Status

**Server URL:** http://127.0.0.1:8000/

The development server is currently running and ready to accept requests.

## 📍 Access Points

### 1. API Documentation (Swagger)
**URL:** http://127.0.0.1:8000/api/docs/

Interactive API documentation where you can:
- Browse all endpoints
- Test API calls directly
- View request/response schemas
- Try authentication

### 2. Admin Panel
**URL:** http://127.0.0.1:8000/admin/

Login with admin credentials to:
- Manage all data
- View incidents, IMEIs, alerts
- Moderate content
- Manage users

### 3. API Base URL
**URL:** http://127.0.0.1:8000/api/

All API endpoints are available under this base URL.

## 🔑 Test Credentials

### Admin User (Full Access)
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** Admin
- **Access:** Full system access

### Authority User (Police/Law Enforcement)
- **Username:** `police_officer`
- **Password:** `police123`
- **Role:** Authority
- **Access:** Can manage alerts, view all data

### Regular User
- **Username:** `john_doe`
- **Password:** `user123`
- **Role:** User
- **Access:** Can report incidents, check IMEIs

## 🚀 Quick API Tests

### 1. Login and Get Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"john_doe\", \"password\": \"user123\"}"
```

### 2. Check IMEI Status
```bash
curl -X POST http://127.0.0.1:8000/api/reports/imei/check/ \
  -H "Content-Type: application/json" \
  -d "{\"imei\": \"123456789012345\"}"
```

### 3. View Crime Heatmap
```bash
curl http://127.0.0.1:8000/api/reports/heatmap/?days=30&city=Lahore
```

### 4. Get Safety Tips
```bash
curl http://127.0.0.1:8000/api/core/safety-tips/
```

## 📊 Sample Data Loaded

The database has been populated with:
- ✅ 3 test users (admin, authority, regular user)
- ✅ 5 incident types (Mobile Snatching, Vehicle Theft, etc.)
- ✅ 6 locations across Pakistan (Lahore, Karachi, Islamabad, Peshawar)
- ✅ 3 sample incidents
- ✅ 2 IMEI records
- ✅ 2 area alerts
- ✅ 3 safety tips

## 📱 API Endpoints Available

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `GET /api/auth/profile/` - Get user profile

### Incidents
- `GET /api/reports/incidents/` - List all incidents
- `POST /api/reports/incidents/create/` - Create incident
- `GET /api/reports/incidents/{id}/` - Get incident details
- `PATCH /api/reports/incidents/{id}/update/` - Update incident
- `GET /api/reports/incidents/my/` - My incidents

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

## 🛠️ Next Steps

### For Testing
1. Visit http://127.0.0.1:8000/api/docs/ for interactive API testing
2. Import `SnatchAlert_API_Collection.json` into Postman
3. Login with test credentials and explore the API

### For Development
1. Check `README.md` for complete documentation
2. Review `API_DOCUMENTATION.md` for detailed API reference
3. See `QUICKSTART.md` for development tips

### For Mobile App Integration
1. Use base URL: `http://127.0.0.1:8000/api/`
2. Implement JWT authentication
3. Follow API documentation for endpoints
4. Handle file uploads for FIR and images

## 📚 Documentation Files

- **README.md** - Complete project documentation
- **QUICKSTART.md** - Quick start guide
- **API_DOCUMENTATION.md** - Detailed API reference
- **PROJECT_SUMMARY.md** - Technical overview
- **DEPLOYMENT.md** - Production deployment guide

## 🔧 Common Commands

### Stop the server
Press `CTRL+C` in the terminal

### Restart the server
```bash
python manage.py runserver
```

### Create a new superuser
```bash
python manage.py createsuperuser
```

### Reset database and reload seed data
```bash
python manage.py flush
python manage.py seed_data
```

### Run tests
```bash
python manage.py test
```

## 💡 Tips

1. **Use Swagger UI** - The easiest way to test the API is through the Swagger interface at `/api/docs/`

2. **Check Admin Panel** - Login to `/admin/` to see all the data and manage it visually

3. **Test with Postman** - Import the provided Postman collection for comprehensive API testing

4. **Read the Docs** - All endpoints are documented with examples in `API_DOCUMENTATION.md`

## ⚠️ Important Notes

- This is a **development server** - not for production use
- Database is PostgreSQL - make sure it's running
- All passwords are for testing only - change them in production
- CORS is enabled for all origins (development only)

## 🎯 What's Working

✅ Complete snowflake schema database
✅ JWT authentication with role-based access
✅ Crime incident reporting (anonymous & authenticated)
✅ IMEI tracking system
✅ Crime heatmaps and analytics
✅ Area safety scores
✅ Location-based alerts
✅ Community safety tips
✅ File uploads (FIR documents, images)
✅ Advanced filtering and search
✅ Pagination
✅ Swagger documentation
✅ Admin panel

## 🆘 Need Help?

- **API Issues:** Check Swagger docs at `/api/docs/`
- **Database Issues:** Verify PostgreSQL is running
- **Authentication Issues:** Check JWT token in Authorization header
- **General Help:** See README.md or API_DOCUMENTATION.md

---

**🎉 Congratulations! Your SnatchAlert backend is ready for mobile app integration!**

Visit http://127.0.0.1:8000/api/docs/ to start exploring the API.
