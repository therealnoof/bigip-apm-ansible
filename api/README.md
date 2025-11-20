# F5 BIG-IP APM REST API

FastAPI-based REST API service for deploying and managing F5 BIG-IP Access Policy Manager solutions.

## Features

- **RESTful API** for APM deployment operations
- **OpenAPI/Swagger** documentation (auto-generated)
- **Pydantic models** for request/response validation
- **Type safety** with Python type hints
- **Async support** for high performance
- **CORS** enabled for web clients

## Architecture

```
api/
├── main.py                 # FastAPI application
├── models.py              # Pydantic models
├── services/              # Business logic
│   ├── f5_client.py      # F5 API client
│   └── ansible_runner.py # Ansible playbook runner
└── routers/              # API routes
    ├── apm.py           # APM operations
    └── admin.py         # Admin operations
```

## Installation

### 1. Install Dependencies

```bash
cd /Users/a.hernandez/Claude/projects/bigip-apm-ansible
pip3 install -r requirements-api.txt
```

### 2. Set Environment Variables (Optional)

```bash
export BIGIP_HOST=10.1.1.4
export BIGIP_USERNAME=admin
export BIGIP_PASSWORD=admin
export API_PORT=8000
```

## Usage

### Start the API Server

```bash
# From project root
cd /Users/a.hernandez/Claude/projects/bigip-apm-ansible

# Start with uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python3 -m api.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Deploy Solution 1 (VPN)
```bash
curl -X POST http://localhost:8000/api/v1/deploy/solution1 \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "host": "10.1.1.4",
      "username": "admin",
      "password": "admin"
    },
    "solution_name": "solution1",
    "dns_name": "solution1.acme.com",
    "ad_config": {
      "ip": "10.1.20.7",
      "domain": "f5lab.local",
      "admin_user": "admin",
      "admin_password": "admin"
    },
    "vpn_config": {
      "lease_pool_start": "10.1.2.1",
      "lease_pool_end": "10.1.2.254",
      "split_tunnel_networks": ["10.1.10.0/24", "10.1.20.0/24"]
    }
  }'
```

#### Deploy Solution 2 (Portal)
```bash
curl -X POST http://localhost:8000/api/v1/deploy/solution2 \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "host": "10.1.1.4",
      "username": "admin",
      "password": "admin"
    },
    "solution_name": "solution2",
    "dns_name": "solution2.acme.com",
    "ad_config": {
      "ip": "10.1.20.7",
      "domain": "f5lab.local",
      "admin_user": "admin",
      "admin_password": "admin"
    },
    "portal_resources": [
      {
        "name": "server1",
        "application_uri": "https://server1.acme.com",
        "caption": "Server 1"
      }
    ],
    "ad_group_mappings": [
      {
        "expression": "expr { [string tolower [mcget -decode {session.ad.last.attr.memberOf}]] contains [string tolower \\"CN=Sales,CN=Users,DC=f5lab,DC=local\\"] }",
        "description": "Sales team access",
        "portal_access_resources": ["/Common/solution2-server1"],
        "webtop": "/Common/solution2-webtop"
      }
    ]
  }'
```

#### Get Deployment Status
```bash
curl http://localhost:8000/api/v1/deploy/{deployment_id}
```

#### Delete Solution
```bash
curl -X DELETE http://localhost:8000/api/v1/deploy/solution1 \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "host": "10.1.1.4",
      "username": "admin",
      "password": "admin"
    },
    "solution_name": "solution1",
    "confirm": true
  }'
```

#### List All Deployments
```bash
curl http://localhost:8000/api/v1/deployments
```

## Python Client Example

```python
import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Deploy Solution 1
response = requests.post(
    f"{BASE_URL}/deploy/solution1",
    json={
        "credentials": {
            "host": "10.1.1.4",
            "username": "admin",
            "password": "admin"
        },
        "solution_name": "my-vpn",
        "dns_name": "vpn.example.com",
        "ad_config": {
            "ip": "10.1.20.7",
            "domain": "example.local",
            "admin_user": "admin",
            "admin_password": "password"
        },
        "vpn_config": {
            "lease_pool_start": "10.1.2.1",
            "lease_pool_end": "10.1.2.254"
        }
    }
)

if response.status_code == 200:
    deployment = response.json()
    deployment_id = deployment["deployment_id"]
    print(f"Deployment started: {deployment_id}")

    # Check status
    status_response = requests.get(f"{BASE_URL}/deploy/{deployment_id}")
    print(f"Status: {status_response.json()['status']}")
else:
    print(f"Error: {response.json()}")
```

## API Models

### Solution1Request
```python
{
  "credentials": {
    "host": "10.1.1.4",
    "port": 443,
    "username": "admin",
    "password": "admin",
    "validate_certs": false
  },
  "solution_name": "solution1",
  "dns_name": "solution1.acme.com",
  "customization_type": "modern",
  "ad_config": {
    "ip": "10.1.20.7",
    "port": 389,
    "domain": "f5lab.local",
    "admin_user": "admin",
    "admin_password": "admin"
  },
  "vpn_config": {
    "lease_pool_start": "10.1.2.1",
    "lease_pool_end": "10.1.2.254",
    "split_tunnel_networks": ["10.1.10.0/24"],
    "enable_compression": true,
    "enable_dtls": true
  },
  "create_connectivity_profile": true,
  "create_network_access": true,
  "create_webtop": true,
  "deploy_as3": false
}
```

### DeploymentResponse
```python
{
  "deployment_id": "uuid-here",
  "solution_type": "vpn",
  "solution_name": "solution1",
  "status": "completed",
  "message": "Deployment successful",
  "tasks": [
    {
      "task_name": "Create AD servers",
      "status": "completed",
      "message": "AAA AD server created"
    }
  ],
  "created_resources": {
    "profiles": ["/Common/solution1-psp", "/Common/solution1-cp"],
    "resources": ["/Common/solution1-vpn", "/Common/solution1-webtop"]
  },
  "errors": []
}
```

## Current Limitations

**Note:** The API is currently a **stub implementation** that returns mock responses. For actual deployments, use the Ansible playbooks directly:

```bash
# Use Ansible instead
ansible-playbook deploy_apm_vpn.yml
ansible-playbook deploy_apm_portal.yml
```

### Planned Features

To make the API fully functional:

1. **Ansible Integration**
   - Execute Ansible playbooks via `ansible-runner`
   - Stream playbook output to API responses
   - Handle async task execution with Celery

2. **F5 API Client**
   - Direct F5 iControl REST API integration
   - Transaction management
   - Error handling and retries

3. **Database**
   - Store deployment history
   - Track resource state
   - Audit logging

4. **Authentication**
   - JWT tokens
   - API keys
   - Role-based access control

5. **WebSocket Support**
   - Real-time deployment progress
   - Live log streaming

## Development

### Run Tests
```bash
pytest api/tests/
```

### Code Formatting
```bash
black api/
```

### Type Checking
```bash
mypy api/
```

### Generate OpenAPI Spec
The OpenAPI specification is auto-generated and available at:
```bash
curl http://localhost:8000/openapi.json > openapi.json
```

## Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

COPY api/ ./api/
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BIGIP_HOST=10.1.1.4
    volumes:
      - ./api:/app/api
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: f5-apm-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: f5-apm-api
  template:
    metadata:
      labels:
        app: f5-apm-api
    spec:
      containers:
      - name: api
        image: f5-apm-api:latest
        ports:
        - containerPort: 8000
```

## Security Considerations

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Enable SSL/TLS** in production
4. **Implement authentication** (JWT, OAuth2)
5. **Rate limiting** to prevent abuse
6. **Input validation** via Pydantic models
7. **CORS** configuration for production

## Related Documentation

- [API Endpoints Reference](../docs/API_ENDPOINTS.md)
- [Ansible Playbooks](../README.md)
- [F5 iControl REST API](https://clouddocs.f5.com/api/icontrol-rest/)

---

**Status:** Alpha - Stub implementation
**For Production Use:** Use Ansible playbooks directly
**Future:** Full API integration planned
