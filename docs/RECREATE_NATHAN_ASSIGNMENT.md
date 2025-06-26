# Recreating Nathan's Lost Presentation Assignment

During the database migration process, Nathan Dobranski's presentation assignment was lost. This document provides instructions for recreating it.

## Background

The lost assignment details (from original documentation):
- **Student**: Nathan Dobranski (student_id: 5)
- **Assigned by**: Ara Alexandrian (assigned_by_id: 4) 
- **Title**: "LLM Information Literacy System Update"
- **Description**: "Present progress on the AI-powered research assistance system"
- **Type**: Research Update
- **Duration**: 20 minutes
- **Requirements**: "Slides, Data/Results, Time Management"
- **Grillometer Settings**: Novelty=2, Methodology=3, Delivery=1
- **Notes**: "Focus on methodology validation and statistical significance"

## Automated Recreation Script

A Python script has been created to automatically recreate this assignment:

### Prerequisites

1. **Backend Dependencies**: Ensure the backend environment is set up with all dependencies installed
2. **Database Access**: The script needs access to the PostgreSQL database
3. **User Existence**: Both Nathan and Ara must exist in the user database

### Running the Script

#### Option 1: Direct Execution (if in DoR-Dash root directory)

```bash
# Navigate to DoR-Dash root directory
cd /path/to/DoR-Dash

# Run the recreation script
python3 scripts/recreate-nathan-assignment.py
```

#### Option 2: Via Docker Container

```bash
# Copy the script into the running container
docker cp scripts/recreate-nathan-assignment.py dor-dash:/app/

# Execute inside the container
docker exec -it dor-dash python3 /app/recreate-nathan-assignment.py
```

#### Option 3: SSH into Container (using MCP SSH)

```bash
# SSH into the DoR-Dash container
ssh root@172.30.98.177

# Run the script from inside the container
cd /app
python3 scripts/recreate-nathan-assignment.py
```

### Script Output

The script will:

1. **Search for Nathan** by name or username containing "nathan"
2. **Search for Ara** by name or username containing "ara" 
3. **Check for existing assignment** to avoid duplicates
4. **Find a recent meeting** to associate with (optional)
5. **Create the assignment** with the original specifications
6. **Display confirmation** with assignment details

### Expected Success Output

```
🔧 Recreating Nathan's Presentation Assignment
==================================================
✅ Found Nathan: Nathan Dobranski (ID: 5)
✅ Found Ara: Ara Alexandrian (ID: 4)
✅ Will associate with meeting: Research Meeting - 2024-12-26 (ID: 11)
🎉 Successfully recreated Nathan's presentation assignment!
   ID: 2
   Title: LLM Information Literacy System Update
   Type: PresentationType.RESEARCH_UPDATE
   Duration: 20 minutes
   Due: 2025-01-02 10:40:15.123456
   Grillometer: Novelty=2, Methodology=3, Delivery=1

✅ Assignment recreation completed successfully!
Nathan can now view and upload files for his presentation assignment.
```

## Manual Recreation (Alternative)

If the automated script fails, you can manually recreate the assignment through the web interface:

### Steps

1. **Login as Faculty/Admin**: Login with Ara's account or any admin account
2. **Navigate to Presentation Assignments**: Go to `/presentation-assignments`
3. **Create New Assignment**: Click "Create New Assignment"
4. **Fill Assignment Details**:
   - **Presenter**: Select "Nathan Dobranski"
   - **Title**: "LLM Information Literacy System Update"
   - **Description**: "Present progress on the AI-powered research assistance system"
   - **Type**: "Research Update"
   - **Duration**: 20 minutes
   - **Requirements**: Check "Slides", "Data/Results", "Time Management"
   - **Grillometer Settings**:
     - Novelty Assessment: Moderate (🔥)
     - Methodology Review: Intense (☢️)
     - Presentation Delivery: Relaxed (🧊)
   - **Notes**: "Focus on methodology validation and statistical significance"
   - **Meeting**: Select an upcoming meeting (optional)
   - **Due Date**: Set appropriate due date

5. **Save Assignment**: Click "Create Assignment"

## Verification

After recreating the assignment, verify it's working correctly:

### Check Assignment Exists

1. **Faculty View**: Login as faculty and check `/presentation-assignments`
2. **Student View**: Login as Nathan and verify the assignment appears in his dashboard
3. **Meeting Agenda**: If associated with a meeting, verify it appears in the meeting agenda

### Test File Upload

1. **Login as Nathan**: Use Nathan's account
2. **Navigate to Assignment**: Go to `/presentation-assignments/{assignment_id}`
3. **Upload Test File**: Try uploading a test presentation file
4. **Verify Download**: Ensure the file can be downloaded

### Check Dashboard Display

1. **Nathan's Dashboard**: Verify the assignment shows up with correct presenter name
2. **Meeting Link**: Ensure any meeting association is displayed correctly
3. **File Upload Interface**: Confirm Nathan can see the file upload section

## Troubleshooting

### Common Issues

#### "Could not find Nathan Dobranski"
- Check if Nathan's user account exists in the database
- Verify the name spelling in the database matches expectations
- List all users to find the correct account

#### "Could not find Ara Alexandrian"  
- Check if Ara's user account exists and has faculty/admin role
- Any faculty or admin user can be used as the assigner if needed

#### "Assignment already exists"
- The script found an existing assignment with similar title
- Check if it's the correct assignment or if duplicate cleanup is needed

#### Import Errors
- Ensure you're running the script from the correct directory
- Verify backend dependencies are installed
- Check Python path configuration

### Database Queries

If manual database investigation is needed:

```sql
-- Check for Nathan's user account
SELECT id, username, full_name, role FROM "user" 
WHERE full_name ILIKE '%Nathan%' OR username ILIKE '%nathan%';

-- Check for Ara's user account  
SELECT id, username, full_name, role FROM "user"
WHERE full_name ILIKE '%Ara%' OR username ILIKE '%ara%';

-- Check for existing presentation assignments
SELECT id, title, student_id, assigned_by_id, created_at 
FROM presentation_assignments 
WHERE title ILIKE '%LLM%' OR title ILIKE '%Information%';

-- List all presentation assignments for verification
SELECT pa.id, pa.title, u.full_name as student_name, ub.full_name as assigned_by
FROM presentation_assignments pa
JOIN "user" u ON pa.student_id = u.id  
JOIN "user" ub ON pa.assigned_by_id = ub.id
ORDER BY pa.created_at DESC;
```

## Post-Recreation Tasks

After successfully recreating the assignment:

1. **Notify Nathan**: Inform Nathan that his assignment has been restored
2. **Verify File Access**: Ensure Nathan can upload presentation files
3. **Update Documentation**: Mark this task as completed in project tracking
4. **Test Integration**: Verify assignment appears correctly in meeting agendas

## Notes

- The recreation script is idempotent - it won't create duplicates if run multiple times
- The assignment will be created with a new due date (1 week from recreation)
- Meeting association is optional and will use the most recent meeting if available
- All original Grillometer settings are preserved as documented