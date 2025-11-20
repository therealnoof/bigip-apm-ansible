"""
Pydantic models for F5 BIG-IP APM API
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class SolutionType(str, Enum):
    """APM solution types"""
    VPN = "vpn"
    PORTAL = "portal"


class CustomizationType(str, Enum):
    """Customization theme types"""
    MODERN = "modern"
    STANDARD = "standard"


class BIGIPCredentials(BaseModel):
    """BIG-IP connection credentials"""
    host: str = Field(..., description="BIG-IP management IP or hostname")
    port: int = Field(443, description="Management port")
    username: str = Field("admin", description="Admin username")
    password: str = Field(..., description="Admin password")
    validate_certs: bool = Field(False, description="Validate SSL certificates")


class ADServerConfig(BaseModel):
    """Active Directory server configuration"""
    ip: str = Field(..., description="AD server IP address")
    port: int = Field(389, description="LDAP port")
    domain: str = Field(..., description="AD domain (e.g., f5lab.local)")
    admin_user: str = Field(..., description="AD admin username")
    admin_password: str = Field(..., description="AD admin password")


class VPNConfig(BaseModel):
    """VPN/Network Access configuration"""
    lease_pool_start: str = Field(..., description="Start IP for VPN pool")
    lease_pool_end: str = Field(..., description="End IP for VPN pool")
    split_tunnel_networks: List[str] = Field(
        default=["10.1.10.0/24", "10.1.20.0/24"],
        description="Networks to include in split tunnel"
    )
    enable_compression: bool = Field(True, description="Enable VPN compression")
    enable_dtls: bool = Field(True, description="Enable DTLS")


class PortalResourceItem(BaseModel):
    """Portal resource item configuration"""
    name: str
    host: str
    port: int = 443
    scheme: str = "https"
    paths: str = "/*"
    home_tab: bool = True
    compression_type: str = "gzip"


class PortalResource(BaseModel):
    """Portal access resource"""
    name: str = Field(..., description="Resource name")
    application_uri: str = Field(..., description="Backend application URL")
    caption: Optional[str] = Field(None, description="Display name")
    description: Optional[str] = Field(None, description="Resource description")
    css_patching: bool = Field(True)
    html_patching: bool = Field(True)
    javascript_patching: bool = Field(True)
    items: List[PortalResourceItem] = Field(default_factory=list)

    @validator('caption', always=True)
    def set_caption(cls, v, values):
        return v or values.get('name')


class ADGroupMapping(BaseModel):
    """AD group to resource mapping"""
    expression: str = Field(..., description="TCL expression for group matching")
    description: str = Field(..., description="Mapping description")
    portal_access_resources: Optional[List[str]] = Field(default=None)
    network_access_resources: Optional[List[str]] = Field(default=None)
    webtop: str = Field(..., description="Webtop resource path")
    webtop_sections: Optional[List[str]] = Field(default=None)


class Solution1Request(BaseModel):
    """Solution 1: VPN with Network Access deployment request"""
    credentials: BIGIPCredentials
    solution_name: str = Field("solution1", description="Solution/prefix name")
    dns_name: str = Field("solution1.acme.com", description="DNS hostname")
    customization_type: CustomizationType = CustomizationType.MODERN

    # AD Configuration
    ad_config: ADServerConfig

    # VPN Configuration
    vpn_config: VPNConfig

    # Feature flags
    create_connectivity_profile: bool = True
    create_network_access: bool = True
    create_webtop: bool = True
    deploy_as3: bool = False

    # Optional AS3 config
    as3_virtual_ip: Optional[str] = None
    as3_virtual_port: int = 443


class Solution2Request(BaseModel):
    """Solution 2: Portal Access with AD Group Mapping deployment request"""
    credentials: BIGIPCredentials
    solution_name: str = Field("solution2", description="Solution/prefix name")
    dns_name: str = Field("solution2.acme.com", description="DNS hostname")
    customization_type: CustomizationType = CustomizationType.MODERN

    # AD Configuration
    ad_config: ADServerConfig

    # Portal Resources
    portal_resources: List[PortalResource]

    # AD Group Mappings
    ad_group_mappings: List[ADGroupMapping]

    # Optional VPN
    vpn_config: Optional[VPNConfig] = None

    # Feature flags
    create_network_access: bool = False
    create_webtop: bool = True
    deploy_as3: bool = False

    # Optional AS3 config
    as3_virtual_ip: Optional[str] = None
    as3_virtual_port: int = 443


class DeploymentStatus(str, Enum):
    """Deployment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskResult(BaseModel):
    """Individual task result"""
    task_name: str
    status: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class DeploymentResponse(BaseModel):
    """Deployment response"""
    deployment_id: str
    solution_type: SolutionType
    solution_name: str
    status: DeploymentStatus
    message: str
    tasks: List[TaskResult] = Field(default_factory=list)
    created_resources: Dict[str, List[str]] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class DeleteRequest(BaseModel):
    """Deletion request"""
    credentials: BIGIPCredentials
    solution_name: str = Field(..., description="Solution name to delete")
    confirm: bool = Field(False, description="Confirmation flag")


class DeleteResponse(BaseModel):
    """Deletion response"""
    solution_name: str
    status: DeploymentStatus
    message: str
    deleted_resources: Dict[str, List[str]] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """API health check response"""
    status: str
    version: str
    uptime_seconds: float


class BIGIPInfo(BaseModel):
    """BIG-IP system information"""
    version: str
    build: str
    hostname: Optional[str] = None
    platform: Optional[str] = None
    as3_installed: bool
    as3_version: Optional[str] = None
