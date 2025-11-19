# Quick Start Guide

Deploy an F5 BIG-IP APM VPN solution in under 10 minutes.

## Prerequisites

- Ansible installed
- Python 3.6+
- Network access to BIG-IP management interface
- BIG-IP with APM licensed
- Active Directory server accessible from BIG-IP

## 5-Minute Setup

### 1. Install Ansible

```bash
pip3 install ansible requests urllib3
```

### 2. Configure Inventory

Edit `inventory.yml`:

```yaml
all:
  children:
    bigip:
      hosts:
        bigip-01:
          ansible_host: 10.1.1.4      # Your BIG-IP IP
          bigip_user: admin             # Your username
          bigip_pass: admin             # Your password
```

### 3. Configure Variables

Edit `vars/main.yml` with minimum required settings:

```yaml
# Solution Naming
vs1_name: "myvpn"
dns1_name: "vpn.mycompany.com"

# Active Directory
ad_server_ip: "10.1.20.7"           # Your AD server IP
ad_domain: "mycompany.local"         # Your AD domain
ad_admin_user: "admin"               # AD admin username
ad_admin_password: "password"        # AD admin password

# VPN IP Pool
vpn_lease_pool_start: "10.1.2.1"
vpn_lease_pool_end: "10.1.2.254"

# Split Tunnel Networks
vpn_split_tunnel_networks:
  - "10.0.0.0/255.0.0.0"
  - "192.168.0.0/255.255.0.0"
```

### 4. Run Playbook

```bash
ansible-playbook deploy_apm_vpn.yml
```

### 5. Test VPN

1. Open browser to `https://vpn.mycompany.com/`
2. Login with AD credentials: `username@mycompany.local`
3. Launch VPN client from webtop
4. Verify connectivity to internal networks

## Common Configurations

### Minimal Deployment (No AS3)

```yaml
# In vars/main.yml
deploy_application_via_as3: false
```

Then manually attach access profile to existing virtual server:

```bash
tmsh modify ltm virtual /Common/my-vs profiles add { /Common/myvpn-psp }
tmsh modify ltm virtual /Common/my-vs profiles add { /Common/myvpn-cp }
```

### Multi-Network Split Tunneling

```yaml
vpn_split_tunnel_networks:
  - "10.0.0.0/255.0.0.0"
  - "172.16.0.0/255.240.0.0"
  - "192.168.0.0/255.255.0.0"
```

### Change VPN IP Pool

```yaml
vpn_lease_pool_start: "192.168.100.1"
vpn_lease_pool_end: "192.168.100.254"
```

### Disable Optional Components

```yaml
create_connectivity_profile: true    # Keep VPN tunnel
create_network_access: true          # Keep network access
create_webtop: false                 # Disable webtop (portal-less VPN)
deploy_application_via_as3: false    # Don't create new VS
configure_external_dns: false        # No GSLB
```

## Troubleshooting

### Playbook Fails - Connection Error

```bash
# Test BIG-IP connectivity
curl -k https://10.1.1.4/mgmt/shared/appsvcs/info

# Verify credentials
curl -k -u admin:admin https://10.1.1.4/mgmt/tm/sys/version
```

### Playbook Fails - AD Server Error

```bash
# SSH to BIG-IP and test AD connectivity
ssh admin@10.1.1.4
ping 10.1.20.7

# Test AD bind
tmsh modify apm aaa active-directory /Common/myvpn-ad-servers server.check-interval 10
tmsh show apm aaa active-directory /Common/myvpn-ad-servers
```

### Policy Not Compiling

```bash
# Check APM logs on BIG-IP
ssh admin@10.1.1.4
tail -f /var/log/apm
```

### Verbose Output

```bash
# Run with debug output
ansible-playbook deploy_apm_vpn.yml -vvv
```

## What Gets Created

After successful deployment, you'll have:

**APM Objects:**
- Access Policy: `/Common/myvpn-psp`
- Access Profile: `/Common/myvpn-psp`
- Network Access Resource: `/Common/myvpn-vpn`
- Webtop: `/Common/myvpn-webtop`
- Connectivity Profile: `/Common/myvpn-cp`
- AD AAA Server: `/Common/myvpn-ad-servers`

**Network Objects:**
- VPN Tunnel: `/Common/myvpn-tunnel`
- IP Lease Pool: `/Common/myvpn-vpn_pool`
- AD Server Pool: `/Common/myvpn-ad-pool`

**Application (if AS3 enabled):**
- Partition: `myvpn`
- Virtual Server: `/myvpn/myvpn/serviceMain`
- Pool: `/myvpn/myvpn/myvpn_pool`

## Next Steps

1. **Review Configuration**
   - Login to BIG-IP GUI
   - Navigate to Access > Profiles / Policies
   - Review policy flow

2. **Customize Appearance**
   - Modify logon page customization
   - Update webtop customization
   - Add company branding

3. **Test VPN Access**
   - Test from external network
   - Verify AD authentication
   - Confirm split tunneling
   - Test resource access

4. **Production Hardening**
   - Use Ansible Vault for credentials
   - Configure session timeouts
   - Enable MFA (if required)
   - Configure client integrity checks
   - Set up monitoring and logging

5. **Scale to Multiple BIG-IPs**
   - Add more hosts to inventory
   - Run playbook against all devices
   - Configure GSLB for redundancy

## Rollback

To remove the configuration:

```bash
# Delete partition (if AS3 used)
tmsh delete sys folder myvpn

# Delete APM objects
tmsh delete apm profile access myvpn-psp
tmsh delete apm policy access-policy myvpn-psp
tmsh delete apm resource network-access myvpn-vpn
tmsh delete apm resource webtop myvpn-webtop
tmsh delete apm profile connectivity myvpn-cp
tmsh delete net tunnels tunnel myvpn-tunnel
tmsh delete apm resource leasepool myvpn-vpn_pool
tmsh delete apm aaa active-directory myvpn-ad-servers
tmsh delete ltm pool myvpn-ad-pool
tmsh delete ltm node 10.1.20.7

# Save configuration
tmsh save sys config
```

Or restore from UCS backup:

```bash
tmsh load sys ucs pre-apm-deployment.ucs
```

## Performance Tips

1. **Transaction Timeout:** If policy creation times out, increase timeout in `ansible.cfg`:
   ```ini
   timeout = 120
   ```

2. **Parallel Execution:** Deploy to multiple BIG-IPs in parallel:
   ```bash
   # In ansible.cfg
   forks = 10
   ```

3. **Skip Verification:** If BIG-IP checks are slow:
   ```yaml
   # In vars/main.yml
   bigip_validate_certs: no
   ```

## Getting Help

- Full documentation: [README.md](README.md)
- API mapping: [docs/API_MAPPING.md](docs/API_MAPPING.md)
- F5 DevCentral: https://devcentral.f5.com/
- Ansible Documentation: https://docs.ansible.com/

---

For detailed documentation, customization options, and troubleshooting, see [README.md](README.md)
