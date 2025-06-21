#!/usr/bin/env python3
"""
Database check script for DoR-Dash - Works with minimal Python installation
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_database_connectivity():
    """Check database connectivity using pg_isready or nc"""
    db_host = os.environ.get("POSTGRES_SERVER", "172.30.98.213")
    db_port = os.environ.get("POSTGRES_PORT", "5432")
    
    print("=== DATABASE CONNECTIVITY CHECK ===")
    print(f"Checking connection to {db_host}:{db_port}")
    
    # Try using netcat to check if port is open
    try:
        result = subprocess.run(
            ["nc", "-z", db_host, str(db_port)], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ Database server is reachable at {db_host}:{db_port}")
            return True
        else:
            print(f"✗ Database server is NOT reachable at {db_host}:{db_port}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ Connection to {db_host}:{db_port} timed out")
        return False
    except FileNotFoundError:
        print("✗ netcat (nc) not available, cannot check connectivity")
        return False

def check_database_files():
    """Check for database-related files and configurations"""
    print("\n=== DATABASE FILES CHECK ===")
    
    # Check for database models
    models_dir = Path("app/db/models")
    if models_dir.exists():
        print(f"✓ Models directory exists: {models_dir}")
        model_files = list(models_dir.glob("*.py"))
        print(f"  Found {len(model_files)} model files:")
        for model_file in model_files:
            print(f"    - {model_file.name}")
    else:
        print(f"✗ Models directory not found: {models_dir}")
    
    # Check for migrations
    migrations_dir = Path("alembic/versions")
    if migrations_dir.exists():
        print(f"✓ Migrations directory exists: {migrations_dir}")
        migration_files = list(migrations_dir.glob("*.py"))
        print(f"  Found {len(migration_files)} migration files:")
        for migration_file in sorted(migration_files):
            print(f"    - {migration_file.name}")
    else:
        print(f"✗ Migrations directory not found: {migrations_dir}")
    
    # Check for alembic config
    alembic_ini = Path("alembic.ini")
    if alembic_ini.exists():
        print(f"✓ Alembic config exists: {alembic_ini}")
    else:
        print(f"✗ Alembic config not found: {alembic_ini}")

def check_user_model_structure():
    """Analyze the user model for potential issues"""
    print("\n=== USER MODEL ANALYSIS ===")
    
    user_model_path = Path("app/db/models/user.py")
    if not user_model_path.exists():
        print(f"✗ User model not found: {user_model_path}")
        return
    
    try:
        with open(user_model_path, 'r') as f:
            content = f.read()
        
        # Check for common issues
        issues = []
        
        # Check for password hash field
        if "hashed_password" in content:
            print("✓ Password hash field found")
        else:
            issues.append("Password hash field not found")
        
        # Check for role field
        if "role:" in content:
            print("✓ Role field found")
        else:
            issues.append("Role field not found")
        
        # Check for UserRole enum
        if "class UserRole" in content:
            print("✓ UserRole enum defined")
        else:
            issues.append("UserRole enum not found")
        
        # Check for is_active field
        if "is_active" in content:
            print("✓ is_active field found")
        else:
            issues.append("is_active field not found")
        
        # Check for relationships
        if "relationship(" in content:
            print("✓ Relationships defined")
        else:
            issues.append("No relationships found")
        
        # Check for potential issues
        if "avatar_url" in content and "# Temporarily disabled" in content:
            print("⚠ Warning: avatar_url field is temporarily disabled")
        
        if issues:
            print("✗ Issues found:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("✓ User model structure looks good")
    
    except Exception as e:
        print(f"✗ Error analyzing user model: {e}")

def check_auth_endpoint():
    """Check the authentication endpoint for potential issues"""
    print("\n=== AUTH ENDPOINT ANALYSIS ===")
    
    auth_path = Path("app/api/endpoints/auth.py")
    if not auth_path.exists():
        print(f"✗ Auth endpoint not found: {auth_path}")
        return
    
    try:
        with open(auth_path, 'r') as f:
            content = f.read()
        
        # Check for potential issues
        issues = []
        warnings = []
        
        # Check for error handling
        if "try:" in content and "except" in content:
            print("✓ Error handling found")
        else:
            issues.append("Limited error handling")
        
        # Check for password verification
        if "verify_password" in content:
            print("✓ Password verification implemented")
        else:
            issues.append("Password verification not found")
        
        # Check for database session handling
        if "get_sync_db" in content:
            print("✓ Database session handling found")
        else:
            issues.append("Database session handling not found")
        
        # Check for admin initialization
        if "initialize_admin" in content:
            print("✓ Admin initialization found")
            # Check for correct admin password
            if '"123"' in content:
                print("✓ Admin password set to '123'")
            else:
                warnings.append("Admin password might not be set correctly")
        else:
            issues.append("Admin initialization not found")
        
        # Check for debugging statements
        debug_count = content.count("print(f\"DEBUG:")
        if debug_count > 0:
            print(f"✓ Debug logging enabled ({debug_count} debug statements)")
        else:
            warnings.append("No debug logging found")
        
        if issues:
            print("✗ Issues found:")
            for issue in issues:
                print(f"    - {issue}")
        
        if warnings:
            print("⚠ Warnings:")
            for warning in warnings:
                print(f"    - {warning}")
        
        if not issues and not warnings:
            print("✓ Auth endpoint structure looks good")
    
    except Exception as e:
        print(f"✗ Error analyzing auth endpoint: {e}")

def check_database_config():
    """Check database configuration"""
    print("\n=== DATABASE CONFIGURATION ===")
    
    config_path = Path("app/core/config.py")
    if not config_path.exists():
        print(f"✗ Config file not found: {config_path}")
        return
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Extract database settings
        db_settings = {}
        
        import re
        
        # Look for database configuration
        patterns = {
            "POSTGRES_SERVER": r'POSTGRES_SERVER.*?=.*?"([^"]+)"',
            "POSTGRES_PORT": r'POSTGRES_PORT.*?=.*?"([^"]+)"',
            "POSTGRES_USER": r'POSTGRES_USER.*?=.*?"([^"]+)"',
            "POSTGRES_PASSWORD": r'POSTGRES_PASSWORD.*?=.*?"([^"]+)"',
            "POSTGRES_DB": r'POSTGRES_DB.*?=.*?"([^"]+)"'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                db_settings[key] = match.group(1)
            else:
                # Try with environment variable format
                env_pattern = rf'{key}.*?=.*?os\.environ\.get\(".*?",\s*"([^"]+)"\)'
                match = re.search(env_pattern, content)
                if match:
                    db_settings[key] = match.group(1)
        
        print("Database configuration:")
        for key, value in db_settings.items():
            if "PASSWORD" in key:
                print(f"  {key}: {'*' * len(value)}")
            else:
                print(f"  {key}: {value}")
        
        # Check for both sync and async database URLs
        if "SQLALCHEMY_DATABASE_URI" in content:
            print("✓ Database URI configuration found")
        else:
            print("✗ Database URI configuration not found")
        
        if "SQLALCHEMY_DATABASE_URI_SYNC" in content:
            print("✓ Sync database URI configuration found")
        else:
            print("✗ Sync database URI configuration not found")
    
    except Exception as e:
        print(f"✗ Error analyzing database config: {e}")

def check_migration_status():
    """Check migration files for potential issues"""
    print("\n=== MIGRATION STATUS ===")
    
    migrations_dir = Path("alembic/versions")
    if not migrations_dir.exists():
        print(f"✗ Migrations directory not found: {migrations_dir}")
        return
    
    migration_files = list(migrations_dir.glob("*.py"))
    print(f"Found {len(migration_files)} migration files")
    
    # Check for recent migrations
    recent_migrations = []
    for migration_file in migration_files:
        if any(keyword in migration_file.name for keyword in 
               ["presentation_assignments", "cascade", "clean_schema"]):
            recent_migrations.append(migration_file.name)
    
    if recent_migrations:
        print("Recent migrations:")
        for migration in recent_migrations:
            print(f"  - {migration}")
    
    # Check for potential issues in migration files
    issues = []
    for migration_file in migration_files:
        try:
            with open(migration_file, 'r') as f:
                content = f.read()
            
            # Check for cascade constraints
            if "cascade" in content.lower():
                print(f"✓ Cascade constraints found in {migration_file.name}")
            
            # Check for enum handling
            if "enum" in content.lower() and "create" in content.lower():
                print(f"✓ Enum handling found in {migration_file.name}")
        
        except Exception as e:
            issues.append(f"Error reading {migration_file.name}: {e}")
    
    if issues:
        print("Migration issues:")
        for issue in issues:
            print(f"  - {issue}")

def generate_database_report():
    """Generate a comprehensive database check report"""
    print("DoR-Dash Database Check Report")
    print("=" * 50)
    
    # Run all checks
    connectivity = check_database_connectivity()
    check_database_files()
    check_user_model_structure()
    check_auth_endpoint()
    check_database_config()
    check_migration_status()
    
    # Summary
    print("\n=== SUMMARY ===")
    if connectivity:
        print("✓ Database server is reachable")
    else:
        print("✗ Database server connectivity issue")
    
    print("\n=== RECOMMENDATIONS ===")
    
    if not connectivity:
        print("1. Check database server status and network connectivity")
        print("2. Verify database credentials in environment variables")
    
    print("3. To test login functionality, ensure:")
    print("   - cerebro user exists with password '123'")
    print("   - All required tables exist")
    print("   - Cascade constraints are properly set")
    
    print("4. If 500 errors persist during login:")
    print("   - Check server logs for detailed error messages")
    print("   - Verify database schema matches model definitions")
    print("   - Run database migrations if needed")
    
    print("\n=== NEXT STEPS ===")
    print("1. If database is reachable, try running migration scripts")
    print("2. If login still fails, check application logs")
    print("3. Consider running the fix_passwords.py script")

if __name__ == "__main__":
    generate_database_report()