"""
ANPTOP Backend - Kubernetes Security Models
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from app.db.base import Base


class KubernetesCluster(Base):
    """Kubernetes cluster information."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Cluster identification
    cluster_name = Column(String(200), nullable=False)
    cluster_id = Column(String(200), nullable=True)  # UID from K8s
    api_server = Column(String(500), nullable=True)
    
    # Cloud provider (if applicable)
    provider = Column(String(50), nullable=True)  # AWS (EKS), Azure (AKS), GCP (GKE), Self-hosted
    
    # Context information
    context_name = Column(String(200), nullable=True)
    namespace = Column(String(200), nullable=True)
    
    # Access credentials
    kubeconfig = Column(Text, nullable=True)  # Base64 encoded kubeconfig
    access_method = Column(String(50), nullable=True)  # in-cluster, local-kubeconfig, service-account
    
    # Discovery method
    discovery_tool = Column(String(100), default="kubectl")  # kubectl, kube-hunter, kube-bench
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="kubernetes_clusters")
    
    def __repr__(self):
        return f"<KubernetesCluster {self.cluster_name}>"


class KubernetesFinding(Base):
    """Kubernetes security finding model."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Cluster reference
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id"), nullable=True)
    
    # Finding categorization
    category = Column(String(50), nullable=False)  # 
    severity = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Affected resource
    resource_type = Column(String(100), nullable=True)  # Pod, Deployment, Service, ConfigMap, Secret, etc.
    resource_name = Column(String(200), nullable=True)
    namespace = Column(String(100), nullable=True)
    
    # K8s specific
    k8s_kind = Column(String(100), nullable=True)  # kind field from K8s manifest
    pod_name = Column(String(200), nullable=True)
    container_name = Column(String(200), nullable=True)
    
    # Finding type (from kube-hunter)
    vulnerability_type = Column(String(100), nullable=True)  # remote_execution, privilege_escalation, etc.
    cve_id = Column(String(20), nullable=True)
    
    # Evidence
    yaml_manifest = Column(Text, nullable=True)
    evidence_data = Column(JSON, nullable=True)
    screenshots = Column(JSON, nullable=True)
    
    # Remediation
    remediation = Column(Text, nullable=True)
    remediation_command = Column(Text, nullable=True)  # Example kubectl command
    
    # CIS Benchmark
    cis_benchmark_id = Column(String(50), nullable=True)  # e.g., "1.1.1"
    cis_benchmark_description = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(20), default="open")
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="kubernetes_findings")
    
    def __repr__(self):
        return f"<KubernetesFinding {self.category}:{self.severity}>"


class KubernetesPod(Base):
    """Kubernetes pod inventory for assessment."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id"), nullable=True)
    
    pod_name = Column(String(200), nullable=False)
    namespace = Column(String(100), nullable=True)
    node_name = Column(String(200), nullable=True)
    
    # Pod spec
    pod_ip = Column(String(50), nullable=True)
    service_account = Column(String(200), nullable=True)
    containers = Column(JSON, nullable=True)
    
    # Security context
    privileged = Column(Boolean, default=False)
    host_network = Column(Boolean, default=False)
    host_pid = Column(Boolean, default=False)
    host_ipc = Column(Boolean, default=False)
    
    # Capabilities
    capabilities = Column(JSON, nullable=True)
    
    # Mounts
    volume_mounts = Column(JSON, nullable=True)
    host_path_mounts = Column(JSON, nullable=True)
    
    # Discovery
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="kubernetes_pods")
    
    def __repr__(self):
        return f"<KubernetesPod {self.namespace}:{self.pod_name}>"
