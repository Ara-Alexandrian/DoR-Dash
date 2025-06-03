# pgAdmin Setup Guide

This guide will help you connect pgAdmin to your PostgreSQL database.

## Accessing pgAdmin

1. Open your browser and navigate to [http://192.168.1.21:5050](http://192.168.1.21:5050)
2. Log in with the following credentials:
   - Email: `admin@dor.local`
   - Password: `dor_admin_password`

## Adding a New Server Connection

1. Right-click on "Servers" in the left sidebar and select "Create" > "Server..."
2. In the "General" tab:
   - Name: `DoR PostgreSQL` (or any name you prefer)
3. In the "Connection" tab:
   - Host name/address: `172.30.98.213`
   - Port: `5432`
   - Maintenance database: `DoR`
   - Username: `DoRadmin`
   - Password: `1232`
4. Click "Save"

You should now be connected to your PostgreSQL database and can manage it through the pgAdmin interface.

## Database Structure

The DoR-Dash application uses the following tables:

- `user`: User accounts and authentication
- `studentupdate`: Bi-monthly student updates
- `supportrequest`: Support requests
- `mockexamrequest`: Mock exam scheduling requests
- `fileupload`: Uploaded files metadata
- `assignedpresentation`: Presentation assignments

## Common Tasks

- **Browse Data**: Expand your server > Databases > DoR > Schemas > public > Tables, then right-click on a table and select "View/Edit Data" > "All Rows"
- **Run SQL Queries**: Click the "Query Tool" button (SQL icon) in the top menu
- **Export Data**: Right-click on a table and select "Backup..." to export data
- **Import Data**: Use the "Restore..." option or execute SQL INSERT statements

## Creating an Initial Admin User

If you need to create an initial admin user in the database directly, you can use the following SQL:

```sql
-- First, be sure the alembic migrations have been applied

-- Create an admin user (replace values as needed)
INSERT INTO "user" (
  username, 
  email, 
  hashed_password, 
  role,
  is_active, 
  created_at, 
  updated_at
) VALUES (
  'admin', 
  'admin@example.com', 
  -- This is a bcrypt hash of 'adminpassword' - you should generate your own
  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 
  'admin',
  TRUE, 
  NOW(), 
  NOW()
);
```

## Setting Up Tables Manually

If you need to create the tables manually (though Alembic should handle this automatically), here's a SQL script for the main tables:

```sql
-- Users table
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(100) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'student', -- 'student' or 'admin'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Student updates table
CREATE TABLE studentupdate (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    progress_text TEXT NOT NULL,
    challenges_text TEXT NOT NULL,
    next_steps_text TEXT NOT NULL,
    submission_date TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Support requests table
CREATE TABLE supportrequest (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    topic VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    submission_date TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Mock exam requests table
CREATE TABLE mockexamrequest (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    preferred_session VARCHAR(100) NOT NULL,
    focus_topics TEXT NOT NULL,
    presentation_length INTEGER NOT NULL DEFAULT 30,
    submission_date TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- File uploads table
CREATE TABLE fileupload (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    student_update_id INTEGER REFERENCES studentupdate(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_date TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Assigned presentations table
CREATE TABLE assignedpresentation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    meeting_date TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'scheduled',
    is_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

For more information, refer to the [pgAdmin documentation](https://www.pgadmin.org/docs/).