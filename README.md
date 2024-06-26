
# My Cool Service

## Overview

This repository contains the code and infrastructure for the My Cool Service application, which includes two REST endpoints for managing users. Authorization is handled using Open Policy Agent (OPA) and the application is deployed on Kubernetes using Helm and ArgoCD.

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

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- [Docker](https://docs.docker.com/get-docker/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm](https://helm.sh/docs/intro/install/)
- [ArgoCD](https://argo-cd.readthedocs.io/en/stable/getting_started/)

## Setup Instructions

### 1. Provision AWS Infrastructure with Terraform

Navigate to the `terraform` directory and run the following commands to provision the necessary AWS infrastructure:

```sh
cd terraform
terraform init
terraform apply
```

## Note: 
After the Terraform apply completes, copy the IP address from the output and manually add it to the Ansible inventory file.

### 2. Deploy the Application with Ansible

Navigate to the `ansible` directory and run the following command to deploy the Kubernetes cluster and the application:

```sh
cd ../ansible
ansible-playbook -i inventory playbook.yml
```

### 3. Build and Push Docker Image

Navigate to the `my-cool-service` directory, build the Docker image, and push it to your Docker repository:

```sh
cd ../my-cool-service
docker build -t your-docker-repo/my-cool-service:latest .
docker push your-docker-repo/my-cool-service:latest
```

### 4. Update OPA Policy

If you need to update the OPA policy, edit the `opa/policy.rego` file. Then update the ConfigMap and apply the changes:

```sh
cd ../ansible
ansible-playbook -i inventory playbook.yml --tags "opa-policy"
```

### 5. Access the Application

- **My Cool Service API**: [https://malamig-na-serbisyo.climacs.net/api](https://malamig-na-serbisyo.climacs.net/api)
- **OPA Service**: [https://malamig-na-serbisyo.climacs.net/opa](https://malamig-na-serbisyo.climacs.net/opa)
- **Swagger UI**: [https://malamig-na-serbisyo.climacs.net/swagger](https://malamig-na-serbisyo.climacs.net/swagger)

### 6. Testing with Postman

Use the provided Postman collection to test the endpoints. Import the collection into Postman and execute the requests to ensure everything is working correctly.

## Additional Notes

- If you need to add a new key pair or adjust the code for an existing key pair, you must update the Terraform script accordingly.
- Ensure all services are up and running in the Kubernetes cluster.
- Check DNS configurations to make sure the FQDN points to the correct IP.
- The OPA policy is critical for authorization and should be thoroughly tested.

By following these instructions, you will be able to set up and deploy the My Cool Service application with proper authorization and access control, as well as ensure it is accessible via the specified FQDN with HTTPS.

