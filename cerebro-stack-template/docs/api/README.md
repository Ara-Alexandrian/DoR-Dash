# API Documentation

This document provides comprehensive information about the REST API endpoints, authentication, and usage examples.

## Base URL

```
Production: https://api.yourproject.com/v1
Staging: https://api-staging.yourproject.com/v1
Development: http://localhost:8000/api/v1
```

## Authentication

### JWT Token Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "123",
      "email": "user@example.com",
      "role": "user"
    }
  }
}
```

### Refreshing Tokens

```bash
POST /auth/refresh
Authorization: Bearer <your-refresh-token>
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": "specific_field",
      "value": "invalid_value"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 400 | Request data validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 3600
```

## Pagination

List endpoints support pagination using query parameters:

```bash
GET /users?page=1&limit=20&sort=created_at&order=desc
```

Parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort`: Sort field (default: id)
- `order`: Sort order (asc/desc, default: asc)

Response includes pagination metadata:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering and Searching

Most list endpoints support filtering and searching:

```bash
GET /users?search=john&role=admin&active=true
```

Common filter parameters:
- `search`: Full-text search across relevant fields
- `created_after`: Filter by creation date
- `created_before`: Filter by creation date
- Custom filters specific to each endpoint

## API Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure-password",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "created_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

#### POST /auth/login
Authenticate user and receive access token.

#### POST /auth/logout
Invalidate current session token.

#### POST /auth/refresh
Refresh access token using refresh token.

#### POST /auth/forgot-password
Request password reset email.

#### POST /auth/reset-password
Reset password using reset token.

### Users

#### GET /users
List all users (admin only).

**Query Parameters:**
- `search`: Search by name or email
- `role`: Filter by user role
- `active`: Filter by active status

#### GET /users/me
Get current user profile.

#### PUT /users/me
Update current user profile.

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

#### GET /users/{id}
Get user by ID (admin only).

#### PUT /users/{id}
Update user by ID (admin only).

#### DELETE /users/{id}
Delete user by ID (admin only).

### Items (Example Resource)

#### GET /items
List items with pagination and filtering.

**Query Parameters:**
- `search`: Search by name or description
- `category`: Filter by category
- `status`: Filter by status
- `owner_id`: Filter by owner

#### POST /items
Create a new item.

**Request:**
```json
{
  "name": "New Item",
  "description": "Item description",
  "category": "category1",
  "price": 29.99,
  "tags": ["tag1", "tag2"]
}
```

#### GET /items/{id}
Get item by ID.

#### PUT /items/{id}
Update item by ID.

#### DELETE /items/{id}
Delete item by ID.

#### POST /items/{id}/upload
Upload file attachment to item.

**Request:** Multipart form data
```
file: <file-upload>
description: "File description"
```

## WebSocket API

### Connection

Connect to WebSocket at:
```
wss://api.yourproject.com/ws?token=<jwt-token>
```

### Message Format

All WebSocket messages follow this format:
```json
{
  "type": "message_type",
  "data": { ... },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Message Types

#### Real-time Updates
```json
{
  "type": "item_updated",
  "data": {
    "id": "123",
    "name": "Updated Item",
    "updated_by": "user@example.com"
  }
}
```

#### System Notifications
```json
{
  "type": "notification",
  "data": {
    "message": "System maintenance in 5 minutes",
    "level": "warning"
  }
}
```

## SDK Examples

### JavaScript/TypeScript

```typescript
import axios from 'axios';

class APIClient {
  private baseURL = 'https://api.yourproject.com/v1';
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` })
    };
  }

  async login(email: string, password: string) {
    const response = await axios.post(`${this.baseURL}/auth/login`, {
      email,
      password
    });
    
    this.setToken(response.data.data.access_token);
    return response.data;
  }

  async getItems(params?: { page?: number; limit?: number; search?: string }) {
    const response = await axios.get(`${this.baseURL}/items`, {
      headers: this.getHeaders(),
      params
    });
    return response.data;
  }

  async createItem(item: CreateItemRequest) {
    const response = await axios.post(`${this.baseURL}/items`, item, {
      headers: this.getHeaders()
    });
    return response.data;
  }
}

// Usage
const client = new APIClient();
await client.login('user@example.com', 'password');
const items = await client.getItems({ page: 1, limit: 10 });
```

### Python

```python
import requests
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str = "https://api.yourproject.com/v1"):
        self.base_url = base_url
        self.token: Optional[str] = None

    def set_token(self, token: str):
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, email: str, password: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        
        data = response.json()
        self.set_token(data["data"]["access_token"])
        return data

    def get_items(self, page: int = 1, limit: int = 20, search: str = None) -> Dict[str, Any]:
        params = {"page": page, "limit": limit}
        if search:
            params["search"] = search

        response = requests.get(
            f"{self.base_url}/items",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

# Usage
client = APIClient()
client.login("user@example.com", "password")
items = client.get_items(page=1, limit=10)
```

### cURL Examples

```bash
# Login
curl -X POST "https://api.yourproject.com/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Get items with authentication
curl -X GET "https://api.yourproject.com/v1/items?page=1&limit=10" \
  -H "Authorization: Bearer <your-token>"

# Create item
curl -X POST "https://api.yourproject.com/v1/items" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"name": "New Item", "description": "Description"}'

# Upload file
curl -X POST "https://api.yourproject.com/v1/items/123/upload" \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@/path/to/file.pdf" \
  -F "description=File description"
```

## OpenAPI Specification

The complete OpenAPI (Swagger) specification is available at:
- Interactive docs: `https://api.yourproject.com/docs`
- JSON specification: `https://api.yourproject.com/openapi.json`

## Postman Collection

Download our Postman collection for easy API testing:
[Download Postman Collection](https://api.yourproject.com/postman-collection.json)

## Support

For API support and questions:
- Email: api-support@yourproject.com
- Documentation: [https://docs.yourproject.com](https://docs.yourproject.com)
- GitHub Issues: [https://github.com/yourusername/yourproject/issues](https://github.com/yourusername/yourproject/issues)

---

*Last updated: [Date]*
*API Version: v1.0.0*