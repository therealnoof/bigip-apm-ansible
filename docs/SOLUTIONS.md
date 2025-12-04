# APM Solutions Overview

This document describes all available F5 BIG-IP APM solutions that can be deployed using this Ansible automation.

## Solution 1: VPN with Network Access
- **Active Directory Authentication** - AAA server configuration
- **VPN Connectivity** - PPP tunnel with compression
- **Network Access** - IP lease pool with split tunneling
- **Webtop** - Full webtop with network access resources
- **Access Policy** - Per-session policy with logon page and AD auth
- **Application Deployment** - AS3-based HTTPS virtual server
- **GSLB** - Optional multi-datacenter DNS configuration

**Source:** [solution1-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution1/postman/solution1-create.postman_collection.json)

## Solution 2: Portal Access with AD Group Mapping
- **Active Directory Authentication** - AAA server with group query
- **Portal Access Resources** - Web application proxying (4 backend apps)
- **AD Group-Based Assignment** - Dynamic resource assignment based on AD group membership
- **Optional VPN Access** - Network access for specific groups
- **Webtop** - User portal showing group-specific resources
- **Access Policy** - Per-session policy with AD group mapping
- **Application Deployment** - AS3-based HTTPS virtual server
- **GSLB** - Optional multi-datacenter DNS configuration

**Source:** [solution2-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution2/postman/solution2-create.postman_collection.json)

## Solution 3: SAML Service Provider with Okta IDP
- **SAML Authentication** - SAML 2.0 Service Provider configuration
- **Identity Provider Integration** - Okta (or other SAML 2.0 IDP) connector
- **Certificate Management** - IDP signing certificate installation
- **Access Policy** - Per-session policy with SAML authentication
- **Application Deployment** - AS3-based HTTPS virtual server with APM profile
- **GSLB** - Optional multi-datacenter DNS configuration

**Source:** [solution3-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution3/postman/solution3-create.postman_collection.json)

## Solution 4: SAML Identity Provider with AD Authentication
- **SAML Identity Provider** - BIG-IP acts as SAML IDP issuing assertions
- **Active Directory Backend** - AD authentication before SAML assertion
- **Self-Signed Certificate** - Automated certificate generation for SAML signing
- **SAML SP Connector** - Configuration for external Service Providers
- **Access Policy** - Per-session policy with Logon Page → AD Auth flow
- **Application Deployment** - AS3-based HTTPS virtual server with APM profile
- **GSLB** - Optional multi-datacenter DNS configuration

**Use Case:** Enterprise SSO hub where BIG-IP acts as the central identity provider, authenticating users via Active Directory and issuing SAML assertions to downstream service providers.

**Source:** [solution4-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution4/postman/solution4-create.postman_collection.json)

## Solution 5: SAML Service Provider with Internal BIG-IP IDP
- **SAML Authentication** - SAML 2.0 Service Provider configuration
- **Internal IDP Integration** - Connects to BIG-IP IDP (Solution 4) instead of external IDP
- **Federation Flow** - SP redirects to internal IDP for AD authentication
- **Access Policy** - Per-session policy with SAML authentication
- **Application Deployment** - AS3-based HTTPS virtual server with APM profile
- **GSLB** - Optional multi-datacenter DNS configuration

**Use Case:** Internal federation where multiple applications (Service Providers) authenticate through a centralized BIG-IP Identity Provider, creating a unified SSO experience with Active Directory as the authentication backend.

**Prerequisites:** Solution 4 (SAML IDP) must be deployed first.

**Source:** [solution5-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution5/postman/solution5-create.postman_collection.json)

## Solution 6: Certificate-based Authentication with Kerberos SSO
- **Client Certificate Authentication** - On-demand X.509 certificate authentication
- **OCSP Validation** - Real-time certificate revocation checking
- **UPN Extraction** - Extract User Principal Name from certificate X.509 extensions
- **LDAP Query** - Query Active Directory for user attributes using UPN
- **Kerberos SSO** - Backend single sign-on to Windows Integrated Auth applications
- **Access Policy** - Per-session policy with certificate validation flow
- **Application Deployment** - AS3-based HTTPS virtual server with client SSL authentication
- **GSLB** - Optional multi-datacenter DNS configuration

**Use Case:** High-security environments requiring strong authentication (certificate + LDAP validation) with seamless SSO to backend applications. Ideal for government, financial services, or enterprises with PKI infrastructure where users have X.509 certificates with UPN extensions.

**Source:** [solution6-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution6/postman/solution6-create.postman_collection.json)

## Solution 7: SAML Authentication with Sideband Communication
- **Two Virtual Servers** - Coordinated VS1 (send-sideband) and VS2 (receive-sideband)
- **SAML Authentication** - VS1 acts as SAML SP with Okta IDP integration
- **Active Directory Query** - Retrieve user attributes (sAMAccountName) after SAML auth
- **Sideband Communication** - iRule-based session data transfer between virtual servers
- **Kerberos SSO** - VS2 provides Kerberos SSO to backend applications
- **Access Policies** - Separate policies for each virtual server with coordinated flow
- **Application Deployment** - AS3-based deployment with two applications and iRules

**Use Case:** Scenarios requiring SAML authentication at the front-end with Kerberos SSO to legacy backend applications. The sideband mechanism allows session data (username) to be securely passed between virtual servers, enabling seamless authentication translation from SAML to Kerberos.

**Authentication Flow:**
1. User accesses VS1 (SAML SP) → Redirected to Okta for authentication
2. After SAML auth, AD Query retrieves sAMAccountName
3. iRule Event sends username via sideband TCP connection to VS2
4. VS2 receives username, sets session variables, applies Kerberos SSO
5. Backend application receives Kerberos ticket (seamless SSO)

## Solution 8: OAuth Authorization Server with AD Authentication
- **OAuth 2.0 Authorization Server** - BIG-IP APM acts as OAuth AS issuing JWT tokens
- **JWK Configuration** - JSON Web Key for JWT token signing (HS256)
- **OAuth Profile** - Complete OAuth profile with token endpoints
- **Active Directory Authentication** - User authentication via AD before token issuance
- **AD Query** - Retrieve user attributes for token claims
- **JWT Tokens** - Access tokens and refresh tokens with configurable lifetimes
- **Access Policy** - Logon Page → AD Auth → AD Query → OAuth Authorization
- **Application Deployment** - AS3-based HTTPS virtual server with OAuth endpoints

**Use Case:** API security and OAuth 2.0 authorization flows. BIG-IP acts as the OAuth Authorization Server, authenticating users via Active Directory and issuing JWT tokens that can be validated by resource servers.

**OAuth Endpoints:**
- Authorization: `/f5-oauth2/v1/authorize`
- Token: `/f5-oauth2/v1/token`
- Token Introspection: `/f5-oauth2/v1/introspect`
- Token Revocation: `/f5-oauth2/v1/revoke`
- JWKS: `/f5-oauth2/v1/jwks`
- OpenID Configuration: `/f5-oauth2/v1/.well-known/openid-configuration`

**Source:** [solution8-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution8/postman/solution8-create.postman_collection.json)

## Solution 9: OAuth Resource Server (Client)
- **OAuth 2.0 Resource Server** - BIG-IP APM validates OAuth tokens from an Authorization Server
- **OAuth Provider** - Connects to OAuth Authorization Server's OIDC discovery endpoint
- **JWK Configuration** - Pre-shared key matching the Authorization Server
- **Token Validation Modes** - External (introspection) or Internal (JWT) validation
- **OAuth Scope Agent** - Validates OAuth tokens in access policy
- **Access Policy** - Simple flow: Start → OAuth Scope → Allow/Deny
- **Application Deployment** - AS3-based HTTPS virtual server with backend pool

**Use Case:** Protected API or application that requires OAuth token validation. Works in conjunction with Solution 8 (OAuth Authorization Server) to create a complete OAuth 2.0 ecosystem.

**Prerequisites:** Solution 8 (OAuth Authorization Server) should be deployed. External mode works even if OAuth AS is not reachable during deployment.

**Token Validation Modes:**
- **External (default):** Uses token introspection against OAuth AS at runtime. Works even if OIDC discovery fails during deployment.
- **Internal:** Uses JWT validation with pre-shared key. Requires OIDC discovery to succeed (OAuth AS must be reachable).

**Authentication Flow:**
1. Client presents OAuth access token
2. OAuth Scope agent validates token (via introspection or JWT validation)
3. If valid, access granted to protected resource
4. If invalid, access denied

**API Limitations & Workarounds:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for critical details about JWT provider list requirements.

**Source:** [solution9-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution9/postman/solution9-create.postman_collection.json)

## Solution 10: OAuth Authorization Server with RSA Signing (RS256)
- **OAuth 2.0 Authorization Server** - BIG-IP APM acts as OAuth AS issuing JWT tokens
- **RS256 Signing** - Asymmetric RSA keys for JWT signing (vs HS256 symmetric in Solution 8)
- **JWK Configuration** - JSON Web Key with RSA certificate and private key
- **JWKS Endpoint** - Public key available for token verification without shared secrets
- **Self-Signed Certificate Option** - Automatic certificate generation for DEMO/LAB environments
- **Active Directory Authentication** - User authentication via AD before token issuance
- **AD Query** - Retrieve user attributes for token claims
- **JWT Tokens** - Access tokens and refresh tokens signed with RSA private key
- **Access Policy** - Logon Page → AD Auth → AD Query → OAuth Authorization
- **Application Deployment** - AS3-based HTTPS virtual server with OAuth endpoints

**Use Case:** API security requiring asymmetric key signing. Unlike Solution 8 (HS256), RS256 allows OAuth clients to verify tokens using the public key from the JWKS endpoint without needing a shared secret. Ideal for public APIs, microservices, and scenarios where token verification must be distributed.

**Key Difference from Solution 8:**
| Feature | Solution 8 (HS256) | Solution 10 (RS256) |
|---------|-------------------|---------------------|
| Algorithm | Symmetric (shared secret) | Asymmetric (public/private key) |
| Token Verification | Requires shared secret | Uses public key from JWKS |
| Certificate Required | No | Yes (wildcard or self-signed) |
| Use Case | Internal APIs | Public APIs, distributed systems |

**OAuth Endpoints:**
- Authorization: `/f5-oauth2/v1/authorize`
- Token: `/f5-oauth2/v1/token`
- Token Introspection: `/f5-oauth2/v1/introspect`
- Token Revocation: `/f5-oauth2/v1/revoke`
- JWKS: `/f5-oauth2/v1/jwks` (returns RSA public key)
- OpenID Configuration: `/f5-oauth2/v1/.well-known/openid-configuration`

**Certificate Options:**

| Mode | Configuration | Use Case |
|------|---------------|----------|
| Self-Signed (Default) | `use_self_signed_cert: true` | DEMO/LAB environments |
| Pre-Imported | `use_self_signed_cert: false` | Production environments |

> **WARNING:** Self-signed certificates should NOT be used in production. For production deployments, import a proper certificate from your organization's CA before running the playbook and set `use_self_signed_cert: false`.

**Prerequisites:**
- For production: Import wildcard certificate via BIG-IP GUI or API before deployment
- Active Directory server accessible from BIG-IP

**Source:** [solution10-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution10/postman/solution10-create.postman_collection.json)

## Solution 11: OAuth Client with OIDC Integration
- **OAuth 2.0 Client** - BIG-IP APM acts as OAuth Client (RP) for OIDC authentication
- **OIDC Provider Integration** - Connects to OAuth Authorization Server's OIDC discovery endpoint
- **Manual Endpoint Configuration** - Supports manual endpoint configuration when OIDC discovery fails
- **OAuth Client App** - Client registration with auto-generated client ID and secret
- **OAuth Provider (AAA)** - Configures connection to Authorization Server
- **OAuth Server (Client Mode)** - AAA server in client mode for token handling
- **Self-Signed Certificate Option** - Automatic certificate generation for DEMO/LAB environments
- **Access Policy** - Simple flow: Start → OAuth Client → Allow/Deny
- **Application Deployment** - AS3-based HTTPS virtual server with backend pool

**Use Case:** Web application that delegates authentication to an OAuth Authorization Server using OIDC. Users accessing the application are redirected to the Authorization Server for login, then returned with tokens after successful authentication. Ideal for SSO integration with OAuth/OIDC providers.

**Prerequisites:**
- Solution 8 (OAuth AS with HS256) or Solution 10 (OAuth AS with RS256) must be deployed first
- This client will be automatically registered on the Authorization Server's OAuth profile

**Authentication Flow:**
1. User accesses OAuth Client application
2. Redirected to OAuth Authorization Server for login
3. User authenticates (AD credentials via Solution 8/10)
4. Authorization Server issues authorization code
5. OAuth Client exchanges code for tokens
6. User granted access to protected application

**OIDC Discovery Options:**

| Mode | Configuration | Use Case |
|------|---------------|----------|
| Auto Discovery (default off) | `skip_discovery: false` | Production environments where BIG-IP can reach AS |
| Manual Endpoints (default) | `skip_discovery: true` | LAB environments with network isolation |

> **LAB NOTE:** In many lab environments, the BIG-IP control plane cannot reach virtual server IPs due to network isolation. Set `skip_discovery: true` (default) and configure endpoints manually. The playbook uses the AS virtual server IP address for all endpoints.

**Certificate Options:**

| Mode | Configuration | Use Case |
|------|---------------|----------|
| Self-Signed (Default) | `use_self_signed: true` | DEMO/LAB environments |
| Pre-Imported | `use_self_signed: false` | Production environments |

**Source:** [solution11-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution11/postman/solution11-create.postman_collection.json)

## Solution 12: Remote Desktop Gateway (RDG) with AD Authentication
- **Remote Desktop Gateway** - HTML5-based RDP access through BIG-IP APM
- **Active Directory Authentication** - AD authentication with SSO to RDP servers
- **RDP Resource** - Remote Desktop resource with auto-logon capability
- **VDI Profile** - Virtual Desktop Infrastructure profile for RDP handling
- **Connectivity Profile** - PPP tunnel for VDI connections
- **RDG Access Profile** - Specialized rdg-rap type profile for RD Gateway
- **Webtop** - Full webtop for presenting RDP resources
- **Variable Assignment** - Domain SSO via session variable injection
- **Access Policy** - Two-policy architecture (RDG + PSP)
- **Application Deployment** - AS3-based HTTPS virtual server with APM profiles

**Use Case:** Enterprise remote desktop access where users authenticate via Active Directory and receive HTML5-based RDP access to backend servers. Enables secure browser-based remote desktop without requiring an RDP client.

**Authentication Flow:**
1. User accesses RDG virtual server
2. User enters AD credentials on logon page
3. APM authenticates against Active Directory
4. RDG policy is assigned for RD Gateway handling
5. Domain variable is set for SSO
6. RDP resource and webtop are assigned
7. User clicks RDP resource in webtop
8. HTML5 RDP connection established with SSO

**Policy Flow:**
```
PSP Policy:
Start → Logon Page → AD Auth → RDG Policy Assign → Variable Assign
                                                  → Resource Assign → Allow

RDG Policy:
Start → Allow (simple allow for RD Gateway traffic)
```

**Required Profiles:**
| Profile Type | Name | Purpose |
|--------------|------|---------|
| Access (PSP) | solution12-psp | Main authentication policy |
| Access (RDG) | solution12-rdg | RD Gateway traffic handling |
| VDI | solution12-vdi | Virtual Desktop Infrastructure |
| Connectivity | solution12-cp | PPP tunnel for VDI |

**Source:** [solution12-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution12/postman/solution12-create.postman_collection.json)

## Solution 14: SAML Service Provider with Azure AD Identity Provider
- **SAML Service Provider** - BIG-IP APM acts as SAML SP with Azure AD integration
- **Multi-Application Support** - Two separate SP applications (sp.acme.com, sp1.acme.com)
- **Azure AD Federation** - Full SAML 2.0 federation with Microsoft Azure Active Directory
- **Per-Request Policy (PRP)** - URL branching with SAML subroutines for each application
- **Per-Session Policy (PSP)** - Simple allow pass-through for session initialization
- **URL-Based Routing** - Category lookup agent routes requests to appropriate SP
- **Subroutines/Macros** - Modular SAML authentication per SP application
- **Backend Pool Assignment** - Dynamic pool assignment after SAML authentication
- **Application Deployment** - AS3-based HTTPS virtual server with dual policy profiles

**Use Case:** Enterprise scenarios requiring SAML SP integration with Azure AD for multiple web applications. Each application has its own Azure AD Enterprise Application configuration, enabling independent access control while sharing a single BIG-IP virtual server. Ideal for organizations using Microsoft 365 and Azure AD as their identity provider.

**Prerequisites:**
- Azure AD tenant with admin access
- Enterprise Application created in Azure AD for each SP
- Azure AD SAML metadata (Entity ID, SSO URL, Certificate)
- DNS entries for all SP hostnames pointing to BIG-IP VIP

**Authentication Flow:**
1. User accesses SP application (sp.acme.com or sp1.acme.com)
2. PRP URL branching identifies target application
3. Appropriate SAML subroutine is invoked
4. User redirected to Azure AD for authentication
5. Azure AD authenticates user (MFA, Conditional Access, etc.)
6. SAML assertion returned to BIG-IP SP
7. Pool assignment routes to correct backend server
8. User granted access to application

**Policy Flow:**
```
PSP Policy:
Start → Allow (pass-through for PRP to handle authentication)

PRP Policy:
Start → URL Branch → sp.acme.com  → SP Subroutine → SAML Auth → Pool Assign → Allow
                  → sp1.acme.com → SP1 Subroutine → SAML Auth → Pool Assign → Allow
                  → (fallback)   → Reject
```

**Key Components:**
| Component | Name | Purpose |
|-----------|------|---------|
| PSP Profile | solution14-psp | Session initialization (simple allow) |
| PRP Policy | solution14-prp | URL-based SAML authentication |
| IDP Connector 1 | solution14-1-idp-conn | Azure AD connection for sp.acme.com |
| IDP Connector 2 | solution14-2-idp-conn | Azure AD connection for sp1.acme.com |
| SP Service 1 | sp.acme.com-sp-serv | SAML SP for first application |
| SP Service 2 | sp1.acme.com-sp-serv | SAML SP for second application |

**Azure AD Configuration Required:**

| Setting | sp.acme.com | sp1.acme.com |
|---------|-------------|--------------|
| Entity ID | https://sp.acme.com | https://sp1.acme.com |
| Reply URL | https://sp.acme.com/saml/sp/profile/post/acs | https://sp1.acme.com/saml/sp/profile/post/acs |
| Sign-on URL | https://sp.acme.com | https://sp1.acme.com |

**Source:** [solution14-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution14/postman/solution14-create.postman_collection.json)
