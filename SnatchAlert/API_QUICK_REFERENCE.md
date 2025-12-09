# SnatchAlert API - Quick Reference

## 🔐 Authentication Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Register with email |
| POST | `/api/auth/login/` | No | Login with email |
| POST | `/api/auth/token/refresh/` | No | Refresh JWT token |
| GET | `/api/auth/profile/` | Yes | Get user profile |
| PATCH | `/api/auth/profile/` | Yes | Update profile |
| POST | `/api/auth/profile/update-email/` | Yes | Update email |
| POST | `/api/auth/profile/update-password/` | Yes | Update password |

## 🔑 Password Reset Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/password-reset/request/` | No | Request password reset |
| POST | `/api/auth/password-reset/verify/` | No | Verify reset token |
| POST | `/api/auth/password-reset/confirm/` | No | Confirm password reset |

## 📱 IMEI Tracking Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/reports/imei/register/` | Yes | Register stolen IMEI |
| POST | `/api/reports/imei/check/` | No | Check IMEI status |
| GET | `/api/reports/imei/list/` | Admin | List all IMEIs |
| PATCH | `/api/reports/imei/{id}/update/` | Admin | Update IMEI status |

## 🔔 IMEI Alert Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/reports/imei/alerts/` | Yes | Get my device alerts |
| POST | `/api/reports/imei/alerts/{id}/read/` | Yes | Mark alert as read |
| POST | `/api/reports/imei/alerts/read-all/` | Yes | Mark all alerts read |
| GET | `/api/reports/imei/check-history/` | Yes | View IMEI check history |

## 🚨 Incident Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/reports/incidents/` | No | List all incidents |
| POST | `/api/reports/incidents/create/` | No | Create incident |
| GET | `/api/reports/incidents/{id}/` | No | Get incident details |
| PATCH | `/api/reports/incidents/{id}/update/` | Yes | Update incident |
| DELETE | `/api/reports/incidents/{id}/delete/` | Yes | Delete incident |
| GET | `/api/reports/incidents/my/` | Yes | Get my incidents |

## 📊 Analytics Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/reports/heatmap/` | No | Get crime heatmap |
| GET | `/api/reports/safety-score/` | No | Get area safety scores |
| GET | `/api/reports/statistics/` | No | Get crime statistics |

## ⚠️ Alert Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/reports/alerts/` | No | List active alerts |
| POST | `/api/reports/alerts/create/` | Admin | Create alert |
| PATCH | `/api/reports/alerts/{id}/update/` | Admin | Update alert |
| DELETE | `/api/reports/alerts/{id}/delete/` | Admin | Delete alert |

## 💡 Community Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/core/safety-tips/` | No | List safety tips |
| POST | `/api/core/safety-tips/create/` | Yes | Create safety tip |
| POST | `/api/core/feedback/` | No | Submit feedback |
| GET | `/api/core/incident-types/` | No | List incident types |

---

## 📝 Quick Examples

### Register & Login
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass123","password2":"Pass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass123"}'
```

### Password Reset
```bash
# Request
curl -X POST http://localhost:8000/api/auth/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# Confirm
curl -X POST http://localhost:8000/api/auth/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{"token":"abc123","new_password":"NewPass123","new_password2":"NewPass123"}'
```

### IMEI Check & Alert
```bash
# Check IMEI
curl -X POST http://localhost:8000/api/reports/imei/check/ \
  -H "Content-Type: application/json" \
  -d '{"imei":"123456789012345"}'

# Get Alerts
curl -X GET http://localhost:8000/api/reports/imei/alerts/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔑 Authentication Header

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

---

**Server:** http://127.0.0.1:8000/
**Docs:** http://127.0.0.1:8000/api/docs/
