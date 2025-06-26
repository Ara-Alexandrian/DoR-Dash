# Changelog

All notable changes to DoR-Dash will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2024-12-25

### 🎯 Major Features Added

#### Presentation Assignment System
- **Complete presentation assignment workflow** for faculty and administrators
- **Role-based assignment management** with faculty/admin creation rights
- **Student/presenter assignment tracking** with alphabetical sorting
- **Meeting integration** - assignments automatically appear in meeting agendas
- **Grillometer feedback system** - innovative intensity guidance for faculty

#### Grillometer Feedback System
- **Three-dimensional feedback intensity** settings across:
  - **Novelty Assessment** (🧊 Relaxed / 🔥 Moderate / ☢️ Intense)
  - **Methodology Review** (🧊 Relaxed / 🔥 Moderate / ☢️ Intense) 
  - **Presentation Delivery** (🧊 Relaxed / 🔥 Moderate / ☢️ Intense)
- **Faculty guidance tool** to set appropriate feedback expectations
- **Visual interface** with emoji-based intensity indicators

#### Meeting Agenda Integration
- **Assigned Presentations section** in meeting agendas with purple theme
- **Timeline integration** showing presentation assignments in meeting schedules
- **Time allocation calculation** based on assignment duration settings
- **Role-based visibility** for grillometer settings and faculty notes

### 🔧 Technical Improvements

#### Backend Enhancements
- **New API endpoints** for presentation assignment CRUD operations
- **Database schema** with proper foreign key relationships and constraints
- **Enum validation** for presentation types with proper SQLAlchemy mapping
- **Eager loading optimization** with joinedload() for relationship queries
- **JSON serialization fix** for FastAPI responses with SQLAlchemy objects

#### Frontend Enhancements
- **Comprehensive assignment interface** at `/presentation-assignments`
- **Inline editing capabilities** with real-time form validation
- **Checkbox-based requirements** selection with custom input support
- **Responsive design** with proper theme integration across all color schemes
- **Alphabetical sorting** for presenter dropdown selection

### 🐛 Bug Fixes

#### Critical Fixes
- **JSON serialization error** in meeting agenda API resolved
- **Database enum type mismatch** corrected for presentation_type field
- **Case sensitivity issues** in role checks fixed
- **Permission errors** for faculty accessing user lists resolved

### 📚 Documentation Updates

#### New Documentation
- **Complete presentation assignment guide** (`docs/PRESENTATION_ASSIGNMENTS.md`)
- **CLAUDE.md updates** with new system capabilities
- **README.md enhancements** with feature descriptions
- **Comprehensive changelog** documenting all recent improvements

## [2.0.1] - 2024-12-20

### Bug Fixes
- Fixed color contrast issues across alternative themes (dracula, MBP, LSU)
- Resolved glow effect interference with text readability
- Updated theme backgrounds to be significantly darker
- Fixed About page card visibility issues

### UI Improvements
- Removed global heading color overrides
- Enhanced theme system with better contrast ratios
- Improved mobile responsiveness across all themes

## [2.0.0] - 2024-12-15

### Major Features
- Enhanced theme system with institutional branding
- Advanced file management with complete lifecycle support
- AI model upgrade to Gemma 3 4B
- User feedback system for LLM improvements
- Registration system with admin approval
- Faculty announcements system
- Inline editing capabilities
- Dashboard consolidation
- Quality assurance framework

---

## Version History

- **2.1.0** - Presentation Assignment System and Grillometer Implementation
- **2.0.1** - Theme System Bug Fixes and UI Improvements  
- **2.0.0** - Major System Overhaul with Advanced Features