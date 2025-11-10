
# My Cool Service

## Overview

This repository contains a cloud-native microservice that provides two REST endpoints for managing users with role-based access control. Authorization is handled using Open Policy Agent (OPA).

### Features
- **FastAPI** REST service with two endpoints:
  - `GET /api/users` - List all users (requires authentication)
  - `POST /api/users` - Create new user (requires admin role)
- **OPA (Open Policy Agent)** for policy-based authorization
- **Multiple deployment options**: Local Docker Compose, Minikube, AWS/Terraform
- **Logging**: All OPA authorization decisions are logged

### Security & Authorization
- Only users with "admin" role can create new users (POST)
- Any authenticated user can read the list of users (GET)
- All other requests are denied by default
- Token-based authentication validated by OPA

## Directory Structure

```
repository-root/
├── ansible/
│   ├── playbook.yml
│   └── inventory
├── helm-charts/
│   ├── my-cool-service/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       └── ingress.yaml
│   └── opa-service/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           └── configmap.yaml
├── my-cool-service/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
├── opa/
│   ├── policy.rego
├── terraform/
│   ├── main.tf
│   └── variables.tf (optional)
├── argo-app.yaml
└── README.md
```

## Quick Start - Local Development

The fastest way to test the service locally using Docker Compose:

```bash
# Start services
docker compose up --build

# Test GET endpoint (user role)
curl -H "token: climacs@climacs.net" http://localhost:8000/api/users

# Test POST endpoint (admin role)
curl -X POST -H "Content-Type: application/json" \
  -H "token: climacs@gmail.com" \
  -d '{"name":"Test User","email":"test@example.com"}' \
  http://localhost:8000/api/users
```

📖 See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed local testing guide.

## Available Tokens

| Token | Role | Permissions |
|-------|------|-------------|
| `climacs@gmail.com` | admin | GET, POST |
| `climacs@climacs.net` | user | GET only |
| `miguelnero.climacosa@gmail.com` | user | GET only |

---

## Production Deployment Options

### Option 1: Local Minikube (Recommended for Testing)

Deploy to local Kubernetes cluster:

```bash
# Start Minikube
minikube start

# Deploy OPA
kubectl apply -f fastapi_service/opa-configmap.yaml
kubectl apply -f fastapi_service/opa-deployment.yaml
kubectl apply -f fastapi_service/opa-service.yaml

# Deploy FastAPI service
kubectl apply -f fastapi_service/service-deployment.yaml
kubectl apply -f fastapi_service/service.yaml

# Get service URL
minikube service my-cool-service --url
```

### Option 2: AWS with Terraform + Ansible (Production)

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- AWS CLI configured

## Setup Instructions

#### Step 1: Provision AWS Infrastructure with Terraform

Navigate to the `terraform` directory and provision EC2 instance:

```bash
cd terraform
terraform init
terraform apply
```

**Note:** Copy the output IP address and add it to `ansible/inventory` file.

#### Step 2: Deploy with Ansible

Configure the server and deploy Kubernetes cluster:

```bash
cd ../ansible
# Edit inventory file with EC2 IP from terraform output
ansible-playbook -i inventory playbook.yml
```

This will:
- Install Minikube, kubectl, Helm
- Deploy ArgoCD for GitOps
- Set up NGINX Ingress and Cert-Manager
- Configure Let's Encrypt SSL
- Deploy the application via Helm charts

#### Step 3: Build and Push Docker Image

```bash
cd fastapi_service/app
docker build -t climacs/my-cool-service:latest .
docker push climacs/my-cool-service:latest
```

#### Step 4: Update OPA Policy

If you need to update the OPA policy, edit the `opa/policy.rego` file. Then update the ConfigMap and apply the changes:

```sh
cd ../ansible
ansible-playbook -i inventory playbook.yml --tags "opa-policy"
```

### 5. Access the Application

- **My Cool Service API**: [https://malamig-na-serbisyo.climacs.net/api](https://malamig-na-serbisyo.climacs.net/api)
- **OPA Service**: [https://malamig-na-serbisyo.climacs.net/opa](https://malamig-na-serbisyo.climacs.net/opa)
- **Swagger UI**: [https://malamig-na-serbisyo.climacs.net/swagger](https://malamig-na-serbisyo.climacs.net/swagger)

---

## Architecture

```
┌─────────────────┐
│     Client      │
└────────┬────────┘
         │ HTTP Request (with token header)
         ▼
┌─────────────────┐
│  FastAPI Service│  
│  (Port 8000)    │
└────────┬────────┘
         │ Authorization Request
         │ POST /v1/data/authz/allow
         │ {"input": {"token": "...", "method": "..."}}
         ▼
┌─────────────────┐
│   OPA Service   │
│  (Port 8181)    │
│  policy.rego    │
└────────┬────────┘
         │ Decision (true/false)
         ▼
    Allow/Deny Access
```

## API Endpoints

### GET /api/users

**Description:** List all users

**Authentication:** Required (any valid token)

**Request:**
```bash
curl -H "token: climacs@climacs.net" http://localhost:8000/api/users
```

**Response:**
```json
[
  {"name": "Admin User", "email": "climacs@gmail.com"},
  {"name": "Regular User", "email": "climacs@climacs.net"}
]
```

### POST /api/users

**Description:** Create a new user

**Authentication:** Required (admin role only)

**Request:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -H "token: climacs@gmail.com" \
  -d '{"name":"New User","email":"new@example.com"}' \
  http://localhost:8000/api/users
```

**Response:**
```json
{"name": "New User", "email": "new@example.com"}
```

**Error Response (403 Forbidden):**
```json
{"detail": "Forbidden"}
```

## Testing & Validation

### View OPA Logs

```bash
# Docker Compose
docker compose logs -f opa

# Kubernetes
kubectl logs -f deployment/opa
```

All authorization decisions are logged in JSON format with debug information.

### Test OPA Policy Directly

```bash
# Test admin access for POST
curl -X POST http://localhost:8181/v1/data/authz/allow \
  -H "Content-Type: application/json" \
  -d '{"input": {"token": "climacs@gmail.com", "method": "POST"}}'

# Expected: {"result": true}
```

## Additional Notes

- If you need to add a new key pair or adjust the code for an existing key pair, you must update the Terraform script accordingly.
- Ensure all services are up and running in the Kubernetes cluster.
- Check DNS configurations to make sure the FQDN points to the correct IP.
- The OPA policy is critical for authorization and should be thoroughly tested.

By following these instructions, you will be able to set up and deploy the My Cool Service application with proper authorization and access control, as well as ensure it is accessible via the specified FQDN with HTTPS.

