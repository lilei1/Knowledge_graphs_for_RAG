#!/usr/bin/env python3
"""
VCF Data Integration Pipeline for Production Knowledge Graph

This module handles the ingestion of millions of genotypes from VCF files,
normalizes variant IDs, and creates efficient graph relationships.
"""

import pandas as pd
import numpy as np
import os
import gzip
import logging
from typing import Dict, List, Optional, Tuple, Iterator, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from neo4j import GraphDatabase
import hashlib
import json
from production_schema import ProductionSchema, NodeType, RelationshipType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VCFVariant:
    """Represents a variant from VCF file"""
    chromosome: str
    position: int
    variant_id: str
    ref_allele: str
    alt_alleles: List[str]
    quality: Optional[float]
    filter_status: str
    info: Dict[str, Any]
    genotypes: Dict[str, str]  # sample_id -> genotype

@dataclass
class ProcessingStats:
    """Statistics for VCF processing"""
    total_variants: int = 0
    processed_variants: int = 0
    skipped_variants: int = 0
    total_genotypes: int = 0
    processing_time: float = 0.0

class VCFProcessor:
    """High-performance VCF file processor for knowledge graph integration"""
    
    def __init__(self, neo4j_driver: GraphDatabase.driver, batch_size: int = 10000):
        self.driver = neo4j_driver
        self.batch_size = batch_size
        self.schema = ProductionSchema()
        self.stats = ProcessingStats()
        
    def parse_vcf_header(self, vcf_file: str) -> Tuple[List[str], Dict[str, Any]]:
        """Parse VCF header to extract sample names and metadata"""
        samples = []
        metadata = {}
        
        open_func = gzip.open if vcf_file.endswith('.gz') else open
        
        with open_func(vcf_file, 'rt') as f:
            for line in f:
                if line.startswith('##'):
                    # Parse metadata lines
                    if '=' in line:
                        key_value = line[2:].strip().split('=', 1)
                        if len(key_value) == 2:
                            metadata[key_value[0]] = key_value[1]
                elif line.startswith('#CHROM'):
                    # Parse sample names from header line
                    fields = line.strip().split('\t')
                    if len(fields) > 9:
                        samples = fields[9:]  # Sample names start from column 10
                    break
        
        logger.info(f"Found {len(samples)} samples in VCF file")
        return samples, metadata
    
    def parse_vcf_line(self, line: str, samples: List[str]) -> Optional[VCFVariant]:
        """Parse a single VCF line into VCFVariant object"""
        fields = line.strip().split('\t')
        
        if len(fields) < 8:
            return None
        
        # Basic variant information
        chrom = fields[0]
        pos = int(fields[1])
        variant_id = fields[2] if fields[2] != '.' else f"{chrom}_{pos}"
        ref = fields[3]
        alt = fields[4].split(',') if fields[4] != '.' else []
        qual = float(fields[5]) if fields[5] != '.' else None
        filter_status = fields[6]
        
        # Parse INFO field
        info = {}
        if len(fields) > 7 and fields[7] != '.':
            for info_item in fields[7].split(';'):
                if '=' in info_item:
                    key, value = info_item.split('=', 1)
                    info[key] = value
                else:
                    info[info_item] = True
        
        # Parse genotypes
        genotypes = {}
        if len(fields) > 9:  # Has genotype data
            format_fields = fields[8].split(':') if len(fields) > 8 else ['GT']
            
            for i, sample in enumerate(samples):
                if i + 9 < len(fields):
                    genotype_data = fields[i + 9].split(':')
                    if len(genotype_data) > 0:
                        genotypes[sample] = genotype_data[0]  # GT is first field
        
        return VCFVariant(
            chromosome=chrom,
            position=pos,
            variant_id=variant_id,
            ref_allele=ref,
            alt_alleles=alt,
            quality=qual,
            filter_status=filter_status,
            info=info,
            genotypes=genotypes
        )
    
    def normalize_variant_id(self, variant: VCFVariant) -> str:
        """Create normalized variant ID for consistent identification"""
        # Create standardized variant ID: chr_pos_ref_alt
        alt_string = '_'.join(variant.alt_alleles) if variant.alt_alleles else 'REF'
        normalized_id = f"{variant.chromosome}_{variant.position}_{variant.ref_allele}_{alt_string}"
        
        # Create hash for very long IDs
        if len(normalized_id) > 100:
            hash_obj = hashlib.md5(normalized_id.encode())
            normalized_id = f"VAR_{hash_obj.hexdigest()[:16]}"
        
        return normalized_id
    
    def create_variant_node(self, variant: VCFVariant) -> Dict[str, Any]:
        """Create variant node data"""
        normalized_id = self.normalize_variant_id(variant)
        
        # Determine variant type
        variant_type = "SNP"
        if variant.alt_alleles:
            for alt in variant.alt_alleles:
                if len(alt) != len(variant.ref_allele):
                    variant_type = "INDEL"
                    break
        
        # Calculate allele frequency if available
        allele_freq = None
        if 'AF' in variant.info:
            try:
                allele_freq = float(variant.info['AF'].split(',')[0])
            except (ValueError, IndexError):
                pass
        
        return {
            'variant_id': normalized_id,
            'original_id': variant.variant_id,
            'chromosome': variant.chromosome,
            'position': variant.position,
            'ref_allele': variant.ref_allele,
            'alt_allele': ','.join(variant.alt_alleles) if variant.alt_alleles else '',
            'variant_type': variant_type,
            'quality_score': variant.quality,
            'filter_status': variant.filter_status,
            'allele_frequency': allele_freq,
            'functional_impact': variant.info.get('ANN', '').split('|')[1] if 'ANN' in variant.info else None
        }
    
    def process_vcf_batch(self, variants: List[VCFVariant]) -> Tuple[List[Dict], List[Dict]]:
        """Process a batch of variants and return node/relationship data"""
        variant_nodes = []
        genotype_relationships = []
        
        for variant in variants:
            # Create variant node
            variant_node = self.create_variant_node(variant)
            variant_nodes.append(variant_node)
            
            # Create genotype relationships
            for sample_id, genotype in variant.genotypes.items():
                if genotype and genotype != './.' and genotype != '.':
                    # Parse genotype (e.g., "0/1", "1/1", "0|1")
                    alleles = genotype.replace('|', '/').split('/')
                    
                    # Calculate dosage (number of alt alleles)
                    dosage = 0
                    for allele in alleles:
                        if allele.isdigit() and int(allele) > 0:
                            dosage += 1
                    
                    genotype_rel = {
                        'from_id': sample_id,  # Germplasm ID
                        'to_id': variant_node['variant_id'],
                        'genotype': genotype,
                        'dosage': dosage,
                        'quality_score': variant.quality
                    }
                    genotype_relationships.append(genotype_rel)
        
        return variant_nodes, genotype_relationships
    
    def batch_insert_variants(self, variant_nodes: List[Dict]) -> None:
        """Batch insert variant nodes into Neo4j"""
        if not variant_nodes:
            return
        
        query = """
        UNWIND $variants as variant
        MERGE (v:Variant {variant_id: variant.variant_id})
        SET v += variant
        RETURN count(v) as created
        """
        
        with self.driver.session() as session:
            result = session.run(query, variants=variant_nodes)
            count = result.single()['created']
            logger.info(f"Created/updated {count} variant nodes")
    
    def batch_insert_genotype_relationships(self, relationships: List[Dict]) -> None:
        """Batch insert genotype relationships into Neo4j"""
        if not relationships:
            return
        
        query = """
        UNWIND $relationships as rel
        MATCH (g:Germplasm {germplasm_id: rel.from_id})
        MATCH (v:Variant {variant_id: rel.to_id})
        MERGE (g)-[r:HAS_VARIANT]->(v)
        SET r.genotype = rel.genotype,
            r.dosage = rel.dosage,
            r.quality_score = rel.quality_score
        RETURN count(r) as created
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(query, relationships=relationships)
                count = result.single()['created']
                logger.info(f"Created/updated {count} genotype relationships")
            except Exception as e:
                logger.error(f"Error creating genotype relationships: {e}")
    
    def process_vcf_file(self, vcf_file: str, max_variants: Optional[int] = None) -> ProcessingStats:
        """Process entire VCF file and integrate into knowledge graph"""
        logger.info(f"Processing VCF file: {vcf_file}")
        
        # Parse header
        samples, metadata = self.parse_vcf_header(vcf_file)
        
        # Initialize statistics
        self.stats = ProcessingStats()
        
        # Process variants in batches
        variant_batch = []
        open_func = gzip.open if vcf_file.endswith('.gz') else open
        
        with open_func(vcf_file, 'rt') as f:
            for line_num, line in enumerate(f):
                if line.startswith('#'):
                    continue
                
                # Parse variant
                variant = self.parse_vcf_line(line, samples)
                if variant is None:
                    self.stats.skipped_variants += 1
                    continue
                
                variant_batch.append(variant)
                self.stats.total_variants += 1
                
                # Process batch when full
                if len(variant_batch) >= self.batch_size:
                    self._process_and_insert_batch(variant_batch)
                    variant_batch = []
                
                # Check max variants limit
                if max_variants and self.stats.total_variants >= max_variants:
                    break
                
                # Progress logging
                if line_num % 50000 == 0:
                    logger.info(f"Processed {line_num} lines, {self.stats.total_variants} variants")
        
        # Process remaining variants
        if variant_batch:
            self._process_and_insert_batch(variant_batch)
        
        logger.info(f"VCF processing complete: {self.stats.total_variants} variants, "
                   f"{self.stats.total_genotypes} genotypes")
        
        return self.stats
    
    def _process_and_insert_batch(self, variant_batch: List[VCFVariant]) -> None:
        """Process and insert a batch of variants"""
        variant_nodes, genotype_relationships = self.process_vcf_batch(variant_batch)
        
        # Insert into Neo4j
        self.batch_insert_variants(variant_nodes)
        self.batch_insert_genotype_relationships(genotype_relationships)
        
        # Update statistics
        self.stats.processed_variants += len(variant_nodes)
        self.stats.total_genotypes += len(genotype_relationships)
    
    def create_germplasm_nodes_from_samples(self, samples: List[str], species: str = "Zea mays") -> None:
        """Create germplasm nodes for VCF samples if they don't exist"""
        logger.info(f"Creating germplasm nodes for {len(samples)} samples")
        
        germplasm_data = []
        for sample in samples:
            germplasm_data.append({
                'germplasm_id': sample,
                'name': sample,
                'species': species
            })
        
        query = """
        UNWIND $germplasm as g
        MERGE (germ:Germplasm {germplasm_id: g.germplasm_id})
        SET germ += g
        RETURN count(germ) as created
        """
        
        with self.driver.session() as session:
            result = session.run(query, germplasm=germplasm_data)
            count = result.single()['created']
            logger.info(f"Created/updated {count} germplasm nodes")

def main():
    """Example usage of VCF integration pipeline"""
    # This would be called with real VCF files in production
    logger.info("VCF Integration Pipeline - Production Ready")
    logger.info("This module provides high-performance VCF processing for knowledge graphs")
    logger.info("Key features:")
    logger.info("- Batch processing for millions of variants")
    logger.info("- Normalized variant IDs for consistency")
    logger.info("- Efficient Neo4j integration")
    logger.info("- Support for compressed VCF files")
    logger.info("- Comprehensive genotype relationship modeling")

if __name__ == "__main__":
    main()
