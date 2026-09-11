# Deployment Orchestrator & Rollback Procedures

Document ID: KB-004
Last Updated: 2026-06-18
Audience: Customer Success Managers, Site Reliability Engineers

## Deployment Strategies

The OmniCorp Deployment Orchestrator supports the following strategies (configurable per environment):

- **Rolling** – Default for most Kubernetes and VM workloads. Updates instances gradually.
- **Blue/Green** – Maintains two identical environments. Traffic is switched only after the new version is verified healthy.
- **Canary** – Routes a small percentage of traffic (default 5%) to the new version. Automatically promotes or aborts based on success metrics.
- **All-at-once** – Used for non-critical or immutable infrastructure changes. Fast but higher risk.

## Pre-Deployment Checks

Before any deployment starts, the orchestrator runs:

1. Policy evaluation (see KB-003)
2. Variable validation
3. Drift detection against the current live state
4. Capacity and quota checks on the target cloud provider
5. Dependency graph analysis (if the package references other packages)

If any blocking check fails, the deployment is rejected and a detailed report is returned.

## Monitoring a Deployment

While a deployment is in progress, CSMs and operators can view:

- Real-time progress percentage
- Current stage (Planning → Applying → Verifying → Completing)
- Individual resource status
- Live logs from the Terraform/OpenTofu or Kubernetes controller
- Health check results from the Observability Hub

## Automatic and Manual Rollback

### Automatic Rollback Triggers

The system will automatically roll back if any of the following occur within the configured observation window (default 15 minutes):

- Health check failure rate exceeds the threshold (default 10%)
- Error rate in application metrics spikes above baseline + 3 standard deviations
- Critical policy violation is detected after the change
- Manual abort signal is received from an authorized user

### Manual Rollback

Any user with the “Deployment Operator” role can trigger a manual rollback from the Deployment History page or via the API:

```
POST /api/v1/deployments/{deployment_id}/rollback
```

The rollback restores the previous known-good version of the configuration package and re-applies it using the same strategy that was originally used.

## Post-Deployment Verification

After a successful deployment the system automatically:

- Runs a final drift check
- Updates the environment’s “last known good” pointer
- Generates a deployment summary report
- Sends notifications to the configured channels (Slack, Teams, email, PagerDuty)

CSMs should review the summary report with the customer, especially the list of resources that changed and any residual drift that requires attention.
