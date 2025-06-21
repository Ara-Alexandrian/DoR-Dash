# DoR-Dash Backend Utilities

This directory contains utility scripts for database maintenance and system checks.

## Database Utilities

- `cleanup_database.py` - Database cleanup and maintenance
- `fix_enum_columns.py` - Fix enum column definitions
- `fix_passwords.py` - Password hash updates
- `fix_user_table.py` - User table structure fixes
- `inspect_db.py` - Database inspection and diagnostics

## System Checks

- `check_enums.py` - Enum type validation

## Usage

These utilities are for maintenance and administrative tasks. Use with caution as they may modify database data.

To run a utility:
```bash
cd /app/backend
python utils/utility_name.py
```

## Safety Notes

- Always backup your database before running maintenance utilities
- Review utility scripts before execution
- These scripts may contain environment-specific configurations
- Test in development environment before production use