# SnatchAlert - Authentication & IMEI Alert System Guide

Complete guide for the updated authentication system and IMEI stolen device alert functionality.

## 🔐 Authentication System Updates

### 1. Email-Based Login (Username Removed)

The system now uses **email as the primary login field** instead of username.

#### Registration

**Endpoint:** `POST /api/auth/register/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "password2": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+923001234567"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+923001234567"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "Registration successful"
}
```

**Features:**
- Email must be unique
- Password validation (minimum 8 characters, not too common, etc.)
- Username is auto-generated from email
- Returns JWT tokens immediately after registration

#### Login

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+923001234567",
    "role": "user"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "Login successful"
}
```

---

## 👤 Profile Management

### 2. Update Email

**Endpoint:** `POST /api/auth/profile/update-email/`

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "new_email": "newemail@example.com",
  "password": "CurrentPassword123"
}
```

**Response:**
```json
{
  "message": "Email updated successfully",
  "user": {
    "id": 1,
    "email": "newemail@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+923001234567"
  }
}
```

**Validation:**
- Current password must be correct
- New email must be unique
- User's `is_verified` status is reset to `false`

### 3. Update Password

**Endpoint:** `POST /api/auth/profile/update-password/`

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "old_password": "CurrentPassword123",
  "new_password": "NewSecurePass456",
  "new_password2": "NewSecurePass456"
}
```

**Response:**
```json
{
  "message": "Password updated successfully"
}
```

**Validation:**
- Old password must be correct
- New passwords must match
- New password must meet security requirements

---

## 🔑 Forgot Password Flow

### Step 1: Request Password Reset

**Endpoint:** `POST /api/auth/password-reset/request/`

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Password reset link sent to your email",
  "token": "abc123xyz..."  // Only in development mode
}
```

**What Happens:**
1. System generates a secure token (valid for 1 hour)
2. Token is saved in database
3. Email is sent with reset link: `http://frontend.com/reset-password?token=abc123xyz`
4. User receives email with instructions

**Email Template:**
```
Subject: Password Reset Request - SnatchAlert

Hello,

You requested to reset your password for SnatchAlert.

Click the link below to reset your password:
http://localhost:3000/reset-password?token=abc123xyz

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
SnatchAlert Team
```

### Step 2: Verify Token (Optional)

**Endpoint:** `POST /api/auth/password-reset/verify/`

**Request:**
```json
{
  "token": "abc123xyz..."
}
```

**Response (Valid):**
```json
{
  "valid": true,
  "message": "Token is valid",
  "email": "user@example.com"
}
```

**Response (Invalid):**
```json
{
  "valid": false,
  "message": "Token is invalid or expired"
}
```

### Step 3: Reset Password

**Endpoint:** `POST /api/auth/password-reset/confirm/`

**Request:**
```json
{
  "token": "abc123xyz...",
  "new_password": "NewSecurePass456",
  "new_password2": "NewSecurePass456"
}
```

**Response:**
```json
{
  "message": "Password reset successful. You can now login with your new password."
}
```

**What Happens:**
1. Token is validated (not expired, not used)
2. Password is updated
3. Token is marked as used
4. User can now login with new password

---

## 📱 IMEI Stolen Device Alert System

### 4. How It Works

When someone checks an IMEI that's registered as stolen:

1. **IMEI Check** - Anyone can check an IMEI
2. **Detection** - System detects it's stolen
3. **Logging** - Check is logged with IP, timestamp, user agent
4. **Alert Creation** - Alert is created for the device owner
5. **Notification** - Owner receives:
   - In-app alert
   - Email notification
   - Push notification (if configured)

### Check IMEI (Public Endpoint)

**Endpoint:** `POST /api/reports/imei/check/`

**Request:**
```json
{
  "imei": "123456789012345"
}
```

**Response (Stolen Device):**
```json
{
  "found": true,
  "status": "stolen",
  "phone_brand": "Samsung",
  "phone_model": "Galaxy S21",
  "reported_at": "2024-12-05T10:30:00Z",
  "message": "⚠️ WARNING: This IMEI is registered as stolen",
  "warning": "This device has been reported stolen. Do not purchase!",
  "advice": "Contact local authorities if you have information about this device."
}
```

**Response (Safe Device):**
```json
{
  "found": false,
  "message": "This IMEI is not in our stolen registry",
  "status": "safe"
}
```

**What Happens Behind the Scenes:**
```python
# 1. Log the check
IMEICheckLog.objects.create(
    imei_registry=record,
    checked_by=user,  # if authenticated
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0...",
    alert_sent=False
)

# 2. Create alert for owner
StolenDeviceAlert.objects.create(
    imei_registry=record,
    owner=record.reported_by,
    alert_type='check_detected',
    message="🚨 Your stolen device has been detected!"
)

# 3. Send email notification
send_mail(
    subject='🚨 ALERT: Your Stolen Device Detected',
    message=alert_message,
    recipient_list=[owner.email]
)
```

### Get My Device Alerts

**Endpoint:** `GET /api/reports/imei/alerts/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "unread_count": 2,
  "total_count": 5,
  "alerts": [
    {
      "id": 1,
      "imei": "123456789012345",
      "phone_brand": "Samsung",
      "phone_model": "Galaxy S21",
      "alert_type": "check_detected",
      "message": "🚨 ALERT: Your stolen device has been detected!...",
      "is_read": false,
      "created_at": "2024-12-05T14:30:00Z",
      "check_info": {
        "ip_address": "192.168.1.100",
        "checked_at": "2024-12-05T14:30:00Z"
      }
    }
  ]
}
```

### Mark Alert as Read

**Endpoint:** `POST /api/reports/imei/alerts/{alert_id}/read/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "message": "Alert marked as read"
}
```

### Mark All Alerts as Read

**Endpoint:** `POST /api/reports/imei/alerts/read-all/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "message": "3 alerts marked as read"
}
```

### View IMEI Check History

**Endpoint:** `GET /api/reports/imei/check-history/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "total_checks": 15,
  "checks": [
    {
      "id": 1,
      "imei": "123456789012345",
      "phone_brand": "Samsung",
      "phone_model": "Galaxy S21",
      "checked_at": "2024-12-05T14:30:00Z",
      "ip_address": "192.168.1.100",
      "alert_sent": true
    }
  ]
}
```

---

## 🔔 Real-Time Alert Flow

### Frontend Implementation Example

```javascript
// 1. User registers stolen IMEI
const registerIMEI = async () => {
  const response = await fetch('/api/reports/imei/register/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      imei: '123456789012345',
      phone_brand: 'Samsung',
      phone_model: 'Galaxy S21',
      owner_name: 'John Doe',
      owner_contact: '+923001234567',
      status: 'stolen'
    })
  });
};

// 2. Buyer checks IMEI before purchase
const checkIMEI = async (imei) => {
  const response = await fetch('/api/reports/imei/check/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ imei })
  });
  
  const data = await response.json();
  
  if (data.found && data.status === 'stolen') {
    // Show warning to buyer
    alert('⚠️ WARNING: This device is stolen!');
  }
};

// 3. Owner receives real-time alert
const checkAlerts = async () => {
  const response = await fetch('/api/reports/imei/alerts/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  const data = await response.json();
  
  if (data.unread_count > 0) {
    // Show popup notification
    showNotification({
      title: '🚨 Stolen Device Alert',
      message: `Your stolen device was detected ${data.unread_count} time(s)!`,
      type: 'urgent'
    });
  }
};

// 4. Poll for alerts every 30 seconds
setInterval(checkAlerts, 30000);
```

---

## 📧 Email Configuration

### Development (Console Backend)

Emails are printed to console for testing:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production (SMTP)

Configure real email sending:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@snatchalert.com'
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate App Password
3. Use App Password in `EMAIL_HOST_PASSWORD`

---

## 🧪 Testing Guide

### Test Email-Based Authentication

```bash
# 1. Register with email
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "password2": "TestPass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# 2. Login with email
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### Test Password Reset

```bash
# 1. Request reset
curl -X POST http://localhost:8000/api/auth/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Verify token (copy from response or email)
curl -X POST http://localhost:8000/api/auth/password-reset/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN_HERE"}'

# 3. Reset password
curl -X POST http://localhost:8000/api/auth/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN_HERE",
    "new_password": "NewPass123",
    "new_password2": "NewPass123"
  }'
```

### Test IMEI Alert System

```bash
# 1. Register stolen IMEI (as owner)
curl -X POST http://localhost:8000/api/reports/imei/register/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "imei": "999888777666555",
    "phone_brand": "iPhone",
    "phone_model": "13 Pro",
    "owner_name": "John Doe",
    "status": "stolen"
  }'

# 2. Check IMEI (as potential buyer - triggers alert)
curl -X POST http://localhost:8000/api/reports/imei/check/ \
  -H "Content-Type: application/json" \
  -d '{"imei": "999888777666555"}'

# 3. Get alerts (as owner)
curl -X GET http://localhost:8000/api/reports/imei/alerts/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔒 Security Features

1. **Email Uniqueness** - Prevents duplicate accounts
2. **Password Validation** - Strong password requirements
3. **Token Expiration** - Reset tokens expire in 1 hour
4. **One-Time Tokens** - Tokens can only be used once
5. **IP Logging** - All IMEI checks are logged with IP
6. **Rate Limiting** - (Recommended for production)

---

## 📱 Mobile App Integration

### Authentication Flow

```
1. User enters email & password
2. App calls /api/auth/login/
3. Store access & refresh tokens
4. Use access token for API calls
5. Refresh token when expired
```

### Alert Notification Flow

```
1. App polls /api/reports/imei/alerts/ every 30s
2. If unread_count > 0, show notification
3. User taps notification
4. App shows alert details
5. User marks as read
```

### Push Notifications (Future)

For real-time push notifications, integrate:
- Firebase Cloud Messaging (FCM)
- Apple Push Notification Service (APNS)
- WebSockets for web app

---

## 🎯 Summary

### What Changed:

✅ **Email-based login** - No more username
✅ **Profile updates** - Change email & password
✅ **Complete forgot-password flow** - Token-based reset
✅ **IMEI alert system** - Real-time stolen device detection
✅ **Alert management** - View, read, and track alerts
✅ **Check logging** - Track all IMEI checks with IP

### New Endpoints:

- `POST /api/auth/register/` - Register with email
- `POST /api/auth/login/` - Login with email
- `POST /api/auth/profile/update-email/` - Update email
- `POST /api/auth/profile/update-password/` - Update password
- `POST /api/auth/password-reset/request/` - Request reset
- `POST /api/auth/password-reset/verify/` - Verify token
- `POST /api/auth/password-reset/confirm/` - Reset password
- `GET /api/reports/imei/alerts/` - Get device alerts
- `POST /api/reports/imei/alerts/{id}/read/` - Mark alert read
- `POST /api/reports/imei/alerts/read-all/` - Mark all read
- `GET /api/reports/imei/check-history/` - View check history

---

**Ready to use! 🚀**
