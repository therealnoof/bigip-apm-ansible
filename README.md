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

### Solution 4: SAML Identity Provider with AD Authentication
- **SAML Identity Provider** - BIG-IP acts as SAML IDP issuing assertions
- **Active Directory Backend** - AD authentication before SAML assertion
- **Self-Signed Certificate** - Automated certificate generation for SAML signing
- **SAML SP Connector** - Configuration for external Service Providers
- **Access Policy** - Per-session policy with Logon Page → AD Auth flow
- **Application Deployment** - AS3-based HTTPS virtual server with APM profile
- **GSLB** - Optional multi-datacenter DNS configuration

**Use Case:** Enterprise SSO hub where BIG-IP acts as the central identity provider, authenticating users via Active Directory and issuing SAML assertions to downstream service providers.

**Source:** [solution4-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution4/postman/solution4-create.postman_collection.json)

### Solution 5: SAML Service Provider with Internal BIG-IP IDP
- **SAML Authentication** - SAML 2.0 Service Provider configuration
- **Internal IDP Integration** - Connects to BIG-IP IDP (Solution 4) instead of external IDP
- **Federation Flow** - SP redirects to internal IDP for AD authentication
- **Access Policy** - Per-session policy with SAML authentication
- **Application Deployment** - AS3-based HTTPS virtual server with APM profile
- **GSLB** - Optional multi-datacenter DNS configuration

**Use Case:** Internal federation where multiple applications (Service Providers) authenticate through a centralized BIG-IP Identity Provider, creating a unified SSO experience with Active Directory as the authentication backend.

**Prerequisites:** Solution 4 (SAML IDP) must be deployed first.

**Source:** [solution5-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution5/postman/solution5-create.postman_collection.json)

### Solution 6: Certificate-based Authentication with Kerberos SSO
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

### Solution 7: SAML Authentication with Sideband Communication
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

### Solution 8: OAuth Authorization Server with AD Authentication
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

### Solution 9: OAuth Resource Server (Client)
- **OAuth 2.0 Resource Server** - BIG-IP APM validates OAuth tokens from an Authorization Server
- **OAuth Provider** - Connects to OAuth Authorization Server's OIDC discovery endpoint
- **JWK Configuration** - Pre-shared key matching the Authorization Server
- **JWT Configuration** - Manual JWT config for token validation
- **JWT Provider List** - Links provider with JWT config
- **OAuth Scope Agent** - Validates OAuth tokens in access policy
- **Access Policy** - Simple flow: Start → OAuth Scope → Allow/Deny
- **Application Deployment** - AS3-based HTTPS virtual server with backend pool

**Use Case:** Protected API or application that requires OAuth token validation. Works in conjunction with Solution 8 (OAuth Authorization Server) to create a complete OAuth 2.0 ecosystem.

**Prerequisites:** Solution 8 (OAuth Authorization Server) must be deployed and accessible at the configured OIDC discovery endpoint.

**Authentication Flow:**
1. Client presents OAuth access token
2. OAuth Scope agent validates token against Authorization Server
3. If valid, access granted to protected resource
4. If invalid, access denied

**Source:** [solution9-create Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution9/postman/solution9-create.postman_collection.json)

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

### Solution 4: SAML Identity Provider Flow

```
Start → Logon Page → AD Authentication → Allow
                            │              │
                            ▼ (Failed)     │
                          Deny             ▼
                                    Issue SAML Assertion
                                           │
                                           ▼
                                    Return to Service Provider
```

**Authentication Flow:** User accesses Service Provider → Redirected to BIG-IP IDP → AD authentication → SAML assertion generated → User returned to SP with assertion

**SAML Assertion:** BIG-IP IDP signs SAML assertion with self-signed certificate, includes AD attributes (sAMAccountName)

### Components Architecture (Solution 4)

```
┌─────────────────────────────────────────────────────────┐
│ Browser Client                                           │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTPS (443)
                    │ SAML Request from SP
                    ▼
┌─────────────────────────────────────────────────────────┐
│ F5 BIG-IP - APM SAML Identity Provider                 │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Virtual Server (HTTPS)                            │  │
│  │ - Client SSL Profile                             │  │
│  │ - Access Profile: idp-psp                        │  │
│  │ - SSO Name: /Common/idp.acme.com                │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                                │
│  ┌──────────────────────┼───────────────────────────┐  │
│  │ Per-Session Policy   ▼                            │  │
│  │                                                    │  │
│  │  1. Logon Page → 2. AD Auth → 3. Allow           │  │
│  │                      │              │             │  │
│  │                      │ Success      │             │  │
│  │                      ▼              ▼             │  │
│  │               Deny Ending    Issue SAML Assertion│  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ SAML IDP Configuration                            │  │
│  │ - IDP Service: idp.acme.com                      │  │
│  │ - Entity ID: https://idp.acme.com                │  │
│  │ - SP Connector: sp.acme.com                      │  │
│  │ - Certificate: idp-saml (self-signed)            │  │
│  │ - Signature Algorithm: RSA-SHA256                │  │
│  │ - Assertion Validity: 600s                       │  │
│  │ - Subject Type: email-address                    │  │
│  │ - Attributes: sAMAccountName                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Certificate Management (Automated)                │  │
│  │ - OpenSSL self-signed cert generation           │  │
│  │ - Private key upload and installation           │  │
│  │ - Certificate upload with commonName            │  │
│  │ - Key association for SAML signing              │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────┘
                    │ LDAP Authentication
                    ▼
┌─────────────────────────────────────────────────────────┐
│ Active Directory Server (10.1.20.7)                     │
│ - Domain: f5lab.local                                   │
│ - User Authentication                                    │
│ - Attribute Retrieval (sAMAccountName)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              SAML Assertion
              with AD Attributes
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Service Provider (sp.acme.com)                          │
│ - Receives SAML assertion from BIG-IP IDP              │
│ - Validates signature with IDP certificate             │
│ - Grants access based on assertion                     │
└─────────────────────────────────────────────────────────┘
```

### Solution 5: SAML SP with Internal IDP Flow

```
User → sp.acme.com (Solution 5 SP) → Redirect → idp.acme.com (Solution 4 IDP)
                                                        │
                                                        ▼
                                              Logon Page → AD Auth
                                                        │
                                                        ▼ (Success)
                                              SAML Assertion Generated
                                                        │
                                                        ▼
                                              Redirect back to SP
                                                        │
                                                        ▼
                                                      Allow
```

**Authentication Flow:**
1. User accesses `https://sp.acme.com` (Solution 5)
2. SP redirects to `https://idp.acme.com` (Solution 4 IDP)
3. User authenticates via AD at the IDP
4. IDP generates SAML assertion with AD attributes
5. User redirected back to SP with assertion
6. SP validates assertion and grants access

### Components Architecture (Solution 5)

```
┌─────────────────────────────────────────────────────────┐
│ Browser Client                                           │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTPS (443)
                    │ Initial Request
                    ▼
┌─────────────────────────────────────────────────────────┐
│ F5 BIG-IP - APM SAML Service Provider (Solution 5)     │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Virtual Server (HTTPS) - sp.acme.com             │  │
│  │ - Client SSL Profile                             │  │
│  │ - Access Profile: solution5-psp                  │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                                │
│  ┌──────────────────────┼───────────────────────────┐  │
│  │ Per-Session Policy   ▼                            │  │
│  │                                                    │  │
│  │  1. Start → 2. SAML Auth → 3. Allow/Deny         │  │
│  │                  │                                │  │
│  │                  │ Redirect to IDP               │  │
│  │                  ▼                                │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ SAML SP Configuration                             │  │
│  │ - SP Service: sp.acme.com-sp                     │  │
│  │ - Entity ID: https://sp.acme.com                 │  │
│  │ - IDP Connector: solution5-sso                   │  │
│  │ - Points to: https://idp.acme.com                │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────┘
                    │ SAML AuthnRequest
                    ▼
┌─────────────────────────────────────────────────────────┐
│ F5 BIG-IP - APM SAML Identity Provider (Solution 4)    │
│ - idp.acme.com                                          │
│ - AD Authentication                                      │
│ - Issues SAML Assertions                                │
└───────────────────┬─────────────────────────────────────┘
                    │ SAML Response
                    ▼
              Back to SP with
              SAML Assertion
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ Backend Application (IIS)                               │
│ - 10.1.20.6:80                                          │
│ - Accessed after successful SAML auth                   │
└─────────────────────────────────────────────────────────┘
```

### Solution 6: Certificate Authentication with Kerberos SSO Flow

```
User → https://solution6.acme.com (Client Cert Required)
   │
   ├─ 1. TLS Handshake: Client presents X.509 certificate
   ├─ 2. BIG-IP requests certificate (on-demand)
   ├─ 3. OCSP validation against dc1.f5lab.local
   ├─ 4. UPN extraction from certificate (using TCL)
   ├─ 5. LDAP query to get sAMAccountName
   ├─ 6. Set session variables (username, domain)
   │
   └─► 7. Kerberos SSO to backend → Backend IIS/App Server
```

### Solution 7: SAML with Sideband Communication Flow

```
User → https://sp.acme.com (VS1 - Send Sideband)
   │
   ├─ 1. SAML Auth: Redirect to Okta IDP
   ├─ 2. User authenticates at Okta
   ├─ 3. SAML assertion returned to VS1
   ├─ 4. AD Query: Retrieve sAMAccountName
   ├─ 5. Variable Assign: Set username
   ├─ 6. iRule Event: Send sideband to VS2
   │         │
   │         ▼ (TCP Sideband Connection)
   │   ┌─────────────────────────────────┐
   │   │ VS2 (Receive Sideband)          │
   │   │  - iRule parses username        │
   │   │  - Variable Assign: Set domain  │
   │   │  - Kerberos SSO applied         │
   │   └─────────────────────────────────┘
   │
   └─► Backend Application (with Kerberos ticket)
```

### Solution 8: OAuth Authorization Server Flow

```
User/Client → https://as.acme.com (OAuth Authorization Server)
   │
   ├─ 1. /f5-oauth2/v1/authorize
   │      ↓
   ├─ 2. Logon Page: Collect credentials
   │      ↓
   ├─ 3. AD Authentication: Validate credentials
   │      ↓
   ├─ 4. AD Query: Retrieve user attributes
   │      ↓
   ├─ 5. OAuth Authorization: Generate tokens
   │      ↓
   └─ 6. Return JWT access_token + refresh_token

Token Validation Flow:
Client → Resource Server → /f5-oauth2/v1/introspect → Valid/Invalid
```

**OAuth Grant Types Supported:**
- Authorization Code
- Client Credentials
- Resource Owner Password

**Authentication Flow:**
1. User accesses `https://solution6.acme.com`
2. BIG-IP requests client certificate (on-demand, not required at TLS layer)
3. On-Demand Client Cert Auth agent validates certificate basic properties
4. OCSP Auth agent validates certificate against revocation list
5. Variable Assign agent extracts UPN from X.509 extension (e.g., user1@f5lab.local)
6. LDAP Query agent searches AD for user by UPN, retrieves sAMAccountName
7. Variable Assign agent sets session.logon.last.username and .domain
8. Kerberos SSO profile requests ticket for backend SPN
9. Backend application receives Kerberos ticket (seamless SSO)

### Components Architecture (Solution 6)

```
┌─────────────────────────────────────────────────────────┐
│ User with X.509 Certificate (UPN: user1@f5lab.local)   │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTPS (443) + Client Certificate
                    ▼
┌─────────────────────────────────────────────────────────┐
│ F5 BIG-IP - APM Certificate Authentication + Kerb SSO  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Virtual Server (HTTPS)                            │  │
│  │ - Client SSL Profile (Request Client Cert)       │  │
│  │   * authenticationInviteCA: ca.f5lab.local       │  │
│  │   * authenticationTrustCA: ca.f5lab.local        │  │
│  │ - Access Profile: solution6-psp                  │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                                │
│  ┌──────────────────────┼───────────────────────────┐  │
│  │ Per-Session Policy   ▼                            │  │
│  │                                                    │  │
│  │  Start → On-Demand Cert → OCSP → UPN Extract →  │  │
│  │          │                  │       │             │  │
│  │          ▼ (Invalid)        ▼ (Bad) ▼             │  │
│  │        Deny              Deny   LDAP Query →     │  │
│  │                                  │                 │  │
│  │                                  ▼ (Pass)          │  │
│  │                          Set Variables → Allow    │  │
│  │                                  │                 │  │
│  │                                  ▼ (Fail)          │  │
│  │                                Deny                │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Kerberos SSO Profile: solution6-kerbsso          │  │
│  │ - Account: HOST/solution6.f5lab.local            │  │
│  │ - Realm: F5LAB.LOCAL                             │  │
│  │ - SPN Pattern: HTTP/solution6.acme.com           │  │
│  │ - Username Source: session.logon.last.username   │  │
│  │ - User Realm Source: session.logon.last.domain   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ OCSP Servers: solution6-ocsp-servers             │  │
│  │ - CA: /Common/ca.f5lab.local                     │  │
│  │ - URL: http://dc1.f5lab.local/ocsp               │  │
│  │ - Validation: Certificate + Signature + Chain    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ LDAP Query: solution6-ldap-servers               │  │
│  │ - Type: Query (not authentication)               │  │
│  │ - Filter: (userPrincipalName=user1@f5lab.local)  │  │
│  │ - Attributes: sAMAccountName                      │  │
│  │ - Search DN: dc=f5lab,dc=local                   │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────┬─────────────┬───────────────────────┘
                    │ LDAP (389)  │ HTTP (OCSP)
                    ▼             ▼
┌──────────────────────────────────────────────────────┐
│ Active Directory / PKI Infrastructure                │
│ - dc1.f5lab.local (10.1.20.7)                       │
│ - CA: ca.f5lab.local                                 │
│ - OCSP Responder                                     │
└──────────────────────────────────────────────────────┘
                    │
                    ▼ Kerberos Ticket Request
┌──────────────────────────────────────────────────────┐
│ Backend Application Server (IIS)                     │
│ - Receives Kerberos ticket                           │
│ - Seamless SSO (no additional auth prompt)          │
└──────────────────────────────────────────────────────┘
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
├── deploy_apm_saml.yml               # Solution 3: SAML SP deployment playbook
├── deploy_apm_saml_idp.yml           # Solution 4: SAML IDP deployment playbook
├── deploy_apm_saml_sp_internal.yml   # Solution 5: SAML SP with internal IDP
├── deploy_apm_cert_kerb.yml          # Solution 6: Certificate + Kerberos SSO
├── deploy_apm_sideband.yml           # Solution 7: SAML with Sideband Communication
├── deploy_apm_oauth_as.yml           # Solution 8: OAuth Authorization Server
├── deploy_apm_oauth_rs.yml           # Solution 9: OAuth Resource Server
├── delete_apm_vpn.yml                # Solution 1/2: Interactive deletion playbook
├── delete_apm_portal.yml             # Solution 2: Interactive deletion playbook
├── delete_apm_saml.yml               # Solution 3: Interactive deletion playbook
├── delete_apm_saml_idp.yml           # Solution 4: Interactive deletion playbook
├── delete_apm_saml_sp_internal.yml   # Solution 5: Interactive deletion playbook
├── delete_apm_cert_kerb.yml          # Solution 6: Interactive deletion playbook
├── delete_apm_sideband.yml           # Solution 7: Interactive deletion playbook
├── delete_apm_oauth_as.yml           # Solution 8: Interactive deletion playbook
├── delete_apm_oauth_rs.yml           # Solution 9: Interactive deletion playbook
├── cleanup_apm_vpn.yml               # Solution 1: Automated cleanup playbook
├── cleanup_apm_portal.yml            # Solution 2: Automated cleanup playbook
├── cleanup_apm_saml.yml              # Solution 3: Automated cleanup playbook
├── cleanup_apm_saml_idp.yml          # Solution 4: Automated cleanup playbook
├── cleanup_apm_saml_sp_internal.yml  # Solution 5: Automated cleanup playbook
├── vars/
│   ├── main.yml                      # Solution 1 variables
│   ├── solution2.yml                 # Solution 2 variables
│   ├── solution3.yml                 # Solution 3 variables (SAML SP)
│   ├── solution4.yml                 # Solution 4 variables (SAML IDP)
│   ├── solution5.yml                 # Solution 5 variables (SAML SP internal)
│   ├── solution6.yml                 # Solution 6 variables (Certificate + Kerberos)
│   ├── solution7.yml                 # Solution 7 variables (SAML + Sideband)
│   ├── solution8.yml                 # Solution 8 variables (OAuth Authorization Server)
│   └── solution9.yml                 # Solution 9 variables (OAuth Resource Server)
├── tasks/
│   ├── aaa_ad_servers.yml            # AD server configuration
│   ├── connectivity_profile.yml       # VPN tunnel and connectivity
│   ├── network_access.yml             # Network access resource
│   ├── portal_resources.yml           # Portal access resources (Solution 2)
│   ├── portal_resource_item.yml       # Single portal resource creation
│   ├── saml_idp_connector.yml        # SAML IDP connector (Solution 3)
│   ├── saml_sp.yml                   # SAML Service Provider (Solution 3)
│   ├── saml_sp_connector.yml         # SAML SP connector (Solution 4)
│   ├── saml_idp_service.yml          # SAML IDP service (Solution 4)
│   ├── create_self_signed_cert.yml   # Certificate generation (Solution 4)
│   ├── webtop.yml                    # Webtop configuration
│   ├── access_policy.yml             # Solution 1 per-session policy
│   ├── access_policy_solution2.yml    # Solution 2 policy with AD groups
│   ├── access_policy_solution3.yml    # Solution 3 policy with SAML auth
│   ├── access_policy_solution4.yml    # Solution 4 policy with AD + SAML IDP
│   ├── access_policy_solution5.yml    # Solution 5 policy with SAML auth
│   ├── access_policy_solution6.yml    # Solution 6 policy with cert auth
│   ├── access_policy_solution7_vs1.yml # Solution 7 VS1 policy (send sideband)
│   ├── access_policy_solution7_vs2.yml # Solution 7 VS2 policy (receive sideband)
│   ├── access_policy_solution8.yml    # Solution 8 policy with OAuth authorization
│   ├── access_policy_solution9.yml    # Solution 9 policy with OAuth scope validation
│   ├── saml_idp_connector_internal.yml # SAML IDP connector for internal IDP (Solution 5)
│   ├── import_ca_certificate.yml      # CA certificate import (Solution 6)
│   ├── kerberos_sso.yml               # Kerberos SSO profile (Solution 6)
│   ├── ocsp_servers.yml               # OCSP validation (Solution 6)
│   ├── ldap_aaa_server.yml            # LDAP AAA server for queries (Solution 6)
│   ├── as3_deployment.yml            # Application deployment
│   └── gslb_configuration.yml        # DNS/GSLB setup
├── templates/
│   └── as3_saml.json.j2              # AS3 SAML template (Solution 4)
└── docs/
    ├── API_MAPPING.md                # Postman to Ansible conversion details
    ├── API_ENDPOINTS.md              # F5 iControl REST API reference
    ├── CLEANUP_GUIDE.md              # Deletion and cleanup guide
    ├── solution1-create.postman_collection.json   # Solution 1 source
    ├── solution1-delete.postman_collection.json   # Solution 1 delete
    ├── solution2-create.postman_collection.json   # Solution 2 source
    ├── solution2-delete.postman_collection.json   # Solution 2 delete
    ├── solution3-create.postman_collection.json   # Solution 3 source
    ├── solution3-delete.postman_collection.json   # Solution 3 delete
    ├── solution4-create.postman_collection.json   # Solution 4 source
    ├── solution4-delete.postman_collection.json   # Solution 4 delete
    ├── solution5-create.postman_collection.json   # Solution 5 source
    └── solution5-delete.postman_collection.json   # Solution 5 delete

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

### Solution 4: SAML Identity Provider Deployment

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

### Solution 5: SAML SP with Internal IDP Deployment

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

### Solution 6: Certificate Authentication with Kerberos SSO Deployment

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

### Solution 7: SAML Authentication with Sideband Communication

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

### Solution 8: OAuth Authorization Server

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

### Solution 9: OAuth Resource Server

Deploy the OAuth Resource Server for protected applications that validate OAuth tokens:

```bash
ansible-playbook deploy_apm_oauth_rs.yml
```

**Prerequisites:**
- Solution 8 (OAuth Authorization Server) must be deployed and accessible
- The OAuth AS OIDC discovery endpoint must be reachable from BIG-IP

**What Gets Deployed:**
- **OAuth Provider:**
  - Connects to OAuth Authorization Server's OIDC endpoint
  - Discovers token validation endpoints

- **JWK Configuration:**
  - Pre-shared key matching the Authorization Server
  - HS256 signing algorithm

- **JWT Configuration:**
  - Manual JWT config with issuer and signing algorithms
  - Links to JWK for token validation

- **JWT Provider List:**
  - Associates OAuth provider with JWT config
  - Required for OAuth scope agent

- **OAuth Client Application:**
  - Client configuration for OAuth flow
  - Redirect URIs for callback handling

- **Access Policy:**
  - OAuth Scope agent for token validation
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

**Important Notes:**
- The JWT provider list requires the OAuth provider to have a manual JWT config attached
- When OIDC discovery fails (AS not reachable), the playbook creates a manual JWT config
- The shared secret must match the JWK configured on the Authorization Server

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

### Remove Solution 3 (SAML SP)

To remove Solution 3 deployment:

```bash
ansible-playbook delete_apm_saml.yml
```

**Interactive confirmation required** - you must type `DELETE` to proceed.

### Remove Solution 4 (SAML IDP)

To remove Solution 4 deployment:

```bash
ansible-playbook delete_apm_saml_idp.yml
```

**Interactive confirmation required** - you must type `DELETE` to proceed.

**Deletes:**
- Access profile and access policy
- All policy items and agents (logon page, AD auth, endings)
- All customization groups (including logon page group)
- SAML IDP service
- SAML SP connector
- AAA AD server, pool, and node
- Self-signed certificate and private key
- AS3 application partition (if deployed)
- GSLB configuration (if deployed)

### Remove Solution 5 (SAML SP Internal)

To remove Solution 5 deployment:

```bash
ansible-playbook delete_apm_saml_sp_internal.yml
```

**Interactive confirmation required** - you must type `DELETE` to proceed.

**Deletes:**
- Access profile and access policy
- All policy items and agents (SAML auth, endings)
- All customization groups
- SAML Service Provider configuration
- SAML IDP Connector (to internal IDP)
- AS3 application partition (if deployed)
- GSLB configuration (if deployed)

**Note:** This does NOT delete Solution 4 (IDP) - delete that separately if needed.

### Remove Solution 6 (Certificate + Kerberos SSO)

To remove Solution 6 deployment:

```bash
ansible-playbook delete_apm_cert_kerb.yml
```

**Deletes:**
- Access profile and access policy
- All policy items and agents (cert auth, OCSP, LDAP query, variable assign, endings)
- All customization groups
- Kerberos SSO profile
- OCSP servers configuration
- LDAP AAA server and pool
- LDAP node (if not used by other configurations)
- CA certificate (if not used by other configurations)
- AS3 application partition (if deployed)
- GSLB configuration (if deployed)

**Note:** CA certificate and LDAP node are only deleted if not in use by other configurations.

### Remove Solution 7 (SAML with Sideband)

To remove Solution 7 deployment:

```bash
ansible-playbook delete_apm_sideband.yml
```

**Deletes:**
- AS3 application tenant (solution7)
- VS1 Access profile and access policy
- VS2 Access profile and access policy
- All policy items and agents for both virtual servers
- All customization groups for both virtual servers
- Kerberos SSO profile
- SAML IDP Service
- SAML SP Connector
- SAML Service Provider
- SAML IDP Connector (Okta)
- IDP certificate (Okta signing cert)
- SAML signing certificate and private key
- AD AAA server, pool, and node

### Remove Solution 8 (OAuth Authorization Server)

To remove Solution 8 deployment:

```bash
ansible-playbook delete_apm_oauth_as.yml
```

**Deletes:**
- AS3 application tenant (solution8)
- Access profile with OAuth profile reference
- Access policy and all policy items
- Policy agents (logon page, AD auth, AD query, OAuth authz, endings)
- All customization groups
- OAuth profile
- JWK configuration
- AD AAA server, pool, and node
- GSLB configuration (if deployed)

### Remove Solution 9 (OAuth Resource Server)

To remove Solution 9 deployment:

```bash
ansible-playbook delete_apm_oauth_rs.yml
```

**Deletes:**
- AS3 application tenant (solution9)
- Access profile and access policy
- All policy items and agents (OAuth scope, endings)
- All customization groups
- OAuth client application
- JWT provider list
- Manual JWT configuration
- Auto JWT configuration (if created)
- JWK configuration
- OAuth provider
- CA certificate (if not used by other configurations)

**Note:** This does NOT delete Solution 8 (OAuth AS) - delete that separately if needed.

### Automated Cleanup (No Confirmation)

For CI/CD pipelines or automated teardown:

```bash
ansible-playbook cleanup_apm_vpn.yml              # Solution 1
ansible-playbook cleanup_apm_portal.yml           # Solution 2
ansible-playbook cleanup_apm_saml.yml             # Solution 3
ansible-playbook cleanup_apm_saml_idp.yml         # Solution 4
ansible-playbook cleanup_apm_saml_sp_internal.yml # Solution 5
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

**Solution 3 (SAML SP):**
- All access policy objects (policy, profile, items, agents)
- SAML Service Provider configuration
- SAML IDP Connector
- IDP signing certificate
- All customization groups
- AS3 application partition (if deployed)
- GSLB configuration (if configured)

**Solution 4 (SAML IDP):**
- All access policy objects (policy, profile, items, agents)
- All customization groups (7 total including logon page)
- SAML IDP Service
- SAML SP Connector
- Self-signed certificate and private key
- AAA AD server configuration
- AD server pool and node
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

### SAML IDP Issues (Solution 4)

**Problem:** Certificate upload fails

**Solutions:**
- Ensure certificate is in PEM format (base64 encoded)
- Verify `Content-Range` header is included: `Content-Range: 0-<size>/<size>`
- Check certificate includes `commonName` attribute in upload
- Verify private key matches certificate

**Problem:** SAML SP connector creation fails

**Solutions:**
- Ensure `assertionConsumerServiceUrl` is a valid HTTPS URL
- Verify `entityId` matches what the SP expects
- Check that referenced certificate exists

**Problem:** SAML assertion not generated

**Solutions:**
- Verify SAML IDP service references correct certificate (`assertionSubjectKeyRef`)
- Check `ssoUri` format: `https://idp.acme.com/saml/idp/sso`
- Ensure access profile has `ssoName` set to `/Common/<idp-host>`
- Review `/var/log/apm` for SAML-specific errors

**Problem:** AD authentication works but SAML assertion fails

**Solutions:**
- Verify AD auth agent `type` is set to `"auth"` (not `"aaa"`)
- Check SAML attribute mapping in IDP service configuration
- Ensure `assertionSubjectType` is set correctly (e.g., `"email-address"`)
- Verify `assertionValidity` is reasonable (e.g., 600 seconds)

**Problem:** Policy customization group errors

**Solutions:**
- Ensure Deny ending customization group is created **first** in the list
- Verify `customizationGroup` references match created groups exactly
- Check `customGroup` vs `customizationGroup` parameter naming (API version dependent)

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

#### Solution 1: VPN with Network Access
- ✅ AAA Active Directory configuration (3 API calls)
- ✅ Connectivity Profile (3 API calls)
- ✅ Network Access Resource (3 API calls)
- ✅ Webtop Configuration (4 API calls)
- ✅ Access Policy Creation (21 API calls with transaction)
- ✅ AS3 Application Deployment (4 API calls)
- ✅ GSLB Configuration (16 API calls - optional)
- **Subtotal: 54 API calls**

#### Solution 2: Portal Access with AD Groups
- ✅ All Solution 1 components (AAA, connectivity, network access)
- ✅ Portal Access Resources (4 apps × 2 API calls each = 8 API calls)
- ✅ AD Group Query and Mapping (2 API calls)
- ✅ Extended Access Policy with group-based assignment (25+ API calls)
- **Subtotal: 60+ API calls**

#### Solution 3: SAML Service Provider
- ✅ SAML IDP Connector (3 API calls)
- ✅ IDP Certificate Upload (2 API calls)
- ✅ SAML Service Provider Configuration (2 API calls)
- ✅ SAML Authentication Access Policy (25+ API calls)
- ✅ AS3 Application Deployment (4 API calls)
- ✅ GSLB Configuration (16 API calls - optional)
- **Subtotal: 52+ API calls**

#### Solution 4: SAML Identity Provider
- ✅ Self-Signed Certificate Generation (OpenSSL - 3 tasks)
- ✅ Certificate and Key Upload (4 API calls with Content-Range)
- ✅ SAML IDP Service Configuration (2 API calls)
- ✅ SAML SP Connector Configuration (2 API calls)
- ✅ AAA Active Directory Configuration (3 API calls)
- ✅ Access Policy with Logon + AD Auth (25+ API calls with transaction)
- ✅ AS3 Application Deployment (4 API calls)
- ✅ GSLB Configuration (16 API calls - optional)
- **Subtotal: 55+ API calls**

#### Solution 5: SAML SP with Internal IDP
- ✅ SAML IDP Connector (pointing to internal IDP - 1 API call)
- ✅ SAML Service Provider Configuration (1 API call)
- ✅ Access Policy with SAML Auth (20+ API calls with transaction)
- ✅ AS3 Application Deployment (4 API calls)
- ✅ GSLB Configuration (16 API calls - optional)
- **Subtotal: 42+ API calls**

#### Solution 7: SAML with Sideband Communication
- ✅ Active Directory configuration (3 API calls)
- ✅ SAML IDP Connector with Okta certificate (4 API calls)
- ✅ Self-signed certificate generation (4 tasks)
- ✅ SAML SP and IDP Service configuration (4 API calls)
- ✅ Kerberos SSO profile (1 API call)
- ✅ VS1 Access Policy with SAML/AD/iRule (25+ API calls with transaction)
- ✅ VS2 Access Policy with Variable Assign (15+ API calls with transaction)
- ✅ AS3 Application with 2 virtual servers and iRules (1 API call)
- **Subtotal: 55+ API calls**

#### Solution 8: OAuth Authorization Server
- ✅ Active Directory configuration (3 API calls)
- ✅ JWK Configuration (1 API call)
- ✅ OAuth Profile (1 API call)
- ✅ Access Policy with OAuth Authorization (25+ API calls with transaction)
- ✅ AS3 Application Deployment (1 API call)
- ✅ GSLB Configuration (optional, 6 API calls)
- **Subtotal: 35+ API calls**

#### Solution 9: OAuth Resource Server (Client)
- ✅ CA Certificate upload and installation (2 API calls)
- ✅ JWK Configuration (1 API call)
- ✅ JWT Configuration (1 API call)
- ✅ OAuth Provider (1 API call)
- ✅ JWT Provider List (1 API call)
- ✅ OAuth Client Application (2 API calls with customization)
- ✅ Access Policy with OAuth Scope (15+ API calls with transaction)
- ✅ AS3 Application Deployment (1 API call)
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

### Version 2.4.0
- **Solution 9: OAuth Resource Server (Client)**
  - BIG-IP APM as OAuth 2.0 Resource Server
  - OAuth Provider connecting to Authorization Server's OIDC endpoint
  - JWK Configuration with pre-shared key (HS256)
  - Manual JWT Configuration for token validation
  - JWT Provider List linking provider to JWT config
  - OAuth Client Application with redirect URIs
  - Access policy: Start → OAuth Scope → Allow/Deny
  - Full deployment and cleanup playbooks
- Prerequisites: Solution 8 (OAuth AS) must be deployed first
- Updated API call counts: 380+ API calls across all solutions

### Version 2.3.0
- **Solution 8: OAuth Authorization Server with AD Authentication**
  - BIG-IP APM as OAuth 2.0 Authorization Server
  - JWK (JSON Web Key) configuration for JWT token signing
  - OAuth Profile with complete token endpoints
  - Access policy: Logon Page → AD Auth → AD Query → OAuth Authorization
  - JWT access tokens and refresh tokens with configurable lifetimes
  - Full deployment and cleanup playbooks
- Updated API call counts: 350+ API calls across all solutions

### Version 2.2.0
- **Solution 7: SAML Authentication with Sideband Communication**
  - Two coordinated virtual servers (VS1 send-sideband, VS2 receive-sideband)
  - SAML SP with Okta IDP integration
  - AD Query to retrieve sAMAccountName after SAML authentication
  - iRule-based sideband communication between virtual servers
  - Kerberos SSO for backend application authentication
  - Separate access policies for each virtual server
  - AS3 deployment with two applications and iRules
  - Full deployment and cleanup playbooks
- Uses default BIG-IP certificate for SSL (default.crt/default.key)

### Version 2.1.0
- **Solution 5: SAML SP with Internal IDP** - SAML Service Provider using BIG-IP IDP
  - SAML IDP connector pointing to internal BIG-IP IDP (Solution 4)
  - SAML Service Provider configuration
  - SAML authentication access policy
  - Internal federation flow: SP → Internal IDP → AD → SAML Assertion
  - Full deployment, cleanup, and interactive delete playbooks
- Updated API call counts: 260+ API calls across all solutions
- Documentation updates with Solution 5 architecture diagrams

### Version 2.0.0
- **Solution 4: SAML Identity Provider** - BIG-IP as SAML IDP with AD backend
  - Automated self-signed certificate generation (OpenSSL)
  - Certificate upload with Content-Range header handling
  - SAML IDP service and SP connector configuration
  - Access policy with Logon Page → AD Auth flow
  - Full deployment and cleanup playbooks
- **Solution 3: SAML Service Provider** - SAML SP with external IDP (Okta)
  - SAML IDP connector for external identity providers
  - IDP certificate installation
  - SAML authentication access policy
- **Solution 2: Portal Access** - AD group-based resource assignment
  - Portal access resources (web application proxying)
  - AD group query and dynamic resource mapping
  - Extended access policy with group-based assignment
- Documentation updates for all solutions
- Interactive deletion playbooks with safety confirmations
- Automated cleanup playbooks for CI/CD pipelines

### Version 1.0.0
- Initial conversion from Postman collection to Ansible
- Complete APM VPN solution automation (Solution 1)
- Modular task organization
- AS3 application deployment
- Optional GSLB configuration
- Comprehensive documentation

---

**Note:** Always test APM configurations in a lab environment before deploying to production. VPN and SAML solutions require careful planning of IP addressing, routing, certificate management, and access control.
