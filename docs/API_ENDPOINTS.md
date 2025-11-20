# F5 BIG-IP APM API Endpoints Reference

Complete reference of all F5 iControl REST API endpoints used in the APM solutions.

## Base Configuration

```
Base URL: https://{bigip_host}:{port}/mgmt
Authentication: Basic Auth (username:password)
SSL Verification: Disabled for lab (enable in production)
```

## Table of Contents

1. [System & Connectivity](#system--connectivity)
2. [Transaction Management](#transaction-management)
3. [AAA Authentication](#aaa-authentication)
4. [Network & Tunnels](#network--tunnels)
5. [APM Profiles & Policies](#apm-profiles--policies)
6. [Policy Items & Agents](#policy-items--agents)
7. [Customization Groups](#customization-groups)
8. [Resources](#resources)
9. [Application Services (AS3)](#application-services-as3)
10. [GSLB/DNS](#gslbdns)

---

## System & Connectivity

### Check BIG-IP Version
```http
GET /mgmt/tm/sys/version
```

**Response:**
```json
{
  "entries": {
    "https://localhost/mgmt/tm/sys/version/0": {
      "nestedStats": {
        "entries": {
          "Version": {
            "description": "15.1.0"
          },
          "Build": {
            "description": "0.0.249"
          }
        }
      }
    }
  }
}
```

### Check AS3 Availability
```http
GET /mgmt/shared/appsvcs/info
```

**Response:**
```json
{
  "version": "3.36.0",
  "release": "1",
  "schemaCurrent": "3.36.0",
  "schemaMinimum": "3.0.0"
}
```

---

## Transaction Management

### Create Transaction
```http
POST /mgmt/tm/transaction
Content-Type: application/json

{}
```

**Response:**
```json
{
  "transId": 1234567890,
  "state": "STARTED",
  "timeoutSeconds": 30,
  "asyncExecution": false
}
```

### Commit Transaction
```http
PATCH /mgmt/tm/transaction/{transId}
Content-Type: application/json
X-F5-REST-Coordination-Id: {transId}

{
  "state": "VALIDATING"
}
```

**Response:**
```json
{
  "transId": 1234567890,
  "state": "COMPLETED",
  "result": "success"
}
```

---

## AAA Authentication

### Create LTM Node (AD Server)
```http
POST /mgmt/tm/ltm/node
Content-Type: application/json

{
  "name": "10.1.20.7",
  "partition": "Common",
  "address": "10.1.20.7"
}
```

### Create AD Server Pool
```http
POST /mgmt/tm/ltm/pool
Content-Type: application/json

{
  "name": "solution1-ad-pool",
  "partition": "Common",
  "members": [
    {
      "name": "10.1.20.7:389",
      "address": "10.1.20.7"
    }
  ],
  "monitor": "/Common/gateway_icmp"
}
```

### Create AAA Active Directory Server
```http
POST /mgmt/tm/apm/aaa/active-directory
Content-Type: application/json

{
  "name": "solution1-ad-servers",
  "partition": "Common",
  "domain": "f5lab.local",
  "adminName": "admin@f5lab.local",
  "adminEncryptedPassword": "admin",
  "timeout": 15,
  "usePool": "enabled",
  "poolName": "/Common/solution1-ad-pool"
}
```

---

## Network & Tunnels

### Create PPP Tunnel
```http
POST /mgmt/tm/net/tunnels/tunnel
Content-Type: application/json

{
  "name": "solution1-tunnel",
  "partition": "Common",
  "profile": "/Common/ppp",
  "autoLasthop": "default",
  "mode": "bidirectional",
  "usePmtu": "enabled"
}
```

---

## APM Profiles & Policies

### Create Access Policy
```http
POST /mgmt/tm/apm/policy/access-policy
Content-Type: application/json
X-F5-REST-Coordination-Id: {transId}

{
  "name": "solution1-psp",
  "partition": "Common",
  "type": "all",
  "defaultEnding": "/Common/solution1-psp_end_deny",
  "startItem": "/Common/solution1-psp_start"
}
```

### Create Access Profile
```http
POST /mgmt/tm/apm/profile/access
Content-Type: application/json

{
  "name": "solution1-psp",
  "partition": "Common",
  "acceptLanguages": ["en"],
  "accessPolicy": "/Common/solution1-psp",
  "defaultsFrom": "/Common/access",
  "type": "all"
}
```

### Create Connectivity Profile
```http
POST /mgmt/tm/apm/profile/connectivity
Content-Type: application/json

{
  "name": "solution1-cp",
  "partition": "Common",
  "adaptiveCompression": "enabled",
  "compression": "enabled",
  "customizationGroup": "/Common/solution1-cp_secure_access_client_customization",
  "defaultsFrom": "/Common/connectivity",
  "tunnelMode": "bidirectional",
  "tunnelReference": "/Common/solution1-tunnel"
}
```

---

## Policy Items & Agents

### Create Start Item
```http
POST /mgmt/tm/apm/policy/policy-item
Content-Type: application/json
X-F5-REST-Coordination-Id: {transId}

{
  "name": "solution1-psp_start",
  "partition": "Common",
  "caption": "Start",
  "color": 1,
  "itemType": "start",
  "agents": [
    {
      "name": "solution1-psp_start_ag",
      "partition": "Common",
      "type": "decider"
    }
  ],
  "rules": [
    {
      "caption": "fallback",
      "nextItem": "/Common/solution1-psp_act_logon_page"
    }
  ]
}
```

### Create Logon Page Agent
```http
POST /mgmt/tm/apm/policy/agent/logon-page
Content-Type: application/json
X-F5-REST-Coordination-Id: {transId}

{
  "name": "solution1-psp_act_logon_page_ag",
  "partition": "Common",
  "customizationGroup": "/Common/solution1-psp_logon_ag_ag_customization",
  "type": "logon-page"
}
```

### Create AD Auth Agent
```http
POST /mgmt/tm/apm/policy/agent/aaa-active-directory
Content-Type: application/json
X-F5-REST-Coordination-Id: {transId}

{
  "name": "solution1-psp_act_active_directory_auth_ag",
  "partition": "Common",
  "authServer": "/Common/solution1-ad-servers",
  "type": "aaa-active-directory"
}
```

### Create Resource Assign Agent
```http
POST /mgmt/tm/apm/policy/agent/resource-assign
Content-Type: application/json
X-F5-REST-Coordination-Id: {transId}

{
  "name": "solution1-psp_act_resource_assign_ag",
  "partition": "Common",
  "type": "resource-assign",
  "resourceAssign": {
    "networkAccessResources": ["/Common/solution1-vpn"],
    "webtop": "/Common/solution1-webtop",
    "webtopSections": ["/Common/solution1-network_access"]
  }
}
```

### Create AD Group Mapping Agent (Solution 2)
```http
POST /mgmt/tm/apm/policy/agent/resource-assign
Content-Type: application/json
X-F5-REST-Coordination-Id: {transId}

{
  "name": "solution2-psp_act_ad_group_mapping_ag",
  "partition": "Common",
  "type": "resource-assign",
  "advancedResourceAssign": [
    {
      "expression": "expr { [string tolower [mcget -decode {session.ad.last.attr.memberOf}]] contains [string tolower \"CN=Sales Engineering,CN=Users,DC=f5lab,DC=local\"] }",
      "networkAccessResources": ["/Common/solution2-vpn"],
      "portalAccessResources": ["/Common/solution2-server1"],
      "webtop": "/Common/solution2-webtop",
      "webtopSections": ["/Common/solution2-network_access"]
    }
  ]
}
```

### Create Allow Ending Agent
```http
POST /mgmt/tm/apm/policy/agent/ending-allow
Content-Type: application/json
X-F5-REST-Coordination-Id: {transId}

{
  "name": "solution1-psp_end_allow_ag",
  "partition": "Common",
  "type": "ending-allow"
}
```

### Create Deny Ending Agent
```http
POST /mgmt/tm/apm/policy/agent/ending-deny
Content-Type: application/json
X-F5-REST-Coordination-Id: {transId}

{
  "name": "solution1-psp_end_deny_ag",
  "partition": "Common",
  "type": "ending-deny"
}
```

---

## Customization Groups

### Valid Customization Group Types
- `access-policy` - Access policy customization
- `logout` - Logout page
- `eps` - Endpoint security
- `errormap` - Error pages
- `framework` - Framework messages
- `general-ui` - General UI elements
- `logon-page` - Logon page
- `aaa-active-directory` - AD authentication
- `secure-access-client` - Connectivity profile (VPN client)
- `resource-web-app` - Portal access resources

### Create Customization Group
```http
POST /mgmt/tm/apm/policy/customization-group
Content-Type: application/json

{
  "name": "solution1-psp_logout",
  "partition": "Common",
  "type": "logout",
  "source": "/Common/logout_modern"
}
```

### Create Portal Resource Customization Group
```http
POST /mgmt/tm/apm/policy/customization-group
Content-Type: application/json

{
  "name": "solution2-server1_resource_web_app_customization",
  "partition": "Common",
  "type": "resource-web-app",
  "source": "/Common/resource-web-app_modern"
}
```

---

## Resources

### Create IP Lease Pool
```http
POST /mgmt/tm/apm/resource/leasepool
Content-Type: application/json

{
  "name": "solution1-vpn_pool",
  "partition": "Common",
  "members": [
    {
      "startingIpAddress": "10.1.2.1",
      "endingIpAddress": "10.1.2.254"
    }
  ]
}
```

### Create Network Access Resource
```http
POST /mgmt/tm/apm/resource/network-access
Content-Type: application/json

{
  "name": "solution1-vpn",
  "partition": "Common",
  "addressSpaceIncludeSubnet": [
    {
      "subnet": "10.1.10.0/255.255.255.0"
    },
    {
      "subnet": "10.1.20.0/255.255.255.0"
    }
  ],
  "clientSideEncryption": "enabled",
  "connectionType": "network-access",
  "description": "Network Access",
  "dtls": "true",
  "dnsAddressSpace": [
    {
      "subnet": "10.1.0.0/255.255.0.0"
    }
  ],
  "ipv4AddressSpace": "yes",
  "ipv4LeasePool": "/Common/solution1-vpn_pool",
  "splitTunneling": "true"
}
```

### Create Portal Access Resource
```http
POST /mgmt/tm/apm/resource/portal-access
Content-Type: application/json

{
  "name": "solution2-server1",
  "partition": "Common",
  "applicationUri": "https://server1.acme.com",
  "caption": "Server 1",
  "cssPatching": "true",
  "customizationGroup": "/Common/solution2-server1_resource_web_app_customization",
  "htmlPatching": "true",
  "javascriptPatching": "true",
  "linkType": "uri",
  "locationSpecific": "true",
  "patchingType": "full-patch",
  "publishOnWebtop": "true",
  "items": [
    {
      "name": "item",
      "clientCachingType": "default",
      "compressionType": "gzip",
      "homeTab": "true",
      "host": "server1.acme.com",
      "linkType": "uri",
      "order": 1,
      "paths": "/*",
      "port": 443,
      "scheme": "https"
    }
  ]
}
```

### Create Webtop
```http
POST /mgmt/tm/apm/resource/webtop
Content-Type: application/json

{
  "name": "solution1-webtop",
  "partition": "Common",
  "type": "full",
  "minimizeToTray": "true",
  "customizationGroup": "/Common/solution1-psp_webtop_ag_customization"
}
```

### Create Webtop Section
```http
POST /mgmt/tm/apm/resource/webtop-section
Content-Type: application/json

{
  "name": "solution1-network_access",
  "partition": "Common",
  "type": "network-access"
}
```

---

## Application Services (AS3)

### Deploy AS3 Application
```http
POST /mgmt/shared/appsvcs/declare
Content-Type: application/json

{
  "class": "AS3",
  "action": "deploy",
  "declaration": {
    "class": "ADC",
    "schemaVersion": "3.0.0",
    "id": "solution1",
    "solution1": {
      "class": "Tenant",
      "solution1": {
        "class": "Application",
        "template": "https",
        "serviceMain": {
          "class": "Service_HTTPS",
          "virtualAddresses": ["10.1.10.100"],
          "virtualPort": 443,
          "profileAccess": {
            "bigip": "/Common/solution1-psp"
          },
          "profileConnectivity": {
            "bigip": "/Common/solution1-cp"
          },
          "serverTLS": "webtls",
          "redirect80": false
        },
        "webtls": {
          "class": "TLS_Server",
          "certificates": [
            {
              "certificate": "webcert"
            }
          ]
        },
        "webcert": {
          "class": "Certificate",
          "certificate": {"bigip": "/Common/default.crt"},
          "privateKey": {"bigip": "/Common/default.key"}
        }
      }
    }
  }
}
```

### Delete AS3 Application
```http
DELETE /mgmt/shared/appsvcs/declare/{tenant}
```

---

## GSLB/DNS

### Create WideIP
```http
POST /mgmt/tm/gtm/wideip/a
Content-Type: application/json

{
  "name": "solution1.acme.com",
  "partition": "Common",
  "pools": [
    {
      "name": "solution1-pool",
      "partition": "Common"
    }
  ]
}
```

---

## Deletion Endpoints

All creation endpoints support DELETE with the resource path:

```http
DELETE /mgmt/tm/apm/profile/access/~Common~solution1-psp
DELETE /mgmt/tm/apm/policy/access-policy/~Common~solution1-psp
DELETE /mgmt/tm/apm/profile/connectivity/~Common~solution1-cp
DELETE /mgmt/tm/apm/resource/network-access/~Common~solution1-vpn
DELETE /mgmt/tm/apm/resource/portal-access/~Common~solution2-server1
DELETE /mgmt/tm/apm/resource/webtop/~Common~solution1-webtop
DELETE /mgmt/tm/apm/resource/leasepool/~Common~solution1-vpn_pool
DELETE /mgmt/tm/apm/aaa/active-directory/~Common~solution1-ad-servers
DELETE /mgmt/tm/ltm/pool/~Common~solution1-ad-pool
DELETE /mgmt/tm/ltm/node/~Common~10.1.20.7
DELETE /mgmt/tm/net/tunnels/tunnel/~Common~solution1-tunnel
```

**Note:** Use tilde `~` instead of forward slash `/` in URL paths for partitions.

---

## Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | Success | Resource retrieved successfully |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid property, wrong type, missing required field |
| 401 | Unauthorized | Invalid credentials |
| 404 | Not Found | Resource doesn't exist, AS3 not installed |
| 409 | Conflict | Resource already exists (usually safe to ignore) |
| 422 | Unprocessable | Transaction validation failed |

---

## Common Patterns

### Idempotent Operations
Accept both 200/201 (success) and 409 (already exists):
```yaml
status_code: [200, 201, 409]
```

### Transaction-Based Policy Creation
1. Create transaction → Get `transId`
2. Add all policy components with `X-F5-REST-Coordination-Id: {transId}` header
3. Commit transaction with `state: VALIDATING`

### Resource References
Use full partition paths:
```
/Common/resource-name
/partition-name/resource-name
```

### URL Encoding
Replace `/` with `~` in resource paths:
```
/Common/solution1-psp  →  ~Common~solution1-psp
```

---

## Rate Limits & Best Practices

1. **Transaction Timeout:** 30 seconds default (configurable)
2. **Concurrent Requests:** Limit to 10 concurrent API calls
3. **Retry Logic:** Use exponential backoff for 429/503 errors
4. **Validation:** Always validate JSON payloads before sending
5. **Logging:** Log all transaction IDs for troubleshooting
6. **SSL:** Disable certificate validation only in lab environments

---

## References

- [F5 iControl REST API Reference](https://clouddocs.f5.com/api/icontrol-rest/)
- [AS3 Documentation](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/)
- [Source Postman Collections](https://github.com/f5devcentral/access-solutions)

---

**Generated from:** `bigip-apm-ansible` project
**Last Updated:** 2025-11-19
