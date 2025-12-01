# services/user_auth_service.py
"""
Enhanced User Authentication Service with Professional Security Practices
Implements sign-up, login, and credential management for multi-platform integration
"""

import jwt
import os
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import sqlite3
from cryptography.fernet import Fernet

from memory.db import get_conn, CacheManager

# Security Configuration
SECRET_KEY = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_HOURS = 24

# Encryption for sensitive credentials
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

class UserAuthService:
    """Enhanced authentication service with security best practices"""
    
    @staticmethod
    def register_user(username: str, email: str, password: str, full_name: str = None) -> Tuple[bool, str, Optional[int]]:
        """
        Register a new user with secure password hashing
        Returns: (success, message, user_id)
        """
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            # Validate inputs
            if not username or not email or not password:
                return False, "Username, email, and password are required", None
            
            # Check if user already exists
            cur.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
            existing_user = cur.fetchone()
            if existing_user:
                return False, "User with this email or username already exists", None
            
            # Hash password with bcrypt
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert new user
            cur.execute("""
                INSERT INTO users (username, email, password_hash, full_name, created_at, is_active)
                VALUES (?, ?, ?, ?, datetime('now'), 1)
            """, (username, email, password_hash, full_name))
            
            user_id = cur.lastrowid
            conn.commit()
            
            # Invalidate user list cache
            CacheManager.invalidate("all_users")
            
            return True, "User registered successfully", user_id
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return False, f"Registration failed: {str(e)}", None
        except Exception as e:
            conn.rollback()
            return False, f"Registration failed: {str(e)}", None
        finally:
            conn.close()
    
    @staticmethod
    def authenticate_user(username_or_email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user with email/username and password
        Returns: (success, message, user_data)
        """
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            # Find user by email or username
            cur.execute("""
                SELECT id, username, email, full_name, password_hash, created_at, last_login, is_active 
                FROM users 
                WHERE (email = ? OR username = ?) AND is_active = 1
            """, (username_or_email, username_or_email))
            
            user_row = cur.fetchone()
            if not user_row:
                return False, "Invalid credentials", None
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user_row['password_hash'].encode('utf-8')):
                return False, "Invalid credentials", None
            
            # Update last login
            cur.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (user_row['id'],))
            conn.commit()
            
            # Prepare user data
            user_data = {
                'id': user_row['id'],
                'username': user_row['username'],
                'email': user_row['email'],
                'full_name': user_row['full_name'],
                'created_at': user_row['created_at'],
                'last_login': user_row['last_login']
            }
            
            return True, "Authentication successful", user_data
            
        except Exception as e:
            return False, f"Authentication failed: {str(e)}", None
        finally:
            conn.close()
    
    @staticmethod
    def generate_jwt_token(user_id: int, username: str, email: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXP_DELTA_HOURS),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def save_platform_credentials(
        user_id: int, 
        platform: str, 
        username: str, 
        password: str = None,
        session_cookie: str = None
    ) -> bool:
        """
        Save encrypted platform credentials for user
        Supports LeetCode and GitHub credentials
        """
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            # Encrypt sensitive data
            encrypted_password = cipher_suite.encrypt(password.encode()).decode() if password else None
            encrypted_session = cipher_suite.encrypt(session_cookie.encode()).decode() if session_cookie else None
            
            # Save or update credentials
            cur.execute("""
                INSERT OR REPLACE INTO user_credentials 
                (user_id, platform, username, encrypted_token, session_cookie, last_synced, sync_status)
                VALUES (?, ?, ?, ?, ?, datetime('now'), 'pending')
            """, (user_id, platform, username, encrypted_password, encrypted_session))
            
            conn.commit()
            
            # Invalidate user cache
            CacheManager.invalidate_user(user_id)
            
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving credentials: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_platform_credentials(user_id: int, platform: str) -> Optional[Dict]:
        """Retrieve and decrypt platform credentials for user"""
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT id, user_id, platform, username, encrypted_token, session_cookie, last_synced, sync_status
                FROM user_credentials 
                WHERE user_id = ? AND platform = ?
            """, (user_id, platform))
            
            row = cur.fetchone()
            if not row:
                return None
            
            # Decrypt sensitive data
            decrypted_token = None
            decrypted_session = None
            
            if row['encrypted_token']:
                try:
                    decrypted_token = cipher_suite.decrypt(row['encrypted_token'].encode()).decode()
                except Exception:
                    pass  # Invalid token or decryption failed
            
            if row['session_cookie']:
                try:
                    decrypted_session = cipher_suite.decrypt(row['session_cookie'].encode()).decode()
                except Exception:
                    pass  # Invalid session or decryption failed
            
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'platform': row['platform'],
                'username': row['username'],
                'password': decrypted_token,
                'session_cookie': decrypted_session,
                'last_synced': row['last_synced'],
                'sync_status': row['sync_status']
            }
            
        except Exception as e:
            print(f"Error retrieving credentials: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_user_profile(user_id: int) -> Optional[Dict]:
        """Get complete user profile with platform credentials"""
        conn = get_conn()
        cur = conn.cursor()
        
        try:
            # Get user base info
            cur.execute("""
                SELECT id, username, email, full_name, created_at, last_login, is_active
                FROM users 
                WHERE id = ? AND is_active = 1
            """, (user_id,))
            
            user_row = cur.fetchone()
            if not user_row:
                return None
            
            user_profile = {
                'id': user_row['id'],
                'username': user_row['username'],
                'email': user_row['email'],
                'full_name': user_row['full_name'],
                'created_at': user_row['created_at'],
                'last_login': user_row['last_login'],
                'platforms': {}
            }
            
            # Get platform credentials
            cur.execute("""
                SELECT platform, username, last_synced, sync_status
                FROM user_credentials 
                WHERE user_id = ?
            """, (user_id,))
            
            platform_rows = cur.fetchall()
            for row in platform_rows:
                user_profile['platforms'][row['platform']] = {
                    'username': row['username'],
                    'last_synced': row['last_synced'],
                    'sync_status': row['sync_status']
                }
            
            return user_profile
            
        except Exception as e:
            print(f"Error retrieving user profile: {e}")
            return None
        finally:
            conn.close()

# Global service instance
auth_service = UserAuthService()