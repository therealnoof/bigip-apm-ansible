# Usage Guide

This document provides deployment instructions for all APM solutions.

## Solution 1: VPN Deployment

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

## Solution 2: Portal Access Deployment

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

## Solution 3: SAML Service Provider Deployment

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

## Solution 4: SAML Identity Provider Deployment

Deploy the SAML IDP solution with AD authentication:

```bash
ansible-playbook deploy_apm_saml_idp.yml
```

**Deploys:**
- Self-signed certificate generation (OpenSSL)
- Private key and certificate upload/installation
- SAML IDP service configuration
- SAML SP connector (for downstream service providers)
- Active Directory AAA server
- AD authentication access policy
- Access profile with SAML IDP settings
- Optional AS3 virtual server deployment
- Optional GSLB/DNS configuration

**Configuration:**

Before deploying, customize `vars/solution4.yml`:

```yaml
# BIG-IP Configuration
vs1_name: "idp"
dns1_name: "idp.acme.com"          # SAML IDP hostname
dns2_name: "sp.acme.com"            # Service Provider hostname

# Active Directory Configuration
ad_pool:
  members:
    - address: "10.1.20.7"          # AD server IP
      name: "10.1.20.7:0"

ad_aaa_server:
  admin_name: "admin"
  admin_password: "admin"
  domain: "f5lab.local"

# SAML IDP Service
saml_idp_service:
  entity_id: "https://idp.acme.com"
  idp_host: "idp.acme.com"
  assertion_validity: 600            # seconds

# SAML SP Connector (downstream service providers)
saml_sp_connector:
  entity_id: "https://sp.acme.com"
  acs_url: "https://sp.acme.com/saml/acs"

# Virtual Server
as3_config:
  virtual_address: "10.1.10.140"
```

**Critical Notes:**
- Certificate is auto-generated (self-signed) - replace with CA-signed cert in production
- `custom_type` set to "standard" for compatibility (not "modern")
- Deny ending customization group must be first in the list
- AD agent requires `type: "auth"` for profile compatibility
- See `docs/API_MAPPING.md` for detailed implementation requirements

## Solution 5: SAML SP with Internal IDP Deployment

Deploy the SAML SP solution that uses an internal BIG-IP IDP (Solution 4):

```bash
ansible-playbook deploy_apm_saml_sp_internal.yml
```

**Prerequisites:**
- Solution 4 (SAML IDP) must be deployed first at `idp.acme.com`
- Wildcard certificate (`acme.com-wildcard`) or configure your own certs

**Deploys:**
- SAML IDP Connector pointing to internal IDP
- SAML Service Provider configuration
- SAML authentication access policy
- Access profile with SAML settings
- Optional AS3 virtual server deployment
- Optional GSLB/DNS configuration

**Configuration:**

Before deploying, customize `vars/solution5.yml`:

```yaml
# Solution naming
vs1_name: "solution5"
dns1_name: "sp.acme.com"          # SAML SP hostname
dns2_name: "idp.acme.com"         # Internal IDP hostname (Solution 4)

# SAML IDP Connector (internal IDP)
saml_idp_connector:
  entity_id: "https://idp.acme.com"
  sso_uri: "https://idp.acme.com/saml/idp/profile/redirectorpost/sso"
  idp_certificate: "/Common/acme.com-wildcard"

# SAML Service Provider
saml_sp:
  entity_id: "https://sp.acme.com"
  sp_host: "sp.acme.com"
  sp_certificate: "/Common/acme.com-wildcard"

# Virtual Server
as3_config:
  virtual_address: "10.1.10.150"
  pool_members:
    - "10.1.20.6:80"
```

**Authentication Flow:**
1. User accesses `https://sp.acme.com`
2. Redirected to `https://idp.acme.com` (Solution 4 IDP)
3. User authenticates via AD at IDP
4. SAML assertion returned to SP
5. Access granted to backend application

## Solution 6: Certificate Authentication with Kerberos SSO Deployment

**Deploy Certificate + Kerberos SSO Solution:**
```bash
ansible-playbook deploy_apm_cert_kerb.yml
```

**Prerequisites:**
- PKI infrastructure with CA certificate
- OCSP responder accessible from BIG-IP
- User certificates with UPN (User Principal Name) in X.509 extensions
- Active Directory with LDAP enabled
- Kerberos realm configured
- Service Principal Name (SPN) registered for delegation account

**What Gets Deployed:**
- CA certificate for client cert validation
- Kerberos SSO profile for backend authentication
- OCSP servers configuration for revocation checking
- LDAP pool and AAA server for user queries
- Access policy with certificate authentication flow:
  - On-demand client cert authentication
  - OCSP validation
  - UPN extraction from certificate
  - LDAP query for user attributes
  - Variable assignment for Kerberos SSO
- AS3 application with client SSL profile
- Optional GSLB configuration

**Configuration Variables** (vars/solution6.yml):
- `vs1_name`: "solution6"
- `dns1_name`: "solution6.acme.com"
- `partition_name`: "solution6"
- `ca_certificate`: CA cert content
- `kerberos_sso`: Kerberos SSO settings
- `ocsp_servers`: OCSP responder configuration
- `ldap_server_ip`: "10.1.20.7"
- `as3_config`: Application deployment settings

**Deploy Specific Components (Tags):**
```bash
# Deploy only certificates and OCSP
ansible-playbook deploy_apm_cert_kerb.yml --tags certificates,ocsp

# Deploy only Kerberos SSO
ansible-playbook deploy_apm_cert_kerb.yml --tags kerberos,sso

# Deploy only access policy
ansible-playbook deploy_apm_cert_kerb.yml --tags policy

# Deploy only application (AS3)
ansible-playbook deploy_apm_cert_kerb.yml --tags application
```

**Authentication Flow:**
1. User accesses `https://solution6.acme.com`
2. BIG-IP requests client certificate (on-demand)
3. Certificate validated against OCSP responder
4. UPN extracted from certificate (e.g., user1@f5lab.local)
5. LDAP query to retrieve sAMAccountName
6. Session variables set for Kerberos SSO
7. Kerberos ticket requested for backend SPN
8. Access granted with seamless SSO to backend

## Solution 7: SAML Authentication with Sideband Communication

Deploy the SAML with Sideband solution for SAML-to-Kerberos authentication translation:

```bash
ansible-playbook deploy_apm_sideband.yml
```

**What Gets Deployed:**
- **VS1 (Send Sideband):**
  - SAML Service Provider with Okta IDP
  - Active Directory AAA server and pool
  - SAML IDP connector (Okta certificate)
  - Self-signed certificate for SAML signing
  - SAML SP connector and IDP service
  - Access policy: SAML Auth → AD Query → Variable Assign → iRule Event → Allow
  - iRule for sending sideband TCP connection to VS2

- **VS2 (Receive Sideband):**
  - Kerberos SSO profile
  - Access policy: Start → Variable Assign (set domain) → Allow
  - iRule for receiving sideband and parsing username
  - HTTP virtual server (internal only)

- **AS3 Application:**
  - Two applications in one tenant
  - HTTPS virtual server for VS1
  - HTTP virtual server for VS2
  - Pool configurations for backend servers

**Configuration Variables** (vars/solution7.yml):
```yaml
# Virtual Server Names
vs1_name: "send-sideband"
vs2_name: "receive-sideband"
dns1_name: "sp.acme.com"

# Partition
partition_name: "solution7"

# Active Directory
ad_server_ip: "10.1.20.7"
ad_domain: "f5lab.local"

# Kerberos SSO
kerberos_sso:
  realm: "F5LAB.LOCAL"
  account_name: "HOST/receive-sideband.f5lab.local"

# AS3 Virtual Addresses
as3_config:
  vs1_virtual_address: "10.1.10.170"
  vs2_virtual_address: "192.168.0.1"
```

**Deploy Specific Components (Tags):**
```bash
# Deploy only AAA/AD configuration
ansible-playbook deploy_apm_sideband.yml --tags aaa,ad

# Deploy only SAML configuration
ansible-playbook deploy_apm_sideband.yml --tags saml

# Deploy only Kerberos SSO
ansible-playbook deploy_apm_sideband.yml --tags kerberos,sso

# Deploy only access policies
ansible-playbook deploy_apm_sideband.yml --tags policy

# Deploy only AS3 application
ansible-playbook deploy_apm_sideband.yml --tags application,as3
```

## Solution 8: OAuth Authorization Server

Deploy the OAuth Authorization Server for API security and token-based authentication:

```bash
ansible-playbook deploy_apm_oauth_as.yml
```

**What Gets Deployed:**
- **JWK Configuration:**
  - JSON Web Key for JWT token signing (HS256 algorithm)
  - Key ID and shared secret for token verification

- **OAuth Profile:**
  - Complete OAuth profile with all token endpoints
  - JWT access tokens and refresh tokens
  - Configurable token lifetimes

- **Access Policy:**
  - Logon Page for credential collection
  - AD Authentication for user validation
  - AD Query for retrieving user attributes
  - OAuth Authorization for token generation
  - Flow: Start → Logon Page → AD Auth → AD Query → OAuth Authz → Allow

- **AS3 Application:**
  - HTTPS virtual server with OAuth endpoints
  - TLS server profile with default certificate

**Configuration Variables** (vars/solution8.yml):
```yaml
# Virtual Server Names
vs1_name: "as"
dns1_name: "as.acme.com"

# Partition
partition_name: "solution8"

# OAuth Configuration
oauth_profile:
  issuer: "https://as.acme.com"
  jwt_access_token_lifetime: 120    # 2 minutes
  jwt_refresh_token_lifetime: 120   # 2 minutes

# JWK Configuration
jwk_config:
  alg_type: "HS256"
  key_id: "lab"
  shared_secret: "secret"

# AS3 Virtual Address
as3_config:
  virtual_address: "10.1.10.108"
```

**OAuth Endpoints (after deployment):**
```
Authorization:    https://as.acme.com/f5-oauth2/v1/authorize
Token:            https://as.acme.com/f5-oauth2/v1/token
Introspection:    https://as.acme.com/f5-oauth2/v1/introspect
Revocation:       https://as.acme.com/f5-oauth2/v1/revoke
JWKS:             https://as.acme.com/f5-oauth2/v1/jwks
OpenID Config:    https://as.acme.com/f5-oauth2/v1/.well-known/openid-configuration
```

**Deploy Specific Components (Tags):**
```bash
# Deploy only AAA/AD configuration
ansible-playbook deploy_apm_oauth_as.yml --tags aaa,ad

# Deploy only OAuth/JWK configuration
ansible-playbook deploy_apm_oauth_as.yml --tags oauth,jwk

# Deploy only access policy
ansible-playbook deploy_apm_oauth_as.yml --tags policy

# Deploy only AS3 application
ansible-playbook deploy_apm_oauth_as.yml --tags application,as3
```

## Solution 9: OAuth Resource Server

Deploy the OAuth Resource Server for protected applications that validate OAuth tokens:

```bash
# Default: External/Introspection mode (recommended)
ansible-playbook deploy_apm_oauth_rs.yml

# Internal/JWT mode (requires OIDC discovery to succeed)
ansible-playbook deploy_apm_oauth_rs.yml -e token_validation_mode=internal
```

**Prerequisites:**
- Solution 8 (OAuth Authorization Server) should be deployed
- For **external mode** (default): OAuth AS must be reachable at runtime for introspection
- For **internal mode**: OAuth AS must be reachable during deployment for OIDC discovery

**What Gets Deployed:**
- **OAuth Provider:**
  - Connects to OAuth Authorization Server's OIDC endpoint
  - Uses `trustedCaBundle: /Common/ca-bundle.crt` for OIDC discovery
  - `useAutoJwtConfig: true` enabled

- **JWK Configuration:**
  - Pre-shared key matching the Authorization Server
  - HS256 signing algorithm

- **JWT Provider List (Internal Mode Only):**
  - Associates OAuth provider with JWT config
  - Only created when `token_validation_mode=internal`
  - Requires OIDC discovery to establish internal linkage

- **OAuth Client Application:**
  - Client configuration for OAuth flow
  - Redirect URIs for callback handling

- **Access Policy:**
  - OAuth Scope agent for token validation
  - External mode: uses `oauthProvider` reference
  - Internal mode: uses `jwtProviderList` reference
  - Simple flow: Start → OAuth Scope → Allow/Deny

- **AS3 Application:**
  - HTTPS virtual server with OAuth protection
  - Backend pool for protected application

**Configuration Variables** (vars/solution9.yml):
```yaml
# Virtual Server Names
vs1_name: "solution9"
dns1_name: "solution9.acme.com"

# Partition
partition_name: "solution9"

# OAuth Authorization Server Reference
oauth_as_dns: "as.acme.com"

# Token validation mode: "external" (introspection) or "internal" (JWT)
token_validation_mode: "external"

# JWK Configuration (must match AS)
jwk_config:
  alg_type: "HS256"
  key_id: "lab"
  shared_secret: "secret"

# AS3 Virtual Address
as3_config:
  virtual_address: "10.1.10.109"
  pool_members:
    - address: "10.1.20.6"
      port: 80
```

**Deploy Specific Components (Tags):**
```bash
# Deploy only OAuth configuration
ansible-playbook deploy_apm_oauth_rs.yml --tags oauth,jwt

# Deploy only access policy
ansible-playbook deploy_apm_oauth_rs.yml --tags policy

# Deploy only AS3 application
ansible-playbook deploy_apm_oauth_rs.yml --tags application,as3
```

**Token Validation Mode Comparison:**

| Feature | External (default) | Internal |
|---------|-------------------|----------|
| OIDC Discovery Required | No (at deployment) | Yes |
| JWT Provider List | Not created | Required |
| Token Validation | Introspection at runtime | JWT validation locally |
| OAuth AS Availability | Required at runtime | Required at deployment |
| Use Case | Standard deployments | Air-gapped/offline validation |

**Important Notes:**
- **External mode is recommended** for most deployments as it doesn't require OIDC discovery
- The shared secret must match the JWK configured on the Authorization Server
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for API limitations and workarounds

## Solution 10: OAuth Authorization Server with RS256

Deploy the OAuth Authorization Server using RSA asymmetric keys for JWT signing:

```bash
# Default: Self-signed certificate (DEMO/LAB only)
ansible-playbook deploy_apm_oauth_as_rsa.yml

# Production: Pre-imported certificate
# First, import your certificate to BIG-IP, then:
ansible-playbook deploy_apm_oauth_as_rsa.yml -e use_self_signed_cert=false
```

**Certificate Options:**

| Mode | Command | Use Case |
|------|---------|----------|
| Self-Signed (Default) | `ansible-playbook deploy_apm_oauth_as_rsa.yml` | DEMO/LAB environments |
| Pre-Imported | `ansible-playbook deploy_apm_oauth_as_rsa.yml -e use_self_signed_cert=false` | Production |

> **WARNING:** Self-signed certificates should NOT be used in production. For production:
> 1. Import your organization's certificate via BIG-IP GUI or API
> 2. Update `wildcard_cert.name` in `vars/solution10.yml` to match your cert name
> 3. Set `use_self_signed_cert: false`

**Prerequisites:**
- Active Directory server accessible from BIG-IP
- For production: Wildcard or domain certificate imported to BIG-IP

**What Gets Deployed:**
- **Self-Signed Certificate (if enabled):** Auto-generated RSA 2048-bit certificate
- **JWK Configuration:** RS256 algorithm with certificate references
- **OAuth Profile:** JWT tokens signed with RSA private key
- **Access Policy:** Logon Page → AD Auth → AD Query → OAuth Authorization
- **AS3 Application:** HTTPS virtual server with OAuth endpoints

**Comparison with Solution 8 (HS256):**

| Feature | Solution 8 | Solution 10 |
|---------|------------|-------------|
| Algorithm | HS256 (symmetric) | RS256 (asymmetric) |
| Token Verification | Shared secret required | Public key from JWKS |
| Certificate | Not required | Required |
| Best For | Internal APIs | Public APIs, distributed systems |

**Tag-Based Partial Deployment:**
```bash
# Deploy only AD infrastructure
ansible-playbook deploy_apm_oauth_as_rsa.yml --tags aaa,ad

# Deploy only certificate and JWK
ansible-playbook deploy_apm_oauth_as_rsa.yml --tags certificate,jwk

# Deploy only OAuth configuration
ansible-playbook deploy_apm_oauth_as_rsa.yml --tags oauth

# Deploy only access policy
ansible-playbook deploy_apm_oauth_as_rsa.yml --tags policy

# Deploy only AS3 application
ansible-playbook deploy_apm_oauth_as_rsa.yml --tags application,as3
```

## Solution 11: OAuth Client with OIDC Integration

Deploy the OAuth Client solution for OIDC authentication:

```bash
ansible-playbook deploy_apm_oauth_client.yml
```

**Prerequisites:**
- Solution 8 (OAuth AS with HS256) or Solution 10 (OAuth AS with RS256) must be deployed first
- This client will be automatically registered on the Authorization Server's OAuth profile

See [SOLUTIONS.md](SOLUTIONS.md) for detailed feature description.

## Solution 12: Remote Desktop Gateway (RDG) with AD Authentication

Deploy the Remote Desktop Gateway solution:

```bash
ansible-playbook deploy_apm_rdg.yml
```

See [SOLUTIONS.md](SOLUTIONS.md) for detailed feature description.

## Solution 14: SAML Service Provider with Azure AD

Deploy the SAML SP solution with Azure AD as the Identity Provider:

```bash
# Default: Self-signed certificate (DEMO/LAB only)
ansible-playbook deploy_apm_saml_sp_azure.yml

# Production: Pre-imported certificate
ansible-playbook deploy_apm_saml_sp_azure.yml -e use_self_signed_cert=false
```

**Prerequisites:**
- Azure AD tenant with admin access
- Enterprise Application configured in Azure AD for each SP
- Azure AD SAML metadata (Entity ID, SSO URL, Certificate)
- DNS entries for all SP hostnames pointing to BIG-IP VIP

**What Gets Deployed:**
- **Azure AD IDP Connectors:** Two connectors (one per SP application)
- **SAML SP Services:** Two SP services (sp.acme.com, sp1.acme.com)
- **Per-Session Policy (PSP):** Simple allow policy for session initialization
- **Per-Request Policy (PRP):** URL branching with SAML subroutines
- **Backend Pools:** Two pools (one per SP application)
- **Self-Signed Certificate (if enabled):** Auto-generated wildcard certificate
- **AS3 Application:** HTTPS virtual server with dual policy profiles

**Azure AD Enterprise Application Setup:**

For each SP application (sp.acme.com, sp1.acme.com), configure in Azure AD:

| Setting | Value |
|---------|-------|
| Entity ID (Identifier) | `https://sp.acme.com` or `https://sp1.acme.com` |
| Reply URL (ACS) | `https://sp.acme.com/saml/sp/profile/post/acs` |
| Sign-on URL | `https://sp.acme.com` or `https://sp1.acme.com` |

**Configuration:**

Before deploying, customize `vars/solution14.yml`:

```yaml
# Azure AD tenant ID
azure_tenant_id: "your-tenant-id-guid"

# IDP Connector 1 (for sp.acme.com)
idp_connector_1:
  entity_id: "https://sts.windows.net/your-tenant-id/"
  sso_uri: "https://login.microsoftonline.com/your-tenant-id/saml2"

# Backend servers
sp1_backend:
  node_address: "10.1.20.6"  # Your first SP backend server
  pool_port: 443

sp2_backend:
  node_address: "10.1.20.7"  # Your second SP backend server
  pool_port: 443

# Virtual server
as3_config:
  virtual_address: "10.1.10.114"  # Your VIP
```

**Tag-Based Partial Deployment:**
```bash
# Deploy only certificates
ansible-playbook deploy_apm_saml_sp_azure.yml --tags certificate

# Deploy only SAML configuration
ansible-playbook deploy_apm_saml_sp_azure.yml --tags saml

# Deploy only access policies
ansible-playbook deploy_apm_saml_sp_azure.yml --tags policy

# Deploy only AS3 application
ansible-playbook deploy_apm_saml_sp_azure.yml --tags application,as3
```

## Deployment Options

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
