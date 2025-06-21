# DoR-Dash Backend Scripts

This directory contains development and testing scripts for the DoR-Dash backend.

## Test Scripts

- `test_auth.py` - Authentication system testing
- `test_auth_simple.py` - Simplified authentication tests  
- `test_db_connection.py` - Database connectivity tests
- `test_meeting_*.py` - Meeting model and API tests
- `test_migration.py` - Database migration testing
- `test_raw_insert.py` - Raw database insertion tests

## Setup Scripts

- `create_initial_migration.py` - Initial database migration setup
- `create_users_only.py` - User-only database setup
- `create_sadiki_user.py` - Specific user creation script
- `debug_login_500.py` - Login error debugging script

## Usage

These scripts are for development and testing purposes only. They should not be run in production environments.

To run a script:
```bash
cd /app/backend
python scripts/script_name.py
```

## Note

These scripts may contain hardcoded development values and should be reviewed before use.