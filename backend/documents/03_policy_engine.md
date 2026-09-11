# Policy Engine and Compliance

Document ID: KB-003
Last Updated: 2026-05-10
Audience: Customer Success Managers, Security & Compliance Teams

## Overview

The OmniCorp Policy Engine evaluates every configuration package against organizational rules before it can be deployed. Policies are written in Open Policy Agent (OPA) Rego or HashiCorp Sentinel and are attached either globally or to specific environments.

## Policy Evaluation Points

Policies are evaluated at three distinct stages:

1. **Authoring time** – Soft warnings appear in Configuration Studio while the engineer is editing.
2. **Publish time** – Hard failures prevent a package from being published if critical policies fail.
3. **Deployment time** – Final gate. Even if a package was previously published, current policies are re-evaluated against the target environment.

## Built-in Policy Categories

OmniCorp ships with several policy packs that can be enabled per tenant:

- **Security Baseline** – Enforces encryption at rest, private networking, least-privilege IAM, and no public S3 buckets.
- **Cost Control** – Blocks oversized instance types, requires tags for cost allocation, and limits the number of resources per package.
- **Compliance** – Maps to common frameworks (SOC 2, ISO 27001, PCI-DSS, HIPAA). Customers can enable the relevant packs.
- **Naming Conventions** – Enforces standardized resource naming (e.g., `{env}-{app}-{resource}-{region}`).

## Custom Policies

Enterprise customers can upload their own Rego or Sentinel files. Custom policies must:

- Be syntactically valid
- Contain at least one `deny` or `violation` rule
- Include a severity level (`advisory`, `warning`, or `blocking`)
- Be approved by a user with the “Policy Administrator” role

## Policy Decision Logging

Every policy evaluation produces an immutable decision record that includes:

- Package ID and version
- Environment name
- Timestamp
- List of policies evaluated and their results
- User or service account that initiated the action

These records are retained for 7 years on the Enterprise tier and can be exported to SIEM systems via the Audit API.

## Common Policy Failures and How to Resolve Them

| Error Message                              | Likely Cause                          | Resolution                                      |
|--------------------------------------------|---------------------------------------|-------------------------------------------------|
| “Public IP not allowed in production”      | Resource has public IP association    | Remove public IP or use private endpoint        |
| “Missing required cost-center tag”         | Tag is absent or empty                | Add `cost-center` tag with valid value          |
| “Instance type exceeds cost policy”        | Using large instance types            | Switch to approved sizes or request exception   |
| “Encryption at rest is not enabled”        | Storage resource lacks encryption     | Enable customer-managed or service-managed keys |
