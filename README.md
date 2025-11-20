# F5 BIG-IP APM Solutions - Ansible Automation

Ansible playbooks for deploying F5 BIG-IP Access Policy Manager (APM) solutions with Active Directory and SAML authentication, converted from Postman REST API collections.

## Overview

This project automates the deployment of production-ready APM solutions including:

### Solution 1: VPN with Network Access
- **Active Directory Authentication** - AAA server configuration
- **VPN Connectivity** - PPP tunnel with compression
- **Network Access** - IP lease pool with split tunneling
- **Webtop** - Full webtop with network access resources
- **Access Policy** - Per-session policy with logon page and AD auth
- **Application Deployment** - AS3-based HTTPS virtual server
- **GSLB** - Optional multi-datacenter DNS configuration

**Source:** [solution1-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution1/postman/solution1-create.postman_collection.json)

### Solution 2: Portal Access with AD Group Mapping
- **Active Directory Authentication** - AAA server with group query
- **Portal Access Resources** - Web application proxying (4 backend apps)
- **AD Group-Based Assignment** - Dynamic resource assignment based on AD group membership
- **Optional VPN Access** - Network access for specific groups
- **Webtop** - User portal showing group-specific resources
- **Access Policy** - Per-session policy with AD group mapping
- **Application Deployment** - AS3-based HTTPS virtual server
- **GSLB** - Optional multi-datacenter DNS configuration

**Source:** [solution2-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution2/postman/solution2-create.postman_collection.json)

### Solution 3: SAML Service Provider with Okta IDP
- **SAML Authentication** - SAML 2.0 Service Provider configuration
- **Identity Provider Integration** - Okta (or other SAML 2.0 IDP) connector
- **Certificate Management** - IDP signing certificate installation
- **Access Policy** - Per-session policy with SAML authentication
- **Application Deployment** - AS3-based HTTPS virtual server with APM profile
- **GSLB** - Optional multi-datacenter DNS configuration

**Source:** [solution3-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution3/postman/solution3-create.postman_collection.json)

## Architecture

### Solution 1: VPN Access Flow

```
Start → Logon Page → AD Authentication → Resource Assign → Allow
                            │                    │
                            ▼ (Failed)           │
                          Deny                   ▼
                                        VPN + Webtop Resources
```

**Resources Assigned:** All authenticated users receive VPN and webtop access

### Solution 2: Portal Access with AD Group Mapping Flow

```
Start → Logon Page → AD Auth → AD Query → AD Group Mapping → Allow
                        │          │              │
                        ▼ (Failed) │              ▼
                      Deny         │      Dynamic Resource Assignment
                                   │      Based on AD Group:
                                   │      - Sales Engineering: server1 + VPN
                                   │      - Product Management: server1 + server2
                                   │      - Product Development: server2/3/4
                                   │      - IT: VPN only
                                   ▼
                            Get AD Group Membership
```

**Resources Assigned:** Users receive different portal applications based on their AD group membership

### Components Architecture (Solution 1)

```
┌─────────────────────────────────────────────────────────┐
│ VPN Client                                               │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTPS (443)
                    ▼
┌─────────────────────────────────────────────────────────┐
│ F5 BIG-IP - APM VPN Solution                            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Virtual Server (HTTPS)                            │  │
│  │ - Client SSL Profile                             │  │
│  │ - Access Profile: solution1-psp                  │  │
│  │ - Connectivity Profile: solution1-cp             │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                                │
│  ┌──────────────────────┼───────────────────────────┐  │
│  │ Per-Session Policy   ▼                            │  │
│  │                                                    │  │
│  │  1. Logon Page → 2. AD Auth → 3. Resource Assign │  │
│  │                      │                    │        │  │
│  │                      │ Success            │        │  │
│  │                      ▼                    ▼        │  │
│  │               Allow Ending      Deny Ending       │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Network Access Resource                           │  │
│  │ - VPN Tunnel (PPP)                               │  │
│  │ - IP Lease Pool (10.1.2.1-254)                   │  │
│  │ - Split Tunneling (10.1.10.0/24, 10.1.20.0/24)  │  │
│  │ - DTLS Enabled                                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Webtop                                            │  │
│  │ - Full Webtop                                     │  │
│  │ - Network Access Section                          │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────┘
                    │ AD Queries
                    ▼
┌─────────────────────────────────────────────────────────┐
│ Active Directory Server (10.1.20.7)                     │
└─────────────────────────────────────────────────────────┘
```

### Components Architecture (Solution 2)

```
┌─────────────────────────────────────────────────────────┐
│ Browser Client                                           │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTPS (443)
                    ▼
┌─────────────────────────────────────────────────────────┐
│ F5 BIG-IP - APM Portal Solution                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Virtual Server (HTTPS)                            │  │
│  │ - Client SSL Profile                             │  │
│  │ - Access Profile: solution2-psp                  │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                                │
│  ┌──────────────────────┼───────────────────────────┐  │
│  │ Per-Session Policy   ▼                            │  │
│  │                                                    │  │
│  │  Logon → AD Auth → AD Query → AD Group Mapping   │  │
│  │                      │           │          │     │  │
│  │                      │ Success   │          │     │  │
│  │                      ▼           ▼          ▼     │  │
│  │               Get Groups   Assign Resources      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Portal Access Resources                           │  │
│  │ - server1.acme.com (Sales, Prod Mgmt)            │  │
│  │ - server2.acme.com (Prod Mgmt, Prod Dev)         │  │
│  │ - server3.acme.com (Prod Dev)                    │  │
│  │ - server4.acme.com (Prod Dev)                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Webtop (Group-Specific Resources)                │  │
│  │ - Dynamic based on AD group membership           │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────┘
                    │ AD Queries (with memberOf)
                    ▼
┌─────────────────────────────────────────────────────────┐
│ Active Directory Server (10.1.20.7)                     │
│ Groups: Sales Engineering, Product Management,          │
│         Product Development, IT                         │
└─────────────────────────────────────────────────────────┘
```

### Solution 3: SAML Authentication Flow

```
Start → SAML Auth → Successful → Allow
           │             │
           │             ▼ (Failed)
           │           Deny
           ▼
     Redirect to IDP
     (Okta SSO)
           │
           ▼
     User authenticates
     at IDP
           │
           ▼
     SAML assertion
     returned to SP
```

**Authentication Flow:** Users are redirected to Okta IDP for authentication, then SAML assertion is validated before granting access

### Components Architecture (Solution 3)

```
┌─────────────────────────────────────────────────────────┐
│ Browser Client                                           │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTPS (443)
                    ▼
┌─────────────────────────────────────────────────────────┐
│ F5 BIG-IP - APM SAML Service Provider                  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Virtual Server (HTTPS)                            │  │
│  │ - Client SSL Profile                             │  │
│  │ - Access Profile: solution3-psp                  │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                                │
│  ┌──────────────────────┼───────────────────────────┐  │
│  │ Per-Session Policy   ▼                            │  │
│  │                                                    │  │
│  │  Start → SAML Auth → Success → Allow             │  │
│  │             │           │                         │  │
│  │             │           ▼ (Failed)                │  │
│  │             │         Deny                        │  │
│  │             ▼                                      │  │
│  │      Redirect to IDP                              │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ SAML Configuration                                │  │
│  │ - Service Provider: sp.acme.com                  │  │
│  │ - Entity ID: https://sp.acme.com                 │  │
│  │ - IDP Connector: solution3-sso                   │  │
│  │ - IDP Certificate: solution3-idp                 │  │
│  │ - SSO Binding: HTTP-POST                         │  │
│  │ - Signature Type: RSA-SHA256                     │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────┘
                    │ SAML Redirect/POST
                    ▼
┌─────────────────────────────────────────────────────────┐
│ Okta Identity Provider (dev-818899.okta.com)           │
│ - Entity ID: http://www.okta.com/exkafm6qvkEv6UK0d4x6  │
│ - SSO URI: https://dev-818899.okta.com/.../sso/saml   │
│ - User Directory & Authentication                       │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
bigip-apm-ansible/
├── README.md                          # This file
├── QUICKSTART.md                      # 5-minute setup guide
├── ansible.cfg                        # Ansible configuration
├── inventory.yml                      # BIG-IP device inventory
├── deploy_apm_vpn.yml                # Solution 1: VPN deployment playbook
├── deploy_apm_portal.yml             # Solution 2: Portal deployment playbook
├── deploy_apm_saml.yml               # Solution 3: SAML deployment playbook
├── delete_apm_vpn.yml                # Solution 1/2: Interactive deletion playbook
├── delete_apm_portal.yml             # Solution 2: Interactive deletion playbook
├── delete_apm_saml.yml               # Solution 3: Interactive deletion playbook
├── cleanup_apm_vpn.yml               # Solution 1: Automated cleanup playbook
├── cleanup_apm_portal.yml            # Solution 2: Automated cleanup playbook
├── cleanup_apm_saml.yml              # Solution 3: Automated cleanup playbook
├── vars/
│   ├── main.yml                      # Solution 1 variables
│   ├── solution2.yml                 # Solution 2 variables
│   └── solution3.yml                 # Solution 3 variables (SAML)
├── tasks/
│   ├── aaa_ad_servers.yml            # AD server configuration
│   ├── connectivity_profile.yml       # VPN tunnel and connectivity
│   ├── network_access.yml             # Network access resource
│   ├── portal_resources.yml           # Portal access resources (Solution 2)
│   ├── portal_resource_item.yml       # Single portal resource creation
│   ├── saml_idp_connector.yml        # SAML IDP connector (Solution 3)
│   ├── saml_sp.yml                   # SAML Service Provider (Solution 3)
│   ├── webtop.yml                    # Webtop configuration
│   ├── access_policy.yml             # Solution 1 per-session policy
│   ├── access_policy_solution2.yml    # Solution 2 policy with AD groups
│   ├── access_policy_solution3.yml    # Solution 3 policy with SAML auth
│   ├── as3_deployment.yml            # Application deployment
│   └── gslb_configuration.yml        # DNS/GSLB setup
└── docs/
    ├── API_MAPPING.md                # Postman to Ansible conversion details
    ├── CLEANUP_GUIDE.md              # Deletion and cleanup guide
    ├── solution1-create.postman_collection.json   # Solution 1 source
    ├── solution1-delete.postman_collection.json   # Solution 1 delete
    ├── solution2-create.postman_collection.json   # Solution 2 source
    ├── solution2-delete.postman_collection.json   # Solution 2 delete
    ├── solution3-create.postman_collection.json   # Solution 3 source
    └── solution3-delete.postman_collection.json   # Solution 3 delete

```

## Requirements

### Software Requirements

- **Ansible:** 2.9 or later
- **Python:** 3.6 or later
- **Python Libraries:**
  - requests
  - urllib3

### BIG-IP Requirements

- **F5 BIG-IP:** Version 13.x or later
- **Modules Licensed:**
  - LTM (Local Traffic Manager)
  - APM (Access Policy Manager)
  - AS3 (Application Services 3 Extension) - for app deployment
  - GTM (Global Traffic Manager) - optional, for GSLB
- **Management Access:** HTTPS (port 443)
- **Credentials:** Administrative privileges

### Network Requirements

- Ansible control node can reach BIG-IP management interface
- BIG-IP can reach Active Directory server
- VPN clients can reach BIG-IP virtual server IP

## Installation

### 1. Clone or Download Repository

```bash
cd /path/to/your/ansible/projects
# Copy the bigip-apm-ansible directory
```

### 2. Install Python Dependencies

```bash
pip3 install ansible requests urllib3
```

### 3. Configure Inventory

Edit `inventory.yml` with your BIG-IP details:

```yaml
all:
  children:
    bigip:
      hosts:
        bigip-01:
          ansible_host: 10.1.1.4
          bigip_user: admin
          bigip_pass: admin
```

**Security Best Practice:** Use Ansible Vault to encrypt credentials:

```bash
ansible-vault encrypt_string 'your_password' --name 'bigip_pass'
```

### 4. Customize Variables

Edit `vars/main.yml` to customize your deployment:

```yaml
# Solution Naming
vs1_name: "solution1"
dns1_name: "solution1.acme.com"
partition_name: "solution1"

# Active Directory
ad_server_ip: "10.1.20.7"
ad_domain: "f5lab.local"

# VPN Network Configuration
vpn_lease_pool_start: "10.1.2.1"
vpn_lease_pool_end: "10.1.2.254"
vpn_split_tunnel_networks:
  - "10.1.10.0/255.255.255.0"
  - "10.1.20.0/255.255.255.0"
```

See `vars/main.yml` for all available options.

## Usage

### Solution 1: VPN Deployment

Deploy the complete APM VPN solution with network access:

```bash
ansible-playbook deploy_apm_vpn.yml
```

**Deploys:**
- Active Directory authentication
- VPN tunnel with split tunneling
- Network access resource
- Webtop with network access section
- Access profile and policy

### Solution 2: Portal Access Deployment

Deploy the Portal Access solution with AD group-based resource assignment:

```bash
ansible-playbook deploy_apm_portal.yml
```

**Deploys:**
- Active Directory authentication with group query
- Portal access resources (4 web applications)
- AD group-based resource assignment
- Optional VPN access
- Webtop with group-specific resources
- Access profile and policy

### Solution 3: SAML Service Provider Deployment

Deploy the SAML authentication solution with Okta IDP:

```bash
ansible-playbook deploy_apm_saml.yml
```

**Deploys:**
- SAML IDP connector (Okta or other SAML 2.0 IDP)
- SAML Service Provider configuration
- IDP signing certificate installation
- SAML authentication access policy
- Access profile with SAML settings
- Optional AS3 virtual server deployment
- Optional GSLB/DNS configuration

**Configuration:**

Before deploying, customize `vars/solution3.yml`:

```yaml
# SAML Identity Provider (Okta)
saml_idp:
  entity_id: "http://www.okta.com/YOUR_APP_ID"
  sso_uri: "https://YOUR_TENANT.okta.com/app/.../sso/saml"
  certificate_content: |
    -----BEGIN CERTIFICATE-----
    YOUR_IDP_CERTIFICATE_HERE
    -----END CERTIFICATE-----

# SAML Service Provider
saml_sp:
  entity_id: "https://sp.acme.com"
  sp_host: "sp.acme.com"

# Virtual Server
as3_config:
  virtual_address: "10.1.10.130"
  pool_members:
    - "10.1.20.6:80"
```

### Deployment Options

**Target Specific Host**
```bash
ansible-playbook deploy_apm_portal.yml --limit bigip-01
```

**Use Custom Variables**
```bash
ansible-playbook deploy_apm_portal.yml -e "@vars/custom.yml"
```

**Use Different Inventory**
```bash
ansible-playbook -i custom_inventory.yml deploy_apm_vpn.yml
```

**Dry Run (Check Mode)**
```bash
ansible-playbook deploy_apm_vpn.yml --check
```

**Verbose Output**
```bash
ansible-playbook deploy_apm_portal.yml -v    # verbose
ansible-playbook deploy_apm_portal.yml -vv   # more verbose
ansible-playbook deploy_apm_portal.yml -vvv  # debug
```

**With Vault-Encrypted Credentials**
```bash
ansible-playbook deploy_apm_vpn.yml --ask-vault-pass
```

**Deploy Specific Components (Tags)**
```bash
# Solution 2: Deploy only portal resources
ansible-playbook deploy_apm_portal.yml --tags portal

# Solution 2: Deploy only AD and policy
ansible-playbook deploy_apm_portal.yml --tags ad,policy

# Solution 1: Deploy only VPN components
ansible-playbook deploy_apm_vpn.yml --tags vpn
```

## Cleanup / Deletion

### Remove Solution 1 (VPN)

To safely remove all deployed components:

```bash
ansible-playbook delete_apm_vpn.yml
```

**Interactive confirmation required** - you must type `DELETE` to proceed.

### Remove Solution 2 (Portal)

To remove Solution 2 deployment:

```bash
ansible-playbook delete_apm_portal.yml
```

**Interactive confirmation required** - you must type `DELETE` to proceed.

### Remove Solution 3 (SAML)

To remove Solution 3 deployment:

```bash
ansible-playbook delete_apm_saml.yml
```

**Interactive confirmation required** - you must type `DELETE` to proceed.

### Automated Cleanup (No Confirmation)

For CI/CD pipelines or automated teardown:

```bash
ansible-playbook cleanup_apm_vpn.yml      # Solution 1
ansible-playbook cleanup_apm_portal.yml   # Solution 2
ansible-playbook cleanup_apm_saml.yml     # Solution 3
```

**WARNING:** These skip safety prompts. Use only in automation.

### Skip Confirmation (CI/CD)

```bash
ansible-playbook delete_apm_vpn.yml -e "confirm_delete=true"
ansible-playbook delete_apm_vpn.yml -e "vs1_name=solution2" -e "confirm_delete=true"
```

**WARNING:** This skips safety prompts. Use only in automation.

### What Gets Deleted

**Solution 1 (VPN):**
- All access policy objects (policy, profile, items, agents)
- Connectivity profile and VPN tunnel
- Network access resource and IP lease pool
- Webtop and webtop sections
- AAA AD server and AD pool
- AS3 application partition (if deployed)

**Solution 2 (Portal):**
- All access policy objects (policy, profile, items, agents)
- Portal access resources (server1, server2, server3, server4)
- Portal customization groups
- Network access resource (if deployed)
- Webtop and webtop sections
- AAA AD server, pool, and node
- AS3 application partition (if deployed)
- GSLB configuration (if configured)

**Solution 3 (SAML):**
- All access policy objects (policy, profile, items, agents)
- SAML Service Provider configuration
- SAML IDP Connector
- IDP signing certificate
- All customization groups
- AS3 application partition (if deployed)
- GSLB configuration (if configured)

See [CLEANUP_GUIDE.md](docs/CLEANUP_GUIDE.md) for detailed cleanup documentation.

## Configuration

### Required Variables

These variables must be configured in `vars/main.yml`:

| Variable | Description | Example |
|----------|-------------|---------|
| `vs1_name` | Virtual server name | `solution1` |
| `dns1_name` | DNS name for VPN | `solution1.acme.com` |
| `ad_server_ip` | Active Directory server IP | `10.1.20.7` |
| `ad_domain` | AD domain name | `f5lab.local` |
| `vpn_lease_pool_start` | VPN IP pool start | `10.1.2.1` |
| `vpn_lease_pool_end` | VPN IP pool end | `10.1.2.254` |

### Optional Features

Enable/disable components via feature flags in `vars/main.yml`:

```yaml
# Feature Flags
create_connectivity_profile: true   # VPN tunnel
create_network_access: true          # Network access resource
create_webtop: true                  # Webtop
deploy_application_via_as3: true     # AS3 app deployment
configure_external_dns: false        # GSLB configuration
```

### Address Management API

If you have an address management service (like in the Postman collection):

```yaml
address_mgmt_enabled: true
address_mgmt_host: "10.1.20.6"
address_mgmt_port: 81
```

### GSLB Configuration

For multi-datacenter deployments:

```yaml
gslb_enabled: true
gslb_dns_server: "10.1.1.11"
gslb_dc1_name: "DC1"
gslb_dc2_enabled: true
gslb_dc2_name: "DC2"
```

## Deployment Workflow

The playbook executes tasks in this order:

1. **Verify Connectivity** - Check BIG-IP API accessibility
2. **AAA AD Servers** - Create AD node, pool, and AAA server
3. **Connectivity Profile** - Create VPN tunnel and connectivity profile
4. **Network Access** - Create IP lease pool and network access resource
5. **Webtop** - Create webtop section and full webtop
6. **Access Policy** - Create all policy items, policy, and profile (in transaction)
7. **AS3 Deployment** - Deploy application with virtual server
8. **GSLB** - Configure DNS with WideIP (optional)

## Verification

After deployment, verify the configuration:

### Via TMSH (on BIG-IP)

```bash
# Access policy
tmsh list apm policy access-policy solution1-psp

# Access profile
tmsh list apm profile access solution1-psp

# Network access resource
tmsh list apm resource network-access solution1-vpn

# Webtop
tmsh list apm resource webtop solution1-webtop

# Connectivity profile
tmsh list apm profile connectivity solution1-cp

# AD AAA server
tmsh list apm aaa active-directory solution1-ad-servers

# Virtual server (if AS3 deployed)
tmsh list ltm virtual /solution1/solution1/serviceMain
```

### Via GUI

1. Navigate to **Access > Profiles / Policies > Access Profiles (Per-Session Policies)**
2. Click **solution1-psp** to view policy
3. Verify policy flow: Start → Logon Page → AD Auth → Resource Assign → Allow
4. Check **Access > Webtops > Webtop Lists** for webtop
5. Verify **Access > Connectivity/VPN > Network Access (VPN)** for network access resource

### Test VPN Connection

1. **Access VPN URL:** `https://solution1.acme.com/`
2. **Login:** Use AD credentials (username@f5lab.local)
3. **Verify Resources:** Should see webtop with network access
4. **Launch VPN:** Click network access resource
5. **Verify Connectivity:** Test access to split tunnel networks

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to BIG-IP

**Solutions:**
- Verify network connectivity: `ping <bigip-ip>`
- Check HTTPS access: `curl -k https://<bigip-ip>`
- Verify credentials in inventory
- Check firewall rules

### Transaction Failures

**Problem:** Transaction commit fails during policy creation

**Solutions:**
- Check BIG-IP logs: `/var/log/ltm`
- Verify all required objects exist (AD server, webtop, network access)
- Ensure no naming conflicts with existing objects
- Check BIG-IP version compatibility

### Policy Compilation Errors

**Problem:** Policy fails to compile

**Solutions:**
- Verify AD server is reachable from BIG-IP
- Check network access resource configuration
- Ensure webtop section exists
- Review APM logs: `/var/log/apm`

### Authentication Failures

**Problem:** AD authentication not working

**Solutions:**
- Verify AD server IP and domain name
- Test AD connectivity from BIG-IP
- Check AD credentials (admin user/password)
- Review AAA server configuration
- Check APM session logs

### AS3 Deployment Issues

**Problem:** AS3 declaration fails

**Solutions:**
```bash
# Verify AS3 is installed
curl -k https://<bigip-ip>/mgmt/shared/appsvcs/info

# Check AS3 version (requires 3.0.0+)
# Review AS3 logs
tail -f /var/log/restjavad.0.log
```

## Conversion Notes

### Postman to Ansible Mapping

| Postman Component | Ansible Equivalent | Notes |
|-------------------|-------------------|-------|
| Collection Variables | `vars/main.yml` | Centralized configuration |
| Pre-request Scripts | Task variables | Set facts before tasks |
| POST requests | `uri` module | HTTP method: POST |
| Transaction | `X-F5-REST-Coordination-Id` header | Used for policy creation |
| Basic Auth | `user/password` in uri | Per-task authentication |
| Status code checks | `status_code` parameter | Accept 200, 201, 409 |

### Key Differences

1. **Idempotency:** Ansible version accepts 409 (conflict) status codes for existing objects
2. **Error Handling:** Better error messages and retry capability
3. **Modularity:** Organized into reusable task files
4. **Variables:** Externalized configuration for easy customization
5. **Documentation:** Inline task names describe each step
6. **Conditional Execution:** Feature flags to enable/disable components

### What Was Converted

- ✅ AAA Active Directory configuration (3 API calls)
- ✅ Connectivity Profile (3 API calls)
- ✅ Network Access Resource (3 API calls)
- ✅ Webtop Configuration (4 API calls)
- ✅ Access Policy Creation (21 API calls with transaction)
- ✅ AS3 Application Deployment (4 API calls)
- ✅ GSLB Configuration (16 API calls - optional)
- ✅ Total: 54 API calls automated

### Not Included (from original collection)

- Loop/monitoring endpoints (replaced with Ansible's built-in capabilities)
- Some Postman test scripts (validation handled by Ansible)

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

## References

- [F5 BIG-IP REST API Documentation](https://clouddocs.f5.com/api/icontrol-rest/)
- [F5 APM Configuration Guide](https://clouddocs.f5.com/apm/)
- [AS3 Documentation](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/)
- [Ansible URI Module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/uri_module.html)
- [Source Postman Collection](https://github.com/f5devcentral/access-solutions/blob/master/solution1/postman/solution1-create.postman_collection.json)

## Support

For issues or questions:
- Review F5 BIG-IP documentation
- Check BIG-IP system logs (`/var/log/ltm`, `/var/log/apm`)
- Review Ansible playbook output with `-vvv` flag
- Consult F5 DevCentral community

## License

This playbook is provided as-is for automation purposes. Test thoroughly before production use.

## Changelog

### Version 1.0.0
- Initial conversion from Postman collection to Ansible
- Complete APM VPN solution automation
- Modular task organization
- AS3 application deployment
- Optional GSLB configuration
- Comprehensive documentation

---

**Note:** Always test APM configurations in a lab environment before deploying to production. VPN solutions require careful planning of IP addressing, routing, and access control.
