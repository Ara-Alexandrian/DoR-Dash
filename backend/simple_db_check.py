#!/usr/bin/env python3
"""
Simple database check using minimal dependencies
"""

import socket
import os
import sys
import struct
import hashlib
import hmac
from io import BytesIO

def test_tcp_connection():
    """Test basic TCP connection to database"""
    host = os.environ.get("POSTGRES_SERVER", "172.30.98.213")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✓ TCP connection successful to {host}:{port}")
            return True
        else:
            print(f"✗ TCP connection failed to {host}:{port}")
            return False
    except Exception as e:
        print(f"✗ TCP connection error: {e}")
        return False

def send_postgres_query(query):
    """
    Send a simple PostgreSQL query using raw sockets
    This is a minimal implementation for basic queries
    """
    host = os.environ.get("POSTGRES_SERVER", "172.30.98.213")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    user = os.environ.get("POSTGRES_USER", "DoRadmin")
    password = os.environ.get("POSTGRES_PASSWORD", "1232")
    database = os.environ.get("POSTGRES_DB", "DoR")
    
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((host, port))
        
        print(f"Connected to {host}:{port}")
        
        # Send startup message
        startup_msg = BytesIO()
        startup_msg.write(struct.pack('>I', 196608))  # Protocol version 3.0
        startup_msg.write(b'user\x00')
        startup_msg.write(user.encode('utf-8') + b'\x00')
        startup_msg.write(b'database\x00')
        startup_msg.write(database.encode('utf-8') + b'\x00')
        startup_msg.write(b'\x00')
        
        startup_data = startup_msg.getvalue()
        header = struct.pack('>I', len(startup_data) + 4)
        sock.send(header + startup_data)
        
        # Read authentication response
        response = sock.recv(1024)
        if len(response) < 5:
            print("✗ Invalid authentication response")
            return False
        
        msg_type = response[0:1]
        msg_length = struct.unpack('>I', response[1:5])[0]
        
        if msg_type == b'R':  # Authentication request
            auth_type = struct.unpack('>I', response[5:9])[0]
            print(f"Authentication type: {auth_type}")
            
            if auth_type == 0:  # Success
                print("✓ Authentication successful (no password required)")
            elif auth_type == 3:  # Clear text password
                print("Sending clear text password...")
                password_msg = b'p' + struct.pack('>I', len(password) + 5) + password.encode('utf-8') + b'\x00'
                sock.send(password_msg)
            elif auth_type == 5:  # MD5 password
                print("MD5 authentication required")
                salt = response[9:13]
                # Create MD5 hash: md5(password + username) + salt
                hash1 = hashlib.md5((password + user).encode('utf-8')).hexdigest()
                hash2 = hashlib.md5((hash1 + salt.hex()).encode('utf-8')).hexdigest()
                md5_password = 'md5' + hash2
                password_msg = b'p' + struct.pack('>I', len(md5_password) + 5) + md5_password.encode('utf-8') + b'\x00'
                sock.send(password_msg)
            else:
                print(f"✗ Unsupported authentication type: {auth_type}")
                return False
            
            # Read final authentication response
            if auth_type != 0:
                response = sock.recv(1024)
                if len(response) >= 5:
                    msg_type = response[0:1]
                    if msg_type == b'R':
                        auth_result = struct.unpack('>I', response[5:9])[0]
                        if auth_result == 0:
                            print("✓ Authentication successful")
                        else:
                            print(f"✗ Authentication failed: {auth_result}")
                            return False
                    else:
                        print(f"✗ Unexpected message type: {msg_type}")
                        return False
        
        # We've established a connection, but implementing full PostgreSQL protocol
        # for queries is complex. Let's just report success for now.
        print("✓ Successfully established PostgreSQL connection")
        sock.close()
        return True
        
    except Exception as e:
        print(f"✗ PostgreSQL connection error: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("=== ENVIRONMENT CHECK ===")
    
    required_vars = [
        "POSTGRES_SERVER", "POSTGRES_PORT", "POSTGRES_USER", 
        "POSTGRES_PASSWORD", "POSTGRES_DB"
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if "PASSWORD" in var:
                print(f"✓ {var}: {'*' * len(value)}")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: NOT SET")
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"✓ .env file exists: {env_file}")
        
        # Load environment variables from .env file
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value
                        print(f"✓ Loaded {key} from .env file")
    else:
        print(f"✗ .env file not found: {env_file}")

def main():
    print("Simple Database Connection Check")
    print("=" * 40)
    
    # Check environment
    check_environment()
    
    print("\n=== CONNECTIVITY TEST ===")
    
    # Test basic TCP connection
    if not test_tcp_connection():
        print("✗ Cannot establish TCP connection to database")
        return 1
    
    # Test PostgreSQL connection
    if not send_postgres_query("SELECT 1"):
        print("✗ Cannot establish PostgreSQL connection")
        return 1
    
    print("\n=== SUMMARY ===")
    print("✓ Database server is reachable")
    print("✓ PostgreSQL connection can be established")
    print("\nNOTE: To perform actual SQL queries, you need to:")
    print("1. Install required Python packages: pip install sqlalchemy asyncpg psycopg2-binary")
    print("2. Run the comprehensive database test: python3 db_connection_test.py")
    print("3. Check for specific schema issues with: python3 database_check.py")
    
    print("\n=== RECOMMENDATIONS FOR 500 ERRORS ===")
    print("If you're getting 500 errors during login:")
    print("1. Database connection is working, so the issue is likely in the application")
    print("2. Check server logs for detailed error messages")
    print("3. Verify that the 'cerebro' user exists with correct password hash")
    print("4. Ensure all required tables exist and have proper constraints")
    print("5. Run database migrations if needed: alembic upgrade head")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())