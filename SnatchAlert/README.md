# SnatchAlert - Crime Reporting & Tracking System

A comprehensive backend API for a mobile crime reporting application with real-time tracking, heatmaps, IMEI registry, and community safety features.

## 🚀 Features

### Core Functionality
- **Crime Incident Reporting** - Report mobile snatching, vehicle theft, and other crimes
- **IMEI Tracking System** - Register and check stolen phone IMEIs
- **Crime Heatmaps** - Visualize crime hotspots with geo-location data
- **Area Safety Scores** - Calculate and display safety ratings for different areas
- **Community Safety Tips** - Share and view safety recommendations
- **Location-based Alerts** - Real-time alerts for high-crime areas
- **File Uploads** - Upload FIR documents and stolen item images

### Technical Features
- **JWT Authentication** - Secure token-based authentication
- **Role-based Access Control** - User, Admin, and Authority roles
- **Snowflake Schema** - Optimized database design with dimension tables
- **RESTful API** - Clean and well-documented API endpoints
- **Swagger Documentation** - Auto-generated API documentation
- **Filtering & Search** - Advanced filtering and search capabilities
- **Pagination** - Efficient data pagination
- **Anonymous Reporting** - Allow anonymous crime reports

## 📊 Database Schema (Snowflake Design)

### Fact Table
- **IncidentFact** - Core table storing crime incidents

### Dimension Tables
- **LocationDim** - Location information (province, city, district, neighborhood, coordinates)
- **VictimDim** - Victim information (name, age, gender, contact)
- **IncidentTypeDim** - Crime categories
- **StolenItemDim** - Stolen items (phones with IMEI, vehicles with license plates)

### Additional Tables
- **IMEIRegistry** - Stolen phone IMEI tracking
- **AreaAlert** - Location-based crime alerts
- **SafetyTip** - Community safety tips
- **UserFeedback** - User feedback and suggestions

## 🛠️ Technology Stack

- **Framework**: Django 5.2.8
- **API**: Django REST Framework 3.15.2
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Filtering**: django-filter
- **CORS**: django-cors-headers

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- pip

### Setup Steps

1. **Clone the repository**
```bash
cd SnatchAlert
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database**
Create a PostgreSQL database:
```sql
CREATE DATABASE snatchalertdb;
CREATE USER snatch_user WITH PASSWORD 'SnatchAlert123';
GRANT ALL PRIVILEGES ON DATABASE snatchalertdb TO snatch_user;
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Load seed data (optional)**
```bash
python manage.py shell < seed_data.py
```

8. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Access Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "password2": "SecurePass123",
  "phone": "+923001234567"
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Get User Profile
```http
GET /api/auth/profile/
Authorization: Bearer <access_token>
```

### Incident Reporting Endpoints

#### Create Incident
```http
POST /api/reports/incidents/create/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "occurred_at": "2024-12-05T14:30:00Z",
  "incident_type_name": "Mobile Snatching",
  "location_data": {
    "province": "Punjab",
    "city": "Lahore",
    "district": "Gulberg",
    "neighborhood": "MM Alam Road",
    "street_address": "Main Boulevard",
    "latitude": 31.5204,
    "longitude": 74.3587
  },
  "victim_data": {
    "name": "John Doe",
    "age": 28,
    "gender": "male",
    "phone_number": "+923001234567"
  },
  "stolen_item_data": {
    "item_type": "phone",
    "imei": "123456789012345",
    "phone_brand": "Samsung",
    "phone_model": "Galaxy S21",
    "value_estimate": 75000
  },
  "value_estimate": 75000,
  "fir_filed": true,
  "description": "Phone snatched at gunpoint",
  "is_anonymous": false
}
```

#### List Incidents (with filters)
```http
GET /api/reports/incidents/?city=Lahore&date_from=2024-12-01&status=reported
Authorization: Bearer <access_token>
```

#### Get My Incidents
```http
GET /api/reports/incidents/my/
Authorization: Bearer <access_token>
```

#### Update Incident
```http
PATCH /api/reports/incidents/{id}/update/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "investigating",
  "description": "Updated description"
}
```

### IMEI Tracking Endpoints

#### Register Stolen IMEI
```http
POST /api/reports/imei/register/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "imei": "123456789012345",
  "phone_brand": "Samsung",
  "phone_model": "Galaxy S21",
  "owner_name": "John Doe",
  "owner_contact": "+923001234567",
  "status": "stolen"
}
```

#### Check IMEI Status
```http
POST /api/reports/imei/check/
Content-Type: application/json

{
  "imei": "123456789012345"
}

Response:
{
  "found": true,
  "status": "stolen",
  "phone_brand": "Samsung",
  "phone_model": "Galaxy S21",
  "reported_at": "2024-12-05T10:30:00Z",
  "message": "This IMEI is registered as stolen"
}
```

#### List All IMEIs (Admin only)
```http
GET /api/reports/imei/list/?status=stolen
Authorization: Bearer <access_token>
```

### Crime Analytics Endpoints

#### Get Crime Heatmap
```http
GET /api/reports/heatmap/?days=30&city=Lahore
```

Response:
```json
[
  {
    "latitude": 31.5204,
    "longitude": 74.3587,
    "incident_count": 15,
    "city": "Lahore",
    "district": "Gulberg"
  }
]
```

#### Get Area Safety Scores
```http
GET /api/reports/safety-score/?city=Lahore&days=90
```

Response:
```json
[
  {
    "location_id": 1,
    "city": "Lahore",
    "district": "Gulberg",
    "neighborhood": "MM Alam Road",
    "incident_count": 15,
    "safety_score": 65.5,
    "risk_level": "Medium"
  }
]
```

#### Get Crime Statistics
```http
GET /api/reports/statistics/?days=30
```

### Area Alerts Endpoints

#### List Active Alerts
```http
GET /api/reports/alerts/?city=Lahore&severity=high
```

#### Create Alert (Admin/Authority only)
```http
POST /api/reports/alerts/create/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "location_id": 1,
  "alert_type": "high_crime",
  "message": "High crime rate in this area",
  "severity": "high",
  "valid_from": "2024-12-05T00:00:00Z"
}
```

### Safety Tips Endpoints

#### List Safety Tips
```http
GET /api/core/safety-tips/?category=Mobile Safety
```

#### Create Safety Tip (Admin only)
```http
POST /api/core/safety-tips/create/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Keep Your Phone Secure",
  "content": "Always keep your phone in your front pocket...",
  "category": "Mobile Safety"
}
```

### Feedback Endpoints

#### Submit Feedback
```http
POST /api/core/feedback/
Content-Type: application/json

{
  "subject": "App Suggestion",
  "message": "It would be great to have...",
  "contact_email": "user@example.com"
}
```

## 🔐 Authentication

All protected endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Token Refresh
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "<your_refresh_token>"
}
```

## 👥 User Roles

- **User** - Can report incidents, check IMEIs, view analytics
- **Authority** - Police/law enforcement, can manage alerts and view all data
- **Admin** - Full access, can manage all resources

## 📁 Project Structure

```
SnatchAlert/
├── accounts/           # User authentication & profiles
├── core/              # Core models (dimensions, tips, feedback)
├── reports/           # Incident reporting, IMEI, alerts
├── phones/            # Phone-related models (legacy)
├── vehicles/          # Vehicle-related models (legacy)
├── SnatchAlert/       # Project settings & main URLs
├── media/             # Uploaded files (FIR, images)
├── manage.py
├── requirements.txt
├── seed_data.py       # Sample data generator
└── README.md
```

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

## 📝 Seed Data

The seed data script creates:
- 3 users (admin, authority, regular user)
- 5 incident types
- 6 locations across Pakistan
- 3 victims
- 4 stolen items
- 3 incidents
- 2 IMEI records
- 2 area alerts
- 3 safety tips

Login credentials after seeding:
- **Admin**: username=`admin`, password=`admin123`
- **Authority**: username=`police_officer`, password=`police123`
- **User**: username=`john_doe`, password=`user123`

## 🚀 Deployment

### Environment Variables
Create a `.env` file:
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use environment variables for secrets
- [ ] Set up proper database (PostgreSQL)
- [ ] Configure static/media file serving
- [ ] Set up HTTPS
- [ ] Configure CORS properly
- [ ] Set up email backend for password reset
- [ ] Enable database backups

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For support, email support@snatchalert.com

---

**Built with ❤️ for community safety**
