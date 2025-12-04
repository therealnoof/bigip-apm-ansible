# Troubleshooting Guide

This document covers common issues and their solutions for APM deployments.

## Connection Issues

**Problem:** Cannot connect to BIG-IP

**Solutions:**
- Verify network connectivity: `ping <bigip-ip>`
- Check HTTPS access: `curl -k https://<bigip-ip>`
- Verify credentials in inventory
- Check firewall rules

## Transaction Failures

**Problem:** Transaction commit fails during policy creation

**Solutions:**
- Check BIG-IP logs: `/var/log/ltm`
- Verify all required objects exist (AD server, webtop, network access)
- Ensure no naming conflicts with existing objects
- Check BIG-IP version compatibility

## Policy Compilation Errors

**Problem:** Policy fails to compile

**Solutions:**
- Verify AD server is reachable from BIG-IP
- Check network access resource configuration
- Ensure webtop section exists
- Review APM logs: `/var/log/apm`

## Authentication Failures

**Problem:** AD authentication not working

**Solutions:**
- Verify AD server IP and domain name
- Test AD connectivity from BIG-IP
- Check AD credentials (admin user/password)
- Review AAA server configuration
- Check APM session logs

## AS3 Deployment Issues

**Problem:** AS3 declaration fails

**Solutions:**
```bash
# Verify AS3 is installed
curl -k https://<bigip-ip>/mgmt/shared/appsvcs/info

# Check AS3 version (requires 3.0.0+)
# Review AS3 logs
tail -f /var/log/restjavad.0.log
```

## Solution 9 Implementation Notes (OAuth Resource Server)

**CRITICAL API LIMITATIONS AND WORKAROUNDS**

This section documents important API limitations discovered during Solution 9 implementation and the workarounds applied.

### JWT Provider List Linkage Issue

**Problem:** The JWT provider list creation fails with:
```
"01071ca0:3: When the manual flag is enabled, OAuth Provider must have manual JWT config attached"
```
or
```
"01071ca0:3: When the auto flag is enabled, OAuth Provider must have auto JWT config attached"
```

**Root Cause:** The JWT provider list requires an internal linkage between the OAuth provider and JWT config that can ONLY be established through successful OIDC discovery. The following API properties do NOT work:

1. **`jwtConfig` on OAuth Provider** - This property is silently ignored when POSTing or PATCHing an OAuth provider. The API accepts it but doesn't apply it.

2. **`provider` on JWT Config** - This property is also silently ignored when creating or updating JWT configs.

3. **`useAutoJwtConfig: "true"`** - Requires `trustedCaBundle` to be set, AND requires OIDC discovery to actually succeed to create the internal linkage.

4. **Pre-creating `auto_jwt_<provider>` config** - Even if you create a JWT config with the correct naming convention before the provider, the internal linkage is NOT established.

**Workaround Applied:** The playbook defaults to **external/introspection mode** which:
- Does NOT require the JWT provider list
- Uses `oauthProvider` reference in the OAuth Scope agent instead of `jwtProviderList`
- Validates tokens at runtime via introspection against the OAuth AS
- Works even when OIDC discovery fails during deployment

**To Use Internal/JWT Mode:**
1. Ensure Solution 8 (OAuth AS) is deployed and reachable
2. Verify OIDC discovery endpoint responds: `https://as.acme.com/f5-oauth2/v1/.well-known/openid-configuration`
3. Deploy with: `ansible-playbook deploy_apm_oauth_rs.yml -e token_validation_mode=internal`

### OAuth Provider trustedCaBundle Requirement

**Problem:** Setting `useAutoJwtConfig: "true"` without `trustedCaBundle` results in:
```
"must have trusted CA present"
```

**Solution:** The playbook sets `trustedCaBundle: "/Common/ca-bundle.crt"` which is a built-in CA bundle on BIG-IP systems.

### OAuth Client Customization Group Deletion Order

**Problem:** Deleting the OAuth client customization group before the OAuth client application fails:
```
"Cannot delete customization group because it is used"
```

**Solution:** The delete playbook deletes the OAuth client application FIRST, then deletes its customization group.

### Ansible Jinja2 Variables in Dictionary Keys

**Problem:** AS3 declarations with Jinja2 variables as dictionary keys don't evaluate properly:
```yaml
# This doesn't work - sends literal "{{ partition_name }}"
declaration:
  "{{ partition_name }}":
    class: "Tenant"
```

**Solution:** Use Ansible's `combine` filter to build dictionaries with dynamic keys:
```yaml
- name: Build tenant config
  set_fact:
    as3_tenant_config:
      class: "Tenant"

- name: Add application to tenant
  set_fact:
    as3_tenant_config: "{{ as3_tenant_config | combine({path_name: as3_app_config}) }}"
```

### Summary of OAuth Workarounds

| Issue | Workaround |
|-------|------------|
| JWT Provider List requires OIDC discovery | Default to external mode |
| `jwtConfig` property ignored on OAuth provider | Use external mode or ensure OIDC works |
| `useAutoJwtConfig` requires `trustedCaBundle` | Set `trustedCaBundle: /Common/ca-bundle.crt` |
| Customization group deletion dependency | Delete OAuth client app before its customization group |
| AS3 Jinja2 dictionary keys | Use `combine` filter for dynamic keys |

## SAML IDP Issues (Solution 4)

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

## Solution 14 (SAML SP with Azure AD) Issues

**Problem:** PRP (Per-Request Policy) subroutine creation fails

**Solutions:**
- Ensure PSP is created and committed before PRP
- Verify all subroutine terminal items are created before the subroutine policy
- Check that macro items correctly reference subroutine policies

**Problem:** URL branching not matching requests

**Solutions:**
- Verify `perflow.branching.url` expression uses correct syntax
- Check that URL patterns include the scheme (https://)
- Ensure fallback rule exists for unmatched requests

**Problem:** Azure AD authentication fails

**Solutions:**
- Verify Entity ID matches Azure AD Enterprise Application configuration
- Check that ACS URL matches: `https://<sp-host>/saml/sp/profile/post/acs`
- Ensure Azure AD certificate is correctly imported
- Verify Azure AD tenant ID is correct

## Certificate Issues

**Problem:** Self-signed certificate generation fails

**Solutions:**
```bash
# Verify OpenSSL is available
which openssl
openssl version

# Check temp directory permissions
ls -la /tmp/
```

**Problem:** Certificate key mismatch

**Solutions:**
```bash
# Compare certificate and key modulus
openssl x509 -noout -modulus -in cert.pem | md5sum
openssl rsa -noout -modulus -in key.pem | md5sum
# Both should match
```

## Kerberos SSO Issues (Solution 6)

**Problem:** Kerberos ticket not obtained

**Solutions:**
- Verify KDC is reachable from BIG-IP
- Check SPN is correctly registered in AD
- Verify delegation account credentials
- Review `/var/log/apm` for Kerberos-specific errors

**Problem:** OCSP validation fails

**Solutions:**
- Verify OCSP responder URL is correct
- Check network connectivity to OCSP responder
- Ensure CA certificate is trusted
- Review certificate revocation status

## Debugging Tips

### Enable Verbose Logging

```bash
# Run with verbose output
ansible-playbook deploy_apm_vpn.yml -vvv

# Check BIG-IP logs
ssh admin@bigip-01 "tail -f /var/log/apm"
ssh admin@bigip-01 "tail -f /var/log/ltm"
```

### API Response Debugging

```bash
# Test API directly
curl -sk -u admin:admin \
  https://10.1.1.4/mgmt/tm/apm/profile/access \
  | python3 -m json.tool
```

### Session Debugging

```bash
# On BIG-IP, check active sessions
tmsh show apm session

# Check session variables
tmsh show apm session all-properties
```

## Related Documentation

- [API_MAPPING.md](API_MAPPING.md) - API details and workarounds
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Complete API reference
- [CLEANUP_GUIDE.md](CLEANUP_GUIDE.md) - Deletion troubleshooting
