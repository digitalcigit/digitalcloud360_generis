# User Management API

<cite>
**Referenced Files in This Document**   
- [auth.py](file://app/api/v1/auth.py#L45-L62)
- [user_service.py](file://app/services/user_service.py#L15-L31)
- [user.py](file://app/models/user.py#L1-L42)
- [user.py](file://app/schemas/user.py#L1-L50)
</cite>

## Table of Contents
1. [User Profile Endpoints](#user-profile-endpoints)
2. [Response Schema](#response-schema)
3. [Update User Profile](#update-user-profile)
4. [Integration with UserService](#integration-with-userservice)
5. [Security and Field-Level Permissions](#security-and-field-level-permissions)
6. [Rate Limiting Considerations](#rate-limiting-considerations)
7. [Example Requests](#example-requests)

## User Profile Endpoints

The system provides two primary endpoints for managing user profile information:

- **GET /api/v1/auth/me**: Retrieves the authenticated user's profile information.
- **PUT /users/me**: Updates the authenticated user's profile (not currently implemented in codebase).

Based on the current implementation, only the `GET /api/v1/auth/me` endpoint is available under the authentication router. The PUT endpoint for updating user data is not present in the existing codebase, despite being referenced in the documentation objective.

The `GET /api/v1/auth/me` endpoint returns the current user's information by validating the provided bearer token and retrieving the associated user record from the database.

```mermaid
sequenceDiagram
participant Client
participant AuthController
participant UserService
participant Database
Client->>AuthController : GET /api/v1/auth/me<br/>Authorization : Bearer <token>
AuthController->>UserService : get_current_user(token)
UserService->>UserService : decode_access_token(token)
UserService->>Database : SELECT * FROM users WHERE id = <user_id>
Database-->>UserService : User record with profile
UserService-->>AuthController : User object
AuthController-->>Client : 200 OK + UserResponse JSON
```

**Diagram sources**
- [auth.py](file://app/api/v1/auth.py#L45-L62)
- [user_service.py](file://app/services/user_service.py#L15-L31)
- [user.py](file://app/models/user.py#L1-L42)

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L45-L62)
- [user_service.py](file://app/services/user_service.py#L15-L31)

## Response Schema

The response schema for user profile retrieval is defined in `UserResponse`, which inherits from the base `User` model and includes an optional `profile` field.

### UserResponse Schema
- **id**: Unique identifier for the user (integer)
- **email**: User's email address (string, required)
- **name**: Full name of the user (string, required)
- **created_at**: Timestamp when the user was created (inherited from BaseModel)
- **profile**: Optional extended profile data (object)

### UserProfile Schema
- **user_id**: Foreign key to the user (integer)
- **country**: User's country (string, optional)
- **city**: User's city (string, optional)
- **region**: User's region (string, optional)
- **preferred_language**: Default "fr" (string)
- **coaching_style**: Preferred coaching approach (string, optional)
- **cultural_context**: Additional cultural data (JSON, optional)
- **business_context**: Business-related context (JSON, optional)

```mermaid
classDiagram
class User {
+int id
+str email
+str name
+datetime created_at
+datetime updated_at
}
class UserProfile {
+int user_id
+str country
+str city
+str region
+str preferred_language = "fr"
+str coaching_style
+Dict~str,any~ cultural_context
+Dict~str,any~ business_context
}
User "1" -- "0..1" UserProfile : has
```

**Diagram sources**
- [user.py](file://app/models/user.py#L1-L42)
- [user.py](file://app/schemas/user.py#L1-L50)

**Section sources**
- [user.py](file://app/models/user.py#L1-L42)
- [user.py](file://app/schemas/user.py#L1-L50)

## Update User Profile

The PUT `/users/me` endpoint for updating user profile information is **not implemented** in the current codebase. While the documentation objective specifies this functionality, no corresponding route exists in `users.py` or `auth.py`.

If implemented, the expected behavior would be:

- **Endpoint**: PUT /users/me
- **Request Body**: JSON with optional `name` field
- **Validation Rules**:
  - `name`: Maximum length of 100 characters
  - Must be a string if provided
- **Response Codes**:
  - 200 OK: Successful update
  - 400 Bad Request: Invalid data (e.g., name too long)
  - 401 Unauthorized: Missing or invalid authentication token

A proper implementation would require adding a new route in either `auth.py` or `users.py` that accepts a partial update payload and persists changes to the database through the UserService.

```mermaid
flowchart TD
A[Client] --> |PUT /users/me| B{Auth Valid?}
B --> |No| C[401 Unauthorized]
B --> |Yes| D{Valid Data?}
D --> |No| E[400 Bad Request]
D --> |Yes| F[Update User Record]
F --> G[Save to Database]
G --> H[200 OK + Updated User]
```

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L45-L62)
- [user_service.py](file://app/services/user_service.py#L15-L31)

## Integration with UserService

User profile operations are integrated with the `UserService` via dependency injection. The `get_current_user` function in `user_service.py` handles authentication and user retrieval.

### Key Functions:
- **get_current_user()**: Extracts user ID from JWT token and fetches the full user record with profile data
- Uses `selectinload(User.profile)` to eagerly load the UserProfile relationship
- Returns a fully hydrated User object for response serialization

### Data Flow:
1. Token received via Authorization header
2. Token decoded to extract `user_id`
3. Database query executed with join on UserProfile
4. Full user object returned to endpoint handler
5. Serialized to UserResponse model for JSON output

This integration ensures that profile data is always available when retrieving user information, minimizing database round trips.

```mermaid
sequenceDiagram
participant Client
participant AuthController
participant UserService
participant Database
Client->>AuthController : GET /api/v1/auth/me
AuthController->>UserService : get_current_user(token)
UserService->>UserService : decode_access_token()
UserService->>Database : SELECT users.*, user_profiles.*<br/>JOIN ON users.id = user_profiles.user_id
Database-->>UserService : Complete user data
UserService-->>AuthController : User object
AuthController-->>Client : JSON response
```

**Diagram sources**
- [user_service.py](file://app/services/user_service.py#L15-L31)
- [user.py](file://app/models/user.py#L1-L42)

**Section sources**
- [user_service.py](file://app/services/user_service.py#L15-L31)

## Security and Field-Level Permissions

The system implements strict field-level security for user data:

### Read-Only Fields:
- **id**: System-generated identifier, cannot be modified
- **email**: Primary identifier, immutable after creation
- **created_at**: Audit timestamp, read-only

### Mutable Fields:
- **name**: Can be updated via PUT /users/me (endpoint not implemented)
- Profile fields (country, city, etc.) could be updated through a future profile update endpoint

Authentication is enforced using OAuth2 Bearer tokens. All access to `/api/v1/auth/me` requires a valid JWT token containing the user ID (`sub` claim). The system validates credentials and returns 401 Unauthorized for invalid or missing tokens.

Field validation is handled through Pydantic models, ensuring type safety and data integrity at the API boundary.

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L45-L62)
- [user_service.py](file://app/services/user_service.py#L15-L31)
- [user.py](file://app/schemas/user.py#L1-L50)

## Rate Limiting Considerations

While no explicit rate limiting is implemented in the current codebase, update operations like PUT `/users/me` should incorporate rate limiting in production:

- **Recommended Strategy**: Token-based rate limiting (e.g., 10 requests per hour per user)
- **Implementation**: Use Redis to track request counts by user ID
- **Headers**: Include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After`
- **Response Codes**:
  - 429 Too Many Requests when limit exceeded

Rate limiting protects against abuse and ensures fair usage of update endpoints. Given that profile updates are infrequent operations, a conservative limit would be appropriate.

## Example Requests

### Retrieve User Profile (Success - 200)
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**
```json
{
  "id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "profile": {
    "user_id": 123,
    "country": "France",
    "city": "Paris",
    "preferred_language": "fr",
    "coaching_style": "directive",
    "cultural_context": {
      "timezone": "Europe/Paris"
    }
  }
}
```

### Invalid Token (401)
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer invalid_token"
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

### Update User Name (Conceptual - Not Implemented)
```bash
curl -X PUT "http://localhost:8000/users/me" \
  -H "Authorization: Bearer <valid_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe"}'
```

**Expected Response (200 OK):**
```json
{
  "id": 123,
  "email": "user@example.com",
  "name": "Jane Doe"
}
```

**Expected Error Response (400 Bad Request):**
```json
{
  "detail": "Name must not exceed 100 characters"
}
```

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L45-L62)
- [user_service.py](file://app/services/user_service.py#L15-L31)
- [user.py](file://app/schemas/user.py#L1-L50)