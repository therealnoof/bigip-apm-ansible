# F5 BIG-IP APM Solutions - Ansible Automation

Ansible playbooks for deploying F5 BIG-IP Access Policy Manager (APM) solutions with Active Directory, SAML, OAuth, and certificate-based authentication.

## Quick Links

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide |
| [docs/SOLUTIONS.md](docs/SOLUTIONS.md) | All solution descriptions |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture diagrams |
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | Requirements & installation |
| [docs/USAGE.md](docs/USAGE.md) | Deployment instructions |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Variable configuration |
| [docs/CLEANUP_GUIDE.md](docs/CLEANUP_GUIDE.md) | Deletion & cleanup |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues & solutions |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Adding new solutions |
| [docs/API_MAPPING.md](docs/API_MAPPING.md) | API reference & workarounds |

## Available Solutions

| Solution | Description | Playbook |
|----------|-------------|----------|
| **1** | VPN with Network Access | `deploy_apm_vpn.yml` |
| **2** | Portal Access with AD Group Mapping | `deploy_apm_portal.yml` |
| **3** | SAML Service Provider (Okta) | `deploy_apm_saml.yml` |
| **4** | SAML Identity Provider (AD) | `deploy_apm_saml_idp.yml` |
| **5** | SAML SP with Internal IDP | `deploy_apm_saml_sp_internal.yml` |
| **6** | Certificate Auth + Kerberos SSO | `deploy_apm_cert_kerb.yml` |
| **7** | SAML + Sideband Communication | `deploy_apm_sideband.yml` |
| **8** | OAuth Authorization Server (HS256) | `deploy_apm_oauth_as.yml` |
| **9** | OAuth Resource Server | `deploy_apm_oauth_rs.yml` |
| **10** | OAuth AS with RS256 | `deploy_apm_oauth_as_rsa.yml` |
| **11** | OAuth Client with OIDC | `deploy_apm_oauth_client.yml` |
| **12** | Remote Desktop Gateway | `deploy_apm_rdg.yml` |
| **14** | SAML SP with Azure AD | `deploy_apm_saml_sp_azure.yml` |

> **Note:** Solution 13 is still in development.

## Quick Start

```bash
# 1. Configure inventory
vi inventory.yml

# 2. Configure variables
vi vars/main.yml

# 3. Deploy a solution
ansible-playbook deploy_apm_vpn.yml
```

## Requirements

- **Ansible:** 2.9+
- **Python:** 3.6+
- **F5 BIG-IP:** 13.x+ with LTM and APM licensed
- **AS3:** 3.0.0+ (for application deployment)

## Project Structure

```
bigip-apm-ansible/
├── deploy_apm_*.yml         # Deployment playbooks
├── delete_apm_*.yml         # Deletion playbooks (interactive)
├── cleanup_apm_*.yml        # Cleanup playbooks (automated)
├── vars/
│   ├── main.yml             # Solution 1 variables
│   ├── solution2.yml        # Solution 2 variables
│   └── ...                  # Solution-specific variables
├── tasks/                   # Reusable task files
├── templates/               # Jinja2 templates
└── docs/                    # Documentation
```

## Deployment Examples

```bash
# Deploy VPN solution
ansible-playbook deploy_apm_vpn.yml

# Deploy SAML IDP with Azure AD
ansible-playbook deploy_apm_saml_sp_azure.yml

# Deploy OAuth Authorization Server
ansible-playbook deploy_apm_oauth_as.yml

# Deploy with custom variables
ansible-playbook deploy_apm_vpn.yml -e "@vars/custom.yml"

# Target specific host
ansible-playbook deploy_apm_vpn.yml --limit bigip-01

# Verbose output
ansible-playbook deploy_apm_vpn.yml -vvv
```

## Cleanup Examples

```bash
# Interactive deletion (requires confirmation)
ansible-playbook delete_apm_vpn.yml

# Automated cleanup (for CI/CD)
ansible-playbook cleanup_apm_vpn.yml

# Skip confirmation
ansible-playbook delete_apm_vpn.yml -e "confirm_delete=true"
```

## Feature Highlights

- **Idempotent deployments** - Safe to run multiple times
- **Modular design** - Reusable task files for each component
- **Transaction support** - Policy creation uses BIG-IP transactions
- **Tag-based deployment** - Deploy specific components only
- **Self-signed certificates** - Automatic generation for lab/demo
- **AS3 integration** - Application deployment via declarative API
- **GSLB support** - Optional multi-datacenter DNS configuration

## API Calls Automated

| Solution | API Calls |
|----------|-----------|
| Solution 1 (VPN) | 54+ |
| Solution 2 (Portal) | 60+ |
| Solution 3 (SAML SP) | 52+ |
| Solution 4 (SAML IDP) | 55+ |
| Solution 5 (SAML SP Internal) | 42+ |
| Solution 7 (Sideband) | 55+ |
| Solution 8 (OAuth AS) | 35+ |
| Solution 9 (OAuth RS) | 25+ |
| **Total** | **380+** |

## References

- [F5 BIG-IP REST API](https://clouddocs.f5.com/api/icontrol-rest/)
- [F5 APM Configuration Guide](https://clouddocs.f5.com/apm/)
- [AS3 Documentation](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/)
- [Source Postman Collections](https://github.com/f5devcentral/access-solutions/)

## Support

For issues or questions:
- Review F5 BIG-IP documentation
- Check BIG-IP system logs (`/var/log/ltm`, `/var/log/apm`)
- Review Ansible playbook output with `-vvv` flag
- Consult F5 DevCentral community

## License

Apache 2.0

## Changelog

See individual commit messages for detailed changes.
