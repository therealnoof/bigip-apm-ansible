# Development Guide

This document covers Postman to Ansible conversion, customization, and adding new solutions.

## Postman to Ansible Mapping

| Postman Component | Ansible Equivalent | Notes |
|-------------------|-------------------|-------|
| Collection Variables | `vars/main.yml` | Centralized configuration |
| Pre-request Scripts | Task variables | Set facts before tasks |
| POST requests | `uri` module | HTTP method: POST |
| Transaction | `X-F5-REST-Coordination-Id` header | Used for policy creation |
| Basic Auth | `user/password` in uri | Per-task authentication |
| Status code checks | `status_code` parameter | Accept 200, 201, 409 |

## Key Differences from Postman

1. **Idempotency:** Ansible version accepts 409 (conflict) status codes for existing objects
2. **Error Handling:** Better error messages and retry capability
3. **Modularity:** Organized into reusable task files
4. **Variables:** Externalized configuration for easy customization
5. **Documentation:** Inline task names describe each step
6. **Conditional Execution:** Feature flags to enable/disable components

## What Was Converted

### Solution 1: VPN with Network Access
- AAA Active Directory configuration (3 API calls)
- Connectivity Profile (3 API calls)
- Network Access Resource (3 API calls)
- Webtop Configuration (4 API calls)
- Access Policy Creation (21 API calls with transaction)
- AS3 Application Deployment (4 API calls)
- GSLB Configuration (16 API calls - optional)
- **Subtotal: 54 API calls**

### Solution 2: Portal Access with AD Groups
- All Solution 1 components (AAA, connectivity, network access)
- Portal Access Resources (4 apps × 2 API calls each = 8 API calls)
- AD Group Query and Mapping (2 API calls)
- Extended Access Policy with group-based assignment (25+ API calls)
- **Subtotal: 60+ API calls**

### Solution 3: SAML Service Provider
- SAML IDP Connector (3 API calls)
- IDP Certificate Upload (2 API calls)
- SAML Service Provider Configuration (2 API calls)
- SAML Authentication Access Policy (25+ API calls)
- AS3 Application Deployment (4 API calls)
- GSLB Configuration (16 API calls - optional)
- **Subtotal: 52+ API calls**

### Solution 4: SAML Identity Provider
- Self-Signed Certificate Generation (OpenSSL - 3 tasks)
- Certificate and Key Upload (4 API calls with Content-Range)
- SAML IDP Service Configuration (2 API calls)
- SAML SP Connector Configuration (2 API calls)
- AAA Active Directory Configuration (3 API calls)
- Access Policy with Logon + AD Auth (25+ API calls with transaction)
- AS3 Application Deployment (4 API calls)
- GSLB Configuration (16 API calls - optional)
- **Subtotal: 55+ API calls**

### Solution 5: SAML SP with Internal IDP
- SAML IDP Connector (pointing to internal IDP - 1 API call)
- SAML Service Provider Configuration (1 API call)
- Access Policy with SAML Auth (20+ API calls with transaction)
- AS3 Application Deployment (4 API calls)
- GSLB Configuration (16 API calls - optional)
- **Subtotal: 42+ API calls**

### Solution 7: SAML with Sideband Communication
- Active Directory configuration (3 API calls)
- SAML IDP Connector with Okta certificate (4 API calls)
- Self-signed certificate generation (4 tasks)
- SAML SP and IDP Service configuration (4 API calls)
- Kerberos SSO profile (1 API call)
- VS1 Access Policy with SAML/AD/iRule (25+ API calls with transaction)
- VS2 Access Policy with Variable Assign (15+ API calls with transaction)
- AS3 Application with 2 virtual servers and iRules (1 API call)
- **Subtotal: 55+ API calls**

### Solution 8: OAuth Authorization Server
- Active Directory configuration (3 API calls)
- JWK Configuration (1 API call)
- OAuth Profile (1 API call)
- Access Policy with OAuth Authorization (25+ API calls with transaction)
- AS3 Application Deployment (1 API call)
- GSLB Configuration (optional, 6 API calls)
- **Subtotal: 35+ API calls**

### Solution 9: OAuth Resource Server (Client)
- CA Certificate upload and installation (2 API calls)
- JWK Configuration (1 API call)
- JWT Configuration (1 API call)
- OAuth Provider (1 API call)
- JWT Provider List (1 API call)
- OAuth Client Application (2 API calls with customization)
- Access Policy with OAuth Scope (15+ API calls with transaction)
- AS3 Application Deployment (1 API call)
- **Subtotal: 25+ API calls**

**Grand Total: 380+ API calls automated across all solutions**

### Not Included (from original collections)

- Loop/monitoring endpoints (replaced with Ansible's built-in capabilities)
- Some Postman test scripts (validation handled by Ansible)
- Address management API calls (optional, configurable)

## Customization

### Modifying Network Access

Edit `vars/main.yml`:

```yaml
# Change IP pool range
vpn_lease_pool_start: "10.2.0.1"
vpn_lease_pool_end: "10.2.0.100"

# Modify split tunnel networks
vpn_split_tunnel_networks:
  - "192.168.1.0/255.255.255.0"
  - "192.168.2.0/255.255.255.0"
  - "172.16.0.0/255.255.0.0"
```

### Changing Customization Type

```yaml
# Use different customization templates
custom_type: "modern"  # or "standard"
```

### Adding Pool Members

For application deployment:

```yaml
app_pool_members:
  - "10.1.20.10:80"
  - "10.1.20.11:80"
```

### Custom Access Policy

To modify the access policy flow, edit `tasks/access_policy.yml` and adjust:
- Policy items
- Agent configurations
- Rules and expressions
- Flow connections

## Security Considerations

### Credential Management

1. **Never commit plaintext passwords** to version control
2. **Use Ansible Vault** for sensitive data:
   ```bash
   ansible-vault create vars/vault.yml
   ansible-vault encrypt vars/main.yml
   ```
3. **Use environment variables** for passwords:
   ```bash
   export BIGIP_PASSWORD="your_password"
   ```

### Network Security

1. Restrict Ansible control node access to management networks
2. Use jump hosts for production environments
3. Enable audit logging on Ansible control node
4. Use SSL/TLS for all communications

### Change Management

1. **Test in non-production** environments first
2. **Create UCS backup** before deployment:
   ```bash
   tmsh save sys ucs pre-apm-deployment.ucs
   ```
3. **Document customizations** from baseline
4. **Review configurations** with security team
5. **Maintain rollback plan**

## Adding More Solutions

This playbook is designed to be extended with additional Postman collections. To add more solutions:

1. **Add new task file** in `tasks/` directory
2. **Define variables** in `vars/main.yml`
3. **Include tasks** in main playbook
4. **Update documentation**

Example structure for adding "solution2":

```yaml
# In deploy_apm_vpn.yml
- name: Deploy Solution 2
  include_tasks: tasks/solution2_tasks.yml
  when: deploy_solution2 | default(false)
```

## Converting a New Postman Collection

### Step 1: Analyze the Collection

```bash
# Download the Postman collection
curl -o collection.json https://raw.githubusercontent.com/.../collection.json

# Review structure
python3 -c "import json; print(json.dumps(json.load(open('collection.json')), indent=2))"
```

### Step 2: Identify API Calls

Extract all API endpoints and their parameters:

```python
import json

with open('collection.json') as f:
    collection = json.load(f)

for item in collection['item']:
    print(f"Name: {item['name']}")
    print(f"Method: {item['request']['method']}")
    print(f"URL: {item['request']['url']['raw']}")
    print("---")
```

### Step 3: Create Task File

Template for a new task:

```yaml
---
# tasks/new_solution.yml

- name: Create Component
  uri:
    url: "https://{{ ansible_host }}/mgmt/tm/apm/..."
    method: POST
    user: "{{ bigip_user }}"
    password: "{{ bigip_pass }}"
    validate_certs: no
    body_format: json
    body:
      name: "{{ component_name }}"
      # ... other parameters
    status_code: [200, 201, 409]
  register: component_result
```

### Step 4: Handle Transactions

For policy creation that requires transactions:

```yaml
- name: Create Transaction
  uri:
    url: "https://{{ ansible_host }}/mgmt/tm/transaction"
    method: POST
    # ...
  register: transaction

- name: Create Policy Item (within transaction)
  uri:
    url: "https://{{ ansible_host }}/mgmt/tm/apm/policy/policy-item"
    method: POST
    headers:
      X-F5-REST-Coordination-Id: "{{ transaction.json.transId }}"
    # ...

- name: Commit Transaction
  uri:
    url: "https://{{ ansible_host }}/mgmt/tm/transaction/{{ transaction.json.transId }}"
    method: PATCH
    body:
      state: "VALIDATING"
    # ...
```

## References

- [F5 BIG-IP REST API Documentation](https://clouddocs.f5.com/api/icontrol-rest/)
- [F5 APM Configuration Guide](https://clouddocs.f5.com/apm/)
- [AS3 Documentation](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/)
- [Ansible URI Module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/uri_module.html)
- [Source Postman Collections](https://github.com/f5devcentral/access-solutions/)
