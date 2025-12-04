# APM Solutions Architecture

This document contains architecture diagrams and flow charts for all APM solutions.

## Solution 1: VPN Access Flow

```
Start → Logon Page → AD Authentication → Resource Assign → Allow
                            │                    │
                            ▼ (Failed)           │
                          Deny                   ▼
                                        VPN + Webtop Resources
```

**Resources Assigned:** All authenticated users receive VPN and webtop access

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

## Solution 2: Portal Access with AD Group Mapping Flow

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

## Solution 3: SAML Authentication Flow

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

## Solution 4: SAML Identity Provider Flow

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

## Solution 5: SAML SP with Internal IDP Flow

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

## Solution 6: Certificate Authentication with Kerberos SSO Flow

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
└───────────────────┬─────────────────┬───────────────────┘
                    │ LDAP (389)      │ HTTP (OCSP)
                    ▼                 ▼
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

## Solution 7: SAML with Sideband Communication Flow

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

## Solution 8: OAuth Authorization Server Flow

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

## Solution 14: SAML SP with Azure AD - Multi-Application Architecture

```
                                   ┌─────────────────────────────┐
                                   │ Microsoft Azure AD          │
                                   │                             │
                                   │ Enterprise Applications:    │
                                   │ - sp.acme.com              │
                                   │ - sp1.acme.com             │
                                   │                             │
                                   │ Entity ID:                  │
                                   │ https://sts.windows.net/    │
                                   │         <tenant-id>/        │
                                   └──────────────┬──────────────┘
                                                  │ SAML 2.0
                                                  │ (Redirect/POST)
┌─────────────────────────────────────────────────┴───────────────────────────┐
│ F5 BIG-IP - APM SAML Service Provider                                       │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Virtual Server (HTTPS:443) - Single VIP for all SP applications       │ │
│  │ - Client SSL Profile                                                   │ │
│  │ - PSP Profile: solution14-psp (session initialization)               │ │
│  │ - PRP Policy: solution14-prp (per-request authentication)            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                         │                                                    │
│  ┌──────────────────────┼───────────────────────────────────────────────┐   │
│  │ Per-Session Policy (PSP)                                              │   │
│  │                      ▼                                                │   │
│  │    Start ────────► Allow (pass-through to PRP)                       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                         │                                                    │
│  ┌──────────────────────┼───────────────────────────────────────────────┐   │
│  │ Per-Request Policy (PRP)                                              │   │
│  │                      ▼                                                │   │
│  │    Start ────► URL Branching (Host Header)                           │   │
│  │                      │                                                │   │
│  │           ┌──────────┼──────────┬───────────────┐                    │   │
│  │           ▼          ▼          ▼               ▼                    │   │
│  │     sp.acme.com  sp1.acme.com  Other       (fallback)               │   │
│  │           │          │          │               │                    │   │
│  │           ▼          ▼          ▼               ▼                    │   │
│  │   ┌───────────┐ ┌────────────┐  │           Reject                   │   │
│  │   │SP Macro   │ │SP1 Macro   │  │                                    │   │
│  │   │(Subroutine)│ │(Subroutine)│  │                                    │   │
│  │   └─────┬─────┘ └─────┬──────┘  │                                    │   │
│  │         │             │          │                                    │   │
│  │         ▼             ▼          │                                    │   │
│  │   SAML Auth     SAML Auth        │                                    │   │
│  │   (Azure AD)    (Azure AD)       │                                    │   │
│  │         │             │          │                                    │   │
│  │         ▼             ▼          │                                    │   │
│  │   Pool Assign   Pool Assign      │                                    │   │
│  │   (sp-pool)     (sp1-pool)       │                                    │   │
│  │         │             │          │                                    │   │
│  │         ▼             ▼          │                                    │   │
│  │       Allow         Allow        │                                    │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │ IDP Connector 1                  │  │ IDP Connector 2                  │  │
│  │ - solution14-1-idp-conn         │  │ - solution14-2-idp-conn         │  │
│  │ - Entity: Azure AD tenant       │  │ - Entity: Azure AD tenant       │  │
│  │ - SSO: login.microsoftonline    │  │ - SSO: login.microsoftonline    │  │
│  │ - For: sp.acme.com              │  │ - For: sp1.acme.com             │  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │ SP Service 1                     │  │ SP Service 2                     │  │
│  │ - sp.acme.com-sp-serv           │  │ - sp1.acme.com-sp-serv          │  │
│  │ - Entity ID: https://sp.acme.com│  │ - Entity ID: https://sp1.acme   │  │
│  │ - ACS: /saml/sp/profile/post/acs│  │ - ACS: /saml/sp/profile/post/acs│  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
                    │                              │
                    ▼                              ▼
         ┌──────────────────┐          ┌──────────────────┐
         │ Backend Server 1 │          │ Backend Server 2 │
         │ 10.1.20.6:443   │          │ 10.1.20.7:443   │
         │ (sp.acme.com)   │          │ (sp1.acme.com)  │
         └──────────────────┘          └──────────────────┘
```
