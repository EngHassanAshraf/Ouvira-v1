# Ouvira - Multi-Tenant Backend API

A comprehensive multi-tenant Django backend application providing authentication, authorization, company management, and audit logging capabilities. Built with Django REST Framework and designed for secure, scalable enterprise applications.

## Table of Contents
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Core Features](#core-features)
- [Authentication & Authorization](#authentication--authorization)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Environment Configuration](#environment-configuration)

## Overview

Ouvira is a production-ready multi-tenant backend service that supports:
- **Multi-tenancy**: Isolated tenant environments with shared infrastructure
- **Role-Based Access Control (RBAC)**: Granular permission management per tenant
- **Company Management**: User and company hierarchy with invitations and memberships
- **Audit Logging**: Comprehensive activity and security audit trails
- **JWT Authentication**: Secure token-based API access

### Key Concepts
- **Tenants**: Isolated application instances with separate data
- **Companies**: Organizations within tenants with parent-subsidiary relationships
- **Roles & Permissions**: Fine-grained access control at the company level
- **Audit Trails**: Complete tracking of user activities and security events

## Tech Stack

- **Framework**: Django 5.2.9 with Django REST Framework 3.16.1
- **Authentication**: JWT (djangorestframework-simplejwt 5.5.1)
- **Database**: PostgreSQL 15
- **Caching**: Redis (Alpine)
- **API Documentation**: Swagger/OpenAPI (drf-yasg)
- **Containerization**: Docker & Docker Compose
- **Python**: 3.10
- **Other**: Twilio SMS integration, Cloudflare Turnstile CAPTCHA support

## Project Structure

```
backend/
├── config/                     # Django configuration & settings
│   ├── settings/
│   │   ├── base.py           # Base configuration (shared)
│   │   ├── local.py          # Local development settings
│   │   └── production.py      # Production settings
│   ├── urls.py               # Main URL routing
│   ├── asgi.py               # ASGI application
│   └── wsgi.py               # WSGI application
│
├── apps/                       # Core application modules
│   ├── access_control/        # RBAC: Roles, permissions, role-permission mapping
│   ├── audit/                 # Activity logging & security audit trails
│   ├── company/               # Company management, invitations, memberships
│   ├── core/                  # Base models, utilities, common functionality
│   ├── tenant/                # Multi-tenancy configuration & middleware
│   ├── identity/              # User authentication & account management
│   │   ├── account/          # Custom user model and account endpoints
│   │   └── auth_app/         # Authentication endpoints (login, token refresh)
│   ├── notifications/         # SMS and notification services
│   ├── entrprise_service/    # Enterprise features (organizational structure)
│   └── shared/                # Shared utilities, exceptions, messages
│
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

## Core Features

### 1. Access Control (`apps/access_control/`)
- **Permission Management**: Define granular permissions (e.g., user.create, user.edit, role.read)
- **Role Management**: Create custom roles per company or system-wide roles
- **Role-Permission Mapping**: Assign permissions to roles with grant/deny logic
- **Module-Based Organization**: Permissions organized by module for better management

### 2. Audit & Security (`apps/audit/`)
- **Activity Logging**: Track user actions (create, read, update, delete)
- **Security Audit Trails**: Monitor sensitive operations and access patterns
- **Activity Services**: Notification and logging services for compliance
- **Date Dimension**: Historical date tracking for trend analysis

### 3. Company Management (`apps/company/`)
- **Company Hierarchy**: Support for parent and subsidiary companies
- **Company Settings**: Configuration per company
- **Invitations & Memberships**: User invitations and company membership tracking
- **Company Status**: Active, deactivated, or deleted states

### 4. Multi-Tenancy (`apps/tenant/`)
- **Tenant Isolation**: Separate data storage per tenant
- **Tenant Middleware**: Automatic tenant detection and routing
- **Domain Management**: Map custom domains to tenants
- **Schema Separation**: Each tenant has isolated database schema

### 5. Identity & Authentication (`apps/identity/`)
- **Custom User Model**: Extended user model with company and tenant association
- **JWT Authentication**: Secure token-based API authentication
- **Account Management**: User profile, password reset, account settings
- **Admin Interface**: Django admin integration for user management

### 6. Notifications (`apps/notifications/`)
- **SMS Integration**: Twilio-based SMS notifications
- **Notification Services**: Extensible notification system

## Authentication & Authorization

### Authentication Type
- **JWT (JSON Web Tokens)**
- **Header Format**: `Authorization: Bearer <ACCESS_TOKEN>`

### Authentication Flow
1. User logs in via `/auth/` endpoint with credentials
2. Backend issues JWT access and refresh tokens
3. Client includes access token in request headers
4. Backend validates token signature and expiration
5. Expired tokens can be refreshed using refresh token

### Authorization
- **Role-Based Access Control (RBAC)**: Users assigned to roles within companies
- **Permission Checks**: API endpoints enforce specific permissions based on user's role
- **Company Isolation**: Users can only access data within their company (tenant-level)

### API Access Rules
- **Open Endpoints**: Authentication endpoints (login, signup)
- **Protected Endpoints**: All sensitive operations require valid JWT token
- **API Gateway**: Kong (production) enforces additional access control rules

📚 **Detailed documentation**:
- Kong API Gateway rules: [docs/kong-notes.md](docs/kong-notes.md)
- API authentication flow: [docs/API.md](docs/API.md)

## Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local development)
- PostgreSQL 15 (included in Docker)
- Redis (included in Docker)

### Environment Configuration

Create a `.env` file in the workspace root:

```env
# Database Configuration
POSTGRES_DB=ouvira_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Django Configuration
DEBUG=True
SECRET_KEY=your-django-secret-key
TEST_MODE=False

# Tenants
TENANT_BASE_DOMAIN=localhost:8000

# Twilio (Optional - for SMS)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Cloudflare Turnstile (Optional - for CAPTCHA)
TURNSTILE_SITE_KEY=your_turnstile_site_key
TURNSTILE_SECRET_KEY=your_turnstile_secret_key
```

### Local Setup (Without Docker)

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure database** (PostgreSQL must be running):
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## Running the Application

### Using Docker Compose (Recommended)

1. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

2. **Run migrations**:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

3. **Create superuser**:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Access the application**:
   - Backend API: `http://localhost:8000`
   - Swagger UI: `http://localhost:8000/swagger/`
   - Django Admin: `http://localhost:8000/admin/`

### Docker Services
- **backend**: Django REST API (port 8000)
- **db**: PostgreSQL 15 database
- **redis**: Redis cache server

### Useful Commands

```bash
# View logs
docker-compose logs -f backend

# Run management commands
docker-compose exec backend python manage.py <command>

# Access Django shell
docker-compose exec backend python manage.py shell

# Stop all services
docker-compose down

# Remove all data (including database)
docker-compose down -v
```

## API Documentation

### Endpoints Overview

#### Authentication (`/auth/`)
- `POST /auth/login/` - User login (returns JWT tokens)
- `POST /auth/token/refresh/` - Refresh access token
- `POST /auth/logout/` - Logout (blacklist token)

#### Account (`/account/`)
- `GET /account/me/` - Get current user profile
- `POST /account/register/` - User registration
- `PUT /account/profile/` - Update user profile
- `POST /account/change-password/` - Change password

#### Company (`/company/`)
- `GET /company/` - List companies
- `POST /company/` - Create company
- `GET /company/{id}/` - Retrieve company details
- `POST /company/{id}/invite/` - Send membership invitation
- `GET /company/{id}/members/` - List company members
- `GET /company/{id}/roles/` - List company roles

#### Access Control
- `GET /access-control/permissions/` - List all permissions
- `GET /access-control/roles/` - List roles
- `POST /access-control/roles/` - Create role
- `POST /access-control/roles/{id}/permissions/` - Assign permissions to role

### Interactive API Documentation
Visit `http://localhost:8000/swagger/` for interactive API documentation with request/response examples.

## Environment Configuration

Key settings can be configured via environment variables or Django settings:

| Variable | Purpose | Default |
|----------|---------|---------|
| `DEBUG` | Debug mode (development only) | False |
| `SECRET_KEY` | Django secret key | Required |
| `TENANT_BASE_DOMAIN` | Base domain for tenant routing | localhost:8000 |
| `POSTGRES_DB` | Database name | ouvira_db |
| `TWILIO_ACCOUNT_SID` | Twilio account ID | - |

For sensitive settings, use environment variables instead of hardcoding in settings files.

## Development Workflow

1. **Create feature branch**: `git checkout -b feature/feature-name`
2. **Make changes**: Edit code following Django best practices
3. **Run migrations**: If models changed, create and apply migrations
4. **Test changes**: Run test suite and manually test endpoints
5. **Commit changes**: `git commit -m "descriptive message"`
6. **Push and create PR**: `git push origin feature/feature-name`

## Architecture Notes

### Multi-Tenancy Implementation
- Built on `django-tenants` package for schema isolation
- Each tenant has separate database schema
- Middleware automatically routes requests to correct tenant
- Shared tables (users signup, payments) remain unseparated

### Security Considerations
- JWT tokens stored in HTTP-only cookies (or mobile app storage)
- Password hashing using Django's PBKDF2 algorithm
- CORS headers configured for secure cross-origin requests
- Additional API Gateway (Kong) security layer in production

## Contributing

When adding new features:
1. Create new app in `backend/apps/` if feature is distinct
2. Follow Django conventions (models.py, serializers.py, views.py, urls.py)
3. Add audit logging for sensitive operations
4. Include migrations for database changes
5. Update API documentation

## Support & Documentation

- **Kong Configuration**: [docs/kong-notes.md](docs/kong-notes.md)
- **API Details**: [docs/API.md](docs/API.md)
- **Django Admin**: `/admin/` (superuser required)
- **API Swagger**: `/swagger/`
