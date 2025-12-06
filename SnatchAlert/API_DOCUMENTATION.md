# SnatchAlert API Documentation

Complete API reference for the SnatchAlert crime reporting and tracking system.

## Base URL

```
http://localhost:8000/api
```

## Authentication

SnatchAlert uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Response Format

All API responses follow this structure:

### Success Response
```json
{
  "data": { ... },
  "message": "Success message"
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": { ... }
}
```

## Endpoints

### 1. Authentication

#### 1.1 Register User
Create a new user account.

**Endpoint:** `POST /auth/register/`

**Permission:** Public

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "password2": "SecurePass123",
  "phone": "+923001234567",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "phone": "+923001234567"
}
```

#### 1.2 Login
Authenticate and receive JWT tokens.

**Endpoint:** `POST /auth/login/`

**Permission:** Public

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 1.3 Refresh Token
Get a new access token using refresh token.

**Endpoint:** `POST /auth/token/refresh/`

**Permission:** Public

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 1.4 Get User Profile
Retrieve authenticated user's profile.

**Endpoint:** `GET /auth/profile/`

**Permission:** Authenticated

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+923001234567",
  "role": "user",
  "is_verified": false,
  "date_joined": "2024-12-05T10:30:00Z"
}
```

---

### 2. Incident Management

#### 2.1 Create Incident
Report a new crime incident.

**Endpoint:** `POST /reports/incidents/create/`

**Permission:** Public (allows anonymous reporting)

**Request Body:**
```json
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
    "phone_number": "+923001234567",
    "email": "john@example.com"
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
  "description": "Phone snatched at gunpoint near MM Alam Road",
  "is_anonymous": false
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "occurred_at": "2024-12-05T14:30:00Z",
  "incident_type": {
    "id": 1,
    "category": "Mobile Snatching"
  },
  "location": {
    "id": 1,
    "city": "Lahore",
    "district": "Gulberg",
    "latitude": "31.520400",
    "longitude": "74.358700"
  },
  "status": "reported",
  "created_at": "2024-12-05T15:00:00Z"
}
```

#### 2.2 List Incidents
Get a list of all incidents with filtering.

**Endpoint:** `GET /reports/incidents/`

**Permission:** Public (read-only)

**Query Parameters:**
- `city` - Filter by city
- `district` - Filter by district
- `neighborhood` - Filter by neighborhood
- `incident_type__category` - Filter by incident type
- `status` - Filter by status (reported, investigating, resolved, closed)
- `date_from` - Filter incidents from date (YYYY-MM-DD)
- `date_to` - Filter incidents to date (YYYY-MM-DD)
- `fir_filed` - Filter by FIR status (true/false)
- `search` - Search in description and location
- `ordering` - Sort by field (occurred_at, created_at)
- `page` - Page number
- `page_size` - Items per page

**Example:** `GET /reports/incidents/?city=Lahore&status=reported&page=1`

**Response:** `200 OK`
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/reports/incidents/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "occurred_at": "2024-12-05T14:30:00Z",
      "incident_type": {
        "id": 1,
        "category": "Mobile Snatching",
        "description": "Theft of mobile phones"
      },
      "location": {
        "id": 1,
        "province": "Punjab",
        "city": "Lahore",
        "district": "Gulberg",
        "neighborhood": "MM Alam Road",
        "latitude": "31.520400",
        "longitude": "74.358700"
      },
      "victim": {
        "id": 1,
        "name": "John Doe",
        "age": 28,
        "gender": "male"
      },
      "stolen_item": {
        "id": 1,
        "item_type": "phone",
        "imei": "123456789012345",
        "phone_brand": "Samsung",
        "phone_model": "Galaxy S21"
      },
      "value_estimate": "75000.00",
      "fir_filed": true,
      "description": "Phone snatched at gunpoint",
      "is_anonymous": false,
      "status": "reported",
      "created_at": "2024-12-05T15:00:00Z"
    }
  ]
}
```

#### 2.3 Get Incident Details
Retrieve details of a specific incident.

**Endpoint:** `GET /reports/incidents/{id}/`

**Permission:** Public (read-only)

**Response:** `200 OK` (same structure as list item)

#### 2.4 Update Incident
Update an existing incident.

**Endpoint:** `PATCH /reports/incidents/{id}/update/`

**Permission:** Authenticated (owner only)

**Request Body:**
```json
{
  "description": "Updated description with more details",
  "status": "investigating",
  "fir_filed": true
}
```

**Response:** `200 OK`

#### 2.5 Delete Incident
Delete an incident report.

**Endpoint:** `DELETE /reports/incidents/{id}/delete/`

**Permission:** Authenticated (owner only)

**Response:** `204 No Content`

#### 2.6 My Incidents
Get incidents reported by the authenticated user.

**Endpoint:** `GET /reports/incidents/my/`

**Permission:** Authenticated

**Response:** `200 OK` (same structure as list)

---

### 3. IMEI Tracking

#### 3.1 Register Stolen IMEI
Register a stolen phone IMEI.

**Endpoint:** `POST /reports/imei/register/`

**Permission:** Authenticated

**Request Body:**
```json
{
  "imei": "123456789012345",
  "phone_brand": "Samsung",
  "phone_model": "Galaxy S21",
  "owner_name": "John Doe",
  "owner_contact": "+923001234567",
  "status": "stolen",
  "notes": "Stolen from car"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "imei": "123456789012345",
  "phone_brand": "Samsung",
  "phone_model": "Galaxy S21",
  "owner_name": "John Doe",
  "owner_contact": "+923001234567",
  "status": "stolen",
  "reported_at": "2024-12-05T15:00:00Z",
  "reported_by_username": "john_doe"
}
```

#### 3.2 Check IMEI Status
Check if an IMEI is registered as stolen.

**Endpoint:** `POST /reports/imei/check/`

**Permission:** Public

**Request Body:**
```json
{
  "imei": "123456789012345"
}
```

**Response (Found):** `200 OK`
```json
{
  "found": true,
  "status": "stolen",
  "phone_brand": "Samsung",
  "phone_model": "Galaxy S21",
  "reported_at": "2024-12-05T15:00:00Z",
  "message": "This IMEI is registered as stolen"
}
```

**Response (Not Found):** `200 OK`
```json
{
  "found": false,
  "message": "This IMEI is not in our stolen registry"
}
```

#### 3.3 List All IMEIs
Get list of all registered IMEIs (Admin only).

**Endpoint:** `GET /reports/imei/list/`

**Permission:** Admin/Authority

**Query Parameters:**
- `status` - Filter by status (stolen, recovered, flagged)
- `search` - Search IMEI, brand, model, owner

**Response:** `200 OK`

#### 3.4 Update IMEI Status
Update IMEI status (Admin only).

**Endpoint:** `PATCH /reports/imei/{id}/update/`

**Permission:** Admin/Authority

**Request Body:**
```json
{
  "status": "recovered",
  "notes": "Phone recovered by police"
}
```

**Response:** `200 OK`

---

### 4. Crime Analytics

#### 4.1 Crime Heatmap
Get crime hotspot data for map visualization.

**Endpoint:** `GET /reports/heatmap/`

**Permission:** Public

**Query Parameters:**
- `days` - Number of days to include (default: 30)
- `city` - Filter by city

**Example:** `GET /reports/heatmap/?days=30&city=Lahore`

**Response:** `200 OK`
```json
[
  {
    "latitude": "31.520400",
    "longitude": "74.358700",
    "incident_count": 15,
    "city": "Lahore",
    "district": "Gulberg"
  },
  {
    "latitude": "31.482400",
    "longitude": "74.304500",
    "incident_count": 8,
    "city": "Lahore",
    "district": "Model Town"
  }
]
```

#### 4.2 Area Safety Score
Calculate safety scores for different areas.

**Endpoint:** `GET /reports/safety-score/`

**Permission:** Public

**Query Parameters:**
- `city` - Filter by city
- `days` - Number of days to analyze (default: 90)

**Example:** `GET /reports/safety-score/?city=Lahore&days=90`

**Response:** `200 OK`
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
  },
  {
    "location_id": 2,
    "city": "Lahore",
    "district": "Model Town",
    "neighborhood": "Block A",
    "incident_count": 5,
    "safety_score": 85.2,
    "risk_level": "Low"
  }
]
```

**Risk Levels:**
- `Low` - Safety score >= 80
- `Medium` - Safety score 60-79
- `High` - Safety score 40-59
- `Critical` - Safety score < 40

#### 4.3 Crime Statistics
Get overall crime statistics.

**Endpoint:** `GET /reports/statistics/`

**Permission:** Public

**Query Parameters:**
- `days` - Number of days to analyze (default: 30)

**Response:** `200 OK`
```json
{
  "total_incidents": 150,
  "period_days": 30,
  "by_incident_type": [
    {
      "incident_type__category": "Mobile Snatching",
      "count": 75
    },
    {
      "incident_type__category": "Vehicle Theft",
      "count": 45
    }
  ],
  "top_cities": [
    {
      "location__city": "Lahore",
      "count": 80
    },
    {
      "location__city": "Karachi",
      "count": 50
    }
  ],
  "fir_filed_percentage": 65.5
}
```

---

### 5. Area Alerts

#### 5.1 List Active Alerts
Get active location-based alerts.

**Endpoint:** `GET /reports/alerts/`

**Permission:** Public

**Query Parameters:**
- `alert_type` - Filter by type (high_crime, recent_incident, warning)
- `severity` - Filter by severity (low, medium, high, critical)
- `location__city` - Filter by city

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "location": {
      "id": 1,
      "city": "Lahore",
      "district": "Gulberg",
      "neighborhood": "MM Alam Road"
    },
    "alert_type": "high_crime",
    "message": "High crime rate reported in this area. Stay vigilant.",
    "severity": "high",
    "is_active": true,
    "valid_from": "2024-12-05T00:00:00Z",
    "valid_until": null,
    "created_by_username": "police_officer",
    "created_at": "2024-12-05T10:00:00Z"
  }
]
```

#### 5.2 Create Alert
Create a new area alert (Admin/Authority only).

**Endpoint:** `POST /reports/alerts/create/`

**Permission:** Admin/Authority

**Request Body:**
```json
{
  "location_id": 1,
  "alert_type": "high_crime",
  "message": "High crime rate in this area",
  "severity": "high",
  "valid_from": "2024-12-05T00:00:00Z",
  "valid_until": "2024-12-31T23:59:59Z"
}
```

**Response:** `201 Created`

---

### 6. Safety Tips

#### 6.1 List Safety Tips
Get community safety tips.

**Endpoint:** `GET /core/safety-tips/`

**Permission:** Public

**Query Parameters:**
- `category` - Filter by category
- `search` - Search in title and content

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Keep Your Phone Secure",
    "content": "Always keep your phone in your front pocket or bag...",
    "category": "Mobile Safety",
    "is_active": true,
    "created_by_username": "admin",
    "created_at": "2024-12-05T10:00:00Z"
  }
]
```

#### 6.2 Create Safety Tip
Create a new safety tip (Admin only).

**Endpoint:** `POST /core/safety-tips/create/`

**Permission:** Authenticated

**Request Body:**
```json
{
  "title": "Vehicle Security Tips",
  "content": "Always lock your vehicle and park in well-lit areas...",
  "category": "Vehicle Safety"
}
```

**Response:** `201 Created`

---

### 7. Feedback

#### 7.1 Submit Feedback
Submit user feedback or suggestions.

**Endpoint:** `POST /core/feedback/`

**Permission:** Public

**Request Body:**
```json
{
  "subject": "App Suggestion",
  "message": "It would be great to have push notifications for nearby incidents",
  "contact_email": "user@example.com"
}
```

**Response:** `201 Created`

#### 7.2 List Feedback
View all feedback (Admin only).

**Endpoint:** `GET /core/feedback/list/`

**Permission:** Admin

**Query Parameters:**
- `is_resolved` - Filter by resolution status

**Response:** `200 OK`

---

### 8. Incident Types

#### 8.1 List Incident Types
Get all available incident types.

**Endpoint:** `GET /core/incident-types/`

**Permission:** Public

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "category": "Mobile Snatching",
    "description": "Theft of mobile phones"
  },
  {
    "id": 2,
    "category": "Vehicle Theft",
    "description": "Theft of cars, bikes, or other vehicles"
  }
]
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

## Rate Limiting

Currently no rate limiting is implemented. In production, consider implementing rate limiting for public endpoints.

## Pagination

List endpoints support pagination with these parameters:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

## File Uploads

For endpoints that support file uploads (FIR documents, item images), use `multipart/form-data` content type.

**Example:**
```bash
curl -X POST http://localhost:8000/api/reports/incidents/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "fir_document=@/path/to/fir.pdf" \
  -F "item_image=@/path/to/phone.jpg" \
  -F "data={...json...}"
```

---

## Support

For API support or questions:
- Email: support@snatchalert.com
- Documentation: http://localhost:8000/api/docs/
- GitHub: [repository-url]
