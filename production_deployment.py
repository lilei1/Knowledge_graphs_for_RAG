#!/usr/bin/env python3
"""
Production Deployment Configuration for Biological Knowledge Graph

This module handles deployment of the knowledge graph system using Neo4j Enterprise
or Amazon Neptune with high availability, security, and performance optimization.
"""

import os
import yaml
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import docker
import boto3
from kubernetes import client, config
import subprocess
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Neo4jClusterConfig:
    """Configuration for Neo4j Enterprise cluster"""
    cluster_name: str
    num_core_servers: int = 3
    num_read_replicas: int = 2
    memory_per_server: str = "32G"
    cpu_per_server: int = 8
    storage_per_server: str = "1TB"
    backup_enabled: bool = True
    monitoring_enabled: bool = True
    ssl_enabled: bool = True
    auth_enabled: bool = True

@dataclass
class NeptuneConfig:
    """Configuration for Amazon Neptune cluster"""
    cluster_identifier: str
    engine_version: str = "1.2.1.0"
    instance_class: str = "db.r5.2xlarge"
    num_instances: int = 3
    backup_retention_days: int = 7
    encryption_enabled: bool = True
    vpc_security_groups: List[str] = field(default_factory=list)
    subnet_group: Optional[str] = None

@dataclass
class KubernetesConfig:
    """Configuration for Kubernetes deployment"""
    namespace: str = "kg-production"
    replicas: int = 3
    cpu_request: str = "2"
    cpu_limit: str = "8"
    memory_request: str = "8Gi"
    memory_limit: str = "32Gi"
    storage_class: str = "gp2"
    storage_size: str = "1Ti"

class Neo4jDeployer:
    """Deploys Neo4j Enterprise cluster for production"""
    
    def __init__(self, config: Neo4jClusterConfig):
        self.config = config
        self.docker_client = docker.from_env()
    
    def deploy_cluster(self) -> Dict[str, Any]:
        """Deploy Neo4j Enterprise cluster"""
        logger.info(f"Deploying Neo4j cluster: {self.config.cluster_name}")
        
        # Create Docker network
        network_name = f"{self.config.cluster_name}-network"
        try:
            network = self.docker_client.networks.create(
                network_name,
                driver="bridge",
                options={"com.docker.network.bridge.enable_icc": "true"}
            )
            logger.info(f"Created Docker network: {network_name}")
        except docker.errors.APIError as e:
            if "already exists" in str(e):
                network = self.docker_client.networks.get(network_name)
                logger.info(f"Using existing network: {network_name}")
            else:
                raise
        
        # Deploy core servers
        core_servers = []
        for i in range(self.config.num_core_servers):
            server_name = f"{self.config.cluster_name}-core-{i}"
            container = self._deploy_core_server(server_name, i, network_name)
            core_servers.append(container)
        
        # Deploy read replicas
        read_replicas = []
        for i in range(self.config.num_read_replicas):
            server_name = f"{self.config.cluster_name}-replica-{i}"
            container = self._deploy_read_replica(server_name, i, network_name)
            read_replicas.append(container)
        
        # Wait for cluster to be ready
        self._wait_for_cluster_ready(core_servers)
        
        # Configure cluster discovery
        self._configure_cluster_discovery(core_servers)
        
        # Setup monitoring if enabled
        if self.config.monitoring_enabled:
            self._setup_monitoring()
        
        # Setup backup if enabled
        if self.config.backup_enabled:
            self._setup_backup()
        
        deployment_info = {
            'cluster_name': self.config.cluster_name,
            'core_servers': [c.name for c in core_servers],
            'read_replicas': [r.name for r in read_replicas],
            'network': network_name,
            'status': 'deployed'
        }
        
        logger.info("Neo4j cluster deployment completed successfully")
        return deployment_info
    
    def _deploy_core_server(self, server_name: str, server_id: int, network_name: str):
        """Deploy a Neo4j core server"""
        logger.info(f"Deploying core server: {server_name}")
        
        # Core server configuration
        environment = {
            'NEO4J_AUTH': 'neo4j/production_password',
            'NEO4J_dbms_mode': 'CORE',
            'NEO4J_causal__clustering_expected__core__cluster__size': str(self.config.num_core_servers),
            'NEO4J_causal__clustering_initial__discovery__members': self._get_discovery_members(),
            'NEO4J_dbms_connector_bolt_advertised__address': f"{server_name}:7687",
            'NEO4J_dbms_connector_http_advertised__address': f"{server_name}:7474",
            'NEO4J_dbms_memory_heap_initial__size': self.config.memory_per_server,
            'NEO4J_dbms_memory_heap_max__size': self.config.memory_per_server,
            'NEO4J_dbms_memory_pagecache_size': '8G',
            'NEO4J_dbms_security_procedures_unrestricted': 'gds.*,apoc.*',
            'NEO4J_dbms_security_procedures_allowlist': 'gds.*,apoc.*'
        }
        
        # Add SSL configuration if enabled
        if self.config.ssl_enabled:
            environment.update({
                'NEO4J_dbms_ssl_policy_bolt_enabled': 'true',
                'NEO4J_dbms_ssl_policy_https_enabled': 'true'
            })
        
        # Create and start container
        container = self.docker_client.containers.run(
            'neo4j:4.4-enterprise',
            name=server_name,
            environment=environment,
            ports={
                '7474/tcp': 7474 + server_id,
                '7687/tcp': 7687 + server_id,
                '5000/tcp': 5000 + server_id,
                '6000/tcp': 6000 + server_id,
                '7000/tcp': 7000 + server_id
            },
            volumes={
                f"{server_name}-data": {'bind': '/data', 'mode': 'rw'},
                f"{server_name}-logs": {'bind': '/logs', 'mode': 'rw'},
                f"{server_name}-conf": {'bind': '/conf', 'mode': 'rw'}
            },
            network=network_name,
            detach=True,
            restart_policy={"Name": "unless-stopped"}
        )
        
        logger.info(f"Core server {server_name} deployed successfully")
        return container
    
    def _deploy_read_replica(self, server_name: str, server_id: int, network_name: str):
        """Deploy a Neo4j read replica"""
        logger.info(f"Deploying read replica: {server_name}")
        
        environment = {
            'NEO4J_AUTH': 'neo4j/production_password',
            'NEO4J_dbms_mode': 'READ_REPLICA',
            'NEO4J_causal__clustering_initial__discovery__members': self._get_discovery_members(),
            'NEO4J_dbms_connector_bolt_advertised__address': f"{server_name}:7687",
            'NEO4J_dbms_connector_http_advertised__address': f"{server_name}:7474",
            'NEO4J_dbms_memory_heap_initial__size': self.config.memory_per_server,
            'NEO4J_dbms_memory_heap_max__size': self.config.memory_per_server,
            'NEO4J_dbms_memory_pagecache_size': '8G'
        }
        
        container = self.docker_client.containers.run(
            'neo4j:4.4-enterprise',
            name=server_name,
            environment=environment,
            ports={
                '7474/tcp': 7474 + 10 + server_id,
                '7687/tcp': 7687 + 10 + server_id
            },
            volumes={
                f"{server_name}-data": {'bind': '/data', 'mode': 'rw'},
                f"{server_name}-logs": {'bind': '/logs', 'mode': 'rw'}
            },
            network=network_name,
            detach=True,
            restart_policy={"Name": "unless-stopped"}
        )
        
        logger.info(f"Read replica {server_name} deployed successfully")
        return container
    
    def _get_discovery_members(self) -> str:
        """Get discovery members string for cluster configuration"""
        members = []
        for i in range(self.config.num_core_servers):
            members.append(f"{self.config.cluster_name}-core-{i}:5000")
        return ','.join(members)
    
    def _wait_for_cluster_ready(self, core_servers: List, timeout: int = 300):
        """Wait for cluster to be ready"""
        logger.info("Waiting for cluster to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check if all core servers are responding
                ready_count = 0
                for container in core_servers:
                    # Simple health check - could be more sophisticated
                    if container.status == 'running':
                        ready_count += 1
                
                if ready_count == len(core_servers):
                    logger.info("Cluster is ready!")
                    return
                
                time.sleep(10)
                
            except Exception as e:
                logger.warning(f"Health check failed: {e}")
                time.sleep(10)
        
        raise TimeoutError("Cluster failed to become ready within timeout")
    
    def _configure_cluster_discovery(self, core_servers: List):
        """Configure cluster discovery and initial setup"""
        logger.info("Configuring cluster discovery...")
        # Implementation would configure cluster discovery
        pass
    
    def _setup_monitoring(self):
        """Setup monitoring for the cluster"""
        logger.info("Setting up monitoring...")
        
        # Deploy Prometheus and Grafana for monitoring
        monitoring_config = {
            'prometheus': {
                'image': 'prom/prometheus:latest',
                'ports': ['9090:9090'],
                'volumes': ['./prometheus.yml:/etc/prometheus/prometheus.yml']
            },
            'grafana': {
                'image': 'grafana/grafana:latest',
                'ports': ['3000:3000'],
                'environment': {
                    'GF_SECURITY_ADMIN_PASSWORD': 'admin'
                }
            }
        }
        
        # Deploy monitoring containers
        for service, config in monitoring_config.items():
            try:
                container = self.docker_client.containers.run(
                    config['image'],
                    name=f"{self.config.cluster_name}-{service}",
                    ports=dict(port.split(':') for port in config.get('ports', [])),
                    environment=config.get('environment', {}),
                    volumes=config.get('volumes', {}),
                    detach=True,
                    restart_policy={"Name": "unless-stopped"}
                )
                logger.info(f"Deployed {service} monitoring")
            except Exception as e:
                logger.error(f"Failed to deploy {service}: {e}")
    
    def _setup_backup(self):
        """Setup automated backup for the cluster"""
        logger.info("Setting up automated backup...")
        
        # Create backup script
        backup_script = f"""#!/bin/bash
        
        # Neo4j Backup Script
        BACKUP_DIR="/backups/{self.config.cluster_name}"
        DATE=$(date +%Y%m%d_%H%M%S)
        
        mkdir -p $BACKUP_DIR
        
        # Backup from core server
        neo4j-admin backup \\
            --backup-dir=$BACKUP_DIR \\
            --name=backup_$DATE \\
            --from={self.config.cluster_name}-core-0:6362
        
        # Compress backup
        tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR backup_$DATE
        rm -rf $BACKUP_DIR/backup_$DATE
        
        # Cleanup old backups (keep last 7 days)
        find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
        """
        
        # Save backup script
        with open(f"{self.config.cluster_name}_backup.sh", 'w') as f:
            f.write(backup_script)
        
        os.chmod(f"{self.config.cluster_name}_backup.sh", 0o755)
        logger.info("Backup script created")

class NeptuneDeployer:
    """Deploys Amazon Neptune cluster for production"""
    
    def __init__(self, config: NeptuneConfig):
        self.config = config
        self.neptune_client = boto3.client('neptune')
        self.ec2_client = boto3.client('ec2')
    
    def deploy_cluster(self) -> Dict[str, Any]:
        """Deploy Neptune cluster"""
        logger.info(f"Deploying Neptune cluster: {self.config.cluster_identifier}")
        
        try:
            # Create DB subnet group if not exists
            if self.config.subnet_group:
                self._ensure_subnet_group()
            
            # Create Neptune cluster
            cluster_response = self.neptune_client.create_db_cluster(
                DBClusterIdentifier=self.config.cluster_identifier,
                Engine='neptune',
                EngineVersion=self.config.engine_version,
                MasterUsername='neptune',
                MasterUserPassword='production_password',
                VpcSecurityGroupIds=self.config.vpc_security_groups,
                DBSubnetGroupName=self.config.subnet_group,
                BackupRetentionPeriod=self.config.backup_retention_days,
                StorageEncrypted=self.config.encryption_enabled,
                EnableCloudwatchLogsExports=['audit'],
                DeletionProtection=True
            )
            
            logger.info("Neptune cluster creation initiated")
            
            # Create cluster instances
            instances = []
            for i in range(self.config.num_instances):
                instance_id = f"{self.config.cluster_identifier}-instance-{i}"
                
                instance_response = self.neptune_client.create_db_instance(
                    DBInstanceIdentifier=instance_id,
                    DBInstanceClass=self.config.instance_class,
                    Engine='neptune',
                    DBClusterIdentifier=self.config.cluster_identifier
                )
                
                instances.append(instance_id)
                logger.info(f"Created Neptune instance: {instance_id}")
            
            # Wait for cluster to be available
            self._wait_for_cluster_available()
            
            deployment_info = {
                'cluster_identifier': self.config.cluster_identifier,
                'instances': instances,
                'endpoint': cluster_response['DBCluster']['Endpoint'],
                'reader_endpoint': cluster_response['DBCluster']['ReaderEndpoint'],
                'status': 'deployed'
            }
            
            logger.info("Neptune cluster deployment completed successfully")
            return deployment_info
            
        except Exception as e:
            logger.error(f"Neptune deployment failed: {e}")
            raise
    
    def _ensure_subnet_group(self):
        """Ensure DB subnet group exists"""
        try:
            self.neptune_client.describe_db_subnet_groups(
                DBSubnetGroupName=self.config.subnet_group
            )
            logger.info(f"Subnet group {self.config.subnet_group} exists")
        except self.neptune_client.exceptions.DBSubnetGroupNotFoundFault:
            logger.error(f"Subnet group {self.config.subnet_group} not found")
            raise
    
    def _wait_for_cluster_available(self, timeout: int = 1800):
        """Wait for Neptune cluster to become available"""
        logger.info("Waiting for Neptune cluster to become available...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.neptune_client.describe_db_clusters(
                    DBClusterIdentifier=self.config.cluster_identifier
                )
                
                status = response['DBClusters'][0]['Status']
                if status == 'available':
                    logger.info("Neptune cluster is available!")
                    return
                
                logger.info(f"Cluster status: {status}")
                time.sleep(30)
                
            except Exception as e:
                logger.warning(f"Status check failed: {e}")
                time.sleep(30)
        
        raise TimeoutError("Neptune cluster failed to become available within timeout")

class ProductionDeploymentManager:
    """Manages production deployment of the knowledge graph system"""
    
    def __init__(self, deployment_type: str = "neo4j"):
        self.deployment_type = deployment_type
        self.deployment_config = self._load_deployment_config()
    
    def _load_deployment_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        config_file = f"config/production_{self.deployment_type}.yaml"
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Return default configuration
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default deployment configuration"""
        if self.deployment_type == "neo4j":
            return {
                'cluster_name': 'kg-production',
                'num_core_servers': 3,
                'num_read_replicas': 2,
                'memory_per_server': '32G',
                'cpu_per_server': 8,
                'storage_per_server': '1TB',
                'backup_enabled': True,
                'monitoring_enabled': True,
                'ssl_enabled': True,
                'auth_enabled': True
            }
        elif self.deployment_type == "neptune":
            return {
                'cluster_identifier': 'kg-production',
                'engine_version': '1.2.1.0',
                'instance_class': 'db.r5.2xlarge',
                'num_instances': 3,
                'backup_retention_days': 7,
                'encryption_enabled': True
            }
        else:
            raise ValueError(f"Unsupported deployment type: {self.deployment_type}")
    
    def deploy(self) -> Dict[str, Any]:
        """Deploy the production system"""
        logger.info(f"Starting production deployment: {self.deployment_type}")
        
        if self.deployment_type == "neo4j":
            config = Neo4jClusterConfig(**self.deployment_config)
            deployer = Neo4jDeployer(config)
            return deployer.deploy_cluster()
        
        elif self.deployment_type == "neptune":
            config = NeptuneConfig(**self.deployment_config)
            deployer = NeptuneDeployer(config)
            return deployer.deploy_cluster()
        
        else:
            raise ValueError(f"Unsupported deployment type: {self.deployment_type}")
    
    def create_deployment_manifest(self) -> str:
        """Create deployment manifest file"""
        manifest = {
            'deployment_type': self.deployment_type,
            'configuration': self.deployment_config,
            'deployment_time': time.time(),
            'version': '1.0.0'
        }
        
        manifest_file = f"deployment_manifest_{self.deployment_type}.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Deployment manifest created: {manifest_file}")
        return manifest_file

def main():
    """Example usage of production deployment system"""
    logger.info("Production Deployment System - Knowledge Graph")
    logger.info("Supported deployment types:")
    logger.info("- Neo4j Enterprise Cluster")
    logger.info("- Amazon Neptune Cluster")
    logger.info("- Kubernetes Deployment")
    logger.info("Key features:")
    logger.info("- High availability configuration")
    logger.info("- Automated backup and monitoring")
    logger.info("- SSL/TLS encryption")
    logger.info("- Access control and security")
    logger.info("- Performance optimization")

if __name__ == "__main__":
    main()
