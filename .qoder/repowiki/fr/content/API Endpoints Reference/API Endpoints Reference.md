# API Endpoints Reference

<cite>
**Referenced Files in This Document**   
- [main.py](file://app/main.py)
- [auth.py](file://app/api/v1/auth.py)
- [coaching.py](file://app/api/v1/coaching.py)
- [business.py](file://app/api/v1/business.py)
- [users.py](file://app/api/v1/users.py)
- [user.py](file://app/schemas/user.py)
- [coaching.py](file://app/schemas/coaching.py)
- [business.py](file://app/schemas/business.py)
- [responses.py](file://app/schemas/responses.py)
- [settings.py](file://app/config/settings.py)
- [middleware.py](file://app/api/middleware.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [API Versioning and Base URL](#api-versioning-and-base-url)
3. [Authentication and Security](#authentication-and-security)
4. [Error Handling and Status Codes](#error-handling-and-status-codes)
5. [Endpoint Details](#endpoint-details)
   - [Authentication Endpoints](#authentication-endpoints)
   - [Coaching Workflow Endpoints](#coaching-workflow-endpoints)
   - [Business Operations Endpoints](#business-operations-endpoints)
6. [Request and Response Examples](#request-and-response-examples)
7. [Middleware Processing](#middleware-processing)
8. [Sample curl Commands](#sample-curl-commands)

## Introduction
This document provides comprehensive documentation for the RESTful API endpoints of the Genesis AI Deep Agents Service. The service is designed as a personal AI coach for African entrepreneurs, leveraging deep agent orchestration through LangGraph to provide comprehensive business guidance. The API is built using FastAPI and follows RESTful principles with clear resource-based endpoints. The documentation covers all public endpoints, including their HTTP methods, URL patterns, request parameters, response schemas, authentication requirements, and example usage. The system integrates with external services like DigitalCloud30 and Tavily for enhanced functionality and uses Redis for session management and caching.

**Section sources**
- [main.py](file://app/main.py#L1-L184)

## API Versioning and Base URL
The API follows a semantic versioning strategy with the current version being v1. All endpoints are prefixed with `/api/v1` as defined in the application settings. This versioning approach allows for future API improvements while maintaining backward compatibility for existing clients. The base URL for all API requests is constructed as `{host}:{port}/api/v1`, where the host and port are determined by the deployment environment. The API version is exposed in the OpenAPI specification available at `/api/v1/openapi.json`, and the service version is included in health check responses and error messages for debugging purposes.

```mermaid
flowchart TD
A["Client Request"] --> B["Base URL: /api/v1"]
B --> C["Endpoint: /auth/register"]
B --> D["Endpoint: /coaching/start"]
B --> E["Endpoint: /business/brief/generate"]
C --> F["Response with v1 format"]
D --> F
E --> F
```

**Diagram sources**
- [settings.py](file://app/config/settings.py#L1-L84)
- [main.py](file://app/main.py#L1-L184)

## Authentication and Security
The API implements token-based authentication using Bearer tokens. Clients must authenticate via the `/auth/token` endpoint using OAuth2 password flow, which returns a JWT (JSON Web Token) that must be included in the `Authorization` header for all subsequent requests. The token has an expiration time of 30 days (43,200 minutes) as configured in the settings. All endpoints except `/health`, `/auth/register`, and `/auth/token` require authentication. The system uses bcrypt for password hashing and validates user credentials securely. CORS (Cross-Origin Resource Sharing) is configured to allow requests from specified origins, and the API supports HTTPS in production environments for secure data transmission.

```mermaid
sequenceDiagram
participant Client
participant AuthAPI
participant Database
Client->>AuthAPI : POST /api/v1/auth/token
activate AuthAPI
AuthAPI->>Database : Verify credentials
Database-->>AuthAPI : User data
AuthAPI->>AuthAPI : Create JWT token
AuthAPI-->>Client : 200 OK {access_token, token_type}
deactivate AuthAPI
Client->>ProtectedAPI : GET /api/v1/coaching/start
activate ProtectedAPI
ProtectedAPI->>ProtectedAPI : Validate Bearer token
alt Token valid
ProtectedAPI-->>Client : 200 OK Response
else Token invalid or expired
ProtectedAPI-->>Client : 401 Unauthorized
end
deactivate ProtectedAPI
```

**Diagram sources**
- [auth.py](file://app/api/v1/auth.py#L1-L63)
- [settings.py](file://app/config/settings.py#L1-L84)
- [main.py](file://app/main.py#L1-L184)

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L1-L63)
- [settings.py](file://app/config/settings.py#L1-L84)

## Error Handling and Status Codes
The API implements comprehensive error handling with standardized response formats. The following HTTP status codes are used throughout the API:

- **200 OK**: Successful GET, PUT, PATCH requests
- **201 Created**: Successful POST requests (resource created)
- **400 Bad Request**: Client sent invalid data or malformed request
- **401 Unauthorized**: Authentication failed or token missing/invalid
- **403 Forbidden**: Authenticated user lacks permission for the resource
- **404 Not Found**: Requested resource does not exist
- **500 Internal Server Error**: Unexpected server error occurred

Error responses follow the `ErrorResponse` schema defined in the responses module, containing an error code, descriptive message, optional details, and timestamp. The API also includes a global exception handler for `GenesisAIException` and general exceptions, ensuring consistent error formatting. Validation errors from Pydantic models are automatically converted to 400 Bad Request responses with detailed information about the validation failures.

```mermaid
flowchart TD
A["API Request"] --> B{"Request Valid?"}
B --> |Yes| C["Process Request"]
B --> |No| D["400 Bad Request"]
C --> E{"Authentication Valid?"}
E --> |Yes| F["Process Business Logic"]
E --> |No| G["401 Unauthorized"]
F --> H{"Resource Exists?"}
H --> |Yes| I["Process Operation"]
H --> |No| J["404 Not Found"]
I --> K{"Operation Successful?"}
K --> |Yes| L["200/201 Response"]
K --> |No| M["500 Internal Server Error"]
```

**Diagram sources**
- [main.py](file://app/main.py#L1-L184)
- [responses.py](file://app/schemas/responses.py#L1-L37)
- [auth.py](file://app/api/v1/auth.py#L1-L63)

**Section sources**
- [main.py](file://app/main.py#L1-L184)
- [responses.py](file://app/schemas/responses.py#L1-L37)

## Endpoint Details

### Authentication Endpoints
The authentication endpoints handle user registration and token-based authentication.

**POST /auth/register**
- **Description**: Register a new user account
- **Authentication**: Not required
- **Request Body**: `UserCreate` schema
  - `email`: User's email address (required)
  - `name`: User's full name (required)
  - `password`: User's password (minimum 8 characters, required)
- **Response**: `UserResponse` schema with 201 status
- **Error Cases**: 
  - 400 if email already exists
  - 400 if validation fails

**POST /auth/token**
- **Description**: Obtain an access token using OAuth2 password flow
- **Authentication**: Not required
- **Request Body**: Form data with username and password
  - `username`: User's email address
  - `password`: User's password
- **Response**: `Token` schema with 200 status
  - `access_token`: JWT token for subsequent requests
  - `token_type`: "bearer"
- **Error Cases**:
  - 401 if credentials are invalid
  - 400 if request format is incorrect

**GET /auth/me**
- **Description**: Retrieve the currently authenticated user's information
- **Authentication**: Required (Bearer token)
- **Request Headers**: `Authorization: Bearer <token>`
- **Response**: `UserResponse` schema with 200 status
- **Error Cases**:
  - 401 if token is invalid or expired
  - 401 if token is missing

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L1-L63)
- [user.py](file://app/schemas/user.py#L1-L56)

### Coaching Workflow Endpoints
These endpoints manage the AI coaching workflow, guiding users through a structured business development process.

**POST /coaching/start**
- **Description**: Start or continue a coaching session
- **Authentication**: Required
- **Request Body**: `CoachingRequest` schema
  - `session_id`: Optional existing session ID to continue
- **Response**: `CoachingResponse` schema with 200 status
  - `session_id`: Unique identifier for the coaching session
  - `current_step`: Current step in the coaching process
  - `coach_message`: Message from the AI coach
  - `examples`: Example responses for the current step
  - `next_questions`: Suggested follow-up questions
  - `progress`: Dictionary showing completion status of all steps
  - `is_step_complete`: Whether the current step is complete
- **Error Cases**:
  - 404 if provided session_id does not exist

**POST /coaching/step**
- **Description**: Submit a response for the current coaching step and advance to the next step
- **Authentication**: Required
- **Request Body**: `CoachingStepRequest` schema
  - `session_id`: ID of the coaching session (required)
  - `user_response`: User's response to the current coaching question (required)
- **Response**: `CoachingResponse` schema with 200 status
  - Returns updated coaching state with next step information
  - Progress tracking reflects completed steps
- **Error Cases**:
  - 404 if session not found
  - 403 if user is not authorized to access the session
  - 400 if request body is invalid

**Section sources**
- [coaching.py](file://app/api/v1/coaching.py#L1-L328)
- [coaching.py](file://app/schemas/coaching.py#L1-L64)

### Business Operations Endpoints
These endpoints handle business brief generation, retrieval, and website creation.

**POST /business/brief/generate**
- **Description**: Generate a comprehensive business brief using AI sub-agents
- **Authentication**: Required
- **Request Body**: `BusinessBriefRequest` schema
  - `session_id`: Coaching session ID
  - `business_needs`: Description of business requirements
  - `target_audience`: Target customer profile
  - `business_name`: Proposed business name
  - `ton_of_voice`: Desired brand voice
  - `key_features`: Key features or services
- **Response**: `BusinessBriefResponse` schema with 200 status
  - `brief_id`: Unique identifier for the generated brief
  - `user_id`: ID of the requesting user
  - `session_id`: Associated coaching session
  - `results`: Comprehensive business analysis from sub-agents
  - `created_at`: Timestamp of brief creation
- **Error Cases**:
  - 500 if brief generation fails

**GET /business/brief/{brief_id}**
- **Description**: Retrieve a previously generated business brief
- **Authentication**: Required
- **Path Parameters**:
  - `brief_id`: Unique identifier of the brief to retrieve
- **Response**: `BusinessBriefResponse` schema with 200 status
- **Error Cases**:
  - 404 if brief not found
  - 500 if retrieval fails

**GET /business/brief/{brief_id}/results**
- **Description**: Retrieve detailed results from all sub-agents for a business brief
- **Authentication**: Required
- **Path Parameters**:
  - `brief_id`: Unique identifier of the brief
- **Response**: `SubAgentResultsResponse` schema with 200 status
  - Contains detailed results from market research, content generation, logo creation, SEO optimization, and template selection sub-agents
- **Error Cases**:
  - 404 if brief not found
  - 404 if sub-agent results not found
  - 500 if retrieval fails

**POST /business/brief/{brief_id}/regenerate**
- **Description**: Regenerate specific sections of an existing business brief
- **Authentication**: Required
- **Path Parameters**:
  - `brief_id`: Unique identifier of the brief to regenerate
- **Request Body**: JSON object with `regenerate_sections` array
  - `regenerate_sections`: Array of section names to regenerate (e.g., ["content", "logo"])
- **Response**: `BusinessBriefResponse` schema with 200 status
  - Returns the updated brief with regenerated sections
- **Error Cases**:
  - 400 if regenerate_sections is empty
  - 404 if brief not found
  - 500 if regeneration fails

**Section sources**
- [business.py](file://app/api/v1/business.py#L1-L271)
- [business.py](file://app/schemas/business.py#L1-L84)

## Request and Response Examples

### Authentication Examples

**Register Request**
```json
{
  "email": "entrepreneur@example.com",
  "name": "Amina Diallo",
  "password": "securepassword123"
}
```

**Register Response (201)**
```json
{
  "id": 1,
  "email": "entrepreneur@example.com",
  "name": "Amina Diallo",
  "profile": {
    "user_id": 1,
    "preferred_language": "fr",
    "experience_level": "débutant"
  }
}
```

**Login Request**
```json
{
  "username": "entrepreneur@example.com",
  "password": "securepassword123"
}
```

**Login Response (200)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzE5NzQ0MDAwfQ.sample",
  "token_type": "bearer"
}
```

**Get Current User Response (200)**
```json
{
  "id": 1,
  "email": "entrepreneur@example.com",
  "name": "Amina Diallo",
  "profile": {
    "user_id": 1,
    "country": "Senegal",
    "sector": "e-commerce",
    "experience_level": "débutant"
  }
}
```

### Coaching Workflow Examples

**Start Coaching Request**
```json
{
  "session_id": "abc123-def456"
}
```

**Start Coaching Response (200)**
```json
{
  "session_id": "abc123-def456",
  "current_step": "vision",
  "coach_message": "Welcome to your Genesis AI coaching session. Let's start by defining your business vision. What is your long-term ambition for your project?",
  "examples": [
    "Become the leader in eco-friendly meal delivery in Europe.",
    "Create an online education platform accessible to everyone worldwide."
  ],
  "next_questions": [
    "What is your business's reason for being?",
    "What core values will guide your decisions?"
  ],
  "progress": {
    "vision": false,
    "mission": false,
    "clientele": false,
    "differentiation": false,
    "offre": false,
    "synthesis": false
  },
  "is_step_complete": false
}
```

**Process Coaching Step Request**
```json
{
  "session_id": "abc123-def456",
  "user_response": "My vision is to create the best restaurant in Dakar that showcases traditional Senegalese cuisine with a modern twist."
}
```

**Process Coaching Step Response (200)**
```json
{
  "session_id": "abc123-def456",
  "current_step": "mission",
  "coach_message": "Excellent vision! Now, let's clarify your MISSION. What is your business's reason for being?",
  "examples": [
    "Feed families with authentic cuisine.",
    "Reveal the unique beauty of each client."
  ],
  "next_questions": [
    "How will you serve your customers daily?",
    "What are your fundamental commitments?"
  ],
  "progress": {
    "vision": true,
    "mission": false,
    "clientele": false,
    "differentiation": false,
    "offre": false,
    "synthesis": false
  },
  "is_step_complete": false
}
```

### Business Operations Examples

**Generate Business Brief Request**
```json
{
  "session_id": "abc123-def456",
  "business_needs": "Create an e-commerce platform for African fashion.",
  "target_audience": "Young adults (18-35) interested in sustainable fashion.",
  "business_name": "AfroChic",
  "ton_of_voice": "Modern, bold, and authentic.",
  "key_features": [
    "Product catalog",
    "Online payment",
    "Fashion blog"
  ]
}
```

**Generate Business Brief Response (200)**
```json
{
  "brief_id": "brief_1a2b3c4d",
  "user_id": 1,
  "session_id": "abc123-def456",
  "results": {
    "market_research": {
      "analysis": "The market is growing rapidly with increasing demand for sustainable African fashion."
    },
    "content_generation": {
      "homepage_text": "Welcome to AfroChic, where tradition meets innovation in African fashion."
    },
    "logo_creation": {
      "logo_url": "https://cdn.example.com/afrochic_logo.png"
    },
    "seo_optimization": {
      "keywords": ["African fashion", "e-commerce", "sustainable"]
    },
    "template_selection": {
      "template_name": "DynamicFashion"
    }
  },
  "overall_confidence": 0.92,
  "is_ready_for_website": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Error Response Example (404)**
```json
{
  "error": "NOT_FOUND",
  "message": "Business brief not found.",
  "timestamp": 1719738000.123
}
```

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L1-L63)
- [coaching.py](file://app/api/v1/coaching.py#L1-L328)
- [business.py](file://app/api/v1/business.py#L1-L271)
- [test_auth.py](file://tests/test_api/test_auth.py#L1-L78)
- [test_coaching.py](file://tests/test_api/test_coaching.py#L1-L78)
- [test_business.py](file://tests/test_api/test_business.py#L1-L168)

## Middleware Processing
The API implements several middleware components that process requests and responses globally. The CORS middleware allows cross-origin requests from specified origins, supporting credentials and all standard HTTP methods. The Prometheus middleware collects metrics on request count and duration, exposing them for monitoring and observability. The Logging middleware provides structured logging of all requests and responses using structlog, capturing method, URL, status code, and duration. These middleware components are executed in sequence for every request, enhancing security, monitoring, and debugging capabilities without requiring changes to individual endpoint implementations.

```mermaid
flowchart TD
A["Incoming Request"] --> B["CORS Middleware"]
B --> C["Prometheus Middleware"]
C --> D["Logging Middleware"]
D --> E["Authentication Check"]
E --> F["Endpoint Logic"]
F --> G["Response Formatting"]
G --> H["Logging Middleware"]
H --> I["Prometheus Middleware"]
I --> J["CORS Headers"]
J --> K["Outgoing Response"]
```

**Diagram sources**
- [middleware.py](file://app/api/middleware.py#L1-L73)
- [main.py](file://app/main.py#L1-L184)

**Section sources**
- [middleware.py](file://app/api/middleware.py#L1-L73)

## Sample curl Commands

### Register a New User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "entrepreneur@example.com",
    "name": "Amina Diallo",
    "password": "securepassword123"
  }'
```

### Obtain Authentication Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=entrepreneur@example.com&password=securepassword123"
```

### Start a Coaching Session
```bash
curl -X POST "http://localhost:8000/api/v1/coaching/start" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123-def456"
  }'
```

### Submit a Coaching Step Response
```bash
curl -X POST "http://localhost:8000/api/v1/coaching/step" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123-def456",
    "user_response": "My vision is to create the best restaurant in Dakar."
  }'
```

### Generate a Business Brief
```bash
curl -X POST "http://localhost:8000/api/v1/business/brief/generate" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123-def456",
    "business_needs": "Create an e-commerce platform for African fashion.",
    "target_audience": "Young adults (18-35) interested in sustainable fashion.",
    "business_name": "AfroChic",
    "ton_of_voice": "Modern, bold, and authentic.",
    "key_features": ["Product catalog", "Online payment", "Fashion blog"]
  }'
```

### Retrieve a Business Brief
```bash
curl -X GET "http://localhost:8000/api/v1/business/brief/brief_1a2b3c4d" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L1-L63)
- [coaching.py](file://app/api/v1/coaching.py#L1-L328)
- [business.py](file://app/api/v1/business.py#L1-L271)