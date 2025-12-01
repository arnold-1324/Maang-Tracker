import sys
sys.path.insert(0, '.')

from memory.db import create_user
from services.auth_service import generate_token

# Create a test user with CORRECT parameter order
username = "testuser"
email = "test@example.com"
password = "password123"
full_name = "Test User"

# create_user(username, email, password, full_name)
user_id = create_user(username, email, password, full_name)

if user_id:
    print(f"✅ User created successfully!")
    print(f"   ID: {user_id}")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    
    # Generate a token
    token = generate_token(user_id, email)
    print(f"\n🔑 JWT Token:")
    print(f"   {token}")
    print(f"\n📋 Use this in your API calls:")
    print(f"   Authorization: Bearer {token}")
else:
    print("❌ User already exists or creation failed")
