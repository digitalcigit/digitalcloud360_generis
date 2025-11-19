# Authentication API

<cite>
**Referenced Files in This Document**   
- [auth.py](file://app/api/v1/auth.py#L1-L62)
- [user.py](file://app/schemas/user.py#L1-L55)
- [security.py](file://app/core/security.py#L1-L46)
- [user_service.py](file://app/services/user_service.py#L1-L31)
- [user.py](file://app/models/user.py#L1-L42)
- [settings.py](file://app/config/settings.py#L1-L83)
- [test_auth.py](file://tests/test_api/test_auth.py#L1-L78)
</cite>

## Table of Contents
1. [Authentication API Overview](#authentication-api-overview)
2. [Authentication Endpoints](#authentication-endpoints)
3. [Request and Response Models](#request-and-response-models)
4. [Authentication Flow](#authentication-flow)
5. [Security Implementation](#security-implementation)
6. [Error Handling](#error-handling)
7. [Usage Examples](#usage-examples)

## Authentication API Overview

The Authentication API provides endpoints for user registration, login, and token-based authentication. It implements a secure authentication system using JWT tokens and password hashing with bcrypt. The API follows RESTful principles and is built using FastAPI framework.

The authentication system consists of three main endpoints:
- POST /auth/register: User registration
- POST /auth/token: User login and token generation
- GET /auth/me: Retrieve current user information

Authentication is implemented using OAuth2PasswordBearer for token-based authentication, with Bearer tokens in the Authorization header for protected endpoints.

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L1-L62)
- [main.py](file://app/main.py#L110-L159)

## Authentication Endpoints

### POST /auth/register

Registers a new user in the system.

**Request Details**
- **Method**: POST
- **Path**: `/api/v1/auth/register`
- **Status Code**: 201 (Created)
- **Authentication**: Not required

**Request Body Schema (UserCreate)**
```json
{
  "email": "string (valid email format)",
  "name": "string",
  "password": "string (minimum 8 characters)"
}
```

**Response Schema (UserResponse)**
```json
{
  "id": 0,
  "email": "string",
  "name": "string",
  "profile": {
    "user_id": 0,
    "country": "string",
    "city": "string",
    "region": "string",
    "sector": "string",
    "experience_level": "string",
    "business_stage": "string",
    "preferred_language": "string",
    "coaching_style": "string",
    "cultural_context": {},
    "business_context": {}
  }
}
```

### POST /auth/token

Authenticates a user and returns an access token.

**Request Details**
- **Method**: POST
- **Path**: `/api/v1/auth/token`
- **Status Code**: 200 (OK)
- **Authentication**: Not required
- **Content-Type**: application/x-www-form-urlencoded

**Request Body Parameters**
- **username**: User's email address
- **password**: User's password

**Response Schema (Token)**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### GET /auth/me

Retrieves the current authenticated user's information.

**Request Details**
- **Method**: GET
- **Path**: `/api/v1/auth/me`
- **Status Code**: 200 (OK)
- **Authentication**: Required (Bearer token)

**Request Headers**
- **Authorization**: Bearer {access_token}

**Response Schema (UserResponse)**
```json
{
  "id": 0,
  "email": "string",
  "name": "string",
  "profile": {
    "user_id": 0,
    "country": "string",
    "city": "string",
    "region": "string",
    "sector": "string",
    "experience_level": "string",
    "business_stage": "string",
    "preferred_language": "string",
    "coaching_style": "string",
    "cultural_context": {},
    "business_context": {}
  }
}
```

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L1-L62)
- [test_auth.py](file://tests/test_api/test_auth.py#L1-L78)

## Request and Response Models

### UserCreate Schema
The UserCreate schema defines the structure for user registration requests.

**Fields**
- **email**: Valid email address (required)
- **name**: User's full name (required)
- **password**: Password with minimum 8 characters (required)

```python
class UserCreate(UserBase):
    name: str = Field(..., description="User name")
    password: str = Field(..., min_length=8, description="Password")
```

### Token Schema
The Token schema defines the structure of the authentication token response.

**Fields**
- **access_token**: JWT token string
- **token_type**: Token type (always "bearer")

```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

### UserResponse Schema
The UserResponse schema defines the structure for user information responses.

**Fields**
- **id**: User's unique identifier
- **email**: User's email address
- **name**: User's full name
- **profile**: Optional UserProfile object containing extended user information

```python
class UserResponse(User):
    profile: Optional[UserProfile] = None
```

**Section sources**
- [user.py](file://app/schemas/user.py#L1-L55)

## Authentication Flow

```mermaid
sequenceDiagram
participant Client
participant AuthController
participant UserService
participant Database
participant Security
Client->>AuthController : POST /auth/register
AuthController->>Database : Check if email exists
Database-->>AuthController : User not found
AuthController->>Security : Hash password
Security-->>AuthController : Hashed password
AuthController->>Database : Create user record
Database-->>AuthController : User created
AuthController->>Client : Return UserResponse (201)
Client->>AuthController : POST /auth/token
AuthController->>Database : Find user by email
Database-->>AuthController : User found
AuthController->>Security : Verify password
Security-->>AuthController : Password valid
AuthController->>Security : Create JWT token
Security-->>AuthController : Access token
AuthController->>Client : Return Token (200)
Client->>AuthController : GET /auth/me
AuthController->>Security : Decode token
Security-->>AuthController : Token valid
AuthController->>Database : Get user by ID
Database-->>AuthController : User data
AuthController->>Client : Return UserResponse (200)
```

**Diagram sources**
- [auth.py](file://app/api/v1/auth.py#L1-L62)
- [security.py](file://app/core/security.py#L1-L46)
- [user_service.py](file://app/services/user_service.py#L1-L31)

## Security Implementation

### Password Hashing
Passwords are securely hashed using bcrypt algorithm through the passlib library.

**Implementation**
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### JWT Token Management
JSON Web Tokens (JWT) are used for session management and authentication.

**Token Configuration**
- **Algorithm**: HS256
- **Expiration**: 43200 minutes (30 days)
- **Secret Key**: Generated using secrets.token_urlsafe(32)

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### Authentication Dependency
The `get_current_user` dependency function validates tokens and retrieves the current user.

```python
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    result = await db.execute(
        select(User).options(selectinload(User.profile)).filter(User.id == token_data.user_id)
    )
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user
```

**Section sources**
- [security.py](file://app/core/security.py#L1-L46)
- [user_service.py](file://app/services/user_service.py#L1-L31)
- [settings.py](file://app/config/settings.py#L1-L83)

## Error Handling

The authentication API implements comprehensive error handling for various scenarios.

### Error Codes

**400 Bad Request**
- **Cause**: Invalid input data
- **Example**: Registering with an existing email
- **Response**:
```json
{
  "detail": "The user with this email already exists in the system."
}
```

**401 Unauthorized**
- **Cause**: Invalid credentials or token
- **Examples**: 
  - Incorrect email or password during login
  - Invalid or expired token when accessing protected endpoints
- **Response**:
```json
{
  "detail": "Incorrect email or password"
}
```
With header: `WWW-Authenticate: Bearer`

**409 Conflict**
- **Cause**: Resource conflict (email already exists)
- **Example**: Attempting to register with an email that's already in use
- **Response**:
```json
{
  "detail": "The user with this email already exists in the system."
}
```

**422 Unprocessable Entity**
- **Cause**: Validation errors in request data
- **Examples**:
  - Email format invalid
  - Password less than 8 characters
  - Missing required fields
- **Response**:
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L1-L62)
- [test_auth.py](file://tests/test_api/test_auth.py#L1-L78)

## Usage Examples

### Registration Example

**curl Command**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword123"
  }'
```

**Successful Response (201)**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "profile": null
}
```

### Login Example

**curl Command**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

**Successful Response (200)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjg1NTM2MDAwfQ.sample",
  "token_type": "bearer"
}
```

### Accessing Protected Endpoint

**curl Command**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjg1NTM2MDAwfQ.sample"
```

**Successful Response (200)**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "profile": null
}
```

**Unauthorized Access (401)**
```json
{
  "detail": "Could not validate credentials"
}
```

**Section sources**
- [auth.py](file://app/api/v1/auth.py#L1-L62)
- [test_auth.py](file://tests/test_api/test_auth.py#L1-L78)