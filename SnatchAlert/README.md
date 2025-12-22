# SnatchAlert - Crime Reporting & IMEI Tracking Backend

A comprehensive Django REST Framework backend for crime reporting and stolen device tracking with real-time IMEI alerts.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone and navigate to project**
```bash
git clone <repository-url>
cd SnatchAlertBackend/SnatchAlert
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup database**
```bash
python manage.py migrate
python manage.py seed_data  # Creates test data
```

5. **Run development server**
```bash
python manage.py runserver
```

🎉 **Server running at:** http://127.0.0.1:8000/

## 📱 Key Features

### 🔐 Email-Based Authentication
- Pure email login (no username required)
- JWT token authentication
- Password reset with email verification
- Profile management

### 📞 IMEI Stolen Device Alerts
- Register stolen phone IMEIs
- Real-time alerts when stolen IMEI is checked
- Email notifications to device owners
- Check history and IP tracking

### 🚨 Crime Reporting
- Anonymous incident reporting
- File uploads (FIR documents, images)
- Advanced filtering and search
- Geo-location support

### 📊 Analytics & Insights
- Crime heatmaps
- Area safety scores
- Statistics dashboard
- Community safety tips

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register with email
- `POST /api/auth/login/` - Login with email
- `GET /api/auth/profile/` - Get user profile

### IMEI Tracking
- **Automatic Registration:** IMEIs are automatically registered when creating incident reports for stolen phones
- `POST /api/reports/imei/check/` - Check IMEI status
- `GET /api/reports/imei/alerts/` - Get device alerts

### Crime Reports
- `GET /api/reports/incidents/` - List incidents
- `POST /api/reports/incidents/create/` - Report incident
- `GET /api/reports/heatmap/` - Crime heatmap data

**📚 Complete API Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 🧪 Test Data

After running `python manage.py seed_data`, use these test accounts:

- **Admin:** `admin@snatchalert.com` / `admin123`
- **Officer:** `officer@police.gov` / `police123`  
- **User:** `john@example.com` / `user123`

## 🛠️ Development Tools

- **API Documentation:** http://127.0.0.1:8000/api/docs/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Postman Collection:** `SnatchAlert_API_Collection.json`

## 📊 Database Schema

Uses optimized snowflake schema design:

- **IncidentFact** - Central crime incidents table
- **LocationDim** - Geographic data
- **VictimDim** - Victim information  
- **IMEIRegistry** - Stolen device tracking
- **StolenDeviceAlert** - Real-time alerts

## 🔒 Security Features

- JWT token authentication
- Role-based access control (User/Authority/Admin)
- Input validation and sanitization
- IP address logging for IMEI checks
- Secure file upload handling

## 🌐 Production Deployment

1. **Environment Setup**
```bash
cp .env.example .env
# Configure production settings in .env
```

2. **Database Migration**
```bash
python manage.py migrate --settings=SnatchAlert.settings_production
```

3. **Collect Static Files**
```bash
python manage.py collectstatic
```

## 📈 Technology Stack

- **Backend:** Django 5.2.8 + Django REST Framework 3.15.2
- **Database:** PostgreSQL (SQLite for development)
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Documentation:** drf-yasg (Swagger/OpenAPI)
- **Filtering:** django-filter
- **Image Processing:** Pillow

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For questions or issues:
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API reference
- Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for complete project overview
- Open an issue in the repository

## 📄 License

This project is licensed under the MIT License.

---

**Built for community safety** 🛡️

**Ready for mobile app integration!** 📱