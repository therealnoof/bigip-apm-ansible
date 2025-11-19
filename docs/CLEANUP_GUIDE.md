# APM Solution Cleanup Guide

Guide for safely removing F5 BIG-IP APM configurations using the delete playbook.

## Overview

The `delete_apm_vpn.yml` playbook provides a safe, automated way to remove all APM solution components from BIG-IP devices. It supports both Solution 1 (VPN) and Solution 2 (Portal Access).

**Sources:**
- [solution1-delete Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution1/postman/solution1-delete.postman_collection.json)
- [solution2-delete Postman collection](https://github.com/f5devcentral/access-solutions/blob/master/solution2/postman/solution2-delete.postman_collection.json)

## What Gets Deleted

### Core APM Objects (Both Solutions)
- Access Profile (`/Common/<solution>-psp`)
- Access Policy (`/Common/<solution>-psp`)
- All policy items (Start, Logon Page, AD Auth, Resource Assign/AD Group Mapping, Allow, Deny)
- All agents (logon page, AD auth, resource assign, AD query, deny, allow)
- All customization groups

### Solution 1: VPN Configuration
- Connectivity Profile (`/Common/solution1-cp`)
- VPN Tunnel (`/Common/solution1-tunnel`)
- Network Access Resource (`/Common/solution1-vpn`)
- IP Lease Pool (`/Common/solution1-vpn_pool`)

### Solution 2: Portal Access Configuration
- Portal Access Resources:
  - `/Common/solution2-server1` (server1.acme.com)
  - `/Common/solution2-server2` (server2.acme.com)
  - `/Common/solution2-server3` (server3.acme.com)
  - `/Common/solution2-server4` (server4.acme.com)
- Portal Customization Groups (one per resource)
- Network Access Resource (optional, if VPN enabled)
- IP Lease Pool (optional, if VPN enabled)

### User Interface (Both Solutions)
- Webtop (`/Common/<solution>-webtop`)
- Webtop Section (`/Common/<solution>-network_access`)

### Authentication (Both Solutions)
- AAA AD Server (`/Common/<solution>-ad-servers`)
- AD Server Pool (`/Common/<solution>-ad-pool`)
- AD Server Node (`10.1.20.7`)

### Application (if AS3 used)
- Entire Partition (`solution1` or `solution2`)
- Virtual Server
- Pool members
- Profiles

### GSLB (if configured)
- WideIP
- GTM Virtual Servers
- Pool members

## Deletion Order

The playbook deletes objects in this specific order to avoid dependency conflicts:

1. **External DNS/GSLB** - WideIP and GTM objects
2. **AS3 Application** - Partition with VS and pools
3. **Access Profile** - Must be deleted before policy
4. **Access Policy** - Deletes all items and agents (including AD group mapping for Solution 2)
5. **Connectivity Profile** - VPN connectivity settings (Solution 1, optional in Solution 2)
6. **VPN Tunnel** - Network tunnel (Solution 1, optional in Solution 2)
7. **AAA AD Server** - Authentication server
8. **AD Pool** - Server pool
9. **AD Node** - Network node
10. **Webtop** - Portal interface
11. **Webtop Section** - Portal section
12. **Portal Access Resources** - Web application resources (Solution 2 only, 4 resources)
13. **Network Access** - VPN resource (Solution 1, optional in Solution 2)
14. **IP Lease Pool** - IP address pool (Solution 1, optional in Solution 2)

## Safety Features

### 1. Confirmation Prompt

By default, the playbook requires manual confirmation:

```bash
ansible-playbook delete_apm_vpn.yml

# You will be prompted:
# Type 'DELETE' to confirm deletion (Ctrl+C to cancel):
```

You must type exactly `DELETE` to proceed.

### 2. Error Handling

- All delete operations use `ignore_errors: yes`
- Accepts both 200 (deleted) and 404 (not found) status codes
- Continues even if objects don't exist
- Safe to run multiple times

### 3. Detailed Logging

- Each deletion is logged with result status
- Summary report shows what was deleted vs not found
- Full Ansible logging in `ansible.log`

## Usage

### Delete Solution 1 (VPN)

```bash
ansible-playbook delete_apm_vpn.yml
```

**You will see:**
```
WARNING: APM Solution Deletion
This will DELETE all components for: solution1

Components to be removed:
- Access Profile: /Common/solution1-psp
- Access Policy: /Common/solution1-psp
- Connectivity Profile: /Common/solution1-cp
- Network Access: /Common/solution1-vpn
- ... [full list] ...

This action CANNOT be undone!

Type 'DELETE' to confirm deletion (Ctrl+C to cancel):
```

### Delete Solution 2 (Portal)

To delete Solution 2 with portal resources, you need to load solution2.yml variables:

```bash
# Method 1: Load vars file explicitly
ansible-playbook delete_apm_vpn.yml -e "@vars/solution2.yml"

# Method 2: Override solution name only (simpler)
ansible-playbook delete_apm_vpn.yml -e "vs1_name=solution2"
```

**Note:** Method 2 works if you just need to delete by name, but Method 1 ensures portal_resources variable is loaded for proper deletion confirmation.

**You will see:**
```
WARNING: APM Solution Deletion
This will DELETE all components for: solution2

Components to be removed:
- Access Profile: /Common/solution2-psp
- Access Policy: /Common/solution2-psp
- Portal Resources: 4 web applications
- Webtop: /Common/solution2-webtop
- Network Access: /Common/solution2-vpn (if configured)
- ... [full list] ...

This action CANNOT be undone!

Type 'DELETE' to confirm deletion (Ctrl+C to cancel):
```

### Skip Confirmation (Dangerous!)

For automation/CI-CD pipelines only:

```bash
# Solution 1
ansible-playbook delete_apm_vpn.yml -e "confirm_delete=true"

# Solution 2
ansible-playbook delete_apm_vpn.yml -e "@vars/solution2.yml" -e "confirm_delete=true"
```

**WARNING:** This skips the confirmation prompt entirely. Use with extreme caution!

### Target Specific Host

```bash
ansible-playbook delete_apm_vpn.yml --limit bigip-01
```

### Verbose Output

```bash
ansible-playbook delete_apm_vpn.yml -v    # verbose
ansible-playbook delete_apm_vpn.yml -vv   # more verbose
ansible-playbook delete_apm_vpn.yml -vvv  # debug
```

### Delete from Different Inventory

```bash
ansible-playbook -i production_inventory.yml delete_apm_vpn.yml
```

## Verification

### Before Deletion

Create a backup:

```bash
# SSH to BIG-IP
ssh admin@10.1.1.4

# Create UCS backup
tmsh save sys ucs before-delete-$(date +%Y%m%d-%H%M%S).ucs

# List existing objects - Solution 1
tmsh list apm profile access solution1-psp
tmsh list apm resource network-access solution1-vpn
tmsh list apm resource webtop solution1-webtop

# List existing objects - Solution 2
tmsh list apm profile access solution2-psp
tmsh list apm resource portal-access solution2-server1
tmsh list apm resource portal-access solution2-server2
tmsh list apm resource portal-access solution2-server3
tmsh list apm resource portal-access solution2-server4
tmsh list apm resource webtop solution2-webtop
```

### After Deletion

Verify objects are gone:

**Solution 1:**
```bash
# Check access profile (should return error)
tmsh list apm profile access solution1-psp
# Error: 01020036:3: The requested Access Profile (/Common/solution1-psp) was not found.

# Check partition (if AS3 used)
tmsh list sys folder solution1
# Error: 01020036:3: The requested folder (solution1) was not found.

# Check network access
tmsh list apm resource network-access solution1-vpn
# Error: 01020036:3: The requested network-access (solution1-vpn) was not found.
```

**Solution 2:**
```bash
# Check access profile (should return error)
tmsh list apm profile access solution2-psp
# Error: 01020036:3: The requested Access Profile (/Common/solution2-psp) was not found.

# Check portal resources (should all return errors)
tmsh list apm resource portal-access solution2-server1
# Error: 01020036:3: The requested portal-access (solution2-server1) was not found.

tmsh list apm resource portal-access solution2-server2
# Error: 01020036:3: The requested portal-access (solution2-server2) was not found.

# Check partition (if AS3 used)
tmsh list sys folder solution2
# Error: 01020036:3: The requested folder (solution2) was not found.
```

**Both Solutions:**
```bash
# Check AD node (shared)
tmsh list ltm node 10.1.20.7
# Error: 01020036:3: The requested node (10.1.20.7) was not found.
```

### Playbook Output

Successful deletion shows:

```
TASK [Display deletion summary]
ok: [bigip-01] => {
    "msg": "
    ============================================
    Deletion Complete!
    ============================================

    Removed Components:
    - Access Profile: solution1-psp ✓
    - Access Policy: solution1-psp ✓
    - Connectivity Profile: solution1-cp ✓
    - VPN Tunnel: solution1-tunnel ✓
    - AAA AD Server: solution1-ad-servers ✓
    - AD Pool: solution1-ad-pool ✓
    - AD Node: 10.1.20.7 ✓
    ...
    ============================================
    "
}
```

## Common Scenarios

### 1. Clean Lab Environment

Reset lab to clean state:

```bash
# Delete current configuration
ansible-playbook delete_apm_vpn.yml -e "confirm_delete=true"

# Redeploy fresh configuration
ansible-playbook deploy_apm_vpn.yml
```

### 2. Failed Deployment Cleanup

If deployment fails mid-way, clean up partial configuration:

```bash
ansible-playbook delete_apm_vpn.yml
```

The delete playbook handles partial configurations gracefully.

### 3. Change Solution Name

To change from solution1 to myvpn:

```bash
# Delete with old name
ansible-playbook delete_apm_vpn.yml  # uses vs1_name: solution1

# Update vars/main.yml
vi vars/main.yml
# Change: vs1_name: "myvpn"

# Deploy with new name
ansible-playbook deploy_apm_vpn.yml
```

### 4. Remove Multiple Solutions

If you have multiple VPN solutions deployed:

```bash
# Delete solution1
ansible-playbook delete_apm_vpn.yml -e "vs1_name=solution1" -e "confirm_delete=true"

# Delete solution2
ansible-playbook delete_apm_vpn.yml -e "vs1_name=solution2" -e "confirm_delete=true"

# Delete myvpn
ansible-playbook delete_apm_vpn.yml -e "vs1_name=myvpn" -e "confirm_delete=true"
```

## Troubleshooting

### Objects Not Deleting

**Problem:** Some objects show "not found" but you know they exist

**Solutions:**

1. Check object names match variables:
   ```bash
   # Verify actual names on BIG-IP
   tmsh list apm profile access
   tmsh list apm resource network-access
   ```

2. Check partition:
   ```bash
   # Object might be in different partition
   tmsh list apm profile access all-properties
   ```

3. Manual verification:
   ```bash
   # Get exact object path
   tmsh list apm profile access recursive
   ```

### Access Profile Delete Fails

**Problem:** "Cannot delete profile - in use by virtual server"

**Solutions:**

1. Find which virtual server is using it:
   ```bash
   tmsh list ltm virtual all-properties | grep solution1-psp
   ```

2. Remove from virtual server first:
   ```bash
   tmsh modify ltm virtual /Common/my-vs profiles delete { /Common/solution1-psp }
   ```

3. Then run delete playbook:
   ```bash
   ansible-playbook delete_apm_vpn.yml
   ```

### Customization Groups Remain

**Problem:** Customization groups still exist after policy deletion

**Solution:** These should auto-delete, but if they remain:

```bash
# List customization groups
tmsh list apm policy customization-group all-properties | grep solution1

# Delete manually if needed
tmsh delete apm policy customization-group /Common/solution1-psp_logout
tmsh delete apm policy customization-group /Common/solution1-psp_eps
# ... etc
```

### AS3 Partition Won't Delete

**Problem:** AS3 partition deletion fails

**Solutions:**

1. Check for active sessions:
   ```bash
   tmsh show apm session
   ```

2. Kill active sessions:
   ```bash
   tmsh delete apm session all
   ```

3. Try delete via TMSH:
   ```bash
   tmsh delete sys folder solution1
   ```

4. Force delete via AS3:
   ```bash
   curl -k -u admin:admin -X DELETE \
     https://10.1.1.4/mgmt/shared/appsvcs/declare/solution1
   ```

## Manual Cleanup

If the playbook fails or for manual cleanup:

### Solution 1: Quick Delete (TMSH)

```bash
# SSH to BIG-IP
ssh admin@10.1.1.4

# Delete profile (deletes policy too)
tmsh delete apm profile access /Common/solution1-psp

# Delete connectivity profile
tmsh delete apm profile connectivity /Common/solution1-cp

# Delete network access
tmsh delete apm resource network-access /Common/solution1-vpn

# Delete webtop
tmsh delete apm resource webtop /Common/solution1-webtop

# Delete webtop section
tmsh delete apm resource webtop-section /Common/solution1-network_access

# Delete lease pool
tmsh delete apm resource leasepool /Common/solution1-vpn_pool

# Delete tunnel
tmsh delete net tunnels tunnel /Common/solution1-tunnel

# Delete AD AAA server
tmsh delete apm aaa active-directory /Common/solution1-ad-servers

# Delete AD pool
tmsh delete ltm pool /Common/solution1-ad-pool

# Delete AD node
tmsh delete ltm node 10.1.20.7

# Delete AS3 application (if used)
curl -k -u admin:admin -X DELETE \
  https://10.1.1.4/mgmt/shared/appsvcs/declare/solution1

# Save configuration
tmsh save sys config
```

### Solution 2: Quick Delete (TMSH)

```bash
# SSH to BIG-IP
ssh admin@10.1.1.4

# Delete profile (deletes policy too)
tmsh delete apm profile access /Common/solution2-psp

# Delete portal access resources
tmsh delete apm resource portal-access /Common/solution2-server1
tmsh delete apm resource portal-access /Common/solution2-server2
tmsh delete apm resource portal-access /Common/solution2-server3
tmsh delete apm resource portal-access /Common/solution2-server4

# Delete network access (if configured)
tmsh delete apm resource network-access /Common/solution2-vpn

# Delete webtop
tmsh delete apm resource webtop /Common/solution2-webtop

# Delete webtop section
tmsh delete apm resource webtop-section /Common/solution2-network_access

# Delete lease pool (if configured)
tmsh delete apm resource leasepool /Common/solution2-vpn_pool

# Delete tunnel (if configured)
tmsh delete net tunnels tunnel /Common/solution2-tunnel

# Delete AD AAA server
tmsh delete apm aaa active-directory /Common/solution2-ad-servers

# Delete AD pool
tmsh delete ltm pool /Common/solution2-ad-pool

# Delete AD node
tmsh delete ltm node 10.1.20.7

# Delete AS3 application (if used)
curl -k -u admin:admin -X DELETE \
  https://10.1.1.4/mgmt/shared/appsvcs/declare/solution2

# Save configuration
tmsh save sys config
```

### Nuclear Option (Delete Everything)

**EXTREME CAUTION - This deletes ALL APM configuration:**

```bash
# Delete all access profiles
tmsh delete apm profile access all

# Delete all access policies
tmsh delete apm policy access-policy all

# Delete all network access resources
tmsh delete apm resource network-access all

# Delete all webtops
tmsh delete apm resource webtop all

# This will break ALL APM configurations!
# Only use in lab/dev environments!
```

## Rollback / Restore

### From UCS Backup

If you need to restore after deletion:

```bash
# List backups
tmsh list sys ucs

# Restore from backup
tmsh load sys ucs before-delete-20250118-143000.ucs

# Verify restoration
tmsh list apm profile access solution1-psp
```

### Redeploy

Simplest option - just redeploy:

```bash
ansible-playbook deploy_apm_vpn.yml
```

## Best Practices

1. **Always create UCS backup before deletion:**
   ```bash
   tmsh save sys ucs pre-delete-$(date +%Y%m%d).ucs
   ```

2. **Test in lab first:**
   - Never run delete playbook in production without testing
   - Verify deletion order in lab environment

3. **Use version control:**
   - Keep your `vars/main.yml` in git
   - Tag configurations before major changes

4. **Document custom changes:**
   - If you manually modified configurations
   - Note them before deletion for recreation

5. **Check for dependencies:**
   ```bash
   # Check what might be using the profile
   tmsh list ltm virtual all-properties | grep solution1
   ```

6. **Verify completion:**
   - Don't assume success
   - Manually verify key objects are gone

7. **Use confirmation prompt:**
   - Don't skip it in production
   - `-e "confirm_delete=true"` only for automation

## Integration with CI/CD

### GitLab CI Example

```yaml
cleanup_dev:
  stage: cleanup
  script:
    - ansible-playbook delete_apm_vpn.yml -e "confirm_delete=true"
  when: manual
  only:
    - development
  environment:
    name: development
    action: delete
```

### Jenkins Pipeline

```groovy
stage('Cleanup') {
    when {
        expression { params.CLEANUP == true }
    }
    steps {
        ansiblePlaybook(
            playbook: 'delete_apm_vpn.yml',
            inventory: 'inventory.yml',
            extras: '-e "confirm_delete=true"'
        )
    }
}
```

## Related Documentation

- [README.md](../README.md) - Main documentation
- [QUICKSTART.md](../QUICKSTART.md) - Deployment guide
- [API_MAPPING.md](API_MAPPING.md) - Postman to Ansible conversion
- [Solution1-delete collection](solution1-delete.postman_collection.json) - Source Postman collection

---

**Remember:** Deletion is permanent. Always backup before running cleanup operations.
