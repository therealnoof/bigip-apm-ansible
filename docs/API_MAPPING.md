## Postman to Ansible API Mapping

Detailed mapping of Postman REST API calls to Ansible tasks.

## Overview

| Metric | Count |
|--------|-------|
| Total Postman Requests | 80+ |
| Converted to Ansible | 70+ |
| Initialization/Check Requests | 6 |
| AAA AD Configuration | 3 |
| SAML Configuration (Solutions 3 & 4) | 8 |
| Connectivity Profile | 3 |
| Network Access | 3 |
| Webtop | 4 |
| Portal Resources (Solution 2) | 5 |
| Access Policy (with transaction) | 25+ |
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

---

For usage examples and troubleshooting, see [README.md](../README.md)
