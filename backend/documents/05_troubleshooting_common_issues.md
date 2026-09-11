# Troubleshooting Common Client Configuration Issues

Document ID: KB-005
Last Updated: 2026-07-22
Audience: Customer Success Managers

## Authentication and Access Problems

### Symptom: User cannot log in to Configuration Studio

Possible causes and resolutions:

1. **SSO misconfiguration** – Verify the customer’s IdP metadata is correctly uploaded and the ACS URL matches the value shown in the OmniCorp admin console.
2. **Role not assigned** – The user may exist but has no roles. Assign at least the “Viewer” role via the Tenant Administration page.
3. **Session timeout** – Default idle timeout is 8 hours. Users can extend it in their profile settings (Enterprise only).

### Symptom: “Insufficient permissions” when trying to publish a package

The user needs the “Package Publisher” role on the specific package or on the parent workspace. CSMs can request elevated temporary access via the Access Request workflow.

## Deployment Failures

### Error: “Drift detected – cannot apply”

This occurs when the live environment has been modified outside of OCP (manual changes, other tools, or previous failed runs).

Resolution steps:

1. Open the Drift Report for the environment.
2. Decide whether to accept the live state (Import Drift) or force the desired state (Overwrite).
3. If Overwrite is chosen, the system will attempt to reconcile. Review the plan carefully before confirming.

### Error: “Quota exceeded on target provider”

Common on AWS and Azure when the customer has reached service quotas.

Resolution:

- Ask the customer to request a quota increase from their cloud provider.
- Alternatively, reduce the number of resources in the package or split it into smaller packages.

## Policy-Related Blocks

When a deployment is blocked by policy, the UI shows the exact policy name and the violating resource.

CSMs should:

1. Copy the policy decision ID.
2. Look up the decision in the Audit Log.
3. Either help the customer remediate the configuration or request a temporary exception from a Policy Administrator.

## Performance and Timeouts

Long-running Terraform applies (especially with large numbers of resources) may hit the default 60-minute timeout.

Enterprise customers can raise the timeout to 180 minutes via a support ticket. For very large environments, recommend breaking the package into logical modules that can be applied independently.
