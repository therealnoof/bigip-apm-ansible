# Installation Guide

This document covers the requirements and installation steps for the F5 BIG-IP APM Ansible automation project.

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

## Installation Steps

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

## Project Structure

```
bigip-apm-ansible/
├── README.md                          # Main documentation
├── QUICKSTART.md                      # 5-minute setup guide
├── ansible.cfg                        # Ansible configuration
├── inventory.yml                      # BIG-IP device inventory
├── deploy_apm_*.yml                   # Deployment playbooks
├── delete_apm_*.yml                   # Interactive deletion playbooks
├── cleanup_apm_*.yml                  # Automated cleanup playbooks
├── vars/
│   ├── main.yml                      # Solution 1 variables
│   ├── solution2.yml                 # Solution 2 variables
│   ├── solution3.yml                 # Solution 3 variables (SAML SP)
│   ├── solution4.yml                 # Solution 4 variables (SAML IDP)
│   ├── solution5.yml                 # Solution 5 variables (SAML SP internal)
│   ├── solution6.yml                 # Solution 6 variables (Certificate + Kerberos)
│   ├── solution7.yml                 # Solution 7 variables (SAML + Sideband)
│   ├── solution8.yml                 # Solution 8 variables (OAuth AS)
│   ├── solution9.yml                 # Solution 9 variables (OAuth RS)
│   ├── solution10.yml                # Solution 10 variables (OAuth AS RS256)
│   ├── solution11.yml                # Solution 11 variables (OAuth Client)
│   ├── solution12.yml                # Solution 12 variables (RDG)
│   └── solution14.yml                # Solution 14 variables (SAML SP Azure AD)
├── tasks/                            # Task files for each component
├── templates/                        # Jinja2 templates
└── docs/                            # Documentation
```

## Verification

After installation, verify your setup:

```bash
# Test Ansible connectivity
ansible bigip -m ping

# Test BIG-IP API connectivity
ansible bigip -m uri -a "url=https://{{ ansible_host }}:443/mgmt/tm/sys/version user={{ bigip_user }} password={{ bigip_pass }} validate_certs=no"
```

## Next Steps

- See [USAGE.md](USAGE.md) for deployment instructions
- See [CONFIGURATION.md](CONFIGURATION.md) for detailed variable configuration
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
