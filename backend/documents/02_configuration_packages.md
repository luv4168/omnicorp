# Working with Configuration Packages

Document ID: KB-002
Last Updated: 2026-04-02
Audience: Customer Success Managers, Implementation Engineers

## What is a Configuration Package?

A Configuration Package is the fundamental unit of work in the OmniCorp Configuration Platform. It is a self-contained, versioned artifact that describes the desired state of one or more resources.

Every package contains:

- `manifest.yaml` – Metadata (name, version, owner, required policies)
- `terraform/` or `opentofu/` – Infrastructure definitions
- `k8s/` – Kubernetes manifests and Helm values (optional)
- `policies/` – OPA/Rego or Sentinel policy files
- `variables.tf` / `values.yaml` – Input variables with validation rules
- `README.md` – Human-readable documentation and change notes

## Creating a Package

1. Open Configuration Studio.
2. Click **New Package**.
3. Choose a template (Empty, AWS Baseline, Azure Landing Zone, Kubernetes Workload, or Multi-Cloud).
4. Fill in the package name (must be lowercase alphanumeric + hyphens, max 64 characters).
5. Assign an owner team and set the initial version (semantic versioning is enforced: MAJOR.MINOR.PATCH).

## Versioning Rules

- Every change that alters the desired state requires a new version.
- The system automatically creates a new version when you click **Publish**.
- Draft versions are only visible to the owning team.
- Published versions are immutable. To change them you must create a new version.

## Variable Validation

Variables defined in a package support the following constraints:

- `type`: string, number, bool, list, map, object
- `required`: true/false
- `validation`: custom regex or expression (e.g., “must match CIDR notation”)
- `sensitive`: true (value is masked in logs and UI)
- `default`: optional default value

If a required variable is missing or fails validation during a deployment, the deployment is blocked and a clear error is returned to the user.

## Package Promotion Workflow

Recommended promotion path for production-bound packages:

1. Develop in a personal or team workspace.
2. Publish to the **Development** environment.
3. After automated tests and peer review, promote to **Staging**.
4. Run full integration and compliance scans in Staging.
5. Promote to **Production** only after Staging has been stable for the required soak period (default 24 hours, configurable per environment).

Promotion can be done manually by a user with the “Environment Promoter” role or automatically via approved pipelines.
