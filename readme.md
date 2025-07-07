# Secure Enterprise Authentication Service

This project implements a secure and modular authentication service using FastAPI, integrating with LDAP for user authentication and managing access via JWT (JSON Web Tokens). It emphasizes best practices in software design, security, and maintainability.

## ✨ Features

- **LDAP Integration:** Authenticates users against an LDAP directory.
- **JWT Authentication:** Issues secure access and refresh tokens.
- **Token Revocation:** Implements an in-memory token blacklist for immediate logout.
- **Refresh Token Flow:** Allows obtaining new access tokens without re-authenticating.
- **User & Group Management:** Endpoints to retrieve user details, list group members, and check group membership from LDAP.
- **Modular Design:** Follows principles like Dependency Injection, Strategy Pattern, and Facade Pattern for extensibility and maintainability.
- **Security Focus:**
  - Input validation to prevent LDAP injection.
  - Rate limiting to mitigate brute-force attacks. \* Centralized, custom exception handling.
  - Externalized configuration via environment variables.
- **Logging:** Comprehensive logging for operational insights and security auditing.
- **Containerization:** Ready for Docker deployment.
- **CI/CD Ready:** Includes a GitHub Actions workflow for automated testing and deployment.

## 🚀 Project Structure

├── .github
/ # GitHub Actions CI/CD workflows
│ └── workflows/
│ └── main.yml # CI/CD pipeline definition
├── src/
│ ├── main.py # FastAPI application entry point
│ ├── api/ # API endpoints (v1)
│ │ └── v1/
│ │ ├── auth_routes.py # Authentication routes (login, logout, refresh)
│ │ └── user_routes.py # User and group related routes
│ ├── config/ # Application configuration classes
│ │ ├── app_config.py
│ │ ├── jwt_config.py
│ │ └── ldap_config.py
│ ├── constants/ # Enums and immutable constants
│ │ ├── auth_constants.py
│ │ ├── error_messages.py
│ │ └── ldap_constants.py
│ ├── dependencies/ # Dependency injection container
│ │ └── container.py
│ ├── exceptions/ # Custom exception classes
│ │ └── custom_exceptions.py
│ ├── models/ # Pydantic models for data validation/serialization
│ │ ├── auth_models.py
│ │ └── user_models.py
│ ├── security/ # Core security components
│ │ ├── authentication/ # Strategy pattern for auth methods
│ │ │ ├── auth_factory.py
│ │ │ ├── auth_strategy.py
│ │ │ └── ldap_strategy.py
│ │ ├── connection/ # Abstraction for connection management
│ │ │ ├── connection_manager.py
│ │ │ └── ldap_connection_manager.py
│ │ ├── jwt/ # JWT handling
│ │ │ ├── jwt_manager.py
│ │ │ └── token_blacklist.py
│ │ ├── user_management/ # Abstraction for user/group management
│ │ │ ├── user_manager.py
│ │ │ └── ldap_user_manager.py
│ │ ├── ldap_manager.py # Facade for LDAP operations
│ │ ├── rate_limiter.py # Rate limiting implementation
│ │ └── security_utils.py # General security utility functions
│ └── utils/
│ └── logger_config.py # Centralized logging configuration
├── tests/ # Unit and integration tests
│ ├── conftest.py # Pytest fixtures and mocks
│ └── test_auth.py # Example authentication tests
├── .env.example # Example environment variables
├── Dockerfile # Docker build instructions
├── README.md # Project README
└── requirements.txt # Python dependencies

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+**
- **pip** (Python package installer)
- **Docker** (Optional, for containerized deployment)
- Access to an **LDAP server** for authentication and user/group lookups.

## 🚀 Setup Guide

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Chetan7378/UserAuthenticationAndAuthorzation-System.git
   cd secure-auth-service
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory of the project (next to `src/` and `Dockerfile`). You can use `.env.example` as a template.

   ```ini
   # .env
   APP_NAME="Secure Enterprise Auth"
   DEBUG_MODE=True

   # JWT Configuration
   JWT_SECRET="YOUR_SUPER_SECRET_JWT_KEY_CHANGE_ME_IN_PRODUCTION"
   JWT_EXPIRATION_SECONDS=3600         # Access token expiration (1 hour)
   JWT_REFRESH_EXPIRATION_SECONDS=604800 # Refresh token expiration (7 days)

   # LDAP Configuration
   LDAP_SERVER="ldap://your-ldap-server:389" # e.g., ldap://localhost:389
   LDAP_BASE_DN="dc=example,dc=com"          # e.g., dc=mycompany,dc=com
   LDAP_GROUP_DN="ou=groups,dc=example,dc=com" # e.g., ou=groups,dc=mycompany,dc=com
   LDAP_AUTH_BIND=True # Set to False if you don't want auto-bind on connection
   ```

   **Important:** Replace `YOUR_SUPER_SECRET_JWT_KEY_CHANGE_ME_IN_PRODUCTION` with a strong, randomly generated secret in a production environment. Configure your LDAP details accurately.

## ▶️ Running the Application

### Locally (for development)

```bash
uvicorn src.main:app --reload
```

The API will be available at <http://127.0.0.1:8000>. You can access the interactive API documentation (Swagger UI) at <http://127.0.0.1:8000/docs>.

With Docker
Build the Docker image:

copy
bash

docker build -t secure-auth-service .
Run the Docker container:

copy
bash

docker run -d -p 8000:8000 --env-file ./.env secure-auth-service
The API will be available at <http://localhost:8000>.

🔒 API Endpoints
All endpoints are prefixed with /auth or /users.

Authentication Endpoints (/auth)\* POST /auth/login
copy
javascript

- **Description:** Authenticates a user against LDAP and returns JWT access and refresh tokens.
- **Request Body:** `{"username": "your_username", "password": "your_password"}`
- **Response:** `{"access_token": "...", "token_type": "bearer", "refresh_token": "..."}`
- **Example (using `curl`):**
  `bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=yourpassword"
`
  POST /auth/logout

Description: Revokes the current access token, effectively logging out the user.
Headers: Authorization: Bearer <access_token>
Response: {"message": "Token revoked successfully"}
Example:
copy
bash

curl -X POST "<http://127.0.0.1:8000/auth/logout>" \
 -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
POST /auth/refresh-token

Description: Exchanges a valid refresh token for a new pair of access and refresh tokens.
Request Body: {"refresh_token": "your_refresh_token"}
Response: {"access_token": "...", "token_type": "bearer", "refresh_token": "..."}
Example:
copy
bash

curl -X POST "<http://127.0.0.1:8000/auth/refresh-token>" \
 -H "Content-Type: application/json" \
 -d '{"refresh_token": "<YOUR_REFRESH_TOKEN>"}'
User Management Endpoints (/users)
All /users endpoints require a valid access token in the Authorization: Bearer header.

GET /users/details

Description: Retrieves details of the authenticated user from the JWT payload.
Headers: Authorization: Bearer <access_token>
Response: {"cn": "...", "mail": "...", "sn": "...", "uid": "..."}
Example:
copy
bash

curl -X GET "<http://127.0.0.1:8000/users/details>" \
 -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
GET /users/group-check/{group_name}

Description: Checks if the authenticated user is a member of a specified LDAP group.
Path Parameter: group_name (e.g., admins, developers)
Headers: Authorization: Bearer <access_token>
Response: {"group": "...", "member": "...", "status": "authorized"} or 403 Forbidden if not a member.
Example:
copy
bash

curl -X GET "<http://127.0.0.1:8000/users/group-check/developers>" \
 -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
GET /users/group-users/{group_name}

Description: Retrieves details for all users who are members of a specified LDAP group.
Path Parameter: group_name
Headers: Authorization: Bearer <access_token>
Response: [{"cn": "...", "mail": "...", "sn": "...", "uid": "..."}, ...]
Example:
copy
bash

curl -X GET "<http://127.0.0.1:8000/users/group-users/developers>" \
 -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
