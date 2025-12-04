## Postman to Ansible API Mapping

Detailed mapping of Postman REST API calls to Ansible tasks.

## Overview

| Metric | Count |
|--------|-------|
| Total Postman Requests | 120+ |
| Converted to Ansible | 110+ |
| Initialization/Check Requests | 6 |
| AAA AD Configuration | 3 |
| SAML Configuration (Solutions 3 & 4) | 8 |
| Connectivity Profile | 3 |
| Network Access | 3 |
| Webtop | 4 |
| Portal Resources (Solution 2) | 5 |
| Access Policy (with transaction) | 25+ |
| Sideband iRules (Solution 7) | 2 |
| OAuth/JWK Configuration (Solution 8) | 2 |
| AS3 Deployment | 6 |
| GSLB Configuration | 16 |

## Conversion Methodology

### Authentication
**Postman:**
```json
"auth": {
  "type": "basic",
  "basic": [
    {"key": "username", "value": "{{username}}"},
    {"key": "password", "value": "{{password}}"}
  ]
}
```

**Ansible:**
```yaml
uri:
  user: "{{ bigip_username }}"
  password: "{{ bigip_password }}"
```

### Variables
**Postman:**
```javascript
pm.collectionVariables.set("VS1_NAME", "solution1");
pm.collectionVariables.set("DNS1_NAME", "solution1.acme.com");
```

**Ansible:**
```yaml
# vars/main.yml
vs1_name: "solution1"
dns1_name: "solution1.acme.com"
```

### Error Handling
**Postman:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
```

**Ansible:**
```yaml
uri:
  status_code: [200, 201, 409]  # Accept success and "already exists"
register: result
```

## Detailed API Mappings

### 1. AAA Active Directory Servers

#### 1.1 Create AD Server Node

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/ltm/node
Content-Type: application/json

{
  "name": "10.1.20.7",
  "address": "10.1.20.7"
}
```

**Ansible:**
```yaml
# tasks/aaa_ad_servers.yml
- name: Create AD server node
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/ltm/node"
    method: POST
    body_format: json
    body:
      name: "{{ ad_server_ip }}"
      address: "{{ ad_server_ip }}"
    status_code: [200, 201, 409]
```

**File:** `tasks/aaa_ad_servers.yml` (lines 7-20)

#### 1.2 Create AD Server Pool

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/ltm/pool/

{
  "name":"{{VS1_NAME}}-ad-pool",
  "members":[
    {
      "name":"10.1.20.7:0",
      "address":"10.1.20.7"
    }
  ]
}
```

**Ansible:**
```yaml
- name: Create AD server pool
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/ltm/pool/"
    method: POST
    body_format: json
    body:
      name: "{{ vs1_name }}-ad-pool"
      members:
        - name: "{{ ad_server_ip }}:0"
          address: "{{ ad_server_ip }}"
```

**File:** `tasks/aaa_ad_servers.yml` (lines 26-40)

#### 1.3 Create APM AAA AD Server

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/aaa/active-directory

{
  "name": "{{VS1_NAME}}-ad-servers",
  "adminEncryptedPassword": "admin",
  "adminName": "admin",
  "domain": "f5lab.local",
  "domainController": "10.1.20.7",
  "usernameSource": "session.logon.last.username",
  "passwordSource": "session.logon.last.password"
}
```

**Ansible:**
```yaml
- name: Create APM AAA Active Directory server
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/aaa/active-directory"
    body:
      name: "{{ vs1_name }}-ad-servers"
      adminEncryptedPassword: "{{ ad_admin_password }}"
      adminName: "{{ ad_admin_user }}"
      domain: "{{ ad_domain }}"
      domainController: "{{ ad_server_ip }}"
      usernameSource: "session.logon.last.username"
      passwordSource: "session.logon.last.password"
```

**File:** `tasks/aaa_ad_servers.yml` (lines 46-63)

---

### 2. SAML SSO Configuration

#### 2.1 Upload IDP Certificate (Solution 3)

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/shared/file-transfer/uploads/{{CERT_NAME}}.crt
Content-Type: application/octet-stream
Content-Range: 0-{size-1}/{size}

{certificate_content}
```

**Ansible:**
```yaml
# tasks/saml_idp_connector.yml
- name: Upload IDP Certificate File
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/shared/file-transfer/uploads/{{ saml_idp.certificate_name }}.crt"
    method: POST
    body: "{{ cert_content_prepared }}"
    headers:
      Content-Type: "application/octet-stream"
      Content-Range: "0-{{ cert_length - 1 }}/{{ cert_length }}"
    status_code: [200, 201]
```

**File:** `tasks/saml_idp_connector.yml` (lines 29-42)

#### 2.2 Create SAML IDP Connector (Solution 3)

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/sso/saml-idp-connector

{
  "name": "{{VS1_NAME}}-sso",
  "entityId": "http://www.okta.com/exkafm6qvkEv6UK0d4x6",
  "ssoUri": "https://dev-818899.okta.com/.../sso/saml",
  "ssoBinding": "http-post",
  "signatureType": "rsa-sha256",
  "idpCertificate": "/Common/{{CERT_NAME}}"
}
```

**Ansible:**
```yaml
- name: Create SAML IDP Connector
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/sso/saml-idp-connector"
    method: POST
    body:
      name: "{{ saml_idp.name }}"
      entityId: "{{ saml_idp.entity_id }}"
      ssoUri: "{{ saml_idp.sso_uri }}"
      ssoBinding: "{{ saml_idp.sso_binding }}"
      signatureType: "{{ saml_idp.signature_type }}"
      idpCertificate: "/Common/{{ saml_idp.certificate_name }}"
    status_code: [200, 201, 409]
```

**File:** `tasks/saml_idp_connector.yml` (lines 86-104)

#### 2.3 Create SAML Service Provider (Solution 3)

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/sso/saml

{
  "name": "{{DNS1_NAME}}-sp",
  "entityId": "https://{{DNS1_NAME}}",
  "spHost": "{{DNS1_NAME}}",
  "idpConnectors": ["/Common/{{VS1_NAME}}-sso"]
}
```

**Ansible:**
```yaml
- name: Create SAML Service Provider
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/sso/saml"
    method: POST
    body:
      name: "{{ saml_sp.name }}"
      entityId: "{{ saml_sp.entity_id }}"
      spHost: "{{ saml_sp.sp_host }}"
      idpConnectors: ["/Common/{{ saml_idp.name }}"]
    status_code: [200, 201, 409]
```

**File:** `tasks/saml_sp.yml` (lines 7-32)

#### 2.4 Create SAML SP Connector (Solution 4)

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/sso/saml-sp-connector

{
  "name": "{{DNS2_NAME}}",
  "entityId": "https://{{DNS2_NAME}}",
  "encryptionType": "aes128",
  "signatureAlgorithm": "rsa-sha256",
  "assertionConsumerServices": [
    {
      "binding": "http-post",
      "uri": "https://{{DNS2_NAME}}/saml/sp/profile/post/acs"
    }
  ]
}
```

**Ansible:**
```yaml
- name: Create SAML SP Connector
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/sso/saml-sp-connector/"
    method: POST
    body:
      name: "{{ saml_sp_connector.name }}"
      entityId: "{{ saml_sp_connector.entity_id }}"
      encryptionType: "{{ saml_sp_connector.encryption_type }}"
      signatureAlgorithm: "{{ saml_sp_connector.signature_algorithm }}"
      assertionConsumerServices:
        - binding: "{{ saml_sp_connector.acs_binding }}"
          uri: "{{ saml_sp_connector.acs_url }}"
    status_code: [200, 201, 409]
```

**File:** `tasks/saml_sp_connector.yml` (lines 7-35)

#### 2.5 Create SAML IDP Service (Solution 4)

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/sso/saml

{
  "name": "{{DNS1_NAME}}",
  "entityId": "https://{{DNS1_NAME}}",
  "idpHost": "{{DNS1_NAME}}",
  "idpSignKey": "/Common/default",
  "assertionValidity": 600,
  "spConnectors": ["/Common/{{DNS2_NAME}}"],
  "samlAttributes": [
    {
      "name": "name",
      "type": "username",
      "value": "sAMAccountName"
    }
  ]
}
```

**Ansible:**
```yaml
- name: Create SAML IDP Service
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/sso/saml/"
    method: POST
    body:
      name: "{{ saml_idp_service.name }}"
      entityId: "{{ saml_idp_service.entity_id }}"
      idpHost: "{{ saml_idp_service.idp_host }}"
      idpSignKey: "{{ saml_idp_service.signature_key }}"
      assertionValidity: "{{ saml_idp_service.assertion_validity }}"
      spConnectors:
        - "{{ saml_idp_service.sp_connector }}"
      samlAttributes: "{{ saml_idp_service.attributes }}"
    status_code: [200, 201, 409]
```

**File:** `tasks/saml_idp_service.yml` (lines 7-39)

---

### 3. Connectivity Profile

#### 3.1 Create PPP Tunnel

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/net/tunnels/tunnel

{
  "name": "{{VS1_NAME}}-tunnel",
  "partition": "Common",
  "autoLasthop": "default",
  "mode": "bidirectional",
  "profile": "/Common/ppp"
}
```

**Ansible:**
```yaml
- name: Create PPP tunnel
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/net/tunnels/tunnel"
    body:
      name: "{{ vs1_name }}-tunnel"
      partition: "Common"
      autoLasthop: "default"
      mode: "bidirectional"
      profile: "/Common/ppp"
      usePmtu: "enabled"
```

**File:** `tasks/connectivity_profile.yml` (lines 7-24)

#### 3.2 Create Customization Group

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/customization-group/

{
  "name": "{{VS1_NAME}}-cp_secure_access_client_customization",
  "partition": "Common",
  "type": "connectivity-profile",
  "source": "/Common/connectivity-profile_modern"
}
```

**Ansible:**
```yaml
- name: Create connectivity profile customization group
  uri:
    body:
      name: "{{ vs1_name }}-cp_secure_access_client_customization"
      partition: "Common"
      type: "connectivity-profile"
      source: "/Common/connectivity-profile_{{ custom_type }}"
```

**File:** `tasks/connectivity_profile.yml` (lines 30-45)

#### 3.3 Create Connectivity Profile

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/profile/connectivity/

{
  "name": "{{VS1_NAME}}-cp",
  "partition": "Common",
  "adaptiveCompression": "enabled",
  "customizationGroup": "/Common/{{VS1_NAME}}-cp_secure_access_client_customization",
  "tunnelMode": "bidirectional",
  "tunnelReference": "/Common/{{VS1_NAME}}-tunnel"
}
```

**Ansible:**
```yaml
- name: Create connectivity profile
  uri:
    body:
      name: "{{ vs1_name }}-cp"
      partition: "Common"
      adaptiveCompression: "{{ 'enabled' if enable_compression else 'disabled' }}"
      customizationGroup: "/Common/{{ vs1_name }}-cp_secure_access_client_customization"
      tunnelMode: "bidirectional"
      tunnelReference: "/Common/{{ vs1_name }}-tunnel"
```

**File:** `tasks/connectivity_profile.yml` (lines 51-69)

---

### 4. Network Access Resource

#### 4.1 Create IP Lease Pool

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/resource/leasepool/

{
  "name": "{{VS1_NAME}}-vpn_pool",
  "partition": "Common",
  "locationSpecific": "true",
  "members": ["10.1.2.1-10.1.2.254"]
}
```

**Ansible:**
```yaml
- name: Create VPN IP lease pool
  uri:
    body:
      name: "{{ vs1_name }}-vpn_pool"
      partition: "Common"
      locationSpecific: "true"
      members:
        - "{{ vpn_lease_pool_start }}-{{ vpn_lease_pool_end }}"
```

**File:** `tasks/network_access.yml` (lines 7-23)

#### 4.2 Create Network Access Resource

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/resource/network-access/

{
  "name": "{{VS1_NAME}}-vpn",
  "addressSpaceIncludeSubnets": ["10.1.10.0/255.255.255.0", "10.1.20.0/255.255.255.0"],
  "ipv4LeasePool": "/Common/{{VS1_NAME}}-vpn_pool",
  "splitTunneling": "true",
  "dtlsEnabled": "true"
}
```

**Ansible:**
```yaml
- name: Create network access resource
  uri:
    body:
      name: "{{ vs1_name }}-vpn"
      addressSpaceIncludeSubnets: "{{ vpn_split_tunnel_networks }}"
      ipv4LeasePool: "/Common/{{ vs1_name }}-vpn_pool"
      splitTunneling: "true"
      dtlsEnabled: "true"
```

**File:** `tasks/network_access.yml` (lines 45-70)

---

### 5. Access Policy (Transaction-based)

#### 5.1 Create Transaction

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/transaction

{}
```

**Postman Script:**
```javascript
var transId = pm.response.json().transId;
pm.collectionVariables.set("TRANSID", transId);
```

**Ansible:**
```yaml
- name: Create transaction for policy configuration
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/transaction"
    method: POST
    body: {}
  register: transaction_result

- name: Set transaction ID
  set_fact:
    trans_id: "{{ transaction_result.json.transId }}"
```

**File:** `tasks/access_policy.yml` (lines 7-18)

#### 5.2 Create Deny Ending (within transaction)

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/agent/ending-deny/
X-F5-REST-Coordination-Id: {{TRANSID}}

{
  "name": "{{VS1_NAME}}-psp_end_deny_ag",
  "partition": "Common",
  "customizationGroup": "/Common/{{VS1_NAME}}-psp_end_deny_ag"
}
```

**Ansible:**
```yaml
- name: Create deny ending agent
  uri:
    headers:
      X-F5-REST-Coordination-Id: "{{ trans_id }}"
    body:
      name: "{{ vs1_name }}-psp_end_deny_ag"
      partition: "Common"
      customizationGroup: "/Common/{{ vs1_name }}-psp_end_deny_ag"
```

**File:** `tasks/access_policy.yml` (lines 63-77)

#### 5.3 Create AD Authentication Agent

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/agent/aaa-active-directory
X-F5-REST-Coordination-Id: {{TRANSID}}

{
  "name": "{{VS1_NAME}}-psp_act_active_directory_auth_ag",
  "authServer": "/Common/{{VS1_NAME}}-ad-servers",
  "maxLogonAttempts": 3
}
```

**Ansible:**
```yaml
- name: Create AD authentication agent
  uri:
    headers:
      X-F5-REST-Coordination-Id: "{{ trans_id }}"
    body:
      name: "{{ vs1_name }}-psp_act_active_directory_auth_ag"
      authServer: "/Common/{{ vs1_name }}-ad-servers"
      maxLogonAttempts: "{{ apm_max_login_failures }}"
```

**File:** `tasks/access_policy.yml` (lines 163-179)

#### 5.4 Create Access Policy

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/access-policy/
X-F5-REST-Coordination-Id: {{TRANSID}}

{
  "name": "{{VS1_NAME}}-psp",
  "partition": "Common",
  "defaultEnding": "{{VS1_NAME}}-psp_end_deny",
  "startItem": "/Common/{{VS1_NAME}}-psp_ent",
  "items": ["/Common/{{VS1_NAME}}-psp_ent", ...]
}
```

**Ansible:**
```yaml
- name: Create access policy
  uri:
    headers:
      X-F5-REST-Coordination-Id: "{{ trans_id }}"
    body:
      name: "{{ vs1_name }}-psp"
      partition: "Common"
      defaultEnding: "{{ vs1_name }}-psp_end_deny"
      startItem: "/Common/{{ vs1_name }}-psp_ent"
      items:
        - "/Common/{{ vs1_name }}-psp_ent"
        - ...
```

**File:** `tasks/access_policy.yml` (lines 274-295)

#### 5.5 Commit Transaction

**Postman:**
```http
PUT https://{{BIGIP_MGMT}}/mgmt/tm/transaction/{{TRANSID}}/

{
  "state": "VALIDATING"
}
```

**Ansible:**
```yaml
- name: Commit transaction
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/transaction/{{ trans_id }}/"
    method: PUT
    body:
      state: "VALIDATING"
```

**File:** `tasks/access_policy.yml` (lines 323-334)

#### 5.6 Apply Policy

**Postman:**
```http
PATCH https://{{BIGIP_MGMT}}/mgmt/tm/apm/profile/access/~Common~{{VS1_NAME}}-psp

{
  "generationAction": "increment"
}
```

**Ansible:**
```yaml
- name: Apply access policy (increment generation)
  uri:
    method: PATCH
    body:
      generationAction: "increment"
```

**File:** `tasks/access_policy.yml` (lines 340-353)

---

### 6. AS3 Application Deployment

#### 6.1 Deploy Application

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/shared/appsvcs/declare

{
  "class": "ADC",
  "action": "deploy",
  "declaration": {
    "{{PARTITION_NAME}}": {
      "class": "Tenant",
      "{{PATH_NAME}}": {
        "class": "Application",
        "serviceMain": {
          "class": "Service_HTTPS",
          "virtualAddresses": ["{{BIGIP_ADDRESS1}}"],
          "profileAccess": {
            "bigip": "/Common/{{VS1_NAME}}-psp"
          }
        }
      }
    }
  }
}
```

**Ansible:**
```yaml
- name: Deploy application using AS3
  uri:
    body:
      class: "ADC"
      action: "deploy"
      declaration:
        "{{ partition_name }}":
          class: "Tenant"
          "{{ path_name }}":
            class: "Application"
            serviceMain:
              class: "Service_HTTPS"
              virtualAddresses:
                - "{{ app_vs_address }}"
              profileAccess:
                bigip: "/Common/{{ vs1_name }}-psp"
              profileConnectivity:
                bigip: "/Common/{{ vs1_name }}-cp"
```

**File:** `tasks/as3_deployment.yml` (lines 36-99)

---

### 7. GSLB Configuration

#### 7.1 Create Datacenter

**Postman:**
```http
POST https://10.1.1.11/mgmt/tm/gtm/datacenter

{
  "name": "DC1"
}
```

**Ansible:**
```yaml
- name: Create DC1 datacenter
  uri:
    url: "https://{{ gslb_dns_server }}:443/mgmt/tm/gtm/datacenter"
    body:
      name: "{{ gslb_dc1_name }}"
```

**File:** `tasks/gslb_configuration.yml` (lines 18-30)

#### 7.2 Create WideIP

**Postman:**
```http
POST https://10.1.1.11/mgmt/shared/appsvcs/declare

{
  "class": "ADC",
  "{{PARTITION_NAME}}": {
    "Application": {
      "{{VS1_NAME}}-wideip": {
        "class": "GSLB_Domain",
        "domainName": "{{DNS1_NAME}}",
        "pools": [...]
      }
    }
  }
}
```

**Ansible:**
```yaml
- name: Create WideIP using AS3
  uri:
    body:
      "{{ partition_name }}":
        Application:
          "{{ vs1_name }}-wideip":
            class: "GSLB_Domain"
            domainName: "{{ dns1_name }}"
            pools:
              - use: "/{{ partition_name }}/Application/{{ vs1_name }}-pool"
```

**File:** `tasks/gslb_configuration.yml` (lines 76-106)

---

## Key Enhancements in Ansible Version

### 1. Idempotency

**Postman:** Re-running causes errors on existing objects

**Ansible:** Accepts 409 status codes (conflict), safe to re-run
```yaml
status_code: [200, 201, 409]
```

### 2. Error Handling

**Postman:** Limited error handling in test scripts

**Ansible:** Built-in retry, register results, conditional logic
```yaml
register: result
ignore_errors: yes
when: result is defined
```

### 3. Variables

**Postman:** Collection variables, environment variables

**Ansible:** Centralized in `vars/main.yml`, can use multiple var files
```yaml
vars_files:
  - vars/main.yml
  - vars/vault.yml  # encrypted
```

### 4. Modularity

**Postman:** Linear execution, folders for organization

**Ansible:** Task files, roles, includes
```yaml
- include_tasks: tasks/aaa_ad_servers.yml
  when: condition
```

### 5. Conditional Execution

**Postman:** Manual enabling/disabling of requests

**Ansible:** Feature flags and conditions
```yaml
when: create_connectivity_profile | bool
```

### 6. Secrets Management

**Postman:** Plain text or environment variables

**Ansible:** Vault encryption
```bash
ansible-vault encrypt vars/main.yml
```

## Performance Comparison

| Operation | Postman (Manual) | Ansible (Automated) |
|-----------|------------------|---------------------|
| Full deployment | 15-20 minutes | 3-5 minutes |
| Multi-device | N x time | Parallel execution |
| Retry on failure | Manual | Automatic |
| Validation | Manual inspection | Task-level checks |
| Documentation | Separate | Inline task names |

## Solution 4 Critical Implementation Details

Solution 4 (SAML Identity Provider with AD Authentication) requires specific API parameter ordering and values that differ from other solutions. These requirements were discovered through iterative debugging and must be followed precisely.

### Self-Signed Certificate Generation

**Postman:** Not included (manual certificate creation assumed)

**Ansible:** Automated using OpenSSL
```yaml
# tasks/create_self_signed_cert.yml
- name: Generate self-signed certificate locally
  command: >
    openssl req -x509 -nodes -days 365 -newkey rsa:2048
    -keyout /tmp/{{ vs1_name }}-saml.key
    -out /tmp/{{ vs1_name }}-saml.crt
    -subj "/C=US/ST=State/L=City/O=Organization/CN={{ dns1_name }}"

- name: Upload private key to BIG-IP
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/shared/file-transfer/uploads/{{ vs1_name }}-saml.key"
    method: POST
    headers:
      Content-Type: "application/octet-stream"
      Content-Range: "0-{{ key_content | length - 1 }}/{{ key_content | length }}"
    body: "{{ key_content }}"
    status_code: [200, 201]

- name: Install private key on BIG-IP
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/sys/crypto/key"
    method: POST
    body:
      name: "{{ vs1_name }}-saml"
      partition: "Common"
      sourcePath: "file:/var/config/rest/downloads/{{ vs1_name }}-saml.key"
    status_code: [200, 201, 400, 409]  # 400 = already exists (idempotent)

- name: Install certificate on BIG-IP
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/sys/crypto/cert"
    method: POST
    body:
      name: "{{ vs1_name }}-saml"
      partition: "Common"
      commonName: "{{ dns1_name }}"  # REQUIRED for SAML
      sourcePath: "file:/var/config/rest/downloads/{{ vs1_name }}-saml.crt"
      key: "/Common/{{ vs1_name }}-saml"  # Associate with key
    status_code: [200, 201, 400, 409]  # 400 = already exists (idempotent)
```

**Critical Notes:**
- Private key MUST be installed before certificate
- `commonName` attribute is REQUIRED for SAML certificates
- `key` field associates certificate with private key
- Status code 400 indicates "already exists" on some BIG-IP versions (not 409)

**File:** `tasks/create_self_signed_cert.yml`

---

### Customization Groups - Ordering Requirements

**CRITICAL:** Customization groups MUST be created in a specific order. Deny ending customization group must be created FIRST.

**Postman Order (Solution 4):**
```json
// 1. Deny ending customization group
{
  "name": "{{VS1_NAME}}-psp_end_deny_ag",
  "partition": "Common",
  "source": "/Common/{{CUSTOM_TYPE}}",
  "type": "logout"
}

// 2. Logout customization group
{
  "name": "{{VS1_NAME}}-psp_logout",
  "partition": "Common",
  "source": "/Common/{{CUSTOM_TYPE}}",
  "type": "logout"
}

// 3-6. Other customization groups (eps, errormap, framework, general_ui)

// 7. Logon page customization group (REQUIRED for Solution 4)
{
  "name": "{{VS1_NAME}}-psp_act_logon_page_ag",
  "partition": "Common",
  "type": "logon",
  "source": "/Common/{{CUSTOM_TYPE}}"
}
```

**Ansible:**
```yaml
# vars/solution4.yml
# NOTE: Order matters! Deny ending MUST be first
customization_groups:
  - name: "{{ vs1_name }}-psp_end_deny_ag"
    type: "logout"
    source: "/Common/{{ custom_type }}"

  - name: "{{ vs1_name }}-psp_logout"
    type: "logout"
    source: "/Common/{{ custom_type }}"

  # ... other groups ...

  - name: "{{ vs1_name }}-psp_act_logon_page_ag"  # Required for logon page agent
    type: "logon"
    source: "/Common/{{ custom_type }}"
```

**Critical Notes:**
- Deny ending customization group MUST be first in the list
- Logon page customization group is REQUIRED (missing in initial implementation)
- `source` must be a valid customization type: `/Common/standard` or `/Common/modern`
- Use `standard` for maximum compatibility (not all BIG-IP versions have `modern`)

**File:** `vars/solution4.yml` (lines 167-194)

---

### Policy Agents - Type Requirements

**CRITICAL:** Policy agents MUST be created in specific order with correct type parameters.

#### Agent Creation Order

**Postman Order:**
```
1. Allow ending agent (NO customizationGroup)
2. Deny ending agent (WITH customizationGroup)
3. Active Directory agent (WITH type: "auth")
4. Logon page agent (WITH customizationGroup)
```

**Incorrect Order (causes transaction failure):**
```yaml
# WRONG - This will fail with "agent type value doesn't match"
- name: Create deny ending agent  # Should be second, not first
- name: Create allow ending agent
```

**Correct Order:**
```yaml
# tasks/access_policy_solution4.yml

# 1. Allow ending agent (no customizationGroup)
- name: Create allow ending agent
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/policy/agent/ending-allow/"
    method: POST
    headers:
      X-F5-REST-Coordination-Id: "{{ transaction_id }}"
    body:
      name: "{{ policy_agents.allow_ending.name }}"
      partition: "Common"
      # NO customizationGroup for allow ending
    status_code: [200, 201, 409]

# 2. Deny ending agent (WITH customizationGroup)
- name: Create deny ending agent
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/policy/agent/ending-deny/"
    method: POST
    headers:
      X-F5-REST-Coordination-Id: "{{ transaction_id }}"
    body:
      name: "{{ policy_agents.deny_ending.name }}"
      partition: "Common"
      customizationGroup: "{{ policy_agents.deny_ending.customization_group }}"
    status_code: [200, 201, 409]
```

#### AAA Active Directory Agent - REQUIRED Type Parameter

**Postman:**
```json
{
  "name": "{{VS1_NAME}}-psp_act_active_directory_auth_ag",
  "partition": "Common",
  "authMaxLogonAttempt": 3,
  "server": "/Common/{{VS1_NAME}}-ad-servers",
  "type": "auth",  // CRITICAL: Required for profile compatibility
  "upn": "false",
  "fetchNestedGroups": "false",
  "showExtendedError": "false"
}
```

**Ansible:**
```yaml
- name: Create AD authentication agent
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/policy/agent/aaa-active-directory/"
    method: POST
    headers:
      X-F5-REST-Coordination-Id: "{{ transaction_id }}"
    body:
      name: "{{ policy_agents.ad_auth.name }}"
      partition: "Common"
      server: "{{ policy_agents.ad_auth.server }}"
      authMaxLogonAttempts: "{{ policy_agents.ad_auth.auth_max_logon_attempts }}"
      type: "auth"  # REQUIRED: Allows association with profile type "all"
      upn: "{{ policy_agents.ad_auth.upn }}"
      fetchNestedGroups: "{{ policy_agents.ad_auth.fetch_nested_groups }}"
      showExtendedError: "{{ policy_agents.ad_auth.show_extended_error }}"
```

**Error Without type: "auth":**
```
transaction failed: Profile access (/Common/idp-psp) of type all cannot be
associated with agent (/Common/idp-psp_act_active_directory_auth_ag) of type
aaa-active-directory
```

**File:** `tasks/access_policy_solution4.yml` (lines 107-129)

---

### Policy Items - Agent Reference Format

**CRITICAL:** Policy items MUST reference agents as objects with name/partition/type, not as simple strings.

**Incorrect Format (causes transaction failure):**
```yaml
# WRONG - Simple string reference
body:
  name: "{{ policy_items.deny_ending.name }}"
  agents:
    - "/Common/{{ policy_agents.deny_ending.name }}"  # WRONG
  itemType: "ending"
```

**Correct Format:**
```yaml
# CORRECT - Object with name, partition, and type
body:
  name: "{{ policy_items.deny_ending.name }}"
  agents:
    - name: "{{ policy_agents.deny_ending.name }}"
      partition: "Common"
      type: "{{ policy_items.deny_ending.agent_type }}"  # e.g., "ending-deny"
  caption: "{{ policy_items.deny_ending.caption }}"
  color: "{{ policy_items.deny_ending.color }}"
  itemType: "{{ policy_items.deny_ending.item_type }}"
```

**Postman Format:**
```json
{
  "name": "{{VS1_NAME}}-psp_end_deny",
  "partition": "Common",
  "caption": "Deny",
  "color": 2,
  "itemType": "ending",
  "agents": [
    {
      "name": "{{VS1_NAME}}-psp_end_deny_ag",
      "partition": "Common",
      "type": "ending-deny"
    }
  ]
}
```

**Agent Type Mappings:**
- Deny ending: `type: "ending-deny"`
- Allow ending: `type: "ending-allow"`
- Logon page: `type: "logon-page"`
- AD authentication: `type: "aaa-active-directory"`

**File:** `tasks/access_policy_solution4.yml` (lines 134-241)

---

### Transaction Validation Errors and Solutions

Common errors encountered during Solution 4 implementation:

| Error Message | Root Cause | Solution |
|---------------|------------|----------|
| `The agent can not have empty customization group` | Logon page agent missing customizationGroup | Add logon page customization group and reference it |
| `Agent of type (1) has agent type value (0) which doesn't match` | Agents created in wrong order | Create allow ending before deny ending |
| `Profile access of type all cannot be associated with agent of type aaa-active-directory` | AD agent missing type: "auth" | Add `type: "auth"` to AD agent body |
| `Configuration group has invalid source '/Common/modern'` | Customization type not available | Change custom_type to "standard" |
| `The requested key(idp-saml) already exists` | Certificate re-upload not idempotent | Add status code 400 to accepted codes |

---

## Solution 6 Critical Implementation Details

Solution 6 (Certificate-based Authentication with Kerberos SSO) implements client certificate validation with OCSP, UPN extraction from X.509 certificates, LDAP queries, and Kerberos SSO. This solution requires careful handling of certificate authentication modes, TCL expressions, and field name conventions.

### CA Certificate Import

**Postman:** Multi-step upload with Content-Range headers

**Ansible:** Automated certificate upload and installation
```yaml
# tasks/import_ca_certificate.yml
- name: Prepare CA certificate content
  set_fact:
    ca_cert_content_raw: "{{ ca_certificate.content }}"
    ca_cert_length: "{{ ca_certificate.content | length }}"

- name: Upload CA certificate file to BIG-IP
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/shared/file-transfer/uploads/{{ ca_certificate.filename }}"
    method: POST
    headers:
      Content-Type: "application/octet-stream"
      Content-Range: "0-{{ ca_cert_length | int - 1 }}/{{ ca_cert_length }}"
    body: "{{ ca_cert_content_raw }}"
    status_code: [200, 201]

- name: Install CA certificate on BIG-IP
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/sys/crypto/cert"
    method: POST
    body:
      command: "install"
      name: "{{ ca_certificate.name }}"
      from-local-file: "/var/config/rest/downloads/{{ ca_certificate.filename }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- Content-Range header is REQUIRED for file uploads
- Range format: `0-{length-1}/{length}` (zero-indexed)
- Certificate must exist before OCSP/client cert agents can reference it
- Status code 409 indicates certificate already exists (idempotent)

**File:** `tasks/import_ca_certificate.yml`

---

### Kerberos SSO Profile

**Postman:** Created outside transaction (no X-F5-REST-Coordination-Id header)

**Ansible:** Created before transaction begins
```yaml
# tasks/kerberos_sso.yml
- name: Create Kerberos SSO profile
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/sso/kerberos/"
    method: POST
    body:
      name: "{{ kerberos_sso.name }}"
      partition: "Common"
      accountName: "{{ kerberos_sso.account_name }}"
      accountPassword: "{{ kerberos_sso.account_password }}"
      realm: "{{ kerberos_sso.realm }}"
      spnPattern: "{{ kerberos_sso.spn_pattern }}"
      usernameSource: "{{ kerberos_sso.username_source }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- Created OUTSIDE transaction (no coordination header)
- Must exist before access profile references it via `ssoName` field
- `accountName` should be domain service account (e.g., `HTTP_SVC@F5LAB.LOCAL`)
- `spnPattern` defines how SPN is constructed (e.g., `HTTP/%h@F5LAB.LOCAL`)
- `usernameSource` typically: `session.logon.last.username`

**File:** `tasks/kerberos_sso.yml`

---

### OCSP Validation Configuration

**Postman:** Simple AAA OCSP server creation

**Ansible:** OCSP responder configuration for certificate revocation checking
```yaml
# tasks/ocsp_servers.yml
- name: Create OCSP servers configuration
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/aaa/ocsp"
    method: POST
    body:
      name: "{{ ocsp_servers.name }}"
      partition: "Common"
      url: "{{ ocsp_servers.url }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- OCSP server must be accessible from BIG-IP management interface
- URL format: `http://ocsp.example.com/ocsp` or `http://ocsp.example.com`
- Created OUTSIDE transaction
- Referenced by OCSP authentication agent via `ocspResponder` field

**File:** `tasks/ocsp_servers.yml`

---

### LDAP Query Configuration (Non-Authentication)

**Postman:** LDAP AAA server with type: "query"

**Ansible:** LDAP node, pool, and AAA server for user attribute lookups
```yaml
# tasks/ldap_aaa_server.yml
- name: Create LDAP server node
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/ltm/node"
    method: POST
    body:
      name: "{{ ldap_server_ip }}"
      address: "{{ ldap_server_ip }}"
    status_code: [200, 201, 409]

- name: Create LDAP server pool
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/ltm/pool/"
    method: POST
    body:
      name: "{{ ldap_pool.name }}"
      members:
        - "{{ ldap_server_ip }}:389"
      monitor: "/Common/tcp"
    status_code: [200, 201, 409]

- name: Create APM AAA LDAP server
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/aaa/ldap/"
    method: POST
    body:
      name: "{{ ldap_aaa_server.name }}"
      partition: "Common"
      adminDn: "{{ ldap_aaa_server.admin_dn }}"
      adminEncryptedPassword: "{{ ldap_aaa_server.admin_password }}"
      searchBaseDn: "{{ ldap_aaa_server.search_base_dn }}"
      searchFilter: "{{ ldap_aaa_server.search_filter }}"
      server: "/Common/{{ ldap_pool.name }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- LDAP is used for QUERY only, not authentication
- `searchFilter` should match UPN: `(userPrincipalName=%{session.custom.upn})`
- `attrName` in LDAP query agent: `["sAMAccountName"]` to retrieve username
- LDAP server must be created OUTSIDE transaction
- Pool reference format: `/Common/pool-name`

**File:** `tasks/ldap_aaa_server.yml`

---

### UPN Extraction from X.509 Certificates

**Critical:** TCL expression must be properly escaped for JSON transmission

**Postman:** TCL expression with newline escaping
```json
{
  "expression": "set x509e_fields [split [mcget {session.ssl.cert.x509extension}] \"\\n\"];\n# For each element...",
  "varname": "session.custom.upn"
}
```

**Ansible:** Single-line with proper escape sequences
```yaml
# vars/solution6.yml
policy_agents:
  upn_extract:
    name: "{{ vs1_name }}-psp_act_variable_assign_ag"
    type: "general"
    variables:
      - varname: "session.custom.upn"
        expression: "set x509e_fields [split [mcget {session.ssl.cert.x509extension}] \\\"\\\\n\\\"];\\n# For each element in the list:\\nforeach field $x509e_fields {\\n# If the element contains UPN:\\nif { $field contains \\\"othername:UPN\\\" } {\\n## set start of UPN variable\\nset start [expr {[string first \\\"othername:UPN<\\\" $field] +14}]\\n# UPN format is <user@domain>\\n# Return the UPN, by finding the index of opening and closing brackets, then use string range to get everything between.\\nreturn [string range $field $start [expr { [string first \\\">\\\" $field $start] - 1 } ] ];  } }\\n# Otherwise return UPN Not Found:\\nreturn \\\"UPN-NOT-FOUND\\\";"
        secure: "false"
        append: "false"
```

**Critical Notes:**
- TCL expression must be on ONE line (use `\\n` for newlines, not actual line breaks)
- Quotes must be escaped: `\\\"` for literal quotes in TCL
- Backslashes must be double-escaped: `\\\\n` for literal `\n` in TCL
- Expression extracts UPN from X.509 extension field `othername:UPN<user@domain>`
- Returns "UPN-NOT-FOUND" if UPN not present in certificate

**File:** `vars/solution6.yml` (line 183)

---

### Client Certificate Authentication Mode

**Critical:** Use "request" mode for on-demand certificate authentication

**Postman:**
```json
{
  "name": "{{VS1_NAME}}-psp_act_ondemand_cert_auth_ag",
  "mode": "request",
  "partition": "Common"
}
```

**Ansible:**
```yaml
# tasks/access_policy_solution6.yml
- name: Create on-demand client cert auth agent
  uri:
    body:
      name: "{{ policy_agents.client_cert_auth.name }}"
      partition: "Common"
      mode: "request"  # CRITICAL: "request" not "require"
```

**Modes Explained:**
- `request`: Client cert is requested but not required at SSL handshake; APM validates during policy execution
- `require`: Client cert is required at SSL handshake; connection fails if not provided
- `ignore`: No client cert authentication

**Why "request" mode:**
- Allows APM policy to control authentication flow
- Better error handling and user feedback
- Can branch on `session.ssl.cert.valid` variable
- Supports fallback to other auth methods

**File:** `tasks/access_policy_solution6.yml` (line 147)

---

### camelCase vs snake_case Field Names

**CRITICAL:** BIG-IP APM API requires camelCase for certain fields, not snake_case

**Incorrect (causes transaction failure):**
```yaml
policy_items:
  entry:
    next_item: "/Common/{{ vs1_name }}-psp_act_ondemand_cert_auth"  # WRONG
```

**Correct:**
```yaml
policy_items:
  entry:
    nextItem: "/Common/{{ vs1_name }}-psp_act_ondemand_cert_auth"  # CORRECT
```

**Field Name Convention:**
- `nextItem` (NOT `next_item`)
- `defaultEnding` (NOT `default_ending`)
- `startItem` (NOT `start_item`)
- `maxMacroLoopCount` (NOT `max_macro_loop_count`)
- `itemType` (NOT `item_type`)

**Common Error:**
```
transaction failed:01070277:3: The requested access policy item () was not found.
```
This error with empty parentheses `()` indicates a field name mismatch.

**File:** `vars/solution6.yml` (lines 227, 240, 242, etc.)

---

### Avoiding Python dict.items() Collision

**CRITICAL:** In Ansible/Jinja2, dictionary keys named "items" collide with Python's built-in `dict.items()` method

**Incorrect (causes error):**
```yaml
access_policy:
  name: "{{ vs1_name }}-psp"
  items:  # WRONG - Collides with dict.items() method
    - name: "{{ vs1_name }}-psp_act_ldap_query"
      partition: "Common"
```

**Error Message:**
```
"items": "<built-in method items of dict object at 0x7fedce781c00>"
```

**Correct:**
```yaml
access_policy:
  name: "{{ vs1_name }}-psp"
  policy_items:  # CORRECT - Renamed to avoid collision
    - name: "{{ vs1_name }}-psp_act_ldap_query"
      partition: "Common"
```

**Then reference as:**
```yaml
items: "{{ access_policy.policy_items }}"  # Maps to API's "items" field
```

**File:** `vars/solution6.yml` (line 301), `tasks/access_policy_solution6.yml` (line 441)

---

### AS3 Dynamic Dictionary Keys with combine Filter

**CRITICAL:** Jinja2 variables used as dictionary keys in YAML don't evaluate properly when nested in `uri` module body

**Incorrect (variables not evaluated):**
```yaml
- name: Create AS3 declaration
  uri:
    body:
      declaration:
        "{{ partition_name }}":  # Sent as literal string "{{ partition_name }}"
          class: "Tenant"
```

**Error:**
```
'/: propertyName "{{ partition_name }}" should match pattern "^[A-Za-z][0-9A-Za-z_.-]*$"'
```

**Correct (use combine filter):**
```yaml
- name: Build declaration
  set_fact:
    declaration_config:
      class: "ADC"
      schemaVersion: "3.14.0"

- name: Add tenant to declaration
  set_fact:
    declaration_config: "{{ declaration_config | combine({partition_name: tenant_config}) }}"

- name: Create AS3 declaration
  uri:
    body: "{{ declaration_config }}"
```

**Why this works:**
- `{partition_name: value}` syntax evaluates `partition_name` as a variable
- `combine` filter merges dictionaries programmatically
- Build nested structure from inside out: pool → app → tenant → declaration

**File:** `deploy_apm_cert_kerb.yml` (lines 70-156)

---

### AS3 Integer Type Preservation

**CRITICAL:** AS3 schema validation requires integer types for certain fields like `virtualPort`

**Incorrect (sent as string):**
```yaml
virtualPort: "{{ as3_config.virtual_port }}"  # Evaluates to string "443"
```

**Error:**
```
'/solution6/solution6/solution6/virtualPort: should be integer'
```

**Correct (preserve integer type):**
```yaml
- name: Build virtual server config
  set_fact:
    vs_config:
      virtualPort: 443  # Unquoted integer literal
```

**Type Preservation Rules:**
- Use unquoted literals in YAML for integers: `443` not `"443"`
- Avoid Jinja2 templates in `vars` blocks for integer fields
- Even with `| int` filter, quoted values become strings in JSON serialization
- Separate `set_fact` tasks preserve types better than inline `vars`

**File:** `deploy_apm_cert_kerb.yml` (line 86)

---

### Policy Item Rules Structure

**Postman:** Rules array with caption, expression, and nextItem

**Ansible:** Identical structure with proper field names
```yaml
policy_items:
  client_cert_auth:
    rules:
      - caption: "Successful"
        expression: "expr {[mcget {session.ssl.cert.valid}] == \"0\"}"
        nextItem: "/Common/{{ vs1_name }}-psp_act_ocsp_auth"
      - caption: "fallback"
        nextItem: "/Common/{{ vs1_name }}-psp_end_deny"
```

**Critical Notes:**
- Certificate validation: `{session.ssl.cert.valid} == "0"` (0 = valid, non-zero = invalid)
- OCSP validation: `{session.ocsp.last.result} == 1` (1 = success)
- LDAP query result: `{session.ldap.last.queryresult} == 1` (1 = success)
- Always include "fallback" rule as final catch-all
- `nextItem` must use camelCase (NOT `next_item`)
- All references must use full path: `/Common/item-name`

**File:** `vars/solution6.yml` (lines 262-282)

---

### File Location Reference (Solution 6)

| Component | File Path |
|-----------|-----------|
| Solution 6 playbook | `deploy_apm_cert_kerb.yml` |
| Solution 6 delete playbook | `delete_apm_cert_kerb.yml` |
| Solution 6 variables | `vars/solution6.yml` |
| CA certificate import | `tasks/import_ca_certificate.yml` |
| Kerberos SSO profile | `tasks/kerberos_sso.yml` |
| OCSP servers | `tasks/ocsp_servers.yml` |
| LDAP AAA server | `tasks/ldap_aaa_server.yml` |
| Access policy (Solution 6) | `tasks/access_policy_solution6.yml` |
| Solution 6 source | [solution6-create.postman_collection.json](https://github.com/f5devcentral/access-solutions/blob/master/solution6/postman/solution6-create.postman_collection.json) |

---

## Migration Path

### From Postman to Ansible

1. **Export** Postman collection
2. **Analyze** API calls and dependencies
3. **Group** related calls into task files
4. **Extract** variables to vars file
5. **Add** error handling and idempotency
6. **Test** in lab environment
7. **Document** customizations

### Adding New Postman Collections

To add additional solutions:

1. Download new Postman collection
2. Create new task file: `tasks/solution2_tasks.yml`
3. Add variables to `vars/main.yml`
4. Include in main playbook
5. Test and validate

## File Location Reference

| Component | File Path |
|-----------|-----------|
| Solution 1 playbook | `deploy_apm_vpn.yml` |
| Solution 2 playbook | `deploy_apm_portal.yml` |
| Solution 3 playbook | `deploy_apm_saml.yml` |
| Solution 4 playbook | `deploy_apm_saml_idp.yml` |
| Solution 5 playbook | `deploy_apm_saml_sp_internal.yml` |
| Solution 6 playbook | `deploy_apm_cert_kerb.yml` |
| Solution 1 variables | `vars/main.yml` |
| Solution 2 variables | `vars/solution2.yml` |
| Solution 3 variables | `vars/solution3.yml` |
| Solution 4 variables | `vars/solution4.yml` |
| Solution 5 variables | `vars/solution5.yml` |
| Solution 6 variables | `vars/solution6.yml` |
| AAA AD tasks | `tasks/aaa_ad_servers.yml` |
| SAML IDP Connector (Sol 3) | `tasks/saml_idp_connector.yml` |
| SAML Service Provider (Sol 3) | `tasks/saml_sp.yml` |
| SAML SP Connector (Sol 4) | `tasks/saml_sp_connector.yml` |
| SAML IDP Service (Sol 4) | `tasks/saml_idp_service.yml` |
| SAML SP (Sol 5) | `tasks/saml_sp_solution5.yml` |
| CA Certificate Import (Sol 6) | `tasks/import_ca_certificate.yml` |
| Kerberos SSO (Sol 6) | `tasks/kerberos_sso.yml` |
| OCSP Servers (Sol 6) | `tasks/ocsp_servers.yml` |
| LDAP AAA Server (Sol 6) | `tasks/ldap_aaa_server.yml` |
| Connectivity tasks | `tasks/connectivity_profile.yml` |
| Network access tasks | `tasks/network_access.yml` |
| Portal resources tasks | `tasks/portal_resources.yml` |
| Webtop tasks | `tasks/webtop.yml` |
| Access policy (Sol 1) | `tasks/access_policy.yml` |
| Access policy (Sol 2) | `tasks/access_policy_solution2.yml` |
| Access policy (Sol 3) | `tasks/access_policy_solution3.yml` |
| Access policy (Sol 4) | `tasks/access_policy_solution4.yml` |
| Access policy (Sol 5) | `tasks/access_policy_solution5.yml` |
| Access policy (Sol 6) | `tasks/access_policy_solution6.yml` |
| AS3 deployment tasks | `tasks/as3_deployment.yml` |
| GSLB tasks | `tasks/gslb_configuration.yml` |
| Solution 1 source | `docs/solution1-create.postman_collection.json` |
| Solution 2 source | `docs/solution2-create.postman_collection.json` |
| Solution 3 source | `docs/solution3-create.postman_collection.json` |
| Solution 4 source | `docs/solution4-create.postman_collection.json` |
| Solution 5 source | [solution5-create.postman_collection.json](https://github.com/f5devcentral/access-solutions/blob/master/solution5/postman/solution5-create.postman_collection.json) |
| Solution 6 source | [solution6-create.postman_collection.json](https://github.com/f5devcentral/access-solutions/blob/master/solution6/postman/solution6-create.postman_collection.json) |
| Solution 7 playbook | `deploy_apm_sideband.yml` |
| Solution 7 delete playbook | `delete_apm_sideband.yml` |
| Solution 7 variables | `vars/solution7.yml` |
| Access policy VS1 (Solution 7) | `tasks/access_policy_solution7_vs1.yml` |
| Access policy VS2 (Solution 7) | `tasks/access_policy_solution7_vs2.yml` |

---

## Solution 7 Critical Implementation Details

Solution 7 (SAML Authentication with Sideband Communication) implements a two-virtual-server architecture where VS1 handles SAML authentication and sends session data via sideband to VS2, which applies Kerberos SSO to backend applications.

### Two Virtual Server Architecture

**VS1 (Send Sideband):**
- SAML Service Provider with Okta IDP
- AD Query to retrieve user attributes
- iRule Event to send sideband connection to VS2
- Access policy flow: SAML Auth → AD Query → Variable Assign → iRule Event → Allow

**VS2 (Receive Sideband):**
- Receives TCP sideband connection from VS1
- iRule parses username from query string
- Variable Assign sets Kerberos domain
- Kerberos SSO to backend applications
- Access policy flow: Start → Variable Assign → Allow

---

### iRule for Send Sideband (VS1)

**Ansible:**
```yaml
# vars/solution7.yml
irules:
  send_sideband:
    name: "{{ vs1_name }}-irule"
    content: |
      when ACCESS_POLICY_AGENT_EVENT {
        switch -glob [string tolower [ACCESS::policy agent_id]] {
          "{{ vs1_name }}" {
            # Establish TCP sideband connection to VS2
            set conn [connect -protocol TCP -timeout 100 -idle 30 -status conn_status /{{ partition_name }}/{{ vs2_name }}/{{ vs2_name }}]

            # Get username from session and send via HTTP request
            set username [ACCESS::session data get "session.ad.last.attr.sAMAccountName"]
            set data "GET /?username=$username HTTP/1.1\r\nHost: {{ dns1_name }}\r\nUser-Agent: Side-band\r\nclientless-mode: 1\r\n\r\n"
            set send_info [send -timeout 3000 -status send_status $conn $data]

            after 1000
            close $conn
          }
        }
      }
```

**Critical Notes:**
- `ACCESS_POLICY_AGENT_EVENT` triggered by iRule Event agent in policy
- `agent_id` must match the iRule Event agent's `id` field
- Sideband connection path format: `/partition/app/virtual_server`
- Username retrieved from AD Query result: `session.ad.last.attr.sAMAccountName`
- `clientless-mode: 1` header required for APM session handling

**File:** `vars/solution7.yml` (lines 189-210)

---

### iRule for Receive Sideband (VS2)

**Ansible:**
```yaml
# vars/solution7.yml
irules:
  receive_sideband:
    name: "{{ vs2_name }}-irule"
    content: |
      when CLIENT_ACCEPTED {
        ACCESS::restrict_irule_events disable
      }

      when HTTP_REQUEST {
        # Parse username from query string
        set username [lindex [split [HTTP::query] =] 1]
      }

      when ACCESS_SESSION_STARTED {
        # Store username in session variable
        ACCESS::session data set session.logon.last.username $username
      }
```

**Critical Notes:**
- `ACCESS::restrict_irule_events disable` allows iRule to set session variables
- Username parsed from query string format: `?username=value`
- `ACCESS_SESSION_STARTED` event is when session variables can be set
- `session.logon.last.username` is used by Kerberos SSO profile

**File:** `vars/solution7.yml` (lines 212-229)

---

### AS3 Deployment with Two Applications

**CRITICAL:** AS3 declaration must include both virtual servers in the same tenant.

**Ansible:**
```yaml
# deploy_apm_sideband.yml
- name: Build VS1 virtual server config
  set_fact:
    vs1_vs_config:
      class: "Service_HTTPS"
      virtualAddresses:
        - "{{ as3_config.vs1_virtual_address }}"
      virtualPort: 443
      serverTLS: "{{ vs1_name }}-clientssl"
      clientTLS: "{{ vs1_name }}-serverssl"
      iRules:
        - "{{ vs1_name }}-irule"
      profileAccess:
        bigip: "/Common/{{ vs1_name }}-psp"
      pool: "{{ vs1_name }}-iis-pool"
      snat: "auto"

- name: Build VS2 virtual server config
  set_fact:
    vs2_vs_config:
      class: "Service_HTTP"
      virtualAddresses:
        - "{{ as3_config.vs2_virtual_address }}"
      virtualPort: 80
      iRules:
        - "{{ vs2_name }}-irule"
      profileAccess:
        bigip: "/Common/{{ vs2_name }}-psp"
      pool: "{{ vs2_name }}-iis-pool"
      snat: "auto"
```

**Critical Notes:**
- VS1 uses `Service_HTTPS` with client/server TLS profiles
- VS2 uses `Service_HTTP` (internal only, no TLS required)
- Both virtual servers reference iRules created via AS3
- Access profiles must exist in `/Common` before AS3 deployment
- Uses default BIG-IP certificate (`default.crt`/`default.key`) for VS1

**File:** `deploy_apm_sideband.yml` (lines 362-475)

---

### iRule Event Agent Configuration

**Ansible:**
```yaml
# vars/solution7.yml
vs1_policy_agents:
  irule_event:
    name: "{{ vs1_name }}-psp_act_irule_event_ag"
    expect_data: "http"
    id: "{{ vs1_name }}"
```

**Critical Notes:**
- `expect_data: "http"` indicates HTTP-based sideband communication
- `id` must match the switch case in the send-sideband iRule
- Agent triggers `ACCESS_POLICY_AGENT_EVENT` in iRule

**File:** `vars/solution7.yml` (lines 269-272)

---

### Sideband Connection Path Format

**CRITICAL:** The sideband connection path must use the correct format to reach VS2.

**Format:** `/partition/application/virtual_server`

**Example:**
```tcl
set conn [connect -protocol TCP -timeout 100 -idle 30 -status conn_status /solution7/receive-sideband/receive-sideband]
```

**Components:**
- `/solution7` - AS3 tenant/partition name
- `/receive-sideband` - AS3 application name (matches `vs2_name`)
- `/receive-sideband` - Virtual server name within application

**Common Error:**
If path is incorrect, sideband connection fails with no error in policy (silent failure).

**File:** `vars/solution7.yml` (line 197)

---

### Kerberos SSO Profile for VS2

**Ansible:**
```yaml
# vars/solution7.yml
kerberos_sso:
  name: "{{ vs2_name }}-sso"
  account_name: "HOST/{{ vs2_name }}.f5lab.local"
  account_password: "{{ vs2_name }}"
  realm: "F5LAB.LOCAL"
  send_authorization: "401"
  spn_pattern: "HTTP/{{ dns1_name }}"
  username_source: "session.logon.last.username"
  user_realm_source: "session.logon.last.domain"
```

**Critical Notes:**
- `account_name` is the Kerberos service account (must exist in AD)
- `realm` must be uppercase (Kerberos convention)
- `spn_pattern` defines how SPN is constructed for backend
- `username_source` reads from session variable set by VS2 iRule
- `user_realm_source` reads from session variable set by VS2 policy

**File:** `vars/solution7.yml` (lines 174-186)

---

### Variable Assign for Domain (VS2)

**Ansible:**
```yaml
# vars/solution7.yml
vs2_policy_agents:
  variable_assign:
    name: "{{ vs2_name }}-psp_act_variable_assign_1_ag"
    type: "general"
    variables:
      - append: "false"
        expression: "return {F5LAB.LOCAL}"
        secure: "false"
        varname: "session.logon.last.domain"
```

**Critical Notes:**
- Sets the Kerberos domain for SSO
- `return {value}` syntax for literal values in TCL
- Domain should match `kerberos_sso.realm` (uppercase)
- This runs AFTER iRule sets `session.logon.last.username`

**File:** `vars/solution7.yml` (lines 494-501)

---

### Transaction Handling for Two Policies

**CRITICAL:** Each access policy requires its own transaction.

**Ansible:**
```yaml
# tasks/access_policy_solution7_vs1.yml
- name: Create transaction for VS1 policy configuration
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/transaction"
    method: POST
    body: {}
  register: transaction_result

- name: Set transaction ID
  set_fact:
    trans_id: "{{ transaction_result.json.transId }}"
```

**Critical Notes:**
- VS1 and VS2 policies use separate transactions
- Transaction ID must be included in all policy-related API calls
- Commit transaction with `state: "VALIDATING"`
- Apply policy with `generationAction: "increment"` after commit

**Files:**
- `tasks/access_policy_solution7_vs1.yml` (lines 5-24)
- `tasks/access_policy_solution7_vs2.yml` (lines 5-24)

---

### File Location Reference (Solution 7)

| Component | File Path |
|-----------|-----------|
| Solution 7 playbook | `deploy_apm_sideband.yml` |
| Solution 7 delete playbook | `delete_apm_sideband.yml` |
| Solution 7 variables | `vars/solution7.yml` |
| VS1 access policy | `tasks/access_policy_solution7_vs1.yml` |
| VS2 access policy | `tasks/access_policy_solution7_vs2.yml` |
| Solution 8 playbook | `deploy_apm_oauth_as.yml` |
| Solution 8 delete playbook | `delete_apm_oauth_as.yml` |
| Solution 8 variables | `vars/solution8.yml` |
| Access policy (Solution 8) | `tasks/access_policy_solution8.yml` |
| Solution 8 source | [solution8-create.postman_collection.json](https://github.com/f5devcentral/access-solutions/blob/master/solution8/postman/solution8-create.postman_collection.json) |

---

## Solution 8 Critical Implementation Details

Solution 8 (OAuth Authorization Server with AD Authentication) implements BIG-IP APM as an OAuth 2.0 Authorization Server, issuing JWT tokens after authenticating users via Active Directory.

### OAuth Authorization Server Architecture

**Components:**
- JWK (JSON Web Key) for JWT signing
- OAuth Profile with token endpoints
- Access Policy: Logon Page → AD Auth → AD Query → OAuth Authorization

**Token Flow:**
1. Client requests authorization at `/f5-oauth2/v1/authorize`
2. User authenticates via Logon Page
3. AD validates credentials
4. AD Query retrieves user attributes for token claims
5. OAuth Authorization agent generates JWT tokens
6. Client receives `access_token` and `refresh_token`

---

### JWK Configuration

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/oauth/jwk-config/

{
  "name": "{{VS_NAME}}-jwk",
  "partition": "Common",
  "algType": "HS256",
  "autoGenerated": "false",
  "includeX5c": "no",
  "keyId": "lab",
  "keyType": "octet",
  "keyUse": "signing",
  "sharedSecret": "secret",
  "sharedSecretEncFormat": "none",
  "useClientSecret": "false"
}
```

**Ansible:**
```yaml
# deploy_apm_oauth_as.yml
- name: Create JWK configuration for JWT signing
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/oauth/jwk-config/"
    method: POST
    body:
      name: "{{ jwk_config.name }}"
      partition: "{{ jwk_config.partition }}"
      algType: "{{ jwk_config.alg_type }}"
      autoGenerated: "{{ jwk_config.auto_generated }}"
      includeX5c: "{{ jwk_config.include_x5c }}"
      keyId: "{{ jwk_config.key_id }}"
      keyType: "{{ jwk_config.key_type }}"
      keyUse: "{{ jwk_config.key_use }}"
      sharedSecret: "{{ jwk_config.shared_secret }}"
      sharedSecretEncFormat: "{{ jwk_config.shared_secret_enc_format }}"
      useClientSecret: "{{ jwk_config.use_client_secret }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- JWK must be created BEFORE OAuth Profile (profile references JWK)
- `algType: "HS256"` - HMAC with SHA-256 (symmetric key)
- `keyType: "octet"` - Required for HS256 algorithm
- `sharedSecret` - Used for token signing/verification
- For production, use a strong secret and consider RS256 with certificates

**File:** `deploy_apm_oauth_as.yml` (lines 107-129)

---

### OAuth Profile Configuration

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/profile/oauth

{
  "name": "{{VS_NAME}}-oauth",
  "partition": "Common",
  "defaultsFrom": "/Common/oauth",
  "dbInstance": "/Common/oauthdb",
  "issuer": "https://{{DNS1_NAME}}",
  "primaryKey": "/Common/{{VS_NAME}}-jwk",
  "jwtToken": "enabled",
  "opaqueToken": "disabled",
  "jwtAccessTokenLifetime": 120,
  "jwtRefreshTokenLifetime": 120,
  "authUrl": "/f5-oauth2/v1/authorize",
  "tokenIssuanceUrl": "/f5-oauth2/v1/token",
  "tokenIntrospectionUrl": "/f5-oauth2/v1/introspect",
  "tokenRevocationUrl": "/f5-oauth2/v1/revoke",
  "jwksUrl": "/f5-oauth2/v1/jwks",
  "openidCfgUrl": "/f5-oauth2/v1/.well-known/openid-configuration",
  "userinfoUrl": "/f5-oauth2/v1/userinfo"
}
```

**Ansible:**
```yaml
# deploy_apm_oauth_as.yml
- name: Create OAuth profile
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/profile/oauth"
    method: POST
    body:
      name: "{{ oauth_profile.name }}"
      partition: "{{ oauth_profile.partition }}"
      defaultsFrom: "{{ oauth_profile.defaults_from }}"
      dbInstance: "{{ oauth_profile.db_instance }}"
      issuer: "{{ oauth_profile.issuer }}"
      primaryKey: "{{ oauth_profile.primary_key }}"
      jwtToken: "{{ oauth_profile.jwt_token }}"
      opaqueToken: "{{ oauth_profile.opaque_token }}"
      jwtAccessTokenLifetime: "{{ oauth_profile.jwt_access_token_lifetime }}"
      jwtRefreshTokenLifetime: "{{ oauth_profile.jwt_refresh_token_lifetime }}"
      authUrl: "{{ oauth_profile.auth_url }}"
      tokenIssuanceUrl: "{{ oauth_profile.token_issuance_url }}"
      # ... additional fields ...
    status_code: [200, 201, 409]
```

**Critical Notes:**
- `dbInstance: "/Common/oauthdb"` - OAuth database MUST exist on BIG-IP
- `issuer` - Must match the URL clients will use to verify tokens
- `primaryKey` - References the JWK created earlier
- `jwtToken: "enabled"` - Use JWT format (not opaque tokens)
- Token lifetimes in seconds (120 = 2 minutes)

**Prerequisite:** OAuth database must exist:
```bash
# Check if oauthdb exists on BIG-IP
tmsh list apm oauth db-instance
```

**File:** `deploy_apm_oauth_as.yml` (lines 135-195)

---

### OAuth Authorization Agent

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/agent/oauth-authz

{
  "name": "{{VS_NAME}}-psp_act_oauth_authz_ag",
  "partition": "Common",
  "customizationGroup": "/Common/{{VS_NAME}}-psp_act_oauth_authz_ag",
  "promptForAuthorization": "false"
}
```

**Ansible:**
```yaml
# tasks/access_policy_solution8.yml
- name: Create OAuth authorization agent
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/policy/agent/oauth-authz"
    method: POST
    headers:
      X-F5-REST-Coordination-Id: "{{ trans_id }}"
    body:
      name: "{{ policy_agents.oauth_authz.name }}"
      partition: "{{ policy_agents.oauth_authz.partition }}"
      customizationGroup: "{{ policy_agents.oauth_authz.customization_group }}"
      promptForAuthorization: "{{ policy_agents.oauth_authz.prompt_for_authorization }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- `promptForAuthorization: "false"` - Auto-approve authorization (no consent screen)
- Set to `"true"` for user consent flow
- Requires `oauth-authz` type customization group
- Agent evaluates `session.oauth.authz.last.result` (1 = success)

**File:** `tasks/access_policy_solution8.yml` (lines 175-190)

---

### OAuth Authorization Policy Item

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/policy-item/

{
  "name": "{{VS_NAME}}-psp_act_oauth_authz",
  "partition": "Common",
  "caption": "OAuth Authorization",
  "color": 1,
  "itemType": "action",
  "loop": "false",
  "agents": [
    {
      "name": "{{VS_NAME}}-psp_act_oauth_authz_ag",
      "partition": "Common",
      "type": "oauth-authz"
    }
  ],
  "rules": [
    {
      "caption": "Successful",
      "expression": "expr {[mcget {session.oauth.authz.last.result}] == 1}",
      "nextItem": "/Common/{{VS_NAME}}-psp_end_allow"
    },
    {
      "caption": "fallback",
      "nextItem": "/Common/{{VS_NAME}}-psp_end_deny"
    }
  ]
}
```

**Ansible:**
```yaml
# tasks/access_policy_solution8.yml
- name: Create OAuth authorization policy item
  uri:
    body:
      name: "{{ policy_items.oauth_authz.name }}"
      partition: "{{ policy_items.oauth_authz.partition }}"
      caption: "{{ policy_items.oauth_authz.caption }}"
      color: "{{ policy_items.oauth_authz.color }}"
      itemType: "{{ policy_items.oauth_authz.item_type }}"
      loop: "{{ policy_items.oauth_authz.loop }}"
      agents:
        - name: "{{ policy_agents.oauth_authz.name }}"
          partition: "{{ policy_agents.oauth_authz.partition }}"
          type: "{{ policy_items.oauth_authz.agent_type }}"
      rules: "{{ policy_items.oauth_authz.rules }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- Agent type must be `oauth-authz` in agents array
- Result expression: `session.oauth.authz.last.result == 1` (success)
- On success → Allow ending (token issued)
- On failure → Deny ending (no token)

**File:** `tasks/access_policy_solution8.yml` (lines 234-256)

---

### Access Profile with OAuth Profile Reference

**CRITICAL:** Access profile MUST reference the OAuth profile via `oauthProfile` field.

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/profile/access/

{
  "name": "{{VS_NAME}}-psp",
  "partition": "Common",
  "accessPolicy": "/Common/{{VS_NAME}}-psp",
  "oauthProfile": "/Common/{{VS_NAME}}-oauth",
  "type": "all",
  ...
}
```

**Ansible:**
```yaml
# tasks/access_policy_solution8.yml
- name: Create access profile with OAuth profile
  uri:
    body:
      name: "{{ access_profile.name }}"
      partition: "{{ access_profile.partition }}"
      accessPolicy: "{{ access_profile.access_policy }}"
      oauthProfile: "{{ access_profile.oauth_profile }}"
      type: "{{ access_profile.type }}"
      # ... other fields ...
    status_code: [200, 201, 409]
```

**Critical Notes:**
- `oauthProfile` field links access profile to OAuth profile
- Without this reference, OAuth endpoints won't work
- OAuth profile must exist before creating access profile
- `type: "all"` allows both client-initiated and resource-server flows

**File:** `tasks/access_policy_solution8.yml` (lines 315-365)

---

### AD Query Agent with Extended Attributes

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/agent/aaa-active-directory

{
  "name": "{{VS_NAME}}-psp_act_active_directory_query_ag",
  "partition": "Common",
  "server": "/Common/{{VS_NAME}}-ad-servers",
  "type": "query",
  "queryFilter": "(sAMAccountName=%{session.logon.last.username})",
  "queryAttrname": [
    "cn", "displayName", "distinguishedName", "dn", "employeeID",
    "givenName", "homeMDB", "mail", "memberOf", "mobile",
    "msDS-ResultantPSO", "name", "objectGUID", "otherMobile", "pager",
    "primaryGroupID", "pwdLastSet", "sAMAccountName", "sn",
    "telephoneNumber", "userAccountControl", "userPrincipalName"
  ]
}
```

**Ansible:**
```yaml
# tasks/access_policy_solution8.yml
- name: Create AD query agent
  uri:
    body:
      name: "{{ policy_agents.ad_query.name }}"
      partition: "{{ policy_agents.ad_query.partition }}"
      server: "{{ policy_agents.ad_query.server }}"
      type: "{{ policy_agents.ad_query.type }}"
      queryFilter: "{{ policy_agents.ad_query.query_filter }}"
      queryAttrname: "{{ policy_agents.ad_query.query_attr_names }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- `type: "query"` - Query mode, not authentication
- Extensive attribute list for JWT token claims
- Attributes available in session: `session.ad.last.attr.<attrname>`
- Common for OAuth: `mail`, `sAMAccountName`, `memberOf`, `givenName`, `sn`

**File:** `tasks/access_policy_solution8.yml` (lines 150-175)

---

### Policy Flow Order

**CRITICAL:** Policy items must be created in specific order for proper flow.

**Order:**
1. Deny Ending (customization group + agent + policy item)
2. Allow Ending (agent + policy item)
3. OAuth Authorization (customization group + agent + policy item)
4. AD Query (agent + policy item)
5. AD Authentication (agent + policy item)
6. Logon Page (customization group + agent + policy item)
7. Start/Entry (policy item only)
8. Access Policy (references all items)
9. Access Profile (references policy + OAuth profile)

**Flow:**
```
Start → Logon Page → AD Auth → AD Query → OAuth Authz → Allow
           ↓           ↓          ↓           ↓
         Deny        Deny       Deny        Deny
```

---

### File Location Reference (Solution 8)

| Component | File Path |
|-----------|-----------|
| Solution 8 playbook | `deploy_apm_oauth_as.yml` |
| Solution 8 delete playbook | `delete_apm_oauth_as.yml` |
| Solution 8 variables | `vars/solution8.yml` |
| Access policy (Solution 8) | `tasks/access_policy_solution8.yml` |
| Solution 8 source | [solution8-create.postman_collection.json](https://github.com/f5devcentral/access-solutions/blob/master/solution8/postman/solution8-create.postman_collection.json) |

---

For usage examples and troubleshooting, see [README.md](../README.md)

---

## Solution 9: OAuth Resource Server Implementation Details

### Overview

Solution 9 deploys BIG-IP APM as an OAuth 2.0 Resource Server (Client) that validates OAuth tokens from an Authorization Server (Solution 8).

**IMPORTANT:** This implementation includes significant workarounds for API limitations discovered during development. The playbook defaults to **external/introspection mode** which does not require OIDC discovery.

**Key Components:**
- JWK Configuration (pre-shared key)
- OAuth Provider (connects to AS's OIDC endpoint)
- OAuth Client Application (client registration)
- Access Policy with OAuth Scope agent

**Optional Components (Internal Mode Only):**
- JWT Configuration (manual token validation config)
- JWT Provider List (links provider to JWT config)

---

### CRITICAL API LIMITATIONS AND WORKAROUNDS

#### 1. JWT Provider List Requires OIDC Discovery

**Problem:** The JWT provider list requires an internal linkage between the OAuth provider and JWT config that can ONLY be established through successful OIDC discovery.

**Error Messages:**
```
"01071ca0:3: When the manual flag is enabled, OAuth Provider must have manual JWT config attached"
"01071ca0:3: When the auto flag is enabled, OAuth Provider must have auto JWT config attached"
```

**What Does NOT Work:**

| Attempted Approach | Result |
|-------------------|--------|
| POST `jwtConfig` on OAuth provider | Property silently ignored |
| PATCH `jwtConfig` on OAuth provider | Returns "one or more properties must be specified" |
| POST `provider` on JWT config | Property silently ignored |
| Pre-creating `auto_jwt_<provider>` config | Internal linkage not established |
| `useAutoJwtConfig: "true"` without OIDC | `useAutoJwtConfig` stays false without successful discovery |

**Workaround:** Use **external/introspection mode** which doesn't require JWT provider list.

#### 2. useAutoJwtConfig Requires trustedCaBundle

**Problem:** Setting `useAutoJwtConfig: "true"` without `trustedCaBundle` fails.

**Error:**
```
"must have trusted CA present"
```

**Solution:** Set `trustedCaBundle: "/Common/ca-bundle.crt"` (built-in CA bundle).

#### 3. OAuth Scope Agent Configuration Varies by Mode

**External Mode:**
```yaml
body:
  oauthProvider: "/Common/solution9-provider"
  tokenValidationMode: "external"
```

**Internal Mode:**
```yaml
body:
  jwtProviderList: "/Common/solution9-list"
  tokenValidationMode: "internal"
```

---

### Token Validation Modes

| Mode | Description | Requirements | Use Case |
|------|-------------|--------------|----------|
| **External (default)** | Token introspection at runtime | OAuth AS reachable at runtime | Standard deployments |
| **Internal** | Local JWT validation | OIDC discovery successful | Air-gapped environments |

**Usage:**
```bash
# External mode (default)
ansible-playbook deploy_apm_oauth_rs.yml

# Internal mode
ansible-playbook deploy_apm_oauth_rs.yml -e token_validation_mode=internal
```

---

### OAuth Provider Configuration

**API Endpoint:** `POST /mgmt/tm/apm/aaa/oauth-provider`

**Postman (Original - relies on OIDC discovery):**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/aaa/oauth-provider

{
  "name": "{{VS_NAME}}-provider",
  "partition": "Common",
  "allowSelfSignedJwkCert": "yes",
  "discoveryInterval": 60,
  "ignoreExpiredCert": "true",
  "introspect": "supported",
  "maxJsonNestingLayers": 8,
  "maxResponseSize": 131072,
  "openidCfgUri": "https://{{AS_DNS}}/f5-oauth2/v1/.well-known/openid-configuration",
  "saveJsonPayload": "disabled",
  "type": "f5",
  "useAutoJwtConfig": "true"
}
```

**Ansible (with workarounds):**
```yaml
# deploy_apm_oauth_rs.yml
- name: Create OAuth provider
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/aaa/oauth-provider"
    method: POST
    body_format: json
    body:
      name: "{{ oauth_provider.name }}"
      partition: "{{ oauth_provider.partition }}"
      allowSelfSignedJwkCert: "{{ oauth_provider.allow_self_signed_jwk_cert }}"
      discoveryInterval: "{{ oauth_provider.discovery_interval }}"
      ignoreExpiredCert: "true"
      introspect: "{{ oauth_provider.introspect }}"
      openidCfgUri: "{{ oauth_provider.openid_cfg_uri }}"
      type: "{{ oauth_provider.type }}"
      trustedCaBundle: "/Common/ca-bundle.crt"  # REQUIRED for useAutoJwtConfig
      useAutoJwtConfig: "true"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- `trustedCaBundle: "/Common/ca-bundle.crt"` - REQUIRED when using `useAutoJwtConfig: "true"`
- `jwtConfig` property is NOT supported via API (silently ignored)
- `useAutoJwtConfig: "true"` only works if OIDC discovery succeeds
- For external mode, the JWT config linkage isn't needed
- `type: "f5"` for F5 OAuth AS, use `"custom"` for third-party AS

**File:** `deploy_apm_oauth_rs.yml`

---

### JWT Configuration (Manual)

When OIDC discovery fails, create a manual JWT configuration.

**API Endpoint:** `POST /mgmt/tm/apm/oauth/jwt-config`

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/oauth/jwt-config

{
  "name": "{{VS_NAME}}-jwt-config",
  "partition": "Common",
  "allowedKeys": ["/Common/{{VS_NAME}}-jwk"],
  "allowedClockSkew": 60,
  "issuer": "https://{{AS_DNS}}",
  "allowedSigningAlgorithms": ["HS256"]
}
```

**Ansible:**
```yaml
# deploy_apm_oauth_rs.yml
- name: Create JWT configuration
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/oauth/jwt-config"
    method: POST
    body_format: json
    body:
      name: "{{ vs1_name }}-jwt-config"
      partition: "Common"
      allowedKeys:
        - "/Common/{{ jwk_config.name }}"
      allowedClockSkew: 60
      issuer: "https://{{ oauth_as_dns }}"
      allowedSigningAlgorithms:
        - "HS256"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- `allowedKeys` must reference existing JWK configuration(s)
- `issuer` must match the OAuth AS's token issuer exactly
- `allowedSigningAlgorithms` must include algorithm used by AS
- `allowedClockSkew` in seconds (handles time drift)
- Create JWT config BEFORE OAuth provider and JWT provider list

**File:** `deploy_apm_oauth_rs.yml` (lines 137-158)

---

### JWK Configuration (Pre-shared Key)

**API Endpoint:** `POST /mgmt/tm/apm/oauth/jwk-config`

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/oauth/jwk-config

{
  "name": "{{VS_NAME}}-jwk",
  "partition": "Common",
  "algType": "HS256",
  "autoGenerated": "false",
  "includeX5c": "no",
  "keyId": "lab",
  "keyType": "octet",
  "keyUse": "signing",
  "sharedSecret": "secret",
  "sharedSecretEncFormat": "none",
  "useClientSecret": "false"
}
```

**Ansible:**
```yaml
# deploy_apm_oauth_rs.yml
- name: Create JWK configuration
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/oauth/jwk-config"
    method: POST
    body_format: json
    body:
      name: "{{ jwk_config.name }}"
      partition: "{{ jwk_config.partition }}"
      algType: "{{ jwk_config.alg_type }}"
      autoGenerated: "{{ jwk_config.auto_generated }}"
      includeX5c: "{{ jwk_config.include_x5c }}"
      keyId: "{{ jwk_config.key_id }}"
      keyType: "{{ jwk_config.key_type }}"
      keyUse: "{{ jwk_config.key_use }}"
      sharedSecret: "{{ jwk_config.shared_secret }}"
      sharedSecretEncFormat: "{{ jwk_config.shared_secret_enc_format }}"
      useClientSecret: "{{ jwk_config.use_client_secret }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- `keyType: "octet"` for symmetric keys (HS256)
- `sharedSecret` MUST match the AS's JWK shared secret exactly
- `keyId` should match the AS's key ID
- Create JWK BEFORE JWT config (JWT config references JWK)

**File:** `deploy_apm_oauth_rs.yml` (lines 100-124)

---

### JWT Provider List

Links OAuth provider with JWT configuration for token validation.

**API Endpoint:** `POST /mgmt/tm/apm/oauth/jwt-provider-list`

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/oauth/jwt-provider-list

{
  "name": "{{VS_NAME}}-list",
  "partition": "Common",
  "accessTokenExpiresIn": 0,
  "providers": ["/Common/{{VS_NAME}}-provider"]
}
```

**Ansible:**
```yaml
# deploy_apm_oauth_rs.yml
- name: Create JWT provider list
  uri:
    url: "https://{{ bigip_mgmt }}:{{ bigip_port }}/mgmt/tm/apm/oauth/jwt-provider-list"
    method: POST
    body_format: json
    body:
      name: "{{ jwt_provider_list.name }}"
      partition: "{{ jwt_provider_list.partition }}"
      accessTokenExpiresIn: "{{ jwt_provider_list.access_token_expires_in }}"
      providers: "{{ jwt_provider_list.providers }}"
    status_code: [200, 201, 409]
```

**Critical Notes:**
- Requires OAuth provider to have manual JWT config attached
- Error message if JWT config not attached: "When the manual flag is enabled, OAuth Provider must have manual JWT config attached"
- `accessTokenExpiresIn: 0` means no override (use token's exp claim)
- Create AFTER OAuth provider has JWT config attached

**File:** `deploy_apm_oauth_rs.yml` (lines 220-235)

---

### OAuth Scope Agent

Validates OAuth tokens in the access policy. Configuration differs by token validation mode.

**API Endpoint:** `POST /mgmt/tm/apm/policy/agent/aaa-oauth`

**Postman (Internal Mode - requires OIDC discovery):**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/agent/aaa-oauth

{
  "name": "{{VS_NAME}}-psp_act_oauth_scope_ag",
  "partition": "Common",
  "grantType": "authorization-code",
  "jwtProviderList": "/Common/{{VS_NAME}}-list",
  "openidConnect": "enabled",
  "openidFlowType": "code",
  "redirectionUri": "https://%{session.server.network.name}/oauth/client/redirect",
  "tokenValidationMode": "internal",
  "type": "scope"
}
```

**Ansible (External Mode - default, no OIDC required):**
```yaml
# tasks/access_policy_solution9.yml
- name: Create OAuth scope agent (external/introspection mode)
  uri:
    body:
      name: "{{ policy_agents.oauth_scope.name }}"
      partition: "{{ policy_agents.oauth_scope.partition }}"
      grantType: "{{ policy_agents.oauth_scope.grant_type }}"
      oauthProvider: "{{ policy_agents.oauth_scope.oauth_provider }}"  # NOT jwtProviderList
      openidConnect: "{{ policy_agents.oauth_scope.openid_connect }}"
      openidFlowType: "{{ policy_agents.oauth_scope.openid_flow_type }}"
      redirectionUri: "{{ policy_agents.oauth_scope.redirection_uri }}"
      tokenValidationMode: "external"  # Introspection mode
      type: "{{ policy_agents.oauth_scope.type }}"
    status_code: [200, 201, 409]
  when: token_validation_mode == "external"
```

**Ansible (Internal Mode - requires OIDC discovery):**
```yaml
- name: Create OAuth scope agent (internal/JWT mode)
  uri:
    body:
      name: "{{ policy_agents.oauth_scope.name }}"
      partition: "{{ policy_agents.oauth_scope.partition }}"
      grantType: "{{ policy_agents.oauth_scope.grant_type }}"
      jwtProviderList: "{{ policy_agents.oauth_scope.jwt_provider_list }}"  # NOT oauthProvider
      openidConnect: "{{ policy_agents.oauth_scope.openid_connect }}"
      openidFlowType: "{{ policy_agents.oauth_scope.openid_flow_type }}"
      redirectionUri: "{{ policy_agents.oauth_scope.redirection_uri }}"
      tokenValidationMode: "internal"  # JWT validation mode
      type: "{{ policy_agents.oauth_scope.type }}"
    status_code: [200, 201, 409]
  when: token_validation_mode == "internal"
```

**Critical Notes:**
- `type: "scope"` - For token validation (Resource Server mode)
- **External mode:** Use `oauthProvider` reference, validates via introspection
- **Internal mode:** Use `jwtProviderList` reference, validates JWT locally
- Do NOT mix `oauthProvider` and `jwtProviderList` - use one or the other
- Agent result: `session.oauth.scope.last.authresult` (1 = success)

**File:** `tasks/access_policy_solution9.yml`

---

### OAuth Scope Policy Item

**API Endpoint:** `POST /mgmt/tm/apm/policy/policy-item/`

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/policy-item/

{
  "name": "{{VS_NAME}}-psp_act_oauth_scope",
  "partition": "Common",
  "caption": "OAuth Scope",
  "color": 1,
  "itemType": "action",
  "loop": "false",
  "agents": [
    {
      "name": "{{VS_NAME}}-psp_act_oauth_scope_ag",
      "partition": "Common",
      "type": "aaa-oauth"
    }
  ],
  "rules": [
    {
      "caption": "Successful",
      "expression": "expr {[mcget {session.oauth.scope.last.authresult}] == 1}",
      "nextItem": "/Common/{{VS_NAME}}-psp_end_allow"
    },
    {
      "caption": "fallback",
      "nextItem": "/Common/{{VS_NAME}}-psp_end_deny"
    }
  ]
}
```

**Critical Notes:**
- Agent type must be `aaa-oauth` in agents array
- Result expression: `session.oauth.scope.last.authresult == 1` (valid token)
- On success → Allow ending (access granted)
- On failure → Deny ending (invalid/expired token)

**File:** `tasks/access_policy_solution9.yml`

---

### Component Creation Order

**CRITICAL:** Components must be created in specific order due to dependencies.

**Order:**
1. CA Certificate (upload and install)
2. JWK Configuration (pre-shared key)
3. JWT Configuration (references JWK)
4. OAuth Provider (references JWT config, `useAutoJwtConfig: false`)
5. JWT Provider List (references OAuth provider)
6. OAuth Client Application (optional for client flows)
7. Customization Groups (policy UI)
8. Policy Agents (endings, OAuth scope)
9. Policy Items (link agents to policy flow)
10. Access Policy (references all items)
11. Access Profile (references access policy)
12. AS3 Application (virtual server with access profile)

**Dependency Flow:**
```
JWK → JWT Config → OAuth Provider → JWT Provider List
                                          ↓
                               OAuth Scope Agent
                                          ↓
                            Policy Item → Access Policy
```

---

### Troubleshooting

**Error:** "When the manual flag is enabled, OAuth Provider must have manual JWT config attached"

**Cause:** JWT provider list created before OAuth provider has `jwtConfig` attached.

**Solution:**
1. Create JWK configuration first
2. Create JWT configuration (references JWK)
3. Create OAuth provider with `useAutoJwtConfig: "false"` AND `jwtConfig: "/Common/<jwt-config-name>"`
4. Then create JWT provider list

---

**Error:** "When use auto JWT config is enabled, OAuth Provider must have trusted CA present"

**Cause:** Trying to use `useAutoJwtConfig: "true"` without a trusted CA bundle.

**Solution:**
- Either set `useAutoJwtConfig: "false"` and provide manual JWT config
- Or configure `trustedCaBundle` with a valid CA bundle reference

---

### File Location Reference (Solution 9)

| Component | File Path |
|-----------|-----------|
| Solution 9 playbook | `deploy_apm_oauth_rs.yml` |
| Solution 9 delete playbook | `delete_apm_oauth_rs.yml` |
| Solution 9 variables | `vars/solution9.yml` |
| Access policy (Solution 9) | `tasks/access_policy_solution9.yml` |
| Solution 9 source | [solution9-create.postman_collection.json](https://github.com/f5devcentral/access-solutions/blob/master/solution9/postman/solution9-create.postman_collection.json) |

---

## Solution 10: OAuth Authorization Server with RS256 Implementation Details

Solution 10 implements an OAuth Authorization Server using RS256 (RSA with SHA-256) asymmetric key signing, unlike Solution 8 which uses HS256 symmetric signing.

### Key Differences from Solution 8 (HS256)

| Feature | Solution 8 (HS256) | Solution 10 (RS256) |
|---------|-------------------|---------------------|
| Algorithm | Symmetric (shared secret) | Asymmetric (RSA key pair) |
| JWK Configuration | `algType: "HS256"`, shared secret | `algType: "RS256"`, certificate + key references |
| Token Verification | Requires shared secret | Uses public key from JWKS endpoint |
| Certificate Required | No | Yes (self-signed or imported) |
| JWKS Response | Returns shared secret info | Returns RSA public key (modulus, exponent) |

### Self-Signed Certificate Workflow

For DEMO/LAB environments, Solution 10 can auto-generate a self-signed certificate:

```yaml
# vars/solution10.yml
use_self_signed_cert: true  # Enable auto-generation
```

**Certificate Generation Flow:**

1. **Generate locally:** OpenSSL creates RSA 2048-bit key pair
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout /tmp/{cert_name}.key \
     -out /tmp/{cert_name}.crt \
     -subj "/C=US/ST=State/L=City/O=Organization/CN={dns_name}"
   ```

2. **Upload to BIG-IP:** Files transferred via REST API
   ```http
   POST /mgmt/shared/file-transfer/uploads/{cert_name}.key
   POST /mgmt/shared/file-transfer/uploads/{cert_name}.crt
   ```

3. **Install key first:** Private key must be installed before certificate
   ```http
   POST /mgmt/tm/sys/crypto/key
   {
     "name": "{cert_name}",
     "partition": "Common",
     "sourcePath": "file:/var/config/rest/downloads/{cert_name}.key"
   }
   ```

4. **Install certificate:** With key association
   ```http
   POST /mgmt/tm/sys/crypto/cert
   {
     "name": "{cert_name}",
     "partition": "Common",
     "commonName": "{dns_name}",
     "sourcePath": "file:/var/config/rest/downloads/{cert_name}.crt",
     "key": "/Common/{cert_name}"
   }
   ```

> **WARNING:** Self-signed certificates should NOT be used in production. For production deployments, import a proper certificate from your organization's CA.

### JWK Configuration for RS256

Unlike HS256 which uses a shared secret, RS256 requires certificate references:

**Postman:**
```json
{
  "name": "{{vs1_name}}-jwk",
  "algType": "RS256",
  "keyType": "rsa",
  "keyUse": "signing",
  "cert": "/Common/{{wildcard_cert_name}}",
  "certChain": "/Common/{{ca_cert_name}}",
  "certKey": "/Common/{{wildcard_cert_name}}",
  "includeX5c": "no",
  "passphrase": "{{cert_passphrase}}"
}
```

**Ansible (with conditional cert chain):**
```yaml
# For pre-imported certificates (with CA chain)
- name: Build JWK config body (with cert chain)
  set_fact:
    jwk_body:
      name: "{{ jwk_config.name }}"
      algType: "RS256"
      keyType: "rsa"
      cert: "/Common/{{ wildcard_cert.name }}"
      certChain: "/Common/{{ ca_cert.name }}"
      certKey: "/Common/{{ wildcard_cert.name }}"
      # ... other fields
  when: not use_self_signed_cert

# For self-signed certificates (no CA chain)
- name: Build JWK config body (self-signed)
  set_fact:
    jwk_body:
      name: "{{ jwk_config.name }}"
      algType: "RS256"
      keyType: "rsa"
      cert: "/Common/{{ wildcard_cert.name }}"
      certKey: "/Common/{{ wildcard_cert.name }}"
      # NO certChain for self-signed
  when: use_self_signed_cert
```

**Critical:** Self-signed certificates do NOT have a CA chain. Including `certChain` with a mismatched CA will cause:
```
01071ca4:3: Invalid certificate order within cert-chain (/Common/ca.acme.com)
associated to JWK config (/Common/as-rsa-jwk)
```

### Certificate Prerequisites

| Mode | Prerequisites | Configuration |
|------|---------------|---------------|
| Self-Signed | None (auto-generated) | `use_self_signed_cert: true` |
| Pre-Imported | Certificate + Key imported to BIG-IP | `use_self_signed_cert: false` |

**Importing Certificates to BIG-IP (for production):**

Via GUI:
- System > Certificate Management > Traffic Certificate Management > SSL Certificate List
- Import both certificate and private key

Via API:
```http
# Upload and install key
POST /mgmt/shared/file-transfer/uploads/mycert.key
POST /mgmt/tm/sys/crypto/key
{
  "name": "mycert",
  "sourcePath": "file:/var/config/rest/downloads/mycert.key"
}

# Upload and install certificate
POST /mgmt/shared/file-transfer/uploads/mycert.crt
POST /mgmt/tm/sys/crypto/cert
{
  "name": "mycert",
  "commonName": "*.example.com",
  "sourcePath": "file:/var/config/rest/downloads/mycert.crt",
  "key": "/Common/mycert"
}
```

### OAuth Profile with RS256 Primary Key

The OAuth profile references the RS256 JWK for token signing:

```yaml
oauth_profile:
  name: "{{ vs1_name }}-oauth"
  primaryKey: "/Common/{{ jwk_config.name }}"        # JWK for access tokens
  idTokenPrimaryKey: "/Common/{{ jwk_config.name }}" # JWK for ID tokens
  jwtToken: "enabled"
  opaqueToken: "disabled"
```

### JWKS Endpoint Response

When RS256 is configured, the `/f5-oauth2/v1/jwks` endpoint returns RSA public key components:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "lab",
      "n": "rQRpUpNgVvYWwm6x...",  // RSA modulus (base64url)
      "e": "AQAB"                    // RSA public exponent (base64url)
    }
  ]
}
```

OAuth clients can use this public key to verify JWT tokens without needing a shared secret.

### AS3 Declaration with TLS

Solution 10 uses AS3 TLS_Server and Certificate classes for proper HTTPS configuration:

```yaml
# Build TLS certificate reference
tls_cert_config:
  class: "Certificate"
  certificate:
    bigip: "/Common/{{ wildcard_cert.name }}"
  privateKey:
    bigip: "/Common/{{ wildcard_cert.name }}"

# Build TLS server profile
tls_server_config:
  class: "TLS_Server"
  certificates:
    - certificate: "tlsserver_local_cert"

# Build virtual server with TLS
vs_config:
  class: "Service_HTTPS"
  virtualAddresses:
    - "{{ as3_config.virtual_address }}"
  virtualPort: 443
  serverTLS: "{{ vs1_name }}-clientssl"
  profileAccess:
    bigip: "/Common/{{ access_profile.name }}"
```

### Common Errors and Solutions

---

**Error:** `File object by name (/Common/cert-name) is missing`

**Cause:** Certificate not properly installed on BIG-IP.

**Solution:**
1. Verify key was installed first: `GET /mgmt/tm/sys/crypto/key/~Common~{cert_name}`
2. Verify certificate exists: `GET /mgmt/tm/sys/crypto/cert/~Common~{cert_name}`
3. Check installation used `sourcePath` not `from-local-file`

---

**Error:** `Invalid certificate order within cert-chain`

**Cause:** Self-signed certificate configured with a CA chain reference.

**Solution:** Do not include `certChain` when using self-signed certificates:
```yaml
# WRONG for self-signed
certChain: "/Common/ca.acme.com"

# CORRECT for self-signed
# (omit certChain entirely)
```

---

**Error:** `servicePort: should be integer`

**Cause:** AS3 pool member servicePort passed as string instead of integer.

**Solution:** Use literal integer, not Jinja2 expression:
```yaml
# WRONG
servicePort: "{{ port | int }}"

# CORRECT
servicePort: 80
```

---

### File Location Reference (Solution 10)

| Component | File Path |
|-----------|-----------|
| Solution 10 playbook | `deploy_apm_oauth_as_rsa.yml` |
| Solution 10 delete playbook | `delete_apm_oauth_as_rsa.yml` |
| Solution 10 variables | `vars/solution10.yml` |
| Access policy (Solution 10) | `tasks/access_policy_solution10.yml` |
| Self-signed cert generation | `tasks/create_self_signed_cert_oauth.yml` |
| Solution 10 source | [solution10-create.postman_collection.json](https://github.com/f5devcentral/access-solutions/blob/master/solution10/postman/solution10-create.postman_collection.json) |

---

## Solution 11: OAuth Client with OIDC Integration

Solution 11 implements an OAuth Client (Relying Party) that authenticates users via an external OAuth Authorization Server using OIDC (OpenID Connect).

### Solution 11 Critical Implementation Details

#### Dependency on OAuth Authorization Server

Solution 11 **requires** Solution 8 or Solution 10 (OAuth Authorization Server) to be deployed first. The OAuth Client will:
1. Connect to the AS's OIDC discovery endpoint
2. Register as a client on the AS's OAuth profile
3. Redirect users to the AS for authentication

#### OIDC Discovery vs Manual Endpoint Configuration

**Problem:** In many lab environments, the BIG-IP control plane cannot reach virtual server IPs due to network isolation. OIDC discovery fails with:
```
java.net.SocketTimeoutException: connect timed out
```

**Solution:** The playbook supports two modes:

| Mode | Configuration | Description |
|------|---------------|-------------|
| Manual Endpoints (default) | `skip_discovery: true` | Configure endpoints manually; works in isolated labs |
| Auto Discovery | `skip_discovery: false` | Use OIDC discovery; requires network connectivity |

**Manual Endpoint Configuration:**
```yaml
# vars/solution11.yml
oauth_as:
  skip_discovery: true  # Default for lab environments
  manual_endpoints:
    authorization_uri: "https://{{ as_virtual_address }}/f5-oauth2/v1/authorize"
    token_uri: "https://{{ as_virtual_address }}/f5-oauth2/v1/token"
    userinfo_uri: "https://{{ as_virtual_address }}/f5-oauth2/v1/userinfo"
    token_validation_scope_uri: "https://{{ as_virtual_address }}/f5-oauth2/v1/introspect"
    jwks_uri: "https://{{ as_virtual_address }}/f5-oauth2/v1/jwks"
```

### OAuth Provider (AAA) Configuration

The OAuth Provider AAA object connects the client to the Authorization Server:

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/aaa/oauth-provider
Content-Type: application/json

{
  "name": "oauth-client-provider",
  "partition": "Common",
  "allowSelfSignedJwkCert": "yes",
  "discoveryInterval": 60,
  "ignoreExpiredCert": "false",
  "introspect": "supported",
  "maxJsonNestingLayers": 8,
  "maxResponseSize": 131072,
  "openidCfgUri": "https://10.1.10.110/f5-oauth2/v1/.well-known/openid-configuration",
  "saveJsonPayload": "disabled",
  "trustedCaBundle": "/Common/ca.acme.com",
  "type": "f5",
  "useAutoJwtConfig": "false",
  "authenticationUri": "https://10.1.10.110/f5-oauth2/v1/authorize",
  "tokenUri": "https://10.1.10.110/f5-oauth2/v1/token",
  "tokenValidationScopeUri": "https://10.1.10.110/f5-oauth2/v1/introspect",
  "userinfoRequestUri": "https://10.1.10.110/f5-oauth2/v1/userinfo",
  "jwksUri": "https://10.1.10.110/f5-oauth2/v1/jwks"
}
```

**Key Parameters:**
- `useAutoJwtConfig: "false"` - Required when using manual endpoints
- `useAutoJwtConfig: "true"` - Required when using OIDC discovery
- `trustedCaBundle` - CA certificate that signed the AS's SSL certificate
- `allowSelfSignedJwkCert: "yes"` - Allow self-signed JWK certificates (lab only)

### OAuth Client App Registration

The OAuth Client App defines the client application and generates credentials:

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/oauth/oauth-client-app
Content-Type: application/json

{
  "name": "oauth-client",
  "partition": "Common",
  "appName": "oauth-client",
  "authType": "secret",
  "grantCode": "enabled",
  "grantPassword": "disabled",
  "grantToken": "disabled",
  "openidConnect": "enabled",
  "redirectUris": ["https://oauth-client.acme.com/oauth/client/redirect"],
  "accessTokenLifetime": 5,
  "authCodeLifetime": 5,
  "idTokenLifetime": 5,
  "refreshTokenLifetime": 480,
  "generateRefreshToken": "true",
  "generateJwtRefreshToken": "true",
  "customizationGroup": "/Common/oauth-client_oauth_authz_client_app_customization"
}
```

**Response (includes auto-generated credentials):**
```json
{
  "name": "oauth-client",
  "clientId": "b99b2f2d3dcbe79f0ac2369f13010617cc0373612fe83069",
  "clientSecret": "5fa9430c4cbed813b8fc2281c10a17b8d7e895dfbe690617cc0373612fe83069"
}
```

### Register Client with Authorization Server

After creating the OAuth Client App, register it with the Authorization Server's OAuth profile:

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/profile/oauth/~Common~as-rsa-oauth/client-apps
Content-Type: application/json

{
  "name": "oauth-client",
  "partition": "solution11"
}
```

**Then apply the AS policy:**
```http
PATCH https://{{BIGIP_MGMT}}/mgmt/tm/apm/profile/access/~Common~as-rsa-psp
Content-Type: application/json

{
  "generationAction": "increment"
}
```

### OAuth Server (Client Mode)

The OAuth Server AAA object in client mode handles token exchange:

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/aaa/oauth-server
Content-Type: application/json

{
  "name": "oauth-client",
  "partition": "Common",
  "mode": "client",
  "clientId": "b99b2f2d3dcbe79f0ac2369f13010617cc0373612fe83069",
  "clientSecret": "5fa9430c4cbed813b8fc2281c10a17b8d7e895dfbe690617cc0373612fe83069",
  "clientServersslProfileName": "/Common/serverssl",
  "dnsResolverName": "/Common/oauth-client-dns",
  "providerName": "/Common/oauth-client-provider",
  "tokenValidationInterval": 60
}
```

**Key Parameters:**
- `mode: "client"` - Operates as OAuth Client (not Authorization Server)
- `clientId` / `clientSecret` - Auto-generated from OAuth Client App
- `providerName` - References the OAuth Provider AAA object
- `dnsResolverName` - DNS resolver for endpoint resolution

### Access Policy (Solution 11)

Simple policy flow: Start → OAuth Client → Allow/Deny

**OAuth Client Agent:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/agent/aaa-oauth/
Content-Type: application/json
X-F5-REST-Coordination-Id: {transaction_id}

{
  "name": "oauth-client-psp_act_oauth_client_ag",
  "partition": "Common",
  "authRedirectRequest": "/Common/F5AuthRedirectRequestJWT",
  "grantType": "authorization-code",
  "openidConnect": "enabled",
  "openidFlowType": "code",
  "openidHybridResponseType": "code-idtoken",
  "openidUserinfoRequest": "/Common/F5UserinfoRequest",
  "redirectionUri": "https://%{session.server.network.name}/oauth/client/redirect",
  "server": "/Common/oauth-client",
  "tokenRefreshRequest": "/Common/F5TokenRefreshRequest",
  "tokenRequest": "/Common/F5TokenJWTRequestByAuthzCode",
  "tokenValidationMode": "external",
  "type": "client"
}
```

**OAuth Client Policy Item:**
```yaml
rules:
  - caption: "Successful"
    expression: "expr {[mcget {session.oauth.client.last.authresult}] == 1}"
    nextItem: "/Common/oauth-client-psp_end_allow"
  - caption: "fallback"
    nextItem: "/Common/oauth-client-psp_end_deny"
```

### Ansible-Specific Implementation Notes

#### Avoiding `.items` Dict Method Collision

When looping over API responses that contain an `items` key, Ansible interprets `.items` as the dictionary method instead of the key. Use bracket notation:

```yaml
# WRONG - Ansible interprets as dict.items() method
loop: "{{ existing_clients.json.items | default([]) }}"

# CORRECT - Explicitly access the 'items' key
- name: Store existing clients list
  set_fact:
    existing_clients_list: "{{ existing_clients.json['items'] | default([]) }}"

- name: Extract existing client credentials
  set_fact:
    client_id: "{{ item.clientId }}"
  loop: "{{ existing_clients_list | default([]) }}"
```

This pattern is used for:
- OIDC discovery task listings
- OAuth client app retrieval
- Any API endpoint returning `{ "items": [...] }`

### Common Errors and Solutions

---

**Error:** `java.net.SocketTimeoutException: connect timed out` during OIDC discovery

**Cause:** BIG-IP control plane cannot reach the OAuth AS virtual server IP.

**Solution:** Set `skip_discovery: true` and configure endpoints manually:
```yaml
oauth_as:
  skip_discovery: true
  manual_endpoints:
    authorization_uri: "https://{{ as_virtual_address }}/f5-oauth2/v1/authorize"
    # ... other endpoints
```

---

**Error:** `'bigip_mgmt' is undefined`

**Cause:** Missing BIG-IP connection variables in vars file.

**Solution:** Add to vars/solution11.yml:
```yaml
bigip_mgmt: "{{ ansible_host }}"
bigip_username: "{{ bigip_user }}"
bigip_password: "{{ bigip_pass }}"
bigip_port: 443
validate_certs: no
```

---

**Error:** `Invalid data passed to 'loop', it requires a list, got this instead: <built-in method items of dict object>`

**Cause:** Using `.items` which Ansible interprets as dict method.

**Solution:** Use bracket notation: `json['items']` instead of `json.items`

---

**Error:** `Unable to find /Common/cert-name for certificate`

**Cause:** Wildcard certificate not installed on BIG-IP.

**Solution:** Set `use_self_signed: true` to auto-generate certificate:
```yaml
wildcard_cert:
  name: "oauth-client-cert"
  use_self_signed: true
  common_name: "oauth-client.acme.com"
```

---

### File Location Reference (Solution 11)

| Component | File Path |
|-----------|-----------|
| Solution 11 playbook | `deploy_apm_oauth_client.yml` |
| Solution 11 delete playbook | `delete_apm_oauth_client.yml` |
| Solution 11 variables | `vars/solution11.yml` |
| Access policy (Solution 11) | `tasks/access_policy_solution11.yml` |
| Self-signed cert generation | `tasks/create_self_signed_cert_oauth.yml` |
| Solution 11 source | [solution11-create.postman_collection.json](https://github.com/f5devcentral/access-solutions/blob/master/solution11/postman/solution11-create.postman_collection.json) |

---

## Solution 12: Remote Desktop Gateway (RDG) with AD Authentication

Solution 12 implements HTML5-based Remote Desktop access through BIG-IP APM with Active Directory authentication.

### Solution 12 Key Components

| Component | Purpose |
|-----------|---------|
| RDP Resource | Remote Desktop connection to backend RDP server |
| RDG Profile | Access profile with rdg-rap type for RD Gateway |
| PSP Profile | Main access policy with AD authentication |
| VDI Profile | Virtual Desktop Infrastructure profile |
| Connectivity Profile | PPP tunnel for VDI connections |
| Webtop | Full webtop for presenting RDP resources |
| Variable Assignment | Domain SSO via session variable |

### Solution 12 Two-Policy Architecture

Solution 12 requires TWO access policies:

1. **RDG Policy (rdg-rap type)** - Simple allow policy for RD Gateway traffic
2. **PSP Policy (all type)** - Main authentication policy with AD auth flow

**Why Two Policies?**
- The RDG policy handles Remote Desktop Gateway protocol traffic
- The PSP policy handles user authentication and resource assignment
- The PSP policy assigns the RDG policy via resource-assign agent

### RDP Resource Creation

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/resource/remote-desktop/rdp
Content-Type: application/json

{
  "name": "solution12-vdi-resource",
  "partition": "Common",
  "ip": "10.1.20.6",
  "port": 3389,
  "autoLogon": "enabled",
  "serverType": "rdsh",
  "enableServersideSsl": "disabled",
  "locationSpecific": "true",
  "userDefinedDst": "disabled",
  "usernameSource": "session.logon.last.username",
  "passwordSource": "session.logon.last.password",
  "domainSource": "session.logon.last.domain"
}
```

**Key Parameters:**
- `serverType: "rdsh"` - RD Session Host (or "rdp" for standard RDP)
- `autoLogon: "enabled"` - Enable SSO to RDP server
- `usernameSource/passwordSource/domainSource` - Session variables for SSO

### VDI Profile Creation

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/profile/vdi/
Content-Type: application/json

{
  "name": "solution12-vdi",
  "partition": "Common",
  "defaultsFrom": "/Common/vdi",
  "vmwareViewUdpTransport": "pcoip"
}
```

### PPP Tunnel Creation

Required for connectivity profile:

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/net/tunnels/tunnel
Content-Type: application/json

{
  "name": "solution12-tunnel",
  "partition": "Common",
  "profile": "/Common/ppp",
  "autoLasthop": "default",
  "idleTimeout": 300,
  "localAddress": "any6",
  "mode": "bidirectional",
  "remoteAddress": "any6",
  "tos": "preserve",
  "usePmtu": "enabled"
}
```

### Connectivity Profile Creation

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/profile/connectivity/
Content-Type: application/json

{
  "name": "solution12-cp",
  "partition": "Common",
  "defaultsFrom": "/Common/connectivity",
  "customizationGroup": "/Common/solution12_secure_access_client_customization",
  "tunnelName": "/Common/solution12-tunnel"
}
```

### RDG Access Profile (rdg-rap type)

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/profile/access
Content-Type: application/json
X-F5-REST-Coordination-Id: {transaction_id}

{
  "name": "solution12-rdg",
  "partition": "Common",
  "type": "rdg-rap",
  "defaultLanguage": "en",
  "acceptLanguages": ["en"],
  "accessPolicyTimeout": 300,
  "inactivityTimeout": 900,
  "maxSessionTimeout": 604800,
  "logSettings": ["/Common/default-log-setting"]
}
```

**Key Point:** `type: "rdg-rap"` is critical for RD Gateway functionality.

### Variable Assignment for Domain SSO

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/agent/variable-assign/
Content-Type: application/json
X-F5-REST-Coordination-Id: {transaction_id}

{
  "name": "solution12-psp_act_variable_assign_ag",
  "partition": "Common",
  "variables": [{
    "append": "false",
    "expression": "return {F5LAB.LOCAL}",
    "secure": "false",
    "varname": "session.logon.last.domain"
  }]
}
```

**Purpose:** Sets the domain for RDP SSO from the session variable.

### RDG Policy Assignment (Resource Assign Agent)

The PSP policy assigns the RDG policy via a resource-assign agent:

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/agent/resource-assign/
Content-Type: application/json
X-F5-REST-Coordination-Id: {transaction_id}

{
  "name": "solution12-psp_act_rdg_policy_assign_ag",
  "partition": "Common",
  "type": "rdg-policy",
  "rdgPolicy": {
    "name": "/Common/solution12-rdg"
  }
}
```

**Key:** `type: "rdg-policy"` with `rdgPolicy` reference.

### Full Resource Assignment

**Postman:**
```http
POST https://{{BIGIP_MGMT}}/mgmt/tm/apm/policy/agent/resource-assign/
Content-Type: application/json
X-F5-REST-Coordination-Id: {transaction_id}

{
  "name": "solution12-psp_act_full_resource_assign_ag",
  "partition": "Common",
  "type": "general-item",
  "rdpResourceAssign": [{
    "name": "/Common/solution12-vdi-resource",
    "type": "rdp"
  }],
  "webtopAssign": {
    "name": "/Common/solution12-webtop",
    "type": "webtop"
  }
}
```

### Virtual Server Profile Attachment

AS3 does not support VDI profiles, so profiles must be added via PATCH after AS3 deployment:

**Postman:**
```http
PATCH https://{{BIGIP_MGMT}}/mgmt/tm/ltm/virtual/~solution12~solution12~solution12
Content-Type: application/json

{
  "profiles": [
    {"name": "/Common/solution12-psp", "context": "all"},
    {"name": "/Common/solution12-cp", "context": "all"},
    {"name": "/Common/solution12-vdi", "context": "all"},
    {"name": "solution12-clientssl", "context": "clientside"},
    {"name": "/Common/serverssl", "context": "serverside"},
    {"name": "/Common/http", "context": "all"},
    {"name": "/Common/tcp", "context": "all"},
    {"name": "/Common/websocket", "context": "all"}
  ]
}
```

**Required Profiles:**
- `solution12-psp` - Access (PSP) profile
- `solution12-cp` - Connectivity profile
- `solution12-vdi` - VDI profile
- `clientssl` - TLS client-side
- `serverssl` - TLS server-side (required for RDP resource)
- `websocket` - For HTML5 RDP transport

### Solution 12 Critical Implementation Details

#### Profile Creation Order
1. Create connectivity customization group
2. Create PPP tunnel
3. Create connectivity profile
4. Create VDI profile
5. Create access policies (RDG and PSP)
6. Deploy AS3 (without APM profiles)
7. PATCH virtual server to add all profiles

#### AS3 Limitation
AS3 does not support `profileVDI` or `profileConnectivity`. The virtual server must be created without these profiles, then patched via REST API.

#### Serverssl Requirement
The virtual server requires a serverssl profile when VDI profile is attached with RDP resources, even if `enableServersideSsl: "disabled"` on the RDP resource.

---

### File Location Reference (Solution 12)

| Component | File Path |
|-----------|-----------|
| Solution 12 playbook | `deploy_apm_rdg.yml` |
| Solution 12 delete playbook | `delete_apm_rdg.yml` |
| Solution 12 variables | `vars/solution12.yml` |
| Access policy (Solution 12) | `tasks/access_policy_solution12.yml` |
| Solution 12 source | [solution12-create.postman_collection.json](https://github.com/f5devcentral/access-solutions/blob/master/solution12/postman/solution12-create.postman_collection.json) |

---

