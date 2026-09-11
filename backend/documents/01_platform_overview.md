# OmniCorp Configuration Platform – Product Overview

Document ID: KB-001
Last Updated: 2026-03-15
Audience: Customer Success Managers, Solution Architects

## Introduction

The OmniCorp Configuration Platform (OCP) is an enterprise-grade configuration management and orchestration system designed for hybrid and multi-cloud environments. It enables organizations to define, version, validate, and deploy infrastructure and application configurations at scale with strong governance and auditability.

OCP consists of four core components:

1. **Configuration Studio** – A web-based visual and code editor for creating and managing configuration packages.
2. **Policy Engine** – Enforces organizational standards, security baselines, and compliance rules before any configuration can be applied.
3. **Deployment Orchestrator** – Handles staged rollouts, canary deployments, blue/green strategies, and automatic rollbacks.
4. **Observability Hub** – Provides real-time visibility into configuration drift, deployment status, and compliance posture.

## Supported Environments

OCP currently supports the following target platforms:

- AWS (EC2, ECS, EKS, Lambda, RDS, S3, IAM)
- Microsoft Azure (VMs, AKS, App Service, Azure Functions, SQL Database)
- Google Cloud Platform (GCE, GKE, Cloud Run, Cloud Functions)
- On-premises Kubernetes clusters (v1.24+)
- VMware vSphere (via Terraform provider integration)

## Licensing Tiers

| Tier          | Max Environments | Concurrent Deployments | Policy Rules | Support Level      |
|---------------|------------------|------------------------|--------------|--------------------|
| Starter       | 3                | 5                      | 25           | Business hours     |
| Professional  | 15               | 25                     | Unlimited    | 24×5               |
| Enterprise    | Unlimited        | Unlimited              | Unlimited    | 24×7 + TAM         |

Enterprise tier also includes dedicated tenant isolation, custom SSO integration, and advanced audit logging with 7-year retention.

## Key Terminology

- **Configuration Package**: A versioned collection of infrastructure-as-code (Terraform/OpenTofu), Kubernetes manifests, and policy rules.
- **Environment**: A logical deployment target (e.g., “prod-us-east”, “staging-eu”).
- **Drift**: Difference between the desired state defined in a package and the actual state running in the environment.
- **Promotion**: Moving a configuration package from one environment to another after successful validation.
