## Postman to Ansible API Mapping

Detailed mapping of Postman REST API calls to Ansible tasks.

## Overview

| Metric | Count |
|--------|-------|
| Total Postman Requests | 60 |
| Converted to Ansible | 54 |
| Initialization/Check Requests | 6 |
| AAA AD Configuration | 3 |
| Connectivity Profile | 3 |
| Network Access | 3 |
| Webtop | 4 |
| Access Policy (with transaction) | 21 |
| AS3 Deployment | 4 |
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

### 2. Connectivity Profile

#### 2.1 Create PPP Tunnel

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

#### 2.2 Create Customization Group

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

#### 2.3 Create Connectivity Profile

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

### 3. Network Access Resource

#### 3.1 Create IP Lease Pool

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

#### 3.2 Create Network Access Resource

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

### 4. Access Policy (Transaction-based)

#### 4.1 Create Transaction

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

#### 4.2 Create Deny Ending (within transaction)

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

#### 4.3 Create AD Authentication Agent

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

#### 4.4 Create Access Policy

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

#### 4.5 Commit Transaction

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

#### 4.6 Apply Policy

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

### 5. AS3 Application Deployment

#### 5.1 Deploy Application

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

### 6. GSLB Configuration

#### 6.1 Create Datacenter

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

#### 6.2 Create WideIP

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
| Main playbook | `deploy_apm_vpn.yml` |
| Variables | `vars/main.yml` |
| AAA AD tasks | `tasks/aaa_ad_servers.yml` |
| Connectivity tasks | `tasks/connectivity_profile.yml` |
| Network access tasks | `tasks/network_access.yml` |
| Webtop tasks | `tasks/webtop.yml` |
| Access policy tasks | `tasks/access_policy.yml` |
| AS3 deployment tasks | `tasks/as3_deployment.yml` |
| GSLB tasks | `tasks/gslb_configuration.yml` |
| Source collection | `docs/solution1-create.postman_collection.json` |

---

For usage examples and troubleshooting, see [README.md](../README.md)
