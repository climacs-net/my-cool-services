# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a cloud-native microservice deployment project that combines:
- **FastAPI service** with OPA (Open Policy Agent) for policy-based authorization
- **Terraform** for AWS infrastructure provisioning
- **Ansible** for server configuration
- **Kubernetes (Minikube)** for container orchestration

The service implements a simple user API with role-based access control enforced by OPA.

## Architecture

### Infrastructure Layer (Terraform)
- Provisions AWS EC2 instance (t3.medium, Ubuntu 24.04) in us-east-1
- Creates Elastic IP for stable endpoint
- Configures Route53 DNS record (my-cool-service.climacs.net)
- User data bootstraps Python, Docker, and Minikube

### Configuration Layer (Ansible)
- Installs Kubernetes tooling (kubectl, Minikube)
- Sets up Docker and cri-dockerd runtime
- Deploys CNI plugins and container networking
- Transfers Kubernetes manifests to target server

### Application Layer
- **FastAPI Service** (`fastapi_service/app/main.py`): Exposes `/api/users` endpoints (GET/POST)
- **OPA Sidecar**: Policy engine validating requests based on email-based tokens
- **Authorization Flow**: FastAPI → OPA service → policy.rego evaluation

### Policy-Based Authorization
- OPA policy (`fastapi_service/policy.rego`) defines roles:
  - `admin` role: Can POST (create users)
  - `user` role: Can GET (read users)
- Token is user's email address
- User data stored in `fastapi_service/app/users.json`

### Deployment Architecture
Two FastAPI implementations exist:
- `fastapi_service/main.py`: Simple in-memory user list
- `fastapi_service/app/main.py`: Persistent storage using users.json (deployed version)

## Common Commands

### Infrastructure Management

```bash
# Provision AWS infrastructure
cd terraform
terraform init
terraform apply

# Get EC2 public IP from Terraform output
terraform output instance_ip

# Destroy infrastructure
terraform destroy
```

### Server Configuration

```bash
# Configure EC2 instance (replace with actual IP from terraform output)
cd ansible
ansible-playbook -i 'YOUR_EC2_IP,' playbook.yml
```

### Kubernetes Deployment

```bash
# Deploy OPA and policy
kubectl apply -f fastapi_service/opa-configmap.yaml
kubectl apply -f fastapi_service/opa-config.yaml
kubectl apply -f fastapi_service/opa-deployment.yaml

# Deploy FastAPI service
kubectl apply -f fastapi_service/service-deployment.yaml
kubectl apply -f fastapi_service/service.yaml

# Check deployment status
kubectl get pods
kubectl get services

# View logs
kubectl logs deployment/my-cool-service
kubectl logs deployment/opa
```

### Local Development

```bash
# Install Python dependencies
cd fastapi_service/app
pip install -r requirements.txt

# Run FastAPI locally
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Build Docker image
docker build -t climacs/my-cool-service:latest .
```

### Testing the Service

```bash
# Test GET endpoint (requires user role token)
curl -H "token: climacs@climacs.net" http://my-cool-service.climacs.net:30001/api/users

# Test POST endpoint (requires admin role token)
curl -X POST -H "Content-Type: application/json" \
  -H "token: climacs@gmail.com" \
  -d '{"name":"New User","email":"new@example.com"}' \
  http://my-cool-service.climacs.net:30001/api/users
```

## Key Files and Relationships

- `terraform/main.tf`: Defines AWS resources (EC2, EIP, Route53)
- `ansible/playbook.yml`: Installs dependencies and sets up Minikube
- `fastapi_service/app/main.py`: Primary application code (deployed)
- `fastapi_service/policy.rego`: OPA authorization policy
- `fastapi_service/app/users.json`: User data store
- `fastapi_service/service-deployment.yaml`: Kubernetes deployment for FastAPI
- `fastapi_service/opa-deployment.yaml`: Kubernetes deployment for OPA
- `fastapi_service/opa-configmap.yaml`: OPA policy ConfigMap

## Important Configuration Details

### Environment Variables
- `OPA_URL`: OPA service endpoint (defaults to `http://opa-service.opa.svc.cluster.local/v1/data/authz/allow`)

### Authentication Tokens
Tokens are email addresses that must match entries in `policy.rego`:
- `climacs@gmail.com` - admin role
- `climacs@climacs.net` - user role
- `miguelnero.climacosa@gmail.com` - user role

### Service Endpoints
- External access: `http://my-cool-service.climacs.net:30001`
- Internal API paths: `/api/users` (GET, POST)

### AWS Configuration
- Region: us-east-1
- Availability Zone: us-east-1b
- Key pair: `terraform_aws_key` (uses `~/.ssh/id_ed25519.pub`)
- Route53 Zone ID: Z3RUW5P7TDNES4

## Development Workflow

1. Modify code in `fastapi_service/app/`
2. Test locally with uvicorn
3. Build and push Docker image: `docker build -t climacs/my-cool-service:latest . && docker push climacs/my-cool-service:latest`
4. Update Kubernetes deployment: `kubectl rollout restart deployment/my-cool-service`
5. Update OPA policies by modifying `policy.rego` and reapplying ConfigMap

## Troubleshooting

```bash
# Check OPA service connectivity
kubectl exec -it deployment/my-cool-service -- curl http://opa-service.opa.svc.cluster.local/v1/data/authz/allow

# View OPA policy decisions
kubectl logs deployment/opa

# Check service endpoints
kubectl get svc -A

# Debug pod issues
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```
