#!/usr/bin/env python
"""
Comprehensive Test Suite for SnatchAlert API Endpoints

This test file validates all API endpoints in the SnatchAlert project using Django's test framework.
It properly handles authentication, database transactions, and HTTP requests.

ENDPOINTS TESTED:

🔐 Authentication Endpoints (5 tests):
- POST /api/auth/register/ - User registration
- POST /api/auth/login/ - User login  
- POST /api/auth/token/refresh/ - JWT token refresh
- GET /api/auth/profile/ - Get user profile
- POST /api/auth/password-reset/request/ - Password reset request

🛡️ Core Endpoints (7 tests):
- GET /api/core/safety-tips/ - List safety tips (public)
- POST /api/core/safety-tips/create/ - Create safety tip (admin)
- PATCH /api/core/safety-tips/{id}/update/ - Update safety tip (admin)
- POST /api/core/feedback/ - Create user feedback
- GET /api/core/feedback/list/ - List feedback (admin)
- GET /api/core/incident-types/ - List incident types (public)
- POST /api/core/incident-types/create/ - Create incident type (admin)

📊 Reports Endpoints (15 tests):
- GET /api/reports/incidents/ - List incidents (public)
- POST /api/reports/incidents/create/ - Create incident (authenticated)
- GET /api/reports/incidents/{id}/ - Get incident detail
- PATCH /api/reports/incidents/{id}/update/ - Update incident (owner)
- GET /api/reports/incidents/my/ - Get user's incidents
- POST /api/reports/imei/check/ - Check IMEI status (public)
- GET /api/reports/imei/list/ - List IMEIs (admin)
- GET /api/reports/imei/alerts/ - Get device alerts
- GET /api/reports/imei/check-history/ - Get IMEI check history
- POST /api/reports/imei/alerts/read-all/ - Mark alerts as read
- GET /api/reports/heatmap/ - Crime heatmap (public)
- GET /api/reports/safety-score/ - Area safety scores (public)
- GET /api/reports/statistics/ - Crime statistics (public)
- GET /api/reports/alerts/ - List area alerts (public)
- POST /api/reports/incidents/create/ - Create anonymous incident

⚠️ Error Cases (3 tests):
- Unauthenticated access to protected endpoints (401)
- Invalid login credentials (400)
- Invalid IMEI format validation (400)

TOTAL: 30 endpoint tests covering authentication, core features, reports, and error handling.

Usage:
    python test_all_endpoints.py

Requirements:
    - Django project must be properly configured
    - Database must be accessible
    - All required packages must be installed
"""

import os
import sys
import django
import json
import uuid
from datetime import datetime, timedelta

# Setup Django BEFORE importing anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SnatchAlert.settings')
django.setup()

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

User = get_user_model()

@override_settings(
    ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
    DEBUG=True
)
class SnatchAlertEndpointTests(APITestCase):
    """Comprehensive endpoint tests for SnatchAlert API"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create regular test user
        unique_id = str(uuid.uuid4())[:8]
        self.test_user = User.objects.create_user(
            email=f'testuser_{unique_id}@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            role='user'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            email=f'admin_{unique_id}@example.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True
        )
        
        self.auth_tokens = {}
        self.test_data = {}
        
        print(f"✅ Created test user: {self.test_user.email}")
        print(f"✅ Created admin user: {self.admin_user.email}")
    
    def get_auth_token(self, user, password):
        """Get authentication token for a user"""
        login_data = {
            "email": user.email,
            "password": password
        }
        response = self.client.post('/api/auth/login/', login_data, format='json')
        if response.status_code == 200:
            return response.data.get('tokens', {}).get('access')
        return None
    
    def authenticate_user(self, user_type='test'):
        """Authenticate as test user or admin"""
        if user_type == 'admin':
            token = self.get_auth_token(self.admin_user, 'AdminPass123!')
        else:
            token = self.get_auth_token(self.test_user, 'TestPass123!')
        
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            return True
        return False
    
    def test_authentication_endpoints(self):
        """Test all authentication-related endpoints"""
        print("\n🔐 Testing Authentication Endpoints")
        
        # 1. Register new user
        register_data = {
            "email": f"newuser_{uuid.uuid4().hex[:8]}@example.com",
            "password": "NewUserPass123!",
            "password2": "NewUserPass123!",
            "first_name": "New",
            "last_name": "User",
            "phone": "+923001234567"
        }
        
        response = self.client.post('/api/auth/register/', register_data, format='json')
        print(f"✅ Register: {response.status_code} (expected 201)")
        self.assertEqual(response.status_code, 201)
        
        # 2. Login with test user
        login_data = {
            "email": self.test_user.email,
            "password": "TestPass123!"
        }
        
        response = self.client.post('/api/auth/login/', login_data, format='json')
        print(f"✅ Login: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        if response.status_code == 200:
            self.auth_tokens['test_user'] = response.data.get('tokens', {}).get('access')
            self.auth_tokens['refresh'] = response.data.get('tokens', {}).get('refresh')
        
        # 3. Token refresh
        if self.auth_tokens.get('refresh'):
            refresh_data = {"refresh": self.auth_tokens['refresh']}
            response = self.client.post('/api/auth/token/refresh/', refresh_data, format='json')
            print(f"✅ Token refresh: {response.status_code} (expected 200)")
            self.assertEqual(response.status_code, 200)
        
        # 4. Get user profile (authenticated)
        self.authenticate_user()
        response = self.client.get('/api/auth/profile/')
        print(f"✅ Get profile: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 5. Password reset request
        self.client.credentials()  # Remove auth
        reset_request_data = {"email": self.test_user.email}
        response = self.client.post('/api/auth/password-reset/request/', reset_request_data, format='json')
        print(f"✅ Password reset request: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
    
    def test_core_endpoints(self):
        """Test core functionality endpoints"""
        print("\n🛡️ Testing Core Endpoints")
        
        # 1. List safety tips (public)
        response = self.client.get('/api/core/safety-tips/')
        print(f"✅ List safety tips: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 2. Create safety tip (admin only)
        self.authenticate_user('admin')
        safety_tip_data = {
            "title": "Test Safety Tip",
            "content": "This is a test safety tip for endpoint testing.",
            "category": "general",
            "is_active": True
        }
        response = self.client.post('/api/core/safety-tips/create/', safety_tip_data, format='json')
        print(f"✅ Create safety tip: {response.status_code} (expected 201)")
        self.assertEqual(response.status_code, 201)
        
        if response.status_code == 201:
            self.test_data['safety_tip_id'] = response.data.get('id')
        
        # 3. Update safety tip (admin only)
        if self.test_data.get('safety_tip_id'):
            update_data = {"title": "Updated Test Safety Tip"}
            response = self.client.patch(f'/api/core/safety-tips/{self.test_data["safety_tip_id"]}/update/', update_data, format='json')
            print(f"✅ Update safety tip: {response.status_code} (expected 200)")
            self.assertEqual(response.status_code, 200)
        
        # 4. Create user feedback
        self.authenticate_user()
        feedback_data = {
            "subject": "Test Feedback",
            "message": "This is test feedback for endpoint testing.",
            "contact_email": "feedback@example.com"
        }
        response = self.client.post('/api/core/feedback/', feedback_data, format='json')
        print(f"✅ Create feedback: {response.status_code} (expected 201)")
        self.assertEqual(response.status_code, 201)
        
        # 5. List feedback (admin only)
        self.authenticate_user('admin')
        response = self.client.get('/api/core/feedback/list/')
        print(f"✅ List feedback: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 6. List incident types
        response = self.client.get('/api/core/incident-types/')
        print(f"✅ List incident types: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 7. Create incident type (admin only)
        incident_type_data = {
            "category": "Test Crime Type",
            "description": "Test crime type for endpoint testing"
        }
        response = self.client.post('/api/core/incident-types/create/', incident_type_data, format='json')
        print(f"✅ Create incident type: {response.status_code} (expected 201)")
        self.assertEqual(response.status_code, 201)
    
    def test_reports_endpoints(self):
        """Test reports and incident management endpoints"""
        print("\n📊 Testing Reports Endpoints")
        
        # 1. List incidents (public)
        response = self.client.get('/api/reports/incidents/')
        print(f"✅ List incidents: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 2. Create incident with IMEI
        self.authenticate_user()
        incident_data = {
            "occurred_at": timezone.now().isoformat(),
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
                "name": "Test Victim",
                "age": 28,
                "gender": "male",
                "phone_number": "+923001234567"
            },
            "stolen_item_data": {
                "item_type": "phone",
                "imei": "123456789012345",  # Use consistent 15-digit IMEI
                "phone_brand": "Samsung",
                "phone_model": "Galaxy S21"
            },
            "value_estimate": 75000,
            "fir_filed": True,
            "description": "Test incident for endpoint testing",
            "is_anonymous": False
        }
        
        response = self.client.post('/api/reports/incidents/create/', incident_data, format='json')
        print(f"✅ Create incident: {response.status_code} (expected 201)")
        self.assertEqual(response.status_code, 201)
        
        if response.status_code == 201:
            self.test_data['incident_id'] = response.data.get('id')
        
        # 3. Get incident detail
        if self.test_data.get('incident_id'):
            response = self.client.get(f'/api/reports/incidents/{self.test_data["incident_id"]}/')
            print(f"✅ Get incident detail: {response.status_code} (expected 200)")
            self.assertEqual(response.status_code, 200)
        
        # 4. Update incident
        if self.test_data.get('incident_id'):
            update_data = {"description": "Updated test incident description"}
            response = self.client.patch(f'/api/reports/incidents/{self.test_data["incident_id"]}/update/', update_data, format='json')
            print(f"✅ Update incident: {response.status_code} (expected 200)")
            self.assertEqual(response.status_code, 200)
        
        # 5. Get my incidents
        response = self.client.get('/api/reports/incidents/my/')
        print(f"✅ Get my incidents: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 6. IMEI check (public)
        self.client.credentials()  # Remove auth
        imei_check_data = {"imei": "123456789012345"}  # Use the same IMEI from incident
        response = self.client.post('/api/reports/imei/check/', imei_check_data, format='json')
        print(f"✅ IMEI check: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 7. List my IMEIs (admin only)
        self.authenticate_user('admin')
        response = self.client.get('/api/reports/imei/list/')
        print(f"✅ List IMEIs (admin): {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 8. Get device alerts (regular user)
        self.authenticate_user()
        response = self.client.get('/api/reports/imei/alerts/')
        print(f"✅ Get device alerts: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 9. Get IMEI check history
        response = self.client.get('/api/reports/imei/check-history/')
        print(f"✅ Get IMEI check history: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 10. Mark all alerts as read
        response = self.client.post('/api/reports/imei/alerts/read-all/')
        print(f"✅ Mark all alerts read: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 11. Crime heatmap (public)
        self.client.credentials()  # Remove auth
        response = self.client.get('/api/reports/heatmap/')
        print(f"✅ Crime heatmap: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 12. Area safety score (public)
        response = self.client.get('/api/reports/safety-score/?city=Lahore')
        print(f"✅ Area safety score: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 13. Crime statistics (public)
        response = self.client.get('/api/reports/statistics/')
        print(f"✅ Crime statistics: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 14. List area alerts (public)
        response = self.client.get('/api/reports/alerts/')
        print(f"✅ List area alerts: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)
        
        # 15. Create anonymous incident
        self.authenticate_user()
        anonymous_incident_data = {
            "occurred_at": timezone.now().isoformat(),
            "incident_type_name": "Theft",
            "location_data": {
                "province": "Punjab",
                "city": "Karachi",
                "district": "Clifton",
                "latitude": 24.8607,
                "longitude": 67.0011
            },
            "value_estimate": 50000,
            "fir_filed": False,
            "description": "Anonymous theft report",
            "is_anonymous": True
        }
        
        response = self.client.post('/api/reports/incidents/create/', anonymous_incident_data, format='json')
        print(f"✅ Create anonymous incident: {response.status_code} (expected 201)")
        self.assertEqual(response.status_code, 201)
    
    def test_error_cases(self):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Cases")
        
        # 1. Unauthenticated access to protected endpoint
        self.client.credentials()  # Remove authentication
        response = self.client.get('/api/auth/profile/')
        print(f"✅ Unauthenticated access: {response.status_code} (expected 401)")
        self.assertEqual(response.status_code, 401)
        
        # 2. Invalid login credentials
        invalid_login = {"email": "invalid@example.com", "password": "wrongpassword"}
        response = self.client.post('/api/auth/login/', invalid_login, format='json')
        print(f"✅ Invalid credentials: {response.status_code} (expected 400)")
        self.assertEqual(response.status_code, 400)
        
        # 3. Invalid IMEI format
        invalid_imei = {"imei": "invalid-imei"}
        response = self.client.post('/api/reports/imei/check/', invalid_imei, format='json')
        print(f"✅ Invalid IMEI: {response.status_code} (expected 400)")
        self.assertEqual(response.status_code, 400)


def run_comprehensive_tests():
    """Run all endpoint tests using Django's test runner"""
    print("🚀 Starting Comprehensive SnatchAlert API Endpoint Tests")
    print("=" * 80)
    
    # Import Django's test runner
    from django.test.utils import get_runner
    from django.conf import settings
    
    # Get the test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run the tests
    failures = test_runner.run_tests(['__main__'])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed")
        return False
    else:
        print(f"\n🎉 All tests passed!")
        return True


if __name__ == '__main__':
    # Run as a standalone script
    import unittest
    
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(SnatchAlertEndpointTests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print("\n" + "=" * 80)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    
    if failures > 0 or errors > 0:
        print(f"\n❌ Some tests failed. Check the output above for details.")
    else:
        print(f"\n🎉 All tests passed! Your API endpoints are working correctly.")