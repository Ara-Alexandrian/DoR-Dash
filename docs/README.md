# DoR-Dash Documentation

This directory contains all documentation for the DoR-Dash (Dose of Reality Dashboard) application.

## Quick Start

- **🚀 [Deployment Instructions](DEPLOY_INSTRUCTIONS.md)** - Complete Unraid deployment guide
- **🔧 [Technical Notes](technical-notes.md)** - Detailed bug fixes and technical solutions
- **🌐 [Reverse Proxy Setup](REVERSE_PROXY_SETUP.md)** - Nginx configuration for SSL termination

## Documentation Index

### Setup & Deployment
- **[DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)** - Step-by-step Unraid deployment
- **[REVERSE_PROXY_SETUP.md](REVERSE_PROXY_SETUP.md)** - Nginx Proxy Manager configuration
- **[UNRAID_DEPLOYMENT.md](UNRAID_DEPLOYMENT.md)** - Unraid-specific deployment details

### Development & Maintenance  
- **[technical-notes.md](technical-notes.md)** - Comprehensive bug fixes, debugging sessions, and architectural solutions
- **[QA_VALIDATION_REPORT_2025-06-15.md](../QA_VALIDATION_REPORT_2025-06-15.md)** - Latest comprehensive system validation report
- **[pgadmin-setup-guide.md](pgadmin-setup-guide.md)** - Database administration setup
- **[GITHUB_GITEA_MIRROR_SETUP.md](GITHUB_GITEA_MIRROR_SETUP.md)** - Repository mirroring configuration
- **[DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md)** - Database schema and relationship reference
- **[architecture-diagram.md](architecture-diagram.md)** - System architecture with mermaid diagrams

## Key Information

### Application URLs
- **Production:** https://dd.kronisto.net (through Nginx reverse proxy)
- **Direct Frontend:** http://172.30.98.177:1717
- **Direct Backend:** http://172.30.98.177:8000

### Default Credentials
- **Admin:** cerebro / 123
- **Test User:** aalexandrian / 12345678

### Recent Critical Fixes (June 2025)
1. **Complete Database Persistence** - All data now safely stored in PostgreSQL database
2. **Faculty Updates Migration** - Fixed file upload system and API 500 errors
3. **QA System Implementation** - Comprehensive automated testing and validation
4. **Student Update Bug** - Identified and documented missing schema method
5. **PostgreSQL Enum Fix** - Resolved user role update failures
6. **JSON Response Parsing** - Fixed user deletion errors
7. **Port Standardization** - Updated to port 1717
8. **SPA Routing Fix** - Custom Express server for proper frontend routing

## Architecture Overview

### Technology Stack
- **Backend:** FastAPI with PostgreSQL and Redis caching
- **Frontend:** SvelteKit with Vite and custom Express server
- **Database:** PostgreSQL with unified AgendaItem model
- **AI Integration:** Ollama API for text refinement
- **Deployment:** Docker on Unraid br0 network
- **Reverse Proxy:** Nginx Proxy Manager with SSL
- **File Storage:** Persistent `/uploads/` directory with database metadata
- **Quality Assurance:** Automated testing and validation system

### Data Safety Status (Updated June 2025)
🎉 **ALL DATA NOW PERSISTENT & SAFE:** 🎉
- User accounts (PostgreSQL 'user' table)
- Student updates (PostgreSQL 'agendaitem' table)
- Faculty updates (PostgreSQL 'agendaitem' table)
- Meeting calendar (PostgreSQL 'meeting' table)
- Registration requests (PostgreSQL 'registrationrequest' table)
- File uploads (Physical files in `/uploads/` + PostgreSQL metadata)
- Database schemas and relationships

**No more data loss risk - complete persistence achieved!**

## Quality Assurance & Testing

### QA System
- **Automated Testing:** Comprehensive QA agent with system validation
- **Health Monitoring:** Database, API, frontend, and security testing
- **Performance Benchmarks:** Response time and load testing
- **Issue Tracking:** Detailed reports with traffic light status indicators

### Latest QA Status (June 15, 2025)
**Overall Health:** 🟡 OPERATIONAL WITH ISSUES  
**Critical Issues:** 2 (student update creation, faculty listing endpoint)  
**Tests Passed:** 21/25  
**System Uptime:** Confirmed operational

## Support

For troubleshooting:
1. Check latest QA report: `QA_VALIDATION_REPORT_2025-06-15.md`
2. Review [technical-notes.md](technical-notes.md) for detailed fixes
3. Check container logs: `docker logs dor-dash`
4. Verify deployment steps in [DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)

---

**Last Updated:** June 15, 2025  
**Version:** Complete Database Persistence + QA System  
**System Status:** 🟡 Operational with minor issues (2 API bugs identified)