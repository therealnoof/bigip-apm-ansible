#!/usr/bin/env python3
"""
F5 BIG-IP APM API Client Example

Demonstrates how to use the REST API to deploy APM solutions.
"""
import requests
import json
import time
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
BIGIP_HOST = "10.1.1.4"
BIGIP_USERNAME = "admin"
BIGIP_PASSWORD = "admin"


def deploy_vpn_solution() -> Dict[str, Any]:
    """Deploy Solution 1: VPN with Network Access"""
    print("=" * 60)
    print("Deploying Solution 1: VPN with Network Access")
    print("=" * 60)

    payload = {
        "credentials": {
            "host": BIGIP_HOST,
            "username": BIGIP_USERNAME,
            "password": BIGIP_PASSWORD
        },
        "solution_name": "my-vpn-solution",
        "dns_name": "vpn.example.com",
        "customization_type": "modern",
        "ad_config": {
            "ip": "10.1.20.7",
            "port": 389,
            "domain": "f5lab.local",
            "admin_user": "admin",
            "admin_password": "admin"
        },
        "vpn_config": {
            "lease_pool_start": "10.1.2.1",
            "lease_pool_end": "10.1.2.254",
            "split_tunnel_networks": [
                "10.1.10.0/24",
                "10.1.20.0/24"
            ],
            "enable_compression": True,
            "enable_dtls": True
        },
        "create_connectivity_profile": True,
        "create_network_access": True,
        "create_webtop": True,
        "deploy_as3": False
    }

    print("\nPayload:")
    print(json.dumps(payload, indent=2))

    response = requests.post(
        f"{API_BASE_URL}/deploy/solution1",
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        print("\n✓ Deployment initiated successfully")
        print(f"Deployment ID: {result['deployment_id']}")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        return result
    else:
        print(f"\n✗ Deployment failed: {response.status_code}")
        print(response.json())
        return {}


def deploy_portal_solution() -> Dict[str, Any]:
    """Deploy Solution 2: Portal Access with AD Group Mapping"""
    print("\n" + "=" * 60)
    print("Deploying Solution 2: Portal Access with AD Groups")
    print("=" * 60)

    payload = {
        "credentials": {
            "host": BIGIP_HOST,
            "username": BIGIP_USERNAME,
            "password": BIGIP_PASSWORD
        },
        "solution_name": "my-portal-solution",
        "dns_name": "portal.example.com",
        "customization_type": "modern",
        "ad_config": {
            "ip": "10.1.20.7",
            "port": 389,
            "domain": "f5lab.local",
            "admin_user": "admin",
            "admin_password": "admin"
        },
        "portal_resources": [
            {
                "name": "server1",
                "application_uri": "https://server1.example.com",
                "caption": "Application Server 1",
                "description": "Internal application server 1"
            },
            {
                "name": "server2",
                "application_uri": "https://server2.example.com",
                "caption": "Application Server 2",
                "description": "Internal application server 2"
            }
        ],
        "ad_group_mappings": [
            {
                "expression": 'expr { [string tolower [mcget -decode {session.ad.last.attr.memberOf}]] contains [string tolower "CN=Sales,CN=Users,DC=f5lab,DC=local"] }',
                "description": "Sales team - server1 access",
                "portal_access_resources": ["/Common/my-portal-solution-server1"],
                "webtop": "/Common/my-portal-solution-webtop"
            },
            {
                "expression": 'expr { [string tolower [mcget -decode {session.ad.last.attr.memberOf}]] contains [string tolower "CN=Engineering,CN=Users,DC=f5lab,DC=local"] }',
                "description": "Engineering team - all servers",
                "portal_access_resources": [
                    "/Common/my-portal-solution-server1",
                    "/Common/my-portal-solution-server2"
                ],
                "webtop": "/Common/my-portal-solution-webtop"
            }
        ],
        "create_network_access": False,
        "create_webtop": True,
        "deploy_as3": False
    }

    print("\nPayload:")
    print(json.dumps(payload, indent=2))

    response = requests.post(
        f"{API_BASE_URL}/deploy/solution2",
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        print("\n✓ Deployment initiated successfully")
        print(f"Deployment ID: {result['deployment_id']}")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        return result
    else:
        print(f"\n✗ Deployment failed: {response.status_code}")
        print(response.json())
        return {}


def check_deployment_status(deployment_id: str):
    """Check deployment status"""
    print(f"\nChecking status for deployment: {deployment_id}")

    response = requests.get(f"{API_BASE_URL}/deploy/{deployment_id}")

    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")

        if result.get('tasks'):
            print("\nTasks:")
            for task in result['tasks']:
                print(f"  - {task['task_name']}: {task['status']}")

        if result.get('created_resources'):
            print("\nCreated Resources:")
            for resource_type, resources in result['created_resources'].items():
                print(f"  {resource_type}:")
                for resource in resources:
                    print(f"    - {resource}")
    else:
        print(f"Failed to get status: {response.status_code}")


def delete_solution(solution_name: str):
    """Delete a deployed solution"""
    print(f"\nDeleting solution: {solution_name}")

    payload = {
        "credentials": {
            "host": BIGIP_HOST,
            "username": BIGIP_USERNAME,
            "password": BIGIP_PASSWORD
        },
        "solution_name": solution_name,
        "confirm": True
    }

    response = requests.delete(
        f"{API_BASE_URL}/deploy/{solution_name}",
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Deletion initiated")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
    else:
        print(f"✗ Deletion failed: {response.status_code}")
        print(response.json())


def list_deployments():
    """List all deployments"""
    print("\nListing all deployments:")

    response = requests.get(f"{API_BASE_URL}/deployments")

    if response.status_code == 200:
        result = response.json()
        print(f"\nTotal deployments: {result['total']}")

        for deployment in result.get('deployments', []):
            print(f"\n  - {deployment['solution_name']}")
            print(f"    ID: {deployment['deployment_id']}")
            print(f"    Type: {deployment['solution_type']}")
            print(f"    Status: {deployment['status']}")
    else:
        print(f"Failed to list deployments: {response.status_code}")


def health_check():
    """Check API health"""
    print("Checking API health...")

    response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ API is {result['status']}")
        print(f"  Version: {result['version']}")
        print(f"  Uptime: {result['uptime_seconds']:.2f} seconds")
    else:
        print(f"✗ API health check failed: {response.status_code}")


def main():
    """Main execution"""
    print("F5 BIG-IP APM API Client Example")
    print("=" * 60)

    # Health check
    health_check()

    # Example 1: Deploy VPN solution
    vpn_deployment = deploy_vpn_solution()

    if vpn_deployment:
        time.sleep(1)
        check_deployment_status(vpn_deployment['deployment_id'])

    # Example 2: Deploy Portal solution
    portal_deployment = deploy_portal_solution()

    if portal_deployment:
        time.sleep(1)
        check_deployment_status(portal_deployment['deployment_id'])

    # List all deployments
    time.sleep(1)
    list_deployments()

    # Example 3: Delete a solution (commented out for safety)
    # delete_solution("my-vpn-solution")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("\nNote: This is a stub API. For actual deployments, use:")
    print("  ansible-playbook deploy_apm_vpn.yml")
    print("  ansible-playbook deploy_apm_portal.yml")
    print("=" * 60)


if __name__ == "__main__":
    main()
