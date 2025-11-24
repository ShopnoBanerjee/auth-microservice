# Inwren Auth - Authentication Microservice

A production-ready FastAPI-based authentication microservice with JWT token management, role-based access control, and comprehensive security features.

## Overview

This microservice provides a complete authentication and authorization solution for distributed systems. It implements secure user registration, login, token refresh, and user management with support for multiple user tiers and administrative controls.

### Key Features

- **JWT Authentication**: RS256 algorithm with public/private key pairs for secure token generation and validation
- **Refresh Token Rotation**: Secure refresh token mechanism with automatic rotation
- **Role-Based Access Control**: Support for regular users and superuser administrators
- **User Tier System**: Built-in support for user tier management (free, premium, etc.)
- **Rate Limiting**: API endpoint protection with configurable rate limits
- **Password Security**: Argon2 hashing for secure password storage
- **Async Database Operations**: PostgreSQL support with SQLAlchemy async ORM
- **Database Migrations**: Alembic integration for schema version control
- **CORS Support**: Configurable cross-origin resource sharing
- **Global Error Handling**: Centralized exception handling for consistent error responses

## Architecture

The microservice follows a clean, layered architecture pattern that separates concerns and promotes maintainability.

```mermaid
graph TB
    subgraph "Client Layer"
        Client[External Clients]
    end

    subgraph "API Layer"
        FastAPI[FastAPI Application]
        CORS[CORS Middleware]
        RateLimit[Rate Limiter]
        ErrorHandler[Global Error Handler]
        
        subgraph "Routers"
            AuthRouter[Auth Router<br/>/auth]
            UserRouter[Users Router<br/>/users]
            AdminRouter[Admin Router<br/>/admin]
        end
    end

    subgraph "Security Layer"
        OAuth2[OAuth2 Password Bearer]
        JWTAuth[JWT Token Validation]
        Deps[API Dependencies]
    end

    subgraph "Business Logic Layer"
        subgraph "Security Services"
            TokenGen[Token Generation<br/>RS256 JWT]
            PassHash[Password Hashing<br/>Argon2]
            TokenVerify[Token Verification]
        end
    end

    subgraph "Data Layer"
        Models[SQLAlchemy Models]
        Schemas[Pydantic Schemas]
        Session[Async DB Session]
    end

    subgraph "Database"
        PostgreSQL[(PostgreSQL Database)]
        Migrations[Alembic Migrations]
    end

    subgraph "Configuration"
        Config[Settings & Config]
        RSAKeys[RSA Public/Private Keys]
    end

    Client -->|HTTP Requests| FastAPI
    FastAPI --> CORS
    FastAPI --> RateLimit
    FastAPI --> ErrorHandler
    FastAPI --> AuthRouter
    FastAPI --> UserRouter
    FastAPI --> AdminRouter
    
    AuthRouter --> Deps
    UserRouter --> Deps
    AdminRouter --> Deps
    
    Deps --> OAuth2
    Deps --> JWTAuth
    Deps --> Session
    
    AuthRouter --> TokenGen
    AuthRouter --> PassHash
    UserRouter --> TokenVerify
    AdminRouter --> TokenVerify
    
    TokenGen --> Config
    TokenGen --> RSAKeys
    JWTAuth --> Config
    JWTAuth --> RSAKeys
    
    AuthRouter --> Models
    UserRouter --> Models
    AdminRouter --> Models
    
    Models --> Session
    Schemas --> Models
    
    Session --> PostgreSQL
    Migrations --> PostgreSQL
    
    Config -.->|Configures| Session
```

## Project Structure

```
auth-microservice/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── deps.py            # Shared dependencies (DB session, auth)
│   │   └── endpoints/
│   │       ├── auth.py        # Authentication endpoints (register, login, refresh)
│   │       ├── users.py       # User management endpoints (get, update, delete)
│   │       └── admin.py       # Admin-only endpoints (user management)
│   ├── core/
│   │   ├── config.py          # Application settings and configuration
│   │   ├── security.py        # JWT and password hashing utilities
│   │   └── limiter.py         # Rate limiting configuration
│   ├── database/
│   │   ├── base.py            # SQLAlchemy declarative base
│   │   └── session.py         # Async database session factory
│   ├── models/
│   │   └── user.py            # User SQLAlchemy model
│   └── schemas/
│       ├── user.py            # User Pydantic schemas
│       └── token.py           # Token Pydantic schemas
├── migrations/                 # Alembic database migrations
│   ├── env.py                 # Migration environment config
│   └── script.py.mako         # Migration template
├── certs/                      # RSA key pairs (not in repo)
│   ├── private.pem            # Private key for signing tokens
│   └── public.pem             # Public key for verifying tokens
├── alembic.ini                # Alembic configuration
├── pyproject.toml             # Project dependencies and metadata
└── README.md                  # This file
```

## API Endpoints

### Authentication Endpoints (`/auth`)

| Method | Endpoint | Description | Rate Limit | Auth Required |
|--------|----------|-------------|------------|---------------|
| POST | `/auth/register` | Register a new user account | 5/min | No |
| POST | `/auth/login` | Login with email and password | 5/min | No |
| POST | `/auth/access-token` | OAuth2 compatible login (for Swagger UI) | 5/min | No |
| POST | `/auth/refresh` | Refresh access token using refresh token | 10/min | No |

**Register Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "tier": "free"
}
```

**Login Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### User Endpoints (`/users`)

| Method | Endpoint | Description | Rate Limit | Auth Required |
|--------|----------|-------------|------------|---------------|
| GET | `/users/me` | Get current user profile | 20/min | Yes |
| PUT | `/users/me` | Update current user profile | 10/min | Yes |
| POST | `/users/me/password` | Change current user password | 5/min | Yes |
| DELETE | `/users/me` | Deactivate user account (soft delete) | 5/min | Yes |

### Admin Endpoints (`/admin`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/users` | List all users (paginated) | Superuser |
| GET | `/admin/users/{user_id}` | Get specific user by ID | Superuser |
| PUT | `/admin/users/{user_id}` | Update user (tier, status, permissions) | Superuser |
| DELETE | `/admin/users/{user_id}` | Hard delete a user | Superuser |

### Health Check Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint | 
| GET | `/health` | Health check endpoint |

## Data Models

### User Model

The core `User` model stored in PostgreSQL:

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Unique user identifier | Primary Key, Auto-generated |
| `email` | String | User email address | Unique, Indexed, Not Null |
| `hashed_password` | String | Argon2 hashed password | Not Null |
| `is_active` | Boolean | Account active status | Default: True |
| `is_superuser` | Boolean | Admin privileges flag | Default: False |
| `tier` | String | User subscription tier | Default: "free" |
| `hashed_refresh_token` | String | Current refresh token hash | Nullable |
| `created_at` | DateTime | Account creation timestamp | Auto-set, UTC |
| `updated_at` | DateTime | Last update timestamp | Auto-update, UTC |

### Pydantic Schemas

**UserCreate** (Registration):
- `email`: EmailStr (validated email format)
- `password`: str (min 8 characters)
- `tier`: str | None (default: "free")

**UserLogin**:
- `email`: EmailStr
- `password`: str

**UserResponse** (API output):
- `id`: UUID
- `email`: EmailStr
- `tier`: str
- `is_active`: bool
- `created_at`: datetime

**Token**:
- `access_token`: str (JWT, expires in 30 minutes)
- `refresh_token`: str (JWT, expires in 7 days)
- `token_type`: str (always "bearer")

**TokenPayload** (decoded JWT):
- `sub`: str (user ID)
- `tier`: str (user tier)
- Custom claims: `email`, `exp`, `iat`, `type`

## Security Features

### JWT Token Management

- **Algorithm**: RS256 (asymmetric cryptography)
- **Access Tokens**: Short-lived (30 minutes), contain user claims (id, email, tier)
- **Refresh Tokens**: Long-lived (7 days), used to obtain new access tokens
- **Token Rotation**: Refresh tokens are rotated on each use for enhanced security
- **Token Revocation**: Refresh tokens are hashed and stored; verification prevents token reuse

### Password Security

- **Hashing Algorithm**: Argon2 (OWASP recommended)
- **Minimum Length**: 8 characters
- **Storage**: Only hashed passwords stored in database
- **Validation**: Password change requires current password verification

### Rate Limiting

All endpoints are protected with rate limits to prevent abuse:
- Authentication endpoints: 5 requests/minute
- User profile reads: 20 requests/minute
- User profile updates: 10 requests/minute
- Password changes: 5 requests/minute
- Token refresh: 10 requests/minute

### CORS Configuration

Configurable allowed origins for cross-origin requests:
- Development: `http://localhost:3000`, `http://localhost:8000`
- Production: Configure via environment variables

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/auth_db

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=RS256

# RSA Keys (paths)
PRIVATE_KEY_PATH=./certs/private.pem
PUBLIC_KEY_PATH=./certs/public.pem

# Application
PROJECT_NAME=Inwren Auth
```

### RSA Key Generation

Generate RSA key pairs for JWT signing:

```bash
mkdir -p certs
# Generate private key
openssl genrsa -out certs/private.pem 2048
# Generate public key
openssl rsa -in certs/private.pem -pubout -out certs/public.pem
```

**Important**: Keep `private.pem` secure and never commit it to version control!

## Setup and Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- UV package manager (recommended) or pip

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd auth-microservice
   ```

2. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Generate RSA keys** (see RSA Key Generation section above)

4. **Configure environment variables** (create `.env` file)

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the application**:
   ```bash
   # Development mode
   fastapi dev app/main.py
   
   # Production mode
   fastapi run app/main.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations

This project uses Alembic for database schema management.

### Create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migration:
```bash
alembic downgrade -1
```

## Dependencies

Key dependencies from `pyproject.toml`:

- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy 2.0**: Async ORM for database operations
- **Alembic**: Database migration tool
- **Passlib[argon2]**: Password hashing with Argon2
- **PyJWT[crypto]**: JWT token encoding/decoding with RS256
- **AsyncPG**: PostgreSQL async driver
- **Pydantic Settings**: Configuration management
- **SlowAPI**: Rate limiting for FastAPI
- **Python Multipart**: Form data parsing for OAuth2

## Design Patterns and Architecture

### Layered Architecture

1. **API Layer** (`app/api/endpoints/`): HTTP request handling, input validation, response formatting
2. **Security Layer** (`app/core/security.py`, `app/api/deps.py`): Authentication, authorization, token management
3. **Data Layer** (`app/models/`, `app/schemas/`): Database models and data validation schemas
4. **Configuration Layer** (`app/core/config.py`): Centralized settings management

### Dependency Injection

FastAPI's dependency injection system is used extensively:
- `get_db()`: Provides async database sessions
- `get_current_user()`: Extracts and validates JWT tokens, returns authenticated user
- `get_current_superuser()`: Ensures user has admin privileges

### Async/Await Pattern

All database operations and endpoint handlers use async/await for non-blocking I/O, enabling high concurrency and better performance.

### Repository Pattern

Database operations are encapsulated in the data layer, separating business logic from data access.

## Development Notes

### Code Style

This project follows Python best practices:
- Type hints throughout the codebase
- Pydantic for data validation and settings management
- Async/await for all I/O operations
- Separation of concerns with clear module boundaries

### Logging

Centralized logging configuration in `main.py` with INFO level logging enabled.

### Error Handling

Global exception handler catches all unhandled exceptions and returns consistent error responses, preventing information leakage.

## Production Considerations

### Security Checklist

- ✅ Use environment variables for all sensitive configuration
- ✅ Secure RSA private keys (never commit to version control)
- ✅ Enable HTTPS in production
- ✅ Configure production CORS origins
- ✅ Use strong DATABASE_URL credentials
- ✅ Enable database SSL connections
- ✅ Review and adjust rate limits for production traffic
- ✅ Set up monitoring and alerting
- ✅ Implement log aggregation
- ✅ Regular security audits

### Scalability

The microservice is designed for horizontal scaling:
- Stateless authentication (JWT tokens)
- Async database connections with connection pooling
- Rate limiting with distributed backend (Redis recommended for multi-instance deployments)

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
