#!/usr/bin/env python3
"""
Production Knowledge Graph Schema for Scaled Biological Applications

This module defines the enhanced schema for a production-ready biological knowledge graph
capable of handling millions of genotypes, real phenotypic data, and complex breeding relationships.
"""

import pandas as pd
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from neo4j import GraphDatabase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeType(Enum):
    """Enhanced node types for production biological knowledge graph"""
    # Core biological entities
    GENE = "Gene"
    TRAIT = "Trait" 
    VARIANT = "Variant"
    QTL = "QTL"
    CHROMOSOME = "Chromosome"
    PATHWAY = "Pathway"
    
    # Germplasm and breeding
    GERMPLASM = "Germplasm"
    POPULATION = "Population"
    PEDIGREE = "Pedigree"
    
    # Experimental design
    TRIAL = "Trial"
    ENVIRONMENT = "Environment"
    LOCATION = "Location"
    SEASON = "Season"
    
    # Molecular markers
    MARKER = "Marker"
    SNP = "SNP"
    INDEL = "INDEL"
    
    # Phenotypic measurements
    MEASUREMENT = "Measurement"
    TIMEPOINT = "Timepoint"
    
    # Ontology terms
    ONTOLOGY_TERM = "OntologyTerm"
    GO_TERM = "GOTerm"
    TRAIT_ONTOLOGY = "TraitOntology"

class RelationshipType(Enum):
    """Enhanced relationship types for complex biological interactions"""
    # Gene-trait relationships
    REGULATES = "REGULATES"
    INFLUENCES = "INFLUENCES"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    
    # Genetic relationships
    HAS_VARIANT = "HAS_VARIANT"
    LINKED_TO = "LINKED_TO"
    MAPS_TO = "MAPS_TO"
    LOCATED_ON = "LOCATED_ON"
    
    # Breeding relationships
    PARENT_OF = "PARENT_OF"
    DERIVED_FROM = "DERIVED_FROM"
    MEMBER_OF = "MEMBER_OF"
    
    # Experimental relationships
    MEASURED_IN = "MEASURED_IN"
    TESTED_IN = "TESTED_IN"
    CONDUCTED_IN = "CONDUCTED_IN"
    OBSERVED_AT = "OBSERVED_AT"
    
    # Environmental relationships
    GROWN_IN = "GROWN_IN"
    EXPOSED_TO = "EXPOSED_TO"
    
    # Pathway relationships
    PARTICIPATES_IN = "PARTICIPATES_IN"
    UPSTREAM_OF = "UPSTREAM_OF"
    DOWNSTREAM_OF = "DOWNSTREAM_OF"
    
    # Ontology relationships
    IS_A = "IS_A"
    PART_OF = "PART_OF"
    ANNOTATED_WITH = "ANNOTATED_WITH"

@dataclass
class NodeSchema:
    """Schema definition for a node type"""
    node_type: NodeType
    required_properties: List[str]
    optional_properties: List[str]
    constraints: List[str]
    indexes: List[str]

@dataclass
class RelationshipSchema:
    """Schema definition for a relationship type"""
    relationship_type: RelationshipType
    from_node: NodeType
    to_node: NodeType
    properties: List[str]
    constraints: List[str]

class ProductionSchema:
    """Production-ready schema for biological knowledge graph"""
    
    def __init__(self):
        self.node_schemas = self._define_node_schemas()
        self.relationship_schemas = self._define_relationship_schemas()
    
    def _define_node_schemas(self) -> Dict[NodeType, NodeSchema]:
        """Define comprehensive node schemas"""
        schemas = {}
        
        # Gene node with genomic coordinates and functional annotations
        schemas[NodeType.GENE] = NodeSchema(
            node_type=NodeType.GENE,
            required_properties=['gene_id', 'symbol', 'chromosome', 'start_pos', 'end_pos'],
            optional_properties=['description', 'biotype', 'strand', 'ensembl_id', 'ncbi_id', 'uniprot_id'],
            constraints=['CREATE CONSTRAINT gene_id_unique IF NOT EXISTS FOR (g:Gene) REQUIRE g.gene_id IS UNIQUE'],
            indexes=['CREATE INDEX gene_symbol_index IF NOT EXISTS FOR (g:Gene) ON (g.symbol)',
                    'CREATE INDEX gene_chromosome_index IF NOT EXISTS FOR (g:Gene) ON (g.chromosome)']
        )
        
        # Germplasm node for breeding materials
        schemas[NodeType.GERMPLASM] = NodeSchema(
            node_type=NodeType.GERMPLASM,
            required_properties=['germplasm_id', 'name', 'species'],
            optional_properties=['origin', 'breeding_program', 'release_year', 'pedigree', 'heterotic_group'],
            constraints=['CREATE CONSTRAINT germplasm_id_unique IF NOT EXISTS FOR (g:Germplasm) REQUIRE g.germplasm_id IS UNIQUE'],
            indexes=['CREATE INDEX germplasm_name_index IF NOT EXISTS FOR (g:Germplasm) ON (g.name)',
                    'CREATE INDEX germplasm_species_index IF NOT EXISTS FOR (g:Germplasm) ON (g.species)']
        )
        
        # Variant node for genetic variants
        schemas[NodeType.VARIANT] = NodeSchema(
            node_type=NodeType.VARIANT,
            required_properties=['variant_id', 'chromosome', 'position', 'ref_allele', 'alt_allele'],
            optional_properties=['variant_type', 'quality_score', 'allele_frequency', 'functional_impact'],
            constraints=['CREATE CONSTRAINT variant_id_unique IF NOT EXISTS FOR (v:Variant) REQUIRE v.variant_id IS UNIQUE'],
            indexes=['CREATE INDEX variant_position_index IF NOT EXISTS FOR (v:Variant) ON (v.chromosome, v.position)',
                    'CREATE INDEX variant_type_index IF NOT EXISTS FOR (v:Variant) ON (v.variant_type)']
        )
        
        # Trial node for field experiments
        schemas[NodeType.TRIAL] = NodeSchema(
            node_type=NodeType.TRIAL,
            required_properties=['trial_id', 'name', 'year', 'design_type'],
            optional_properties=['description', 'planting_date', 'harvest_date', 'plot_size', 'replication'],
            constraints=['CREATE CONSTRAINT trial_id_unique IF NOT EXISTS FOR (t:Trial) REQUIRE t.trial_id IS UNIQUE'],
            indexes=['CREATE INDEX trial_year_index IF NOT EXISTS FOR (t:Trial) ON (t.year)',
                    'CREATE INDEX trial_design_index IF NOT EXISTS FOR (t:Trial) ON (t.design_type)']
        )
        
        # Environment node for environmental conditions
        schemas[NodeType.ENVIRONMENT] = NodeSchema(
            node_type=NodeType.ENVIRONMENT,
            required_properties=['environment_id', 'location', 'year'],
            optional_properties=['temperature_avg', 'precipitation', 'soil_type', 'irrigation', 'stress_type'],
            constraints=['CREATE CONSTRAINT environment_id_unique IF NOT EXISTS FOR (e:Environment) REQUIRE e.environment_id IS UNIQUE'],
            indexes=['CREATE INDEX environment_location_index IF NOT EXISTS FOR (e:Environment) ON (e.location)',
                    'CREATE INDEX environment_year_index IF NOT EXISTS FOR (e:Environment) ON (e.year)']
        )
        
        # Trait node with ontology integration
        schemas[NodeType.TRAIT] = NodeSchema(
            node_type=NodeType.TRAIT,
            required_properties=['trait_id', 'name', 'category'],
            optional_properties=['description', 'unit', 'method', 'crop_ontology_id', 'heritability'],
            constraints=['CREATE CONSTRAINT trait_id_unique IF NOT EXISTS FOR (t:Trait) REQUIRE t.trait_id IS UNIQUE'],
            indexes=['CREATE INDEX trait_name_index IF NOT EXISTS FOR (t:Trait) ON (t.name)',
                    'CREATE INDEX trait_category_index IF NOT EXISTS FOR (t:Trait) ON (t.category)']
        )
        
        # Measurement node for phenotypic data
        schemas[NodeType.MEASUREMENT] = NodeSchema(
            node_type=NodeType.MEASUREMENT,
            required_properties=['measurement_id', 'value', 'timestamp'],
            optional_properties=['unit', 'method', 'quality_flag', 'replicate', 'observer'],
            constraints=['CREATE CONSTRAINT measurement_id_unique IF NOT EXISTS FOR (m:Measurement) REQUIRE m.measurement_id IS UNIQUE'],
            indexes=['CREATE INDEX measurement_timestamp_index IF NOT EXISTS FOR (m:Measurement) ON (m.timestamp)',
                    'CREATE INDEX measurement_value_index IF NOT EXISTS FOR (m:Measurement) ON (m.value)']
        )
        
        return schemas
    
    def _define_relationship_schemas(self) -> Dict[RelationshipType, RelationshipSchema]:
        """Define comprehensive relationship schemas"""
        schemas = {}
        
        # Germplasm-Variant relationships for genotypic data
        schemas[RelationshipType.HAS_VARIANT] = RelationshipSchema(
            relationship_type=RelationshipType.HAS_VARIANT,
            from_node=NodeType.GERMPLASM,
            to_node=NodeType.VARIANT,
            properties=['genotype', 'dosage', 'quality_score'],
            constraints=[]
        )
        
        # Gene-Trait regulatory relationships
        schemas[RelationshipType.REGULATES] = RelationshipSchema(
            relationship_type=RelationshipType.REGULATES,
            from_node=NodeType.GENE,
            to_node=NodeType.TRAIT,
            properties=['effect_size', 'confidence', 'evidence_type', 'publication'],
            constraints=[]
        )
        
        # Trial-Environment relationships
        schemas[RelationshipType.CONDUCTED_IN] = RelationshipSchema(
            relationship_type=RelationshipType.CONDUCTED_IN,
            from_node=NodeType.TRIAL,
            to_node=NodeType.ENVIRONMENT,
            properties=['start_date', 'end_date', 'management_practices'],
            constraints=[]
        )
        
        # Germplasm-Measurement relationships for phenotypic data
        schemas[RelationshipType.MEASURED_IN] = RelationshipSchema(
            relationship_type=RelationshipType.MEASURED_IN,
            from_node=NodeType.GERMPLASM,
            to_node=NodeType.MEASUREMENT,
            properties=['trial_id', 'plot_id', 'block', 'replicate'],
            constraints=[]
        )
        
        return schemas
    
    def create_schema_constraints(self, driver: GraphDatabase.driver) -> None:
        """Create all schema constraints and indexes"""
        logger.info("Creating schema constraints and indexes...")
        
        with driver.session() as session:
            # Create node constraints and indexes
            for node_type, schema in self.node_schemas.items():
                logger.info(f"Creating constraints for {node_type.value}")
                
                for constraint in schema.constraints:
                    try:
                        session.run(constraint)
                        logger.info(f"Created constraint: {constraint}")
                    except Exception as e:
                        logger.warning(f"Constraint may already exist: {e}")
                
                for index in schema.indexes:
                    try:
                        session.run(index)
                        logger.info(f"Created index: {index}")
                    except Exception as e:
                        logger.warning(f"Index may already exist: {e}")
    
    def validate_node_data(self, node_type: NodeType, data: Dict[str, Any]) -> bool:
        """Validate node data against schema"""
        if node_type not in self.node_schemas:
            logger.error(f"Unknown node type: {node_type}")
            return False
        
        schema = self.node_schemas[node_type]
        
        # Check required properties
        for prop in schema.required_properties:
            if prop not in data:
                logger.error(f"Missing required property '{prop}' for {node_type.value}")
                return False
        
        return True
    
    def get_node_creation_query(self, node_type: NodeType) -> str:
        """Generate Cypher query for creating nodes of given type"""
        schema = self.node_schemas[node_type]
        all_props = schema.required_properties + schema.optional_properties
        
        # Create parameter placeholders
        prop_params = ', '.join([f'{prop}: ${prop}' for prop in all_props])
        
        return f"""
        MERGE (n:{node_type.value} {{{prop_params}}})
        RETURN n
        """
    
    def get_relationship_creation_query(self, rel_type: RelationshipType) -> str:
        """Generate Cypher query for creating relationships of given type"""
        schema = self.relationship_schemas[rel_type]
        
        # Create parameter placeholders for relationship properties
        if schema.properties:
            prop_params = ', '.join([f'{prop}: ${prop}' for prop in schema.properties])
            rel_props = f' {{{prop_params}}}'
        else:
            rel_props = ''
        
        return f"""
        MATCH (from:{schema.from_node.value} {{id: $from_id}})
        MATCH (to:{schema.to_node.value} {{id: $to_id}})
        MERGE (from)-[r:{rel_type.value}{rel_props}]->(to)
        RETURN r
        """
