#!/usr/bin/env python3
"""
Production Knowledge Graph System - Main Integration Module

This is the main orchestration module that integrates all components of the
production-ready biological knowledge graph system for scaled applications.
"""

import os
import sys
import logging
import argparse
import json
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
from pathlib import Path

# Import all production modules
from production_schema import ProductionSchema, NodeType, RelationshipType
from vcf_integration import VCFProcessor
from phenotype_normalization import PhenotypeProcessor, CropOntologyClient
from environmental_integration import EnvironmentalIntegrator
from gnn_inference import GNNInferenceEngine, GNNConfig
from production_deployment import ProductionDeploymentManager
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_kg.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionKGSystem:
    """Main production knowledge graph system orchestrator"""
    
    def __init__(self, config_file: str = "config/production_config.yaml"):
        """Initialize the production system"""
        self.config = self._load_config(config_file)
        self.neo4j_driver = None
        self.schema = ProductionSchema()
        
        # Initialize components
        self.vcf_processor = None
        self.phenotype_processor = None
        self.environmental_integrator = None
        self.gnn_engine = None
        self.deployment_manager = None
        
        logger.info("Production Knowledge Graph System initialized")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load system configuration"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_file}")
        else:
            # Default configuration
            config = {
                'neo4j': {
                    'uri': 'bolt://localhost:7687',
                    'username': 'neo4j',
                    'password': 'password',
                    'database': 'neo4j'
                },
                'data_sources': {
                    'vcf_directory': 'data/vcf/',
                    'phenotype_directory': 'data/phenotypes/',
                    'environmental_directory': 'data/environment/'
                },
                'processing': {
                    'batch_size': 10000,
                    'max_variants_per_file': None,
                    'parallel_workers': 4
                },
                'gnn': {
                    'hidden_dim': 128,
                    'num_layers': 3,
                    'dropout': 0.2,
                    'learning_rate': 0.001,
                    'num_epochs': 100
                },
                'deployment': {
                    'type': 'neo4j',  # or 'neptune'
                    'environment': 'production'
                }
            }
            logger.info("Using default configuration")
        
        return config
    
    def initialize_database(self) -> None:
        """Initialize database connection and schema"""
        logger.info("Initializing database connection...")
        
        neo4j_config = self.config['neo4j']
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_config['uri'],
            auth=(neo4j_config['username'], neo4j_config['password'])
        )
        
        # Test connection
        with self.neo4j_driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single()['test'] == 1:
                logger.info("Database connection successful")
            else:
                raise ConnectionError("Database connection test failed")
        
        # Create schema constraints and indexes
        self.schema.create_schema_constraints(self.neo4j_driver)
        logger.info("Database schema initialized")
    
    def initialize_components(self) -> None:
        """Initialize all system components"""
        logger.info("Initializing system components...")
        
        # Initialize VCF processor
        self.vcf_processor = VCFProcessor(
            neo4j_driver=self.neo4j_driver,
            batch_size=self.config['processing']['batch_size']
        )
        
        # Initialize phenotype processor
        self.phenotype_processor = PhenotypeProcessor(
            neo4j_driver=self.neo4j_driver
        )
        
        # Initialize environmental integrator
        self.environmental_integrator = EnvironmentalIntegrator(
            neo4j_driver=self.neo4j_driver
        )
        
        # Initialize GNN engine
        gnn_config = GNNConfig(**self.config['gnn'])
        self.gnn_engine = GNNInferenceEngine(
            neo4j_driver=self.neo4j_driver,
            config=gnn_config
        )
        
        # Initialize deployment manager
        self.deployment_manager = ProductionDeploymentManager(
            deployment_type=self.config['deployment']['type']
        )
        
        logger.info("All components initialized successfully")
    
    def process_vcf_data(self, vcf_directory: Optional[str] = None) -> Dict[str, Any]:
        """Process all VCF files in the specified directory"""
        vcf_dir = vcf_directory or self.config['data_sources']['vcf_directory']
        logger.info(f"Processing VCF data from {vcf_dir}")
        
        vcf_files = list(Path(vcf_dir).glob("*.vcf*"))
        if not vcf_files:
            logger.warning(f"No VCF files found in {vcf_dir}")
            return {'processed_files': 0, 'total_variants': 0}
        
        total_stats = {'processed_files': 0, 'total_variants': 0, 'total_genotypes': 0}
        
        for vcf_file in vcf_files:
            logger.info(f"Processing VCF file: {vcf_file}")
            
            try:
                # Parse header to get samples
                samples, metadata = self.vcf_processor.parse_vcf_header(str(vcf_file))
                
                # Create germplasm nodes for samples
                self.vcf_processor.create_germplasm_nodes_from_samples(samples)
                
                # Process VCF file
                stats = self.vcf_processor.process_vcf_file(
                    str(vcf_file),
                    max_variants=self.config['processing']['max_variants_per_file']
                )
                
                total_stats['processed_files'] += 1
                total_stats['total_variants'] += stats.total_variants
                total_stats['total_genotypes'] += stats.total_genotypes
                
                logger.info(f"Completed processing {vcf_file}: "
                           f"{stats.total_variants} variants, {stats.total_genotypes} genotypes")
                
            except Exception as e:
                logger.error(f"Failed to process {vcf_file}: {e}")
                continue
        
        logger.info(f"VCF processing complete: {total_stats}")
        return total_stats
    
    def process_phenotype_data(self, phenotype_directory: Optional[str] = None) -> Dict[str, Any]:
        """Process all phenotype files in the specified directory"""
        pheno_dir = phenotype_directory or self.config['data_sources']['phenotype_directory']
        logger.info(f"Processing phenotype data from {pheno_dir}")
        
        phenotype_files = list(Path(pheno_dir).glob("*.csv"))
        if not phenotype_files:
            logger.warning(f"No phenotype files found in {pheno_dir}")
            return {'processed_files': 0, 'total_measurements': 0}
        
        total_measurements = 0
        processed_files = 0
        
        for pheno_file in phenotype_files:
            logger.info(f"Processing phenotype file: {pheno_file}")
            
            try:
                # Determine format (wide vs long) based on file structure
                df = pd.read_csv(pheno_file)
                format_type = "wide" if "germplasm_id" in df.columns and len(df.columns) > 5 else "long"
                
                # Process phenotype file
                measurements = self.phenotype_processor.process_phenotype_file(
                    str(pheno_file), 
                    format_type=format_type
                )
                
                # Create time-series measurements in graph
                self.phenotype_processor.create_time_series_measurements(measurements)
                
                total_measurements += len(measurements)
                processed_files += 1
                
                logger.info(f"Completed processing {pheno_file}: {len(measurements)} measurements")
                
            except Exception as e:
                logger.error(f"Failed to process {pheno_file}: {e}")
                continue
        
        stats = {'processed_files': processed_files, 'total_measurements': total_measurements}
        logger.info(f"Phenotype processing complete: {stats}")
        return stats
    
    def process_environmental_data(self, environmental_directory: Optional[str] = None) -> Dict[str, Any]:
        """Process environmental data"""
        env_dir = environmental_directory or self.config['data_sources']['environmental_directory']
        logger.info(f"Processing environmental data from {env_dir}")
        
        # For demonstration, process some example locations
        example_locations = [
            {'name': 'Ames_Iowa', 'lat': 42.0308, 'lon': -93.6319},
            {'name': 'Lincoln_Nebraska', 'lat': 40.8136, 'lon': -96.7026},
            {'name': 'Urbana_Illinois', 'lat': 40.1106, 'lon': -88.2073}
        ]
        
        processed_locations = 0
        
        for location in example_locations:
            try:
                # Process environmental profile for location
                start_date = datetime(2020, 1, 1)
                end_date = datetime(2023, 12, 31)
                
                profile = self.environmental_integrator.process_location(
                    location['name'],
                    location['lat'],
                    location['lon'],
                    start_date,
                    end_date
                )
                
                # Integrate into knowledge graph
                self.environmental_integrator.integrate_environmental_profile(profile)
                
                processed_locations += 1
                logger.info(f"Processed environmental data for {location['name']}")
                
            except Exception as e:
                logger.error(f"Failed to process environmental data for {location['name']}: {e}")
                continue
        
        stats = {'processed_locations': processed_locations}
        logger.info(f"Environmental processing complete: {stats}")
        return stats
    
    def train_gnn_models(self) -> Dict[str, Any]:
        """Train Graph Neural Network models"""
        logger.info("Training GNN models...")
        
        try:
            # Initialize and train models
            self.gnn_engine.initialize_models()
            
            # Save trained models
            model_dir = "models/production"
            os.makedirs(model_dir, exist_ok=True)
            self.gnn_engine.save_models(model_dir)
            
            stats = {'status': 'success', 'model_dir': model_dir}
            logger.info("GNN model training completed successfully")
            return stats
            
        except Exception as e:
            logger.error(f"GNN model training failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def generate_predictions(self, gene_ids: List[str], trait_ids: List[str]) -> List[Dict]:
        """Generate gene-trait association predictions"""
        logger.info(f"Generating predictions for {len(gene_ids)} genes and {len(trait_ids)} traits")
        
        try:
            predictions = self.gnn_engine.predict_gene_trait_associations(gene_ids, trait_ids)
            
            # Convert to serializable format
            prediction_data = []
            for pred in predictions:
                prediction_data.append({
                    'gene_id': pred.source_id,
                    'trait_id': pred.target_id,
                    'prediction_score': pred.prediction_score,
                    'confidence': pred.confidence,
                    'prediction_type': pred.prediction_type
                })
            
            logger.info(f"Generated {len(prediction_data)} predictions")
            return prediction_data
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return []
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete production pipeline"""
        logger.info("Starting full production pipeline...")
        
        pipeline_stats = {
            'start_time': datetime.now().isoformat(),
            'stages': {}
        }
        
        try:
            # Stage 1: Initialize system
            self.initialize_database()
            self.initialize_components()
            pipeline_stats['stages']['initialization'] = {'status': 'success'}
            
            # Stage 2: Process VCF data
            vcf_stats = self.process_vcf_data()
            pipeline_stats['stages']['vcf_processing'] = vcf_stats
            
            # Stage 3: Process phenotype data
            pheno_stats = self.process_phenotype_data()
            pipeline_stats['stages']['phenotype_processing'] = pheno_stats
            
            # Stage 4: Process environmental data
            env_stats = self.process_environmental_data()
            pipeline_stats['stages']['environmental_processing'] = env_stats
            
            # Stage 5: Train GNN models
            gnn_stats = self.train_gnn_models()
            pipeline_stats['stages']['gnn_training'] = gnn_stats
            
            pipeline_stats['end_time'] = datetime.now().isoformat()
            pipeline_stats['status'] = 'success'
            
            logger.info("Full production pipeline completed successfully")
            
        except Exception as e:
            pipeline_stats['end_time'] = datetime.now().isoformat()
            pipeline_stats['status'] = 'failed'
            pipeline_stats['error'] = str(e)
            logger.error(f"Production pipeline failed: {e}")
        
        finally:
            if self.neo4j_driver:
                self.neo4j_driver.close()
        
        return pipeline_stats
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and statistics"""
        logger.info("Retrieving system status...")
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'database_status': 'unknown',
            'node_counts': {},
            'relationship_counts': {},
            'model_status': 'unknown'
        }
        
        try:
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    # Check database connectivity
                    session.run("RETURN 1")
                    status['database_status'] = 'connected'
                    
                    # Get node counts
                    for node_type in NodeType:
                        result = session.run(f"MATCH (n:{node_type.value}) RETURN count(n) as count")
                        count = result.single()['count']
                        status['node_counts'][node_type.value] = count
                    
                    # Get relationship counts
                    result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count")
                    for record in result:
                        status['relationship_counts'][record['rel_type']] = record['count']
            
            # Check model status
            model_dir = "models/production"
            if os.path.exists(model_dir) and os.listdir(model_dir):
                status['model_status'] = 'available'
            else:
                status['model_status'] = 'not_trained'
                
        except Exception as e:
            logger.error(f"Error retrieving system status: {e}")
            status['error'] = str(e)
        
        return status

def main():
    """Main entry point for the production system"""
    parser = argparse.ArgumentParser(description='Production Knowledge Graph System')
    parser.add_argument('--config', default='config/production_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--action', choices=['full_pipeline', 'status', 'vcf_only', 'phenotype_only'],
                       default='full_pipeline', help='Action to perform')
    parser.add_argument('--vcf-dir', help='VCF files directory')
    parser.add_argument('--phenotype-dir', help='Phenotype files directory')
    
    args = parser.parse_args()
    
    # Initialize system
    kg_system = ProductionKGSystem(config_file=args.config)
    
    if args.action == 'full_pipeline':
        # Run complete pipeline
        results = kg_system.run_full_pipeline()
        print(json.dumps(results, indent=2))
        
    elif args.action == 'status':
        # Get system status
        kg_system.initialize_database()
        status = kg_system.get_system_status()
        print(json.dumps(status, indent=2))
        
    elif args.action == 'vcf_only':
        # Process VCF data only
        kg_system.initialize_database()
        kg_system.initialize_components()
        results = kg_system.process_vcf_data(args.vcf_dir)
        print(json.dumps(results, indent=2))
        
    elif args.action == 'phenotype_only':
        # Process phenotype data only
        kg_system.initialize_database()
        kg_system.initialize_components()
        results = kg_system.process_phenotype_data(args.phenotype_dir)
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
