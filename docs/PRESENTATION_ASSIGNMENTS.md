# Presentation Assignment System Documentation

## Overview

The DoR-Dash Presentation Assignment System provides a comprehensive solution for faculty and administrators to assign, track, and manage student presentations within the research meeting framework. The system integrates seamlessly with meeting agendas and includes a novel "Grillometer" feedback intensity system.

## System Architecture

### Database Schema

The system is built around the `presentation_assignments` table with the following structure:

```sql
CREATE TABLE presentation_assignments (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES user(id),
    assigned_by_id INTEGER NOT NULL REFERENCES user(id),
    meeting_id INTEGER REFERENCES meeting(id),
    
    -- Assignment Details
    title VARCHAR(500) NOT NULL,
    description TEXT,
    presentation_type presentation_type_enum NOT NULL,
    duration_minutes INTEGER,
    requirements TEXT,
    
    -- Scheduling
    due_date TIMESTAMP,
    assigned_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Status Tracking
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completion_date TIMESTAMP,
    
    -- Grillometer Settings (1-3 scale)
    grillometer_novelty INTEGER,
    grillometer_methodology INTEGER,
    grillometer_delivery INTEGER,
    
    -- Metadata
    notes TEXT,
    extra_data JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Presentation Types

The system supports multiple presentation types via enum:

- `CASUAL` - Informal research update or discussion
- `MOCK_DEFENSE` - Practice run for thesis or dissertation defense
- `PRE_CONFERENCE` - Practice for upcoming conference presentation
- `THESIS_PROPOSAL` - Formal thesis proposal presentation
- `DISSERTATION_DEFENSE` - Final dissertation defense
- `JOURNAL_CLUB` - Literature review presentation
- `RESEARCH_UPDATE` - Progress update on current research

## API Endpoints

### Core Assignment Endpoints

- **GET** `/api/v1/presentation-assignments/` - List all assignments (filtered by role)
- **POST** `/api/v1/presentation-assignments/` - Create new assignment (faculty/admin only)
- **GET** `/api/v1/presentation-assignments/{id}` - Get specific assignment
- **PUT** `/api/v1/presentation-assignments/{id}` - Update assignment
- **DELETE** `/api/v1/presentation-assignments/{id}` - Delete assignment

### Meeting Integration

- **GET** `/api/v1/meetings/{id}/agenda` - Returns meeting agenda including presentation assignments

### Request/Response Examples

#### Create Assignment Request
```json
{
  "student_id": 5,
  "meeting_id": 11,
  "title": "LLM Information Literacy System Update",
  "description": "Present progress on the AI-powered research assistance system",
  "presentation_type": "research_update",
  "duration_minutes": 20,
  "requirements": "Slides, Data/Results, Time Management",
  "grillometer_novelty": 2,
  "grillometer_methodology": 3,
  "grillometer_delivery": 1,
  "notes": "Focus on methodology validation and statistical significance"
}
```

#### Assignment Response
```json
{
  "id": 2,
  "student_id": 5,
  "student_name": "Nathan Dobranski",
  "assigned_by_id": 4,
  "assigned_by_name": "Ara Alexandrian",
  "meeting_id": 11,
  "title": "LLM Information Literacy System Update",
  "description": "Present progress on the AI-powered research assistance system",
  "presentation_type": "research_update",
  "duration_minutes": 20,
  "requirements": "Slides, Data/Results, Time Management",
  "due_date": "2024-12-28T10:00:00Z",
  "assigned_date": "2024-12-25T23:05:36Z",
  "is_completed": false,
  "completion_date": null,
  "grillometer_novelty": 2,
  "grillometer_methodology": 3,
  "grillometer_delivery": 1,
  "notes": "Focus on methodology validation and statistical significance",
  "created_at": "2024-12-25T23:05:36Z",
  "updated_at": "2024-12-25T23:05:36Z"
}
```

## Grillometer System

The Grillometer is a unique feature that allows faculty to set feedback intensity expectations across three dimensions:

### Scale Definition
- **1 (🧊 Relaxed)**: Gentle feedback, focus on encouragement
- **2 (🔥 Moderate)**: Standard academic feedback level
- **3 (☢️ Intense)**: Rigorous critical evaluation

### Dimensions

#### Novelty Assessment (`grillometer_novelty`)
How critically faculty should assess the originality and innovation of the research:
- **Relaxed**: Focus on understanding and clarity over novelty
- **Moderate**: Standard evaluation of contribution significance
- **Intense**: Rigorous assessment of innovation and uniqueness

#### Methodology Review (`grillometer_methodology`) 
How rigorously faculty should examine the research methods:
- **Relaxed**: Basic methodology review, focus on learning
- **Moderate**: Standard methodological scrutiny
- **Intense**: Comprehensive evaluation of experimental design and validity

#### Presentation Delivery (`grillometer_delivery`)
How critically faculty should evaluate presentation skills:
- **Relaxed**: Supportive feedback on communication skills
- **Moderate**: Standard presentation evaluation
- **Intense**: Professional-level presentation standards

### Example Usage
A faculty member might set a 3-2-1 grillometer for a PhD student's mock defense:
- **Novelty (3)**: Intensely evaluate the research contribution
- **Methodology (2)**: Standard review of experimental approach  
- **Delivery (1)**: Relaxed on presentation skills to reduce stress

## Frontend Implementation

### Assignment Management Page (`/presentation-assignments`)

The main interface provides:
- **Assignment List**: All assignments with filtering by status and user
- **Create/Edit Forms**: Comprehensive assignment creation with inline editing
- **Grillometer Controls**: Visual interface for setting feedback intensity
- **Requirements Checkboxes**: Structured requirement selection
- **Role-based Access**: Faculty/admin can create, students can view their assignments

### Meeting Agenda Integration

Presentation assignments appear in meeting agendas in two places:

#### 1. Assigned Presentations Section
- **Purple-themed section** showing all assignments for the meeting
- **Detailed view** with grillometer settings (faculty-only)
- **Completion status** and assignment metadata
- **Faculty notes** (role-restricted)

#### 2. Presentation Schedule Timeline
- **Time-slot calculation** based on meeting start time and duration
- **Visual highlighting** for assigned presenters
- **Integration** with student updates and general agenda items

### UI Components

#### Grillometer Display
```svelte
<div class="text-lg mb-1">
  {#if assignment.grillometer_novelty === 1}🧊
  {:else if assignment.grillometer_novelty === 2}🔥
  {:else if assignment.grillometer_novelty === 3}☢️
  {:else}❓{/if}
</div>
```

#### Requirements Display
- **Checkbox format** for clear requirement tracking
- **Custom requirements** with text input support
- **Backward compatibility** with string-based requirements

## Role-Based Access Control

### Permissions Matrix

| Action | Student | Faculty | Admin |
|--------|---------|---------|-------|
| View own assignments | ✅ | ✅ | ✅ |
| View all assignments | ❌ | ✅ | ✅ |
| Create assignments | ❌ | ✅ | ✅ |
| Edit assignments | ❌ | ✅ | ✅ |
| Delete assignments | ❌ | ✅ | ✅ |
| View grillometer settings | ❌ | ✅ | ✅ |
| View faculty notes | ❌ | ✅ | ✅ |
| Mark completion | ✅ | ✅ | ✅ |

### Implementation
- **Backend**: Role checks in FastAPI dependencies
- **Frontend**: Conditional rendering based on user role
- **Database**: User role stored in JWT token and validated

## Integration Points

### Meeting System Integration
- **Foreign key relationship** to meetings table
- **Automatic agenda inclusion** when meeting_id is set
- **Timeline calculation** for meeting schedules
- **Due date synchronization** with meeting dates

### User Management Integration
- **Student assignment** via user_id foreign key
- **Faculty tracking** via assigned_by_id relationship
- **Role-based UI** rendering and API access

### File Upload Integration
While not yet implemented, the system is designed to support:
- **Presentation files** attached to assignments
- **Supporting materials** upload capability
- **Version tracking** for iterative submissions

## Recent Technical Improvements

### Database Enhancements
- **Enum Type Conversion**: Changed `presentation_type` from String to proper Enum for validation
- **Foreign Key Optimization**: Proper relationships with cascade deletion
- **Index Optimization**: Database indexes on frequently queried fields

### API Improvements
- **JSON Serialization Fix**: Resolved FastAPI serialization of SQLAlchemy objects
- **Eager Loading**: Optimized database queries with relationship preloading
- **Error Handling**: Comprehensive error responses and validation

### UI/UX Enhancements
- **Icon Updates**: Changed to ice cube (🧊), flame (🔥), nuclear trefoil (☢️)
- **Terminology**: "Student" changed to "Presenter" for inclusivity
- **Alphabetical Sorting**: Presenter dropdown sorted by name
- **Visual Hierarchy**: Purple theme for assignment sections

## Development Notes

### Testing Considerations
- **Database transactions** for assignment creation/modification
- **Role permissions** validation in API tests
- **Frontend component** testing for grillometer controls
- **Integration testing** for meeting agenda inclusion

### Performance Considerations
- **Eager loading** of relationships to prevent N+1 queries
- **Database indexing** on foreign keys and frequently filtered fields
- **Caching strategies** for meeting agenda responses
- **Pagination** for large assignment lists

### Security Considerations
- **SQL injection prevention** via SQLAlchemy ORM
- **Authorization checks** on all endpoints
- **Input validation** for all user-provided data
- **Faculty notes isolation** from student view

## Future Enhancements

### Planned Features
- **File attachment** support for presentation materials
- **Email notifications** for assignment deadlines
- **Calendar integration** with meeting schedules
- **Presentation feedback** collection system
- **Analytics dashboard** for presentation tracking

### Technical Debt
- **Legacy string requirements** backward compatibility can be removed after migration
- **Error message localization** for international users
- **API versioning** for future breaking changes
- **Database migration scripts** for production deployments

## Troubleshooting

### Common Issues

#### 500 Error on Meeting Agenda
**Symptom**: Internal server error when accessing meeting agenda
**Cause**: JSON serialization of SQLAlchemy objects
**Solution**: Ensure Meeting object is converted to dictionary before JSON response

#### Assignment Not Appearing in Agenda
**Symptom**: Assignment exists but doesn't show in meeting agenda
**Cause**: Missing meeting_id or incorrect eager loading
**Solution**: Verify meeting_id is set and joinedload() includes assignment relationships

#### Permission Denied for Faculty
**Symptom**: Faculty user cannot create assignments
**Cause**: Case sensitivity in role checks
**Solution**: Use `.toUpperCase()` or `.upper()` for role comparisons

#### Grillometer Icons Not Displaying
**Symptom**: Question marks instead of emoji icons
**Cause**: Missing font support or incorrect value handling
**Solution**: Verify emoji support and check grillometer value ranges (1-3)

### Debug Commands

```bash
# Check assignment database entries
docker exec -it dor-dash-backend psql -U postgres -d dor_dash -c "SELECT * FROM presentation_assignments;"

# Verify user roles
docker exec -it dor-dash-backend psql -U postgres -d dor_dash -c "SELECT username, role FROM user;"

# Check meeting relationships
docker exec -it dor-dash-backend psql -U postgres -d dor_dash -c "SELECT pa.id, pa.title, m.title as meeting_title FROM presentation_assignments pa JOIN meeting m ON pa.meeting_id = m.id;"
```

## Conclusion

The Presentation Assignment System represents a significant enhancement to the DoR-Dash platform, providing structured presentation management with innovative feedback guidance through the Grillometer system. The integration with meeting agendas creates a seamless workflow from assignment creation to presentation delivery, supporting the academic research community's collaborative needs.