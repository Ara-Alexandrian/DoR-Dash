# DoR-Dash Agent Subroutines & Quick Commands

This file contains quick subroutines for each specialized agent to reduce typing and streamline common tasks.

## 🔧 **CRITICAL**: All Agent Deployments Must Reference CLAUDE.md

**Every agent deployment MUST inherit the full context from CLAUDE.md, especially:**
- **Deployment Information**: dd.kronisto.net (172.30.98.177), reverse proxy setup, port configurations
- **Database Connections**: PostgreSQL (172.30.98.213:5432), Redis (172.30.98.214:6379) 
- **MCP Server Tools**: Available database, filesystem, git, ssh access tools
- **Live Data Warnings**: Current production status and data safety requirements
- **Authentication Details**: Current user accounts (cerebro/admin, aalexandrian/student)

All commands below automatically inherit this context through individual agent files that reference `/config/workspace/gitea/DoR-Dash/CLAUDE.md`.

## 🌐 Website Testing Agent Subroutines

### Quick Deploy
```
Task(description="Test Web", prompt="Deploy Website Testing Agent. FIRST: Read /config/workspace/gitea/DoR-Dash/CLAUDE.md for full context including deployment at dd.kronisto.net (172.30.98.177), database connections, and live data warnings. THEN: Run comprehensive test suite: status check, auth testing, API validation, error handling. Provide executive summary with pass/fail status.")
```

### Specific Test Types
```
# Authentication Only
Task(description="Auth Test", prompt="Website Testing Agent: Test only authentication with all user types (admin/student/faculty). Report login success/failure for each account.")

# API Testing Only  
Task(description="API Test", prompt="Website Testing Agent: Comprehensive API endpoint testing. Test all /api routes, validate responses, check error handling.")

# UI Testing Only
Task(description="UI Test", prompt="Website Testing Agent: Frontend testing - page loads, form validation, responsive design, user workflows.")

# Performance Test
Task(description="Perf Test", prompt="Website Testing Agent: Performance testing - page load times, API response times, stress testing.")

# Regression Test
Task(description="Regression", prompt="Website Testing Agent: Full regression test suite after changes. Compare against known working state.")
```

## 🗄️ Database Management Agent Subroutines

### Quick Deploy
```
Task(description="DB Admin", prompt="Deploy Database Management Agent. FIRST: Read /config/workspace/gitea/DoR-Dash/CLAUDE.md for full deployment context including PostgreSQL at 172.30.98.213:5432 (DoRadmin:1232@DoR), MCP tools, and live data safety. THEN: Check database health, verify schema integrity, ensure all tables exist with proper data.")
```

### Specific Database Tasks
```
# Schema Check
Task(description="Schema Check", prompt="Database Agent: Verify database schema integrity, check all tables exist, validate foreign keys and constraints.")

# Migration Management
Task(description="DB Migrate", prompt="Database Agent: Check current migration status, run pending migrations if needed, handle any migration conflicts.")

# Data Integrity
Task(description="Data Check", prompt="Database Agent: Comprehensive data integrity check - orphaned records, constraint violations, data consistency.")

# Performance Analysis
Task(description="DB Perf", prompt="Database Agent: Database performance analysis - slow queries, index usage, connection pooling, optimization recommendations.")

# Backup & Recovery
Task(description="DB Backup", prompt="Database Agent: Create database backup, verify backup integrity, document recovery procedures.")

# User Management
Task(description="User DB", prompt="Database Agent: User account management - verify test accounts, check roles, password hashes, authentication data.")

# Schema Repair
Task(description="Schema Fix", prompt="Database Agent: Emergency schema repair - fix broken tables, recreate missing structures, resolve constraint issues.")
```

## 🎨 UI Management Agent Subroutines

### Quick Deploy
```
Task(description="UI Dev", prompt="Deploy UI Management Agent. FIRST: Read /config/workspace/gitea/DoR-Dash/CLAUDE.md for deployment context including frontend at dd.kronisto.net:1717, reverse proxy setup, and live user interface. THEN: Review frontend architecture, check component structure, validate user experience, report UI issues.")
```

### Specific UI Tasks
```
# Component Review
Task(description="UI Components", prompt="UI Agent: Review SvelteKit components, check reusability, validate props and events, ensure consistent styling.")

# Responsive Design
Task(description="Responsive", prompt="UI Agent: Test responsive design across breakpoints, mobile-first approach, touch interfaces, accessibility.")

# User Experience
Task(description="UX Review", prompt="UI Agent: UX analysis - user workflows, navigation, form usability, error states, loading indicators.")

# Frontend Build
Task(description="Build Check", prompt="UI Agent: Frontend build process - check for errors, optimize bundle size, validate production build.")

# Accessibility Audit
Task(description="A11y Audit", prompt="UI Agent: Accessibility audit - WCAG compliance, keyboard navigation, screen reader support, color contrast.")

# Performance Optimization
Task(description="UI Perf", prompt="UI Agent: Frontend performance - Core Web Vitals, bundle analysis, lazy loading, code splitting optimization.")
```

## 🤖 LLM Integration Agent Subroutines

### Quick Deploy
```
Task(description="LLM Setup", prompt="Deploy LLM Integration Agent. FIRST: Read /config/workspace/gitea/DoR-Dash/CLAUDE.md for deployment context including Ollama at localhost:11434 (CPU/RAM Mistral), MCP tools, and live AI features. THEN: Check Ollama connectivity, test AI features, validate text refinement capabilities.")
```

### Specific LLM Tasks
```
# Ollama Health Check
Task(description="Ollama Check", prompt="LLM Agent: Check Ollama service health at 172.30.98.14:11434, verify Mistral model loaded, test basic generation.")

# Text Refinement
Task(description="Text Refine", prompt="LLM Agent: Test text refinement features - student update enhancement, faculty announcements, academic writing assistance.")

# AI Feature Testing
Task(description="AI Features", prompt="LLM Agent: Test all AI-assisted features - text enhancement, summarization, analysis, error handling.")

# Performance Monitoring
Task(description="LLM Perf", prompt="LLM Agent: Monitor LLM performance - response times, resource usage, cache effectiveness, error rates.")

# Prompt Engineering
Task(description="Prompt Tune", prompt="LLM Agent: Review and optimize prompts for better results - academic tone, clarity improvements, context handling.")
```

## 📁 Repository Management Agent Subroutines

### Quick Deploy
```
Task(description="Repo Admin", prompt="Deploy Repository Management Agent. FIRST: Read /config/workspace/gitea/DoR-Dash/CLAUDE.md for deployment context including git repository at /config/workspace/gitea/DoR-Dash, MCP tools, and live production code safety. THEN: Analyze repository structure, check code quality, validate documentation, assess git health.")
```

## 🔍 Quality Assurance (QA) Agent Subroutines

### Quick Deploy
```
Task(description="QA Full", prompt="Deploy QA Agent. FIRST: Read /config/workspace/gitea/DoR-Dash/CLAUDE.md for complete deployment context including dd.kronisto.net, all database connections, MCP tools, live data warnings, and current user accounts. THEN: Execute comprehensive QA test suite covering authentication, core functionality, performance, security, data integrity. Generate timestamped report with pass/fail status for all components.")
```

### Specific QA Tasks
```
# Authentication Testing
Task(description="QA Auth", prompt="QA Agent: Authentication-focused testing - test all user types (cerebro/admin, aalexandrian/student), role permissions, session management, security boundaries.")

# Core Features Test
Task(description="QA Core", prompt="QA Agent: Core functionality testing - student updates, faculty updates, meeting management, file uploads/downloads, user management workflows.")

# Performance Testing
Task(description="QA Perf", prompt="QA Agent: Performance testing - page load times, API response times, file upload speeds, database query performance, stress testing.")

# Security Audit
Task(description="QA Sec", prompt="QA Agent: Security testing - role-based access control, data isolation, file permissions, API endpoint security, session security.")

# Data Integrity Check
Task(description="QA Data", prompt="QA Agent: Data integrity testing - database consistency, file storage integrity, cross-table relationships, constraint validation.")

# End-to-End Testing
Task(description="QA E2E", prompt="QA Agent: End-to-end workflow testing - complete user journeys from login to task completion, cross-browser testing, mobile responsiveness.")

# Regression Testing
Task(description="QA Regression", prompt="QA Agent: Post-deployment regression testing - verify no existing functionality broken, validate recent fixes, ensure system stability.")

# Integration Testing
Task(description="QA Integration", prompt="QA Agent: Integration testing - frontend-backend API integration, database transactions, file system integration, LLM features.")
```

### Specific Repository Tasks
```
# Git Health Check
Task(description="Git Health", prompt="Repository Agent: Check git repository health - integrity, branch status, commit history, remote synchronization.")

# Code Refactoring
Task(description="Refactor", prompt="Repository Agent: Analyze code structure for refactoring opportunities - duplicated code, long functions, technical debt.")

# Documentation Audit
Task(description="Docs Audit", prompt="Repository Agent: Comprehensive documentation review - completeness, accuracy, broken links, formatting consistency.")

# Project Structure
Task(description="Structure", prompt="Repository Agent: Analyze and optimize project structure - file organization, configuration management, build system.")

# Dependency Management
Task(description="Dependencies", prompt="Repository Agent: Review dependencies - security audit, version updates, unused packages, optimization.")

# Code Quality Check
Task(description="Quality Check", prompt="Repository Agent: Code quality analysis - linting, formatting, complexity metrics, naming conventions.")

# Repository Cleanup
Task(description="Cleanup", prompt="Repository Agent: Repository maintenance - dead code removal, branch cleanup, file organization, performance optimization.")
```

## 🔧 Cross-Agent Coordination Subroutines

### Full System Check
```
Task(description="System Check", prompt="Deploy all agents in sequence: 1) Repository Agent - check git health, 2) Database Agent - verify schema, 3) Website Testing Agent - test functionality, 4) UI Agent - check frontend, 5) LLM Agent - verify AI features. Provide unified status report.")
```

### Emergency Recovery
```
Task(description="Emergency Fix", prompt="Deploy Database Agent for emergency recovery: fix critical database issues, restore user accounts, ensure application functionality. Then deploy Website Testing Agent to verify recovery.")
```

### Deployment Validation
```
Task(description="Deploy Validate", prompt="Post-deployment validation: Database Agent checks schema, Website Testing Agent validates functionality, UI Agent checks frontend build.")
```

### Performance Audit
```
Task(description="Perf Audit", prompt="Full performance audit: Database Agent analyzes DB performance, Website Testing Agent tests response times, UI Agent checks frontend metrics, LLM Agent monitors AI response times.")
```

## 🚀 Quick Agent Access Patterns

### Single Character Shortcuts (for ultra-fast access)
```
# Q = Quality Assurance (COMPREHENSIVE)
Task(description="Q", prompt="QA Agent: Comprehensive system validation - authentication, core functionality, performance, security, data integrity. Generate timestamped report with pass/fail status for all major components.")

# W = Website Testing
Task(description="W", prompt="Website Testing Agent: Quick health check - frontend/backend status, basic auth test, API connectivity.")

# D = Database  
Task(description="D", prompt="Database Agent: Quick database check - connection, schema integrity, user accounts status.")

# U = UI
Task(description="U", prompt="UI Agent: Quick frontend check - build status, component integrity, basic UX validation.")

# L = LLM
Task(description="L", prompt="LLM Agent: Quick Ollama check - service status, model availability, basic text generation test.")

# R = Repository
Task(description="R", prompt="Repository Agent: Quick repo check - git health, project structure, code quality, documentation status.")
```

### Two Character Combos (for specific tasks)
```
# WT = Website Test Full
Task(description="WT", prompt="Website Testing Agent: Full comprehensive test suite with detailed report.")

# DB = Database Backup
Task(description="DB", prompt="Database Agent: Create backup and verify data integrity.")

# UI = UI Build
Task(description="UI", prompt="UI Agent: Frontend build and optimization check.")

# AI = AI Features
Task(description="AI", prompt="LLM Agent: Test all AI features and text refinement capabilities.")

# GIT = Repository Management
Task(description="GIT", prompt="Repository Agent: Complete repository analysis - git health, code quality, documentation audit, dependency review.")
```

## 📋 Common Workflow Patterns

### Bug Investigation
```
Task(description="Bug Hunt", prompt="Deploy Website Testing Agent to identify issue, then Database Agent to check data integrity, then UI Agent if frontend related, then LLM Agent if AI features affected.")
```

### Feature Development
```
Task(description="Feature Dev", prompt="UI Agent designs interface, Database Agent handles schema changes, LLM Agent adds AI features, Website Testing Agent validates everything.")
```

### Production Readiness
```
Task(description="Prod Ready", prompt="All agents validate production readiness: Repository Agent - code quality and documentation, Database Agent - backup/migration plan, Website Testing Agent - comprehensive testing, UI Agent - performance optimization, LLM Agent - service reliability.")
```

---

## 💡 Usage Tips

1. **Copy-paste ready**: All subroutines are formatted for direct copy-paste
2. **Hierarchical**: Start with quick deploy, then use specific tasks as needed
3. **Combinable**: Chain multiple subroutines for complex workflows
4. **Customizable**: Modify prompts for specific project needs

Save this file for quick reference during development and debugging sessions!