# Configuration Guide

This document covers variable configuration and deployment workflow for APM solutions.

## Required Variables

These variables must be configured in `vars/main.yml`:

| Variable | Description | Example |
|----------|-------------|---------|
| `vs1_name` | Virtual server name | `solution1` |
| `dns1_name` | DNS name for VPN | `solution1.acme.com` |
| `ad_server_ip` | Active Directory server IP | `10.1.20.7` |
| `ad_domain` | AD domain name | `f5lab.local` |
| `vpn_lease_pool_start` | VPN IP pool start | `10.1.2.1` |
| `vpn_lease_pool_end` | VPN IP pool end | `10.1.2.254` |

## Optional Features

Enable/disable components via feature flags in `vars/main.yml`:

```yaml
# Feature Flags
create_connectivity_profile: true   # VPN tunnel
create_network_access: true          # Network access resource
create_webtop: true                  # Webtop
deploy_application_via_as3: true     # AS3 app deployment
configure_external_dns: false        # GSLB configuration
```

## Address Management API

If you have an address management service (like in the Postman collection):

```yaml
address_mgmt_enabled: true
address_mgmt_host: "10.1.20.6"
address_mgmt_port: 81
```

## GSLB Configuration

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

### Test VPN Connection (Solution 1)

1. **Access VPN URL:** `https://solution1.acme.com/`
2. **Login:** Use AD credentials (username@f5lab.local)
3. **Verify Resources:** Should see webtop with network access
4. **Launch VPN:** Click network access resource
5. **Verify Connectivity:** Test access to split tunnel networks

### Verify Solution 4 (SAML IDP)

#### Via TMSH (on BIG-IP)

```bash
# Access policy and profile
tmsh list apm policy access-policy idp-psp
tmsh list apm profile access idp-psp

# SAML IDP service
tmsh list apm aaa saml-idp-service /Common/idp.acme.com

# SAML SP connector
tmsh list apm aaa saml-sp-connector /Common/sp.acme.com

# Self-signed certificate
tmsh list sys file ssl-cert idp-saml.crt
tmsh list sys file ssl-key idp-saml.key

# AD AAA server
tmsh list apm aaa active-directory idp-ad-servers

# Virtual server (if AS3 deployed)
tmsh list ltm virtual /idp/idp/serviceMain
```

#### Via GUI

1. Navigate to **Access > Profiles / Policies > Access Profiles (Per-Session Policies)**
2. Click **idp-psp** to view policy
3. Verify policy flow: Start → Logon Page → AD Auth → Allow
4. Check **Access > Federation > SAML Identity Provider > Local IdP Services** for `idp.acme.com`
5. Check **Access > Federation > SAML Identity Provider > External SP Connectors** for `sp.acme.com`
6. Verify **System > Certificate Management > Traffic Certificate Management > SSL Certificate List** for `idp-saml`

#### Test SAML IDP Flow

1. **Access IDP URL:** `https://idp.acme.com/`
2. **Login:** Use AD credentials (username@f5lab.local)
3. **Verify SAML Assertion:** After authentication, assertion should be generated
4. **Check SP Redirect:** User should be redirected to configured SP with SAML assertion
5. **Verify Attributes:** SAML assertion should include `sAMAccountName` attribute

## Solution-Specific Variables

### Solution 3 (SAML SP with Okta)

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
```

### Solution 4 (SAML IDP)

```yaml
# BIG-IP Configuration
vs1_name: "idp"
dns1_name: "idp.acme.com"
dns2_name: "sp.acme.com"

# Active Directory
ad_aaa_server:
  admin_name: "admin"
  admin_password: "admin"
  domain: "f5lab.local"

# SAML IDP Service
saml_idp_service:
  entity_id: "https://idp.acme.com"
  assertion_validity: 600
```

### Solution 8 (OAuth AS)

```yaml
# OAuth Configuration
oauth_profile:
  issuer: "https://as.acme.com"
  jwt_access_token_lifetime: 120
  jwt_refresh_token_lifetime: 120

# JWK Configuration
jwk_config:
  alg_type: "HS256"
  key_id: "lab"
  shared_secret: "secret"
```

### Solution 14 (SAML SP with Azure AD)

```yaml
# Azure AD tenant ID
azure_tenant_id: "your-tenant-id-guid"

# IDP Connector
idp_connector_1:
  entity_id: "https://sts.windows.net/your-tenant-id/"
  sso_uri: "https://login.microsoftonline.com/your-tenant-id/saml2"

# Backend servers
sp1_backend:
  node_address: "10.1.20.6"
  pool_port: 443
```

## Environment Variables

You can also use environment variables for sensitive data:

```bash
export BIGIP_USER=admin
export BIGIP_PASS=admin
export AD_ADMIN_PASS=admin

ansible-playbook deploy_apm_vpn.yml \
  -e "bigip_user=$BIGIP_USER" \
  -e "bigip_pass=$BIGIP_PASS"
```

## Ansible Vault

For production, encrypt sensitive variables:

```bash
# Create encrypted file
ansible-vault create vars/secrets.yml

# Edit encrypted file
ansible-vault edit vars/secrets.yml

# Run with vault password
ansible-playbook deploy_apm_vpn.yml --ask-vault-pass

# Use password file
ansible-playbook deploy_apm_vpn.yml --vault-password-file ~/.vault_pass
```

## Related Documentation

- [INSTALLATION.md](INSTALLATION.md) - Installation requirements
- [USAGE.md](USAGE.md) - Deployment instructions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
