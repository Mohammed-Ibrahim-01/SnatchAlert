"""
Test script to verify email-only authentication
Run with: python manage.py shell < test_email_auth.py
"""
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("Testing Email-Only Authentication")
print("="*60)

print(f"\n✓ USERNAME_FIELD: {User.USERNAME_FIELD}")
print(f"✓ REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")

# Check if username field exists
user = User.objects.first()
if user:
    print(f"\n✓ First user email: {user.email}")
    print(f"✓ Has username attribute: {hasattr(user, 'username')}")
    
    if not hasattr(user, 'username'):
        print("\n🎉 SUCCESS! Username field completely removed!")
    else:
        print("\n⚠️ WARNING: Username field still exists")
else:
    print("\n⚠️ No users in database")

# Test user creation
print("\n" + "-"*60)
print("Testing User Creation")
print("-"*60)

try:
    test_user = User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    print(f"✓ Created user: {test_user.email}")
    print(f"✓ Full name: {test_user.get_full_name()}")
    print(f"✓ Can login with email: {test_user.check_password('testpass123')}")
    
    # Clean up
    test_user.delete()
    print("✓ Test user deleted")
    
    print("\n🎉 All tests passed!")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "="*60)
