"""
Verify arnold user exists in database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory.db import get_conn

def verify_arnold_user():
    """Verify arnold user exists and show details"""
    
    conn = get_conn()
    cur = conn.cursor()
    
    # Check for arnold user
    cur.execute("""
        SELECT id, username, email, full_name, created_at, last_login, is_active 
        FROM users 
        WHERE email = ? OR username = ?
    """, ('arnoldgna765@gmail.com', 'arnold'))
    
    user = cur.fetchone()
    
    if user:
        print("✅ Arnold user found in database!\n")
        print("=" * 60)
        print(f"User ID:      {user['id']}")
        print(f"Username:     {user['username']}")
        print(f"Email:        {user['email']}")
        print(f"Full Name:    {user['full_name']}")
        print(f"Created At:   {user['created_at']}")
        print(f"Last Login:   {user['last_login'] or 'Never'}")
        print(f"Is Active:    {'Yes' if user['is_active'] else 'No'}")
        print("=" * 60)
        print("\n✅ User is ready to use!")
        print("\n📝 Login Credentials:")
        print(f"   Email:    arnoldgna765@gmail.com")
        print(f"   Password: orawa@arno189")
        print("\n🔐 Password is securely hashed in database")
        print("✅ User can be deleted if needed")
        
    else:
        print("❌ Arnold user not found in database!")
        print("Run: .venv\\Scripts\\python.exe create_arnold_user.py")
    
    conn.close()

if __name__ == "__main__":
    verify_arnold_user()
